# Infrastructure, Secrets, and Logging

## Secrets pattern (Python — pydantic-settings)

```python
# settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",  # crash on unknown env vars — catches typos
    )

    database_url: str
    jwt_secret: str
    sentry_dsn: str | None = None
    env: str = "development"

settings = Settings()  # fail-fast on missing required values at import time
```

`extra="forbid"` is the underused gem — it crashes on typos in env var names instead of silently using defaults.

## Secrets pattern (SvelteKit)

```ts
// src/lib/server/config.ts — server-only by convention
import { env } from '$env/dynamic/private';

if (!env.DATABASE_URL) throw new Error("Missing DATABASE_URL");
if (!env.JWT_SECRET) throw new Error("Missing JWT_SECRET");

export const config = {
  databaseUrl: env.DATABASE_URL,
  jwtSecret: env.JWT_SECRET,
  env: env.NODE_ENV ?? "development"
};
```

Fail-fast at startup. A misconfigured app should not boot.

## Secret rotation

- **Database creds:** rotate quarterly minimum; immediately on suspicion.
- **JWT signing keys:** support old + new keys during rotation window; sign with new, verify with both for 24h, then drop old.
- **Webhook secrets:** rotate when the third party allows; keep an overlap window.
- **OAuth client secrets:** rotate on provider's schedule (varies).

Never store secrets in:
- Git (use `gitleaks` in pre-commit)
- Docker images (use runtime env or secret mounts)
- Frontend bundles (`PUBLIC_*` vars are visible to anyone — they're not secrets)
- Logs (redact at logging time, not after the fact)

## Railway secrets

```bash
railway variables set DATABASE_URL=postgresql://...
railway variables --kv  # list
```

Railway encrypts at rest and injects at runtime. Use Railway's variable references (`${{Postgres.DATABASE_URL}}`) for service-to-service.

## Hetzner + Coolify secrets

- Coolify has env var management per-app in the UI
- For sensitive secrets, use Coolify's "Secret" type (vs. "Environment Variable") — it's hidden in the UI after creation
- For dynamic secrets (rotating credentials), use Doppler or HashiCorp Vault as the source of truth, with Coolify reading via API

## Docker hardening

```dockerfile
# ❌ Don't run as root
FROM python:3.12-slim
USER root
COPY . /app

# ✅ Drop privileges
FROM python:3.12-slim AS builder
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
RUN useradd -m -u 1000 app
COPY --from=builder --chown=app:app /root/.venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
USER app
WORKDIR /app
COPY --chown=app:app . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- Multi-stage to reduce attack surface (no build tools in final image)
- Non-root user (UID >= 1000)
- `--chown` on COPY to set ownership
- No SSH server, no shell access in production images
- `EXPOSE` is documentation, not security — bind explicitly

## Network exposure

- **Default-deny ingress.** Railway and Coolify expose nothing by default; you opt in per service.
- **Private networking** for service-to-service (Railway's private network, Coolify's docker network). Public IP only at the edge proxy.
- **Database NEVER public.** Always behind the application's network. If you need external access, use a bastion / SSH tunnel.

## Logging without leaking PII

```python
import structlog
from structlog.processors import CallsiteParameter

def redact_pii(_, __, event_dict):
    for key in ("password", "token", "api_key", "ssn", "credit_card"):
        if key in event_dict:
            event_dict[key] = "[REDACTED]"
    return event_dict

structlog.configure(processors=[
    redact_pii,
    structlog.processors.JSONRenderer(),
])

logger = structlog.get_logger()

# ✅ Logs without exposing the password value
logger.info("login_attempt", email=email, password=password)
```

For Logfire:
```python
import logfire
logfire.configure(scrubbing=logfire.ScrubbingOptions(extra_patterns=["my-secret-*"]))
```

## Backups and restore

- **Database backups daily.** Automated, off-site (different region/provider).
- **Restore-test quarterly.** A backup you've never restored is a hope, not a backup.
- **Encrypted at rest.** Provider-side or `pgbackrest` with GPG for self-managed.
- **Retention: 30d daily + 12 monthly + 7 yearly** is a reasonable default; adjust for compliance.

## Incident response — minimum runbook

1. **Detect:** Logfire alerts on error rate spikes, auth failures, 5xx surges
2. **Triage:** identify scope (which users, which data, time window)
3. **Contain:** revoke compromised tokens; disable affected endpoints; rotate secrets
4. **Communicate:** notify affected users within 72h (GDPR window); status page update
5. **Postmortem:** blameless writeup; root cause; action items with owners
6. **Verify:** action items closed; new monitors in place to detect recurrence
