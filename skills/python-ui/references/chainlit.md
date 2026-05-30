# Chainlit ⚠️

> **Status check first:** Founding team left May 2025, now community-maintained, security CVEs in late 2025. Verify the package has been patched (check release notes since the CVE date) before adding to any project that handles sensitive data or is customer-facing.
>
> **Default recommendation in 2026:** prefer NiceGUI's chat primitives for new chat UIs unless Chainlit-specific features (chain-of-thought UI, retrieval tracing) are critical.

## When Chainlit is still the right choice
- Internal LLM experimentation behind auth
- Prototypes where you need chain-of-thought / step-by-step UI for free
- Integration tests for agent behavior with a UI fallback
- Migration of existing Chainlit apps (don't rewrite for the sake of rewriting)

## Project setup

```bash
pip install chainlit
chainlit run app.py -w  # -w for hot reload in dev
```

## Minimal chat app

```python
# app.py
import chainlit as cl

@cl.on_chat_start
async def start():
    await cl.Message(content="Hello! How can I help?").send()

@cl.on_message
async def main(message: cl.Message):
    response = f"You said: {message.content}"
    await cl.Message(content=response).send()
```

## With PydanticAI

```python
import chainlit as cl
from pydantic_ai import Agent

agent = Agent("openai:gpt-5.4-mini", system_prompt="You are helpful.")

@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])

@cl.on_message
async def main(message: cl.Message):
    history = cl.user_session.get("history", [])

    async with cl.Step(name="agent") as step:
        result = await agent.run(message.content, message_history=history)
        step.output = result.output

    cl.user_session.set("history", result.all_messages())
    await cl.Message(content=result.output).send()
```

## Streaming

```python
@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    await msg.send()

    async with agent.run_stream(message.content) as stream:
        async for chunk in stream.stream_text(delta=True):
            await msg.stream_token(chunk)

    await msg.update()
```

## Session state

```python
@cl.on_chat_start
async def start():
    cl.user_session.set("user_name", "Anonymous")

@cl.on_message
async def main(msg):
    name = cl.user_session.get("user_name")
    # ...
```

**Critical:** `cl.user_session` is in-memory. Server restart = lost state. For anything beyond a single conversation, persist to a database.

## Steps (chain-of-thought UI)

```python
@cl.on_message
async def main(message: cl.Message):
    async with cl.Step(name="reasoning") as step:
        # do some computation
        step.output = "Thought 1"

    async with cl.Step(name="action") as step:
        # do an action
        step.output = "Did X"

    await cl.Message(content="Final answer").send()
```

This is Chainlit's unique value — built-in visualization of agent reasoning steps. If you don't need this, NiceGUI is simpler.

## Auth

```python
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # check credentials
    if username == "admin" and password == "secret":
        return cl.User(identifier="admin", metadata={"role": "admin"})
    return None
```

**Don't ship without auth.** Chainlit's CVEs in 2025 involved unauthenticated endpoints.

## Deployment

- **Always behind a reverse proxy with TLS** (Caddy, nginx, Traefik)
- **Always with auth enabled**
- **Pin the version explicitly** and read changelog before upgrading (community-maintained, breaking changes possible)
- **Audit `chainlit.md` and config** for any features that expose internal state

## Gotchas

- `cl.user_session` is in-memory only — persist to DB if you need real history
- File uploads land in `.files/` by default — gitignore it and clean periodically
- `chainlit.md` (the welcome screen) is loaded as Markdown — be careful about HTML injection if you template it from user data
- The `-w` flag (watch mode) is dev-only; production runs without it
