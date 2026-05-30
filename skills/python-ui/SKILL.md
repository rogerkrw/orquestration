---
name: python-ui
description: Build UIs in Python — NiceGUI, Gradio, or Chainlit. Use when the project is Python-first and needs a web UI without a separate frontend stack. Covers framework selection, layout, forms, async/streaming, deployment, and the security and maintenance status of each option.
---

# Python UI — NiceGUI / Gradio / Chainlit

For Python-first projects (FastAPI backends, AI demos, data tools, internal apps) where a separate TS frontend would be overhead. Consumed by `swe-backend` and `ux-ui-designer`.

## Framework selection — decide before coding

| Use case | Pick | Why |
|---|---|---|
| Internal tool / dashboard / admin / form-heavy CRUD | **NiceGUI** | Real layout primitives, FastAPI underneath, async-first, runs Quasar+Vue under the hood. Best general-purpose choice. |
| ML model demo, parameter explorer, single-page interactive | **Gradio** | Built for ML I/O patterns; one-liner deployments to HuggingFace Spaces. Weak as a general app framework. |
| Chat UI for an LLM agent | **Chainlit** ⚠️ or NiceGUI | Chainlit has chat-first primitives but **security/maintenance concerns** (see below). NiceGUI's `ui.chat_message` is a viable alternative. |
| Real production app with auth, multi-page, complex state | **None of these — use SvelteKit/React** | All three are best for tools and demos, not customer-facing products. |

## ⚠️ Chainlit status (verified 2026)

- Founding team left in May 2025; pivoted to a separate startup
- Now community-maintained
- Security vulnerabilities surfaced in late 2025
- **Do not use** for anything customer-facing or handling sensitive data
- **Acceptable** for internal LLM experimentation behind auth
- For new chat UIs, prefer NiceGUI's chat primitives or a small SvelteKit app

## Core rules
1. **NiceGUI is built on FastAPI.** If the project already has FastAPI, NiceGUI mounts cleanly — no duplicate servers.
2. **Long operations must be async** in all three. Sync calls block the entire event loop and freeze every connected user.
3. **State scoping matters.** Global module state is shared across all users — use per-session/per-client containers (NiceGUI: `app.storage.user`; Gradio: `gr.State()`; Chainlit: `cl.user_session`).
4. **Don't ship without auth** unless the surface is truly internal/local. None of these have first-class auth — wrap with FastAPI auth (NiceGUI) or run behind a reverse proxy with auth (Gradio, Chainlit).
5. **Streaming requires async generators** — `yield` from an async function. Returning a list at the end defeats the purpose.

## Top 5 gotchas
1. **NiceGUI sync function in async context.** Calling a blocking function (e.g., `requests.get`) inside an event handler freezes everyone. Use `httpx.AsyncClient` or wrap with `run.io_bound()`.
2. **Gradio `gr.State()` confusion.** `gr.State()` is per-session; module-level variables are global and shared. Hot bug source.
3. **Chainlit `cl.user_session` is in-memory.** Restart wipes it. For real persistence, use a database explicitly.
4. **NiceGUI `ui.run(reload=True)` in production.** `reload=True` is for dev only — disables proper multi-worker mode. Production: `reload=False` + run behind a process manager.
5. **HuggingFace Spaces auto-sleep.** Free Gradio Spaces sleep after inactivity; first request after wake takes 30–60s. Use Pro tier or self-host for production.

## When to load references
- Building with NiceGUI (any case) → `references/nicegui.md`
- ML demo or model UI → `references/gradio.md`
- Chat UI with Chainlit (after reading the warning above) → `references/chainlit.md`
