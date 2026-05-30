# Gradio

Best for: ML model demos, parameter explorers, single-page interactive tools. Weak as a general app framework.

## Two APIs — pick the right one

### `gr.Interface` — for single function-as-app
```python
import gradio as gr

def classify(text: str) -> dict:
    return {"positive": 0.8, "negative": 0.2}

gr.Interface(
    fn=classify,
    inputs=gr.Textbox(label="Input"),
    outputs=gr.Label(label="Sentiment"),
).launch()
```

Use when: one function, fixed inputs/outputs, no custom layout needed.

### `gr.Blocks` — for everything else
```python
import gradio as gr

with gr.Blocks(title="My App") as demo:
    gr.Markdown("# Welcome")
    with gr.Row():
        with gr.Column():
            input_box = gr.Textbox(label="Prompt")
            submit = gr.Button("Run", variant="primary")
        with gr.Column():
            output = gr.Markdown()

    submit.click(fn=run, inputs=input_box, outputs=output)

demo.launch()
```

Use when: custom layout, multiple components, state, or any non-trivial flow.

## State management

```python
import gradio as gr

with gr.Blocks() as demo:
    # ✅ per-session state
    history = gr.State([])

    def add_message(msg, hist):
        hist = hist + [msg]
        return hist, "\n".join(hist)

    msg = gr.Textbox()
    out = gr.Textbox()
    msg.submit(add_message, [msg, history], [history, out])
```

**Critical:** `gr.State()` is per-session. Module-level lists/dicts are global and shared across users — classic bug. Never store user data in a module-level variable.

## Streaming

```python
def generate(prompt):
    for chunk in stream_from_llm(prompt):
        yield chunk  # accumulates by default

demo = gr.Interface(generate, "text", "text")
```

For replace-each-chunk instead of accumulate, return the full latest string each yield.

## ChatInterface (LLM chat)

```python
import gradio as gr

def respond(message, history):
    # history: list of (user, assistant) tuples
    return f"You said: {message}"

gr.ChatInterface(respond).launch()
```

For streaming chat:
```python
def respond_stream(message, history):
    partial = ""
    for chunk in stream(message):
        partial += chunk
        yield partial

gr.ChatInterface(respond_stream).launch()
```

## File handling

```python
def process(file):
    # file is a tempfile-like object; file.name is the path
    with open(file.name) as f:
        return f.read()[:100]

gr.Interface(process, gr.File(), gr.Textbox()).launch()
```

For images: `gr.Image(type="pil")` returns a PIL Image directly.

## Deployment

- **HuggingFace Spaces:** push to a Space repo; `requirements.txt` + `app.py`. Free tier sleeps after inactivity. Pro tier ($9/mo) keeps it warm.
- **Self-host:** `demo.launch(server_name="0.0.0.0", server_port=7860)`; behind nginx/Caddy with TLS.
- **Railway/Hetzner**: Dockerfile with `gradio` installed; expose 7860.
- **Auth:** `demo.launch(auth=("user", "pass"))` for basic auth — fine for internal, not for production. For real auth, run behind an authenticated proxy.

## Gotchas

- **`demo.launch(share=True)`** creates a public tunnel via Gradio's servers. Don't use in production — it's for quick demos only.
- **`gr.Examples`** with mutable defaults: examples are cached at launch, mutating them mutates the example for everyone.
- **Custom CSS via `css=`**: works but scoped poorly. Major design overhaul is a sign you should be using NiceGUI or SvelteKit.
- **Queue is on by default in newer versions.** If you see "queue full" errors, check `demo.queue(default_concurrency_limit=10)`.

## When NOT to use Gradio
- Multi-page apps → NiceGUI
- Heavy form workflows → NiceGUI
- Public-facing product → SvelteKit/React
- Real-time multi-user collaboration → NiceGUI or full frontend
