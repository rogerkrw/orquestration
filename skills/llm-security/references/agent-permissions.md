# Agent Permissions & Access Control

## Core principle: LLM agents do not enforce least privilege by default

Agents will use every tool they're given, with whatever permissions those tools have.
The developer is responsible for scoping every tool to the minimum needed.

---

## Tool scoping patterns (PydanticAI)

### ❌ Excessive agency — god-mode agent

```python
@agent.tool
async def execute_anything(ctx: RunContext, command: str) -> str:
    return subprocess.check_output(command, shell=True).decode()
```

### ✅ Least privilege — single-purpose, scoped tool

```python
@agent.tool
async def search_product_catalog(
    ctx: RunContext,
    query: str,
    max_results: int = 5,
) -> list[dict]:
    """Read-only search against public product catalog only."""
    return await catalog_service.search(query, limit=min(max_results, 20))
```

Rules per tool:
- **Single responsibility**: one tool, one action domain
- **Read before write**: expose read-only tools by default; require explicit privilege for writes
- **No shell access**: never expose `subprocess`, `os.system`, or `eval` to an agent
- **Scoped DB access**: DB user for agent has SELECT only (and only on required tables)
- **Timeout**: every tool call must have a timeout; long-running tools block the agent

---

## Multi-agent isolation

When agents call other agents (orchestrator → subagent), each hop must:
1. Re-validate authorization — don't inherit the calling agent's full permissions
2. Pass only the minimum context needed (not the full conversation history)
3. Log the inter-agent call as a distinct audit event

```python
# Wrong: passing full context with potential system prompt leakage
subagent_result = await subagent.run(full_history)

# Right: pass only the structured task
subagent_result = await subagent.run(
    TaskPayload(query=sanitized_query, user_id=ctx.deps.user_id)
)
```

---

## Human-in-the-loop (HITL) triggers

For any action that is:
- **Irreversible** (delete, send email, post externally, charge payment)
- **High-impact** (modify >N records, access sensitive PII, admin operations)
- **Externally visible** (publish, notify, webhook to third party)

...require explicit human confirmation before execution:

```python
@agent.tool
async def send_email(ctx: RunContext, to: str, subject: str, body: str) -> str:
    if not ctx.deps.human_approved:
        raise RequiresApproval(
            action="send_email",
            payload={"to": to, "subject": subject},
            summary=f"Send email to {to}: '{subject}'",
        )
    return await email_service.send(to, subject, body)
```

Expose a confirmation endpoint in the UI; do not allow the LLM to self-approve.

---

## RAG access control

### Problem

Loading all corporate data into a single vector store gives every user root access
to the entire dataset. The LLM retrieves whatever matches the query, regardless of
who should see it.

### Pattern: ACL-filtered retrieval

Apply access control **at retrieval time**, before chunks reach the LLM context:

```python
async def retrieve_with_acl(
    query: str,
    user_id: str,
    user_roles: list[str],
    k: int = 5,
) -> list[str]:
    # Filter candidates by user's permitted namespaces/tags
    permitted_filters = build_acl_filter(user_id, user_roles)
    chunks = await vector_store.similarity_search(
        query=query,
        k=k,
        filter=permitted_filters,  # vector DB metadata filter
    )
    return [c.page_content for c in chunks]
```

Metadata tags on every document at index time: `tenant_id`, `classification_level`,
`permitted_roles`. Never retrieve across tenant boundaries.

### Multi-tenant vector store isolation

Preferred: **separate collections per tenant** (hard isolation).
Acceptable: **metadata filtering** with strict enforcement + audit of filter bypass.
Never: shared collection with no isolation.

---

## Credential-less design for agents

Prefer **workload identity** over static API keys wherever the infrastructure supports
it (AWS IAM roles, GCP Workload Identity, Railway service tokens with short TTL).

Where static keys are unavoidable:
1. Store in secrets manager (not `.env` files, not environment variables in code)
2. Rotate on a schedule (max 90-day TTL)
3. Scope to minimum permissions (`read:catalog`, not `admin:all`)
4. Monitor for unusual usage patterns (spike detection on API key usage)

```python
# PydanticAI agent deps — credentials from secrets manager, not hardcoded
@dataclass
class AgentDeps:
    db_pool: asyncpg.Pool       # connection pool, not connection string
    search_client: SearchClient # pre-authenticated at startup
    user_id: str
    user_roles: list[str]

# Agent never sees raw credentials — it uses pre-authenticated service clients
```

---

## Ollama local model hardening

Default Ollama configuration is insecure for any networked environment:

```bash
# Default (insecure): listens on all interfaces
# Harden: bind to loopback only
OLLAMA_HOST=127.0.0.1:11434

# If Docker: expose only to internal network
# docker-compose.yml
services:
  ollama:
    image: ollama/ollama
    expose: ["11434"]   # internal only — no 'ports' mapping
    networks: [internal]
```

No authentication on Ollama by default. If multiple services need it, proxy behind
FastAPI with auth middleware rather than exposing Ollama directly.
