---
name: qa-testing
description: Test authorship and quality across Python (pytest + httpx) and TypeScript (vitest + playwright) stacks, plus PydanticAI agent testing. Use when writing new tests, reviewing test coverage, investigating flaky failures, or building a test strategy for a feature. Loaded by qa-tester agent.
---

# QA Testing

For `qa-tester` (primary) and `code-reviewer` (when assessing test coverage).

## Runtime baseline

Use the project's declared runtime and lockfile as the source of truth. For new TypeScript
projects, Node 24 LTS is a safe default; current Vitest/Playwright versions may require a
newer Node and Vite combination, so check their official compatibility notes before upgrading.
Do not introduce a second test runner merely to follow a newer version.

## Testing philosophy

**Test behavior, not implementation.** A test that asserts "function X calls function Y" breaks on every refactor and protects nothing. A test that asserts "user can register and log in" survives refactors and catches real regressions.

**Test pyramid (still right):**
- **Many unit tests** (fast, isolated, pure)
- **Some integration tests** (real DB, real HTTP — slower but catch real bugs)
- **Few E2E tests** (browser-driven, slowest, brittlest — cover golden paths only)

Inverted pyramids (lots of E2E, few unit) are slow, brittle, and a sign that the architecture is hard to unit-test.

## Tools by stack

| Stack | Unit | Integration | E2E |
|---|---|---|---|
| Python / FastAPI | pytest | pytest + httpx + real DB | playwright-python (rare) |
| Python / PydanticAI agent | pytest + TestModel | pytest + recorded LLM (cassettes) | — |
| SvelteKit | vitest (browser mode) | vitest + msw + real DB | playwright |
| React | vitest + Testing Library | vitest + msw | playwright |
| Mastra agent | vitest | vitest + recorded LLM | — |

## Core rules
1. **Tests live next to the code or in a clear parallel tree** — never far from what they test. `src/foo.py` ↔ `tests/test_foo.py` or `src/foo.test.ts` co-located.
2. **One assertion concept per test.** Multiple `assert` lines for one behavior is fine; testing two unrelated behaviors in one test obscures failures.
3. **Arrange–Act–Assert.** Visible structure. Tests are documentation; structure reveals intent.
4. **No I/O in unit tests.** Network, disk, time — all faked. If you need real I/O, it's an integration test.
5. **No conditional logic in tests.** `if/else` in a test means you're testing two things — split into two tests.

## Top 5 gotchas
1. **Mocking what you don't own.** Mock your collaborators, not third-party libs. Mocking `httpx.AsyncClient` directly couples your tests to httpx; use a fake at your boundary.
2. **Asserting on order in unordered collections.** `assert result == [a, b, c]` when the function returns a set — flaky if hash order changes. Use `assertCountEqual` (Python) or sort before comparing.
3. **Time-dependent tests without `freezegun` / fake timers.** Tests that compare to `datetime.now()` are flaky at midnight UTC and during DST transitions.
4. **Shared mutable test state.** Module-level lists/dicts that tests mutate cause cross-test contamination. Use fixtures with proper teardown.
5. **`asyncio.run` in sync test.** Use `pytest-asyncio` with `@pytest.mark.asyncio` (or `asyncio_mode="auto"` in `pyproject.toml`); never wrap async with `asyncio.run` inside the test.

## Flakiness — detection and response

- Run new tests **5 times** locally before considering them stable
- In CI, mark flaky tests with `@pytest.mark.flaky(reruns=2)` or vitest equivalent
- **A flaky test is worse than no test** — it trains people to ignore failures
- Track flakiness: if a test fails intermittently, fix or delete within a sprint
- Common causes: shared state, network, time, file system, concurrency, ordering assumptions

## Coverage as signal, not target

- 80% line coverage is a common bar but **not a goal**; it's a checkpoint
- 100% coverage on a module says nothing about the quality of the assertions
- Look at branch coverage and missing critical paths, not the percentage
- Lines without coverage that **must** be covered: auth checks, error handling on writes, money-touching code, security boundaries

## When to load references
- Python / FastAPI testing → `references/python-testing.md`
- PydanticAI agent testing → `references/pydanticai-testing.md`
- SvelteKit / React testing → `references/frontend-testing.md`
- Debugging flaky tests → `references/flaky-prevention.md`
