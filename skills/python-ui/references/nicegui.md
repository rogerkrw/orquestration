# NiceGUI 3.0

Built on FastAPI + Vue/Quasar. Async-first. Components map to HTML elements with `ui.*` factories.

## Project setup

```bash
pip install nicegui
```

```python
# main.py
from nicegui import ui

@ui.page("/")
def index():
    ui.label("Hello")

ui.run()  # dev: http://localhost:8080
```

## Layout primitives

```python
from nicegui import ui

with ui.column().classes("w-full max-w-4xl mx-auto p-4 gap-4"):
    ui.label("Title").classes("text-2xl font-bold")
    with ui.row().classes("items-center gap-2"):
        ui.input("Name", placeholder="Alice")
        ui.button("Submit", on_click=handle_submit)
```

- `ui.column()` / `ui.row()` / `ui.grid()` for layout
- `.classes(...)` accepts Tailwind classes (Quasar is also available)
- Use `with` blocks for nesting — the active container is implicit

## Forms (with Pydantic)

```python
from nicegui import ui
from pydantic import BaseModel, EmailStr, ValidationError

class LoginForm(BaseModel):
    email: EmailStr
    password: str

def submit():
    try:
        form = LoginForm(email=email.value, password=password.value)
        ui.notify(f"Welcome {form.email}", type="positive")
    except ValidationError as e:
        ui.notify(str(e), type="negative")

email = ui.input("Email")
password = ui.input("Password", password=True)
ui.button("Login", on_click=submit)
```

## Async + long operations

```python
import httpx
from nicegui import ui, run

async def fetch_data():
    # ✅ Async HTTP — non-blocking
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.example.com/data")
        return r.json()

# For sync-only libraries:
def heavy_sync_work(x):
    # blocks the event loop if called directly!
    return some_blocking_lib.process(x)

async def handle_click():
    # ✅ offload to a thread
    result = await run.io_bound(heavy_sync_work, 42)
    ui.notify(result)
```

## State scoping

```python
from nicegui import app, ui

# ❌ DON'T: shared across all users
current_user = None

# ✅ DO: per-user via app.storage.user (requires storage_secret)
@ui.page("/")
def index():
    user = app.storage.user.get("name", "guest")
    ui.label(f"Hello {user}")

ui.run(storage_secret="REPLACE_ME")
```

| Storage | Scope | Persists |
|---|---|---|
| `app.storage.user` | Per browser/user | Yes (encrypted cookie + server) |
| `app.storage.tab` | Per tab | While tab is open |
| `app.storage.client` | Per WebSocket connection | While connection alive |
| `app.storage.general` | Global, all users | Yes (disk) |

## Mounting on existing FastAPI

```python
from fastapi import FastAPI
from nicegui import ui, app as nicegui_app

api = FastAPI()

@api.get("/api/health")
def health():
    return {"ok": True}

@ui.page("/")
def home():
    ui.label("UI here")

# mount NiceGUI on the same server
ui.run_with(api, storage_secret="REPLACE_ME")

# run with: uvicorn main:api
```

## PydanticAI integration

```python
from nicegui import ui
from pydantic_ai import Agent

agent = Agent("openai:gpt-5.4-mini", system_prompt="You are helpful.")

async def ask(prompt: str):
    result = await agent.run(prompt)
    return result.output

prompt = ui.input("Ask…")
output = ui.markdown()

async def submit():
    output.set_content("Thinking…")
    output.set_content(await ask(prompt.value))

ui.button("Ask", on_click=submit)
```

For streaming:
```python
async def stream():
    output.set_content("")
    async with agent.run_stream(prompt.value) as stream:
        async for chunk in stream.stream_text(delta=True):
            output.content += chunk
```

## Deployment

- **Behind nginx/Caddy with TLS**, never expose port 8080 directly
- **Use `reload=False`** in production
- **`storage_secret` is mandatory** if you use `app.storage.user`
- **Single worker** unless you set up sticky sessions (NiceGUI uses WebSockets)
- **Docker**: `python:3.12-slim` base; expose 8080; `CMD ["python", "main.py"]`
- **Railway/Hetzner+Coolify**: works out of the box with a Dockerfile or Procfile

## Auth pattern (minimal)

```python
from fastapi import HTTPException
from nicegui import ui, app

@app.middleware("http")
async def auth(request, call_next):
    if not request.cookies.get("session"):
        return RedirectResponse("/login")
    return await call_next(request)
```

For real auth use FastAPI's `OAuth2PasswordBearer` or a library like `fastapi-users`.
