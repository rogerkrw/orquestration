# Flaky Test Prevention

A flaky test is a test that sometimes passes and sometimes fails without any code change. **It is worse than no test** — it trains the team to ignore failures.

## Common causes and fixes

### 1. Time

| Symptom | Fix |
|---|---|
| Test compares to `datetime.now()` | Freeze time: `freezegun` (Python), `vi.useFakeTimers()` (vitest), `page.clock` (playwright) |
| Test relies on "wait N seconds" | Use explicit waits on conditions, never time |
| Test fails near midnight UTC | Same — freeze time at fixture level |
| Test passes locally, fails in CI tz | Set test tz explicitly: `TZ=UTC pytest` |

```python
# Python — fixture-level frozen time
@pytest.fixture(autouse=True)
def freeze_clock():
    with freeze_time("2026-01-01 12:00:00"):
        yield
```

```ts
// vitest
beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());
```

### 2. Randomness

| Symptom | Fix |
|---|---|
| Test uses `random.choice` directly | Inject a seeded `random.Random` or fix the seed at fixture |
| Test compares unordered collections | Sort before compare, or use set equality |
| `uuid4` in fixture data | Use deterministic UUIDs or replace with sequential IDs in tests |

```python
@pytest.fixture(autouse=True)
def deterministic_random():
    import random
    random.seed(42)
```

### 3. Network / external services

| Symptom | Fix |
|---|---|
| Test sometimes can't reach external API | Mock it (respx for httpx, MSW for fetch) |
| Test depends on third-party uptime | Same — mock; add a contract test that runs separately |
| DNS resolution flakes | Mock at the HTTP client layer, not at DNS |

**Rule:** unit and integration tests should never make real network calls. E2E may, but ideally against your own test environment.

### 4. Database

| Symptom | Fix |
|---|---|
| Tests pass alone, fail in suite | Cross-test contamination; use transaction-rollback fixture |
| Order-dependent failures | Same; tests must be runnable in any order (`pytest --random-order` to detect) |
| "Duplicate key" errors | Each test should set up its own data with unique values, or use rollback |

```python
@pytest_asyncio.fixture
async def db_session(engine):
    async with engine.connect() as conn:
        trans = await conn.begin()
        Session = async_sessionmaker(bind=conn, expire_on_commit=False)
        async with Session() as s:
            yield s
        await trans.rollback()
```

### 5. Concurrency / async

| Symptom | Fix |
|---|---|
| Test passes when run with `-p no:randomly`, fails otherwise | Shared mutable state somewhere |
| `RuntimeError: This event loop is already running` | Mixed sync/async; use `pytest-asyncio` everywhere |
| Test depends on order of async operations | `await` everything; use `asyncio.gather` if intentional parallelism |
| Race condition in production code | The test is right — fix the code |

### 6. File system

| Symptom | Fix |
|---|---|
| Tests write to a shared `/tmp` path | Use `tmp_path` fixture (pytest) or `os.tmpdir()` (Node) per test |
| Tests fail on case-sensitive filesystems (Linux CI vs macOS dev) | Always use canonical case in paths |
| Test reads file that another test wrote | Isolation failure; use per-test temp dir |

### 7. UI / browser

| Symptom | Fix |
|---|---|
| Element not found, sometimes | Use auto-retrying assertions: `expect(locator).toBeVisible()` not `expect(await locator.isVisible()).toBe(true)` |
| Animation timing | Disable animations in test mode: `prefers-reduced-motion: reduce` |
| Network race in E2E | `page.waitForResponse('/api/data')` before assertion |
| Headless vs headed differences | Run headed locally for debugging; require headless to pass before merge |

## Detection

### Run new tests N times before committing

```bash
# pytest
pytest --count=10 tests/test_new_feature.py

# vitest
vitest --run --reporter=verbose tests/new.test.ts && \
  vitest --run --reporter=verbose tests/new.test.ts && \
  vitest --run --reporter=verbose tests/new.test.ts
```

### Random order

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "-p random_order"  # via pytest-random-order
```

Reveals order-dependent tests immediately.

### Parallel execution

```bash
pytest -n auto         # via pytest-xdist
vitest --threads true  # default
```

Reveals shared-state issues.

### CI re-run on failure

```yaml
# GitHub Actions
- run: pytest --reruns 2 --reruns-delay 1
```

**Use sparingly.** Reruns mask flakiness rather than fix it. If a test needs reruns, it should be marked and tracked for fixing, not normalized.

## Response policy

When a test starts flaking:

1. **Reproduce locally.** Run 20 times; if it fails any, it's flaky.
2. **Pin the cause.** Add logging, capture state, identify the variable.
3. **Fix or quarantine within 1 sprint.** Don't let flakiness backlog.
4. **Quarantine syntax:**
   - pytest: `@pytest.mark.flaky` or `@pytest.mark.skip(reason="flaky, tracked in #123")`
   - vitest: `test.skip` or `test.fails`
5. **Track in an issue.** Flaky test count is a quality metric — review monthly.

## Anti-patterns

- **`time.sleep(N)` in tests.** Always replace with a condition wait.
- **`try/except` to swallow failures.** Tests don't catch their own assertion errors.
- **Retrying inside the test.** Either the assertion is right (let it fail) or the code is wrong (fix the code).
- **Ignoring "intermittent" failures.** They are diagnostic signals, not noise.
- **Marking everything flaky to keep CI green.** This is technical debt at compound interest.
