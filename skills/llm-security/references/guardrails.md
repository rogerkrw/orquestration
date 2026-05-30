# Guardrails — Input & Output Security for LLM Harnesses

## Architecture principle

Guardrails live in **application code**, not in model instructions. They must be:
- Deterministic (same input → same block decision)
- Testable (unit-testable, CI-integrated)
- Model-agnostic (survive model swaps)
- Versioned and auditable

```
User Input
    │
    ▼
[Input Guardrail Layer]   ← PII detection, length cap, injection patterns
    │
    ▼
[Prompt Construction]     ← System prompt + sanitized user content, clearly separated
    │
    ▼
[LLM Call]
    │
    ▼
[Output Guardrail Layer]  ← Schema validation, PII scan, content filter
    │
    ▼
[Downstream / User]
```

---

## Input guardrails

### 1. Length and token budget

```python
MAX_PROMPT_CHARS = 4_000   # tune per use case
MAX_TOKENS_OUT   = 1_000   # always set on LLM call

def check_input_length(text: str) -> None:
    if len(text) > MAX_PROMPT_CHARS:
        raise ValueError(f"Input exceeds {MAX_PROMPT_CHARS} characters")
```

### 2. PII detection and redaction (pre-LLM)

Use `presidio-analyzer` + `presidio-anonymizer` (Microsoft, open-source):

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer  = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def redact_pii(text: str, language: str = "pt") -> str:
    results = analyzer.analyze(text=text, language=language)
    return anonymizer.anonymize(text=text, analyzer_results=results).text
```

Key PII entities for Brazilian context: `CPF`, `CNPJ`, `PHONE_NUMBER`, `EMAIL_ADDRESS`,
`CREDIT_CARD`, `IBAN_CODE`, `DATE_TIME`, `PERSON`, `LOCATION`.

Log the **redacted** version, never the original.

### 3. Prompt injection pattern detection

No single regex catches all injections. Layer:
1. **Structural check** — detect role-boundary tokens (`[INST]`, `<|system|>`, `###`)
2. **Instruction override patterns** — "ignore previous instructions", "disregard",
   "forget your guidelines", "you are now", "act as", "jailbreak"
3. **Encoding obfuscation** — base64, rot13, leetspeak fragments in input

```python
import re

INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|prior)\s+instructions",
    r"forget\s+(your|the)\s+(guidelines|rules|instructions)",
    r"you\s+are\s+now\s+",
    r"act\s+as\s+(if\s+you\s+are|a\s+)",
    r"\[INST\]|\[\/INST\]|<\|system\|>|###\s*System",
    r"disregard\s+(your|all)",
]

def detect_injection(text: str) -> bool:
    lower = text.lower()
    return any(re.search(p, lower) for p in INJECTION_PATTERNS)
```

These are heuristics, not guarantees. Log and flag; decide whether to block or allow
with elevated scrutiny based on risk level.

### 4. Context isolation in prompt construction

Clearly delimit user content from system instructions. Never f-string interpolate raw
user input directly into the system prompt:

```python
# WRONG
system = f"You are a helpful assistant. User context: {user_input}"

# RIGHT — user content in a dedicated, labeled block
system = "You are a helpful assistant. Answer only from the provided context."
user_message = f"<user_input>\n{sanitized_input}\n</user_input>"
```

For RAG, label retrieved content separately:
```
<retrieved_documents>
{chunks}
</retrieved_documents>

<user_question>
{question}
</user_question>
```

---

## Output guardrails

### 1. Structured output enforcement (PydanticAI)

Prefer `result_type` on agents. Invalid responses are retried or raised:

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class Answer(BaseModel):
    response: str
    confidence: float  # 0.0–1.0
    sources: list[str]

agent = Agent(model, result_type=Answer)
```

Reject or gate low-confidence responses:
```python
result = await agent.run(query)
if result.data.confidence < 0.7:
    return fallback_response()
```

### 2. Output PII scan (post-LLM)

Run the same presidio pipeline on LLM output before returning to the user or logging:
```python
output = await agent.run(prompt)
safe_output = redact_pii(output.data.response)
```

### 3. Output encoding before downstream use

If LLM output is rendered in HTML (Chainlit, SvelteKit), HTML-encode it:
```python
import html
safe_html = html.escape(llm_output)
```

If output is used in SQL queries — don't. Use parameterized queries; never pass
LLM output directly into a query string.

### 4. Content safety filter

For public-facing apps, add a lightweight toxicity/safety classifier as a second
pass. Options: `detoxify` (open-source, runs locally), or a secondary LLM judge call.

```python
from detoxify import Detoxify

model = Detoxify("multilingual")

def is_safe_output(text: str, threshold: float = 0.7) -> bool:
    scores = model.predict(text)
    return scores["toxicity"] < threshold
```

---

## Guardrail event logging schema

Every guardrail event (block, flag, redact) must be logged:

```json
{
  "event_type": "input_blocked | input_flagged | output_redacted | output_blocked",
  "timestamp": "ISO-8601",
  "session_id": "uuid",
  "user_id": "hashed or pseudonymous",
  "rule_triggered": "injection_pattern | pii_detected | length_exceeded | toxicity",
  "action_taken": "blocked | redacted | flagged_for_review",
  "prompt_hash": "sha256 of sanitized prompt",
  "model_version": "qwen3:4b-instruct"
}
```

Never include raw prompt or response text in the log. Use hashes for correlation.
