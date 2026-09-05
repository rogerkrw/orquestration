---
name: llm-security
description: >
  Security knowledge for web applications that serve as harnesses for LLMs and AI
  agents. Covers OWASP GenAI LLM Top 10:2026, prompt injection defense, input/output
  guardrails, PII redaction, excessive agency prevention, RAG access control, secrets
  management for AI stacks, HTTP hardening, audit logging, and pre-deploy security
  checklists. Trigger on: any mention of LLM security, prompt injection, guardrails,
  AI agent permissions, RAG access control, sensitive data in LLM context, system
  prompt leakage, LLM API keys, or any "is this safe" question about an AI-powered
  app. Also trigger before any deploy of a PydanticAI/Chainlit/FastAPI+LLM
  application. Use alongside the cybersecurity skill for full-stack coverage; this
  skill adds the AI-specific layer on top.
---

# llm-security

Security for LLM harness applications: FastAPI + PydanticAI backends, Python UI
layers (NiceGUI / Gradio / Chainlit), SvelteKit frontends, local models via Ollama,
and cloud LLM APIs. Complements the `cybersecurity` skill (web app baseline) with the
AI-specific threat layer.

> ⚠️ **UI caveat:** Chainlit, NiceGUI and Gradio are application frameworks, not
> authentication or authorization boundaries. Check the current release/security
> posture before adoption and put any non-local deployment behind explicit auth.

## OWASP GenAI LLM Top 10:2026 — quick map

| # | Risk | Harness-level mitigation |
|---|---|---|
| LLM01 | Prompt Injection (direct + indirect) | Input guardrails, context isolation, structured output enforcement |
| LLM02 | Sensitive Information Disclosure | PII redaction pre-LLM, output scanning, no secrets in system prompts |
| LLM03 | Excessive Agency | Least-privilege tools, human-in-the-loop for high-impact actions |
| LLM04 | Supply Chain | Pin model versions, verify checksums, vet third-party tools |
| LLM05 | Data & Model Poisoning | Audit RAG sources, anomaly detection on retrieval, signed training data |
| LLM06 | Unbounded Consumption | Token budgets, rate limiting, cost alerts, prompt length caps |
| LLM07 | Misinformation | Groundedness checks, source citation enforcement, confidence gating |
| LLM08 | Hidden Context Exposure | Isolate system prompts, tool context and retrieved content; do not expose internal context |
| LLM09 | Vector/Embedding Weaknesses | Tenant isolation in vector DBs, ACL at retrieval layer |
| LLM10 | Improper Output Handling | Sanitize/encode outputs before downstream use; prevent XSS/RCE |

> **Critical insight:** System prompts are not security boundaries. LLMs are
> stochastic and cannot be audited line-by-line. All security controls must live
> outside the model in deterministic, auditable application code.

## Always-on rules

**1. No secrets in system prompts**
API keys, passwords, connection strings, role structures → environment variables +
secrets manager. If the model knows it, attackers can extract it.

**2. Least privilege for every tool**
Each PydanticAI tool gets only the permissions it needs for its specific task.
No "god-mode" agents. Prefer multiple single-purpose agents over one omnipotent agent.

**3. Validate and sanitize at both boundaries**
- *Input*: before prompt construction — max length, character allowlists, PII detection
- *Output*: before any downstream use — HTML-encode if rendering, strip executable content

**4. Token and cost budget per request**
Set `max_tokens` on every LLM call. Reject prompts exceeding a character/token cap.
Rate-limit at IP and user level. Set hard spend alerts on LLM provider dashboards.

**5. Structured outputs over freeform where possible**
`response_model=YourPydanticModel` on PydanticAI agents. Reject responses that don't
validate against schema. Removes an entire class of output injection.

**6. Immutable audit log for every LLM interaction**
Log: user ID, session ID, timestamp, prompt hash, response hash, model version,
guardrail events. Never log raw PII — log redacted versions or hashes only.

## Reference files — read when needed

- **`references/guardrails.md`** — input/output guardrail patterns, PII redaction,
  jailbreak detection, structured output enforcement (PydanticAI-specific)
- **`references/agent-permissions.md`** — tool scoping, least privilege patterns,
  human-in-the-loop, multi-agent isolation, RAG access control
- **`references/api-hardening.md`** — FastAPI auth for LLM endpoints, rate limiting,
  HTTP security headers, CORS for Python UI / SvelteKit frontends
- **`references/deploy-checklist.md`** — pre-deploy security checklist: infra,
  secrets, headers, logging, cost controls, red-team prompts

## Gotchas (always in context)

1. **Indirect prompt injection is invisible** — malicious instructions in documents,
   web pages, or emails retrieved by RAG are parsed as legitimate instructions.
   Always isolate external content from the instruction context.

2. **RAG = new attack surface, not a safety shield** — embedding inversion attacks can
   extract source data from vector stores. Enforce ACL at retrieval time, not just
   at query time. Multi-tenant RAG requires hard isolation per tenant.

3. **`allow_origins=["*"]` on LLM API endpoints** — doubly dangerous: exposes both
   the app and the LLM budget. Always restrict CORS to known frontend origins.

4. **Excessive agency chains** — in multi-agent flows, each hop can escalate
   privileges. Validate authorization at every agent boundary, not just at entry.

5. **Logging raw prompts stores PII** — if users paste documents or personal data,
   your logs become a PII store. Redact or hash before persistence.

6. **Local Ollama with no auth** — by default, Ollama listens on `0.0.0.0:11434`
   with no authentication. Bind to `127.0.0.1` only; never expose to public network.

7. **Cost as a security metric** — a spike in token consumption is often the first
   signal of a DoS or prompt injection attack. Monitor spend in real time.
