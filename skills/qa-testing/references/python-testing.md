# Python / FastAPI Testing — pytest

## Project structure

```
src/
  app/
    main.py
    routes/users.py
    services/auth.py
tests/
  conftest.py
  unit/
    test_auth_service.py
  integration/
    test_users_route.py
```

## conftest.py — shared fixtures

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_session

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session
    await engine.dispose()

@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    app.dependency_overrides[get_session] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

For integration tests against a real Postgres: use `testcontainers-python` to spin up a container per test session.

## Rollback-per-test pattern (real DB, no contamination)

```python
@pytest_asyncio.fixture
async def db_session(engine):
    async with engine.connect() as connection:
        trans = await connection.begin()
        Session = async_sessionmaker(bind=connection, expire_on_commit=False)
        async with Session() as session:
            yield session
        await trans.rollback()
```

Each test runs in a transaction that gets rolled back at teardown — true isolation, real DB behavior.

## Async test pattern

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # all async functions auto-marked
```

```python
import pytest

async def test_create_user(client):
    response = await client.post("/users", json={"email": "alice@x.com", "password": "supersecret123"})
    assert response.status_code == 201
    assert response.json()["email"] == "alice@x.com"
```

## Parametrize for table-driven tests

```python
@pytest.mark.parametrize("email,is_valid", [
    ("alice@x.com", True),
    ("invalid", False),
    ("", False),
    ("a@b", False),  # too short
    ("a" * 200 + "@x.com", False),  # too long
])
def test_email_validation(email, is_valid):
    if is_valid:
        UserEmail(email=email)
    else:
        with pytest.raises(ValidationError):
            UserEmail(email=email)
```

Catches edge cases in one place; failure shows which input failed.

## Mocking HTTP (httpx)

Use `respx` for httpx-specific mocking:

```python
import respx
from httpx import Response

@respx.mock
async def test_external_call(service):
    respx.get("https://api.example.com/data").mock(return_value=Response(200, json={"ok": True}))
    result = await service.fetch()
    assert result["ok"] is True
```

For broader interception, `pytest-httpx` is the alternative.

## Time and randomness

```python
from freezegun import freeze_time

@freeze_time("2026-01-15 10:00:00")
def test_token_expiration():
    token = create_token(ttl_hours=1)
    # ... advance time
    with freeze_time("2026-01-15 11:01:00"):
        with pytest.raises(TokenExpired):
            verify_token(token)
```

For randomness: seed at fixture level, or inject a `random.Random` instance into the code under test.

## Snapshot testing (when appropriate)

```python
def test_response_shape(client, snapshot):
    response = client.get("/api/users/1")
    assert response.json() == snapshot
```

With `syrupy`: snapshots in `__snapshots__/` next to test files. Useful for API contract changes; review snapshots in PRs.

## Coverage

```bash
pytest --cov=src --cov-branch --cov-report=term-missing --cov-fail-under=80
```

- `--cov-branch` catches if-else branches, not just lines
- `--cov-fail-under` blocks CI if coverage drops
- `--cov-report=html` for navigable browser report

## Common failures

- **`RuntimeError: This event loop is already running`** → mixed sync/async; use `pytest-asyncio` consistently
- **`sqlalchemy.exc.InvalidRequestError`** → fixture scope mismatch; check that `db_session` and `client` share scope
- **Tests pass individually, fail in suite** → shared state; check for module-level mutables, missing teardown, ordering assumptions
- **Tests fail in CI, pass locally** → likely time zone, file system case sensitivity, or missing env var
