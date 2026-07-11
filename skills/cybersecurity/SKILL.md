---
name: cybersecurity
description: Application security applied to FastAPI/SvelteKit + Railway/Hetzner stacks. Covers OWASP Top 10:2025, auth, secrets, transport, dependency hygiene, headers, CSP, incident triage. Use for security reviews, threat modeling, pre-deploy audits, dependency vulnerabilities, or any security question on a Python/TS web stack.
---

# Cybersecurity — Web Stack Edition

Consumed by `devsecops` (primary) and `code-reviewer` (for security-focused reviews). Applied to the stack: FastAPI + SvelteKit + Railway/Hetzner/Coolify + PostgreSQL.

## OWASP Top 10:2025 — quick map

| # | Category | Stack-specific watchouts |
|---|---|---|
| 1 | **Broken Access Control** (now includes SSRF) | FastAPI: every endpoint needs an auth dependency; never trust `user_id` from request body. SvelteKit: check `locals.user` in `+page.server.ts` load + actions. SSRF: validate any URL the server fetches against an allowlist. |
| 2 | **Security Misconfiguration** ⬆ | No debug mode in prod. Set security headers (see below). Disable docs (`docs_url=None`) in prod or auth-gate them. |
| 3 | **Software Supply Chain Failures** ⬆ (new) | Pin dependencies. Audit `uv.lock`/`package-lock.json` regularly. `pip-audit` and `npm audit` in CI. Broader than "vulnerable components": build systems and tooling too. |
| 4 | Cryptographic Failures ⬇ | Don't roll your own crypto. Use `pwdlib` w/ Argon2 (Python) or `@node-rs/argon2` (TS) for passwords. TLS 1.3 only at the edge. |
| 5 | Injection ⬇ | Use parametrized queries always — SQLAlchemy `text()` with bindparams, never f-strings into SQL. Validate user input with Pydantic / Zod at the boundary. |
| 6 | Insecure Design | Threat-model before shipping. Default-deny on all auth checks. |
| 7 | Authentication Failures | Rate-limit login. Lockout after N failures. MFA where it matters. Session fixation prevention. |
| 8 | Software & Data Integrity Failures | SRI for third-party scripts. Verify webhooks with HMAC. Sign release artifacts. |
| 9 | Logging & Alerting Failures | Log auth events, admin actions, data access — and alert on them. Logfire for traces; PII redaction at log time. |
| 10 | Mishandling of Exceptional Conditions (new) | Don't "fail open": an unhandled exception must deny, not bypass. Custom exception handlers return generic messages; no stack traces to the client. Consistent error paths. |

## Core rules (always apply)
1. **Validate at the boundary.** Pydantic models / Zod schemas on every request body, query, path param. No raw dicts past the boundary.
2. **Auth as a dependency, not a check.** FastAPI: `Depends(get_current_user)` on every route or use `dependencies=[]` at router level. SvelteKit: `event.locals.user` set in `hooks.server.ts`.
3. **Secrets via environment, never in repo.** `pydantic-settings` for Python, `$env/static/private` for SvelteKit. `.env*` always gitignored.
4. **Default-deny CORS.** Specify allowed origins explicitly; never `allow_origins=["*"]` with `allow_credentials=True` (it's a no-op + footgun).
5. **Rate-limit auth endpoints and write endpoints.** `slowapi` for FastAPI, middleware in `hooks.server.ts` for SvelteKit (or use a layer like Cloudflare / fail2ban at infra).

## Top 5 gotchas
1. **`allow_origins=["*"]` + `allow_credentials=True`.** Silently ignored by browsers, but devs think it works. The right answer is an explicit origin list.
2. **JWT in localStorage.** XSS-readable. Prefer `httpOnly` cookies; if you must use JWT in JS, accept the XSS risk explicitly and harden everywhere else.
3. **Password hashing with bcrypt's 72-byte limit.** bcrypt silently truncates passwords > 72 bytes. Use Argon2 via `pwdlib` — `PasswordHash.recommended()` gives argon2id out of the box. (`passlib` is unmaintained since 2020 and breaks with bcrypt 4.x; keep it only to read legacy hashes.)
4. **SvelteKit form actions without CSRF awareness.** SvelteKit checks origin by default for actions, but if you accept JSON POSTs to `+server.ts`, you must implement CSRF protection (double-submit cookie or `SameSite=strict`).
5. **Verbose error messages in production.** FastAPI default exception responses include stack info in dev; ensure prod uses a custom exception handler that returns generic messages.

## Quick-hit checklist (before any deploy)
- [ ] No secrets in repo (`git secrets --scan` or `gitleaks`)
- [ ] All dependencies have a recent security audit
- [ ] HTTPS-only at the edge; HSTS header set
- [ ] Auth required on every non-public endpoint
- [ ] CORS origins explicit; no wildcards with credentials
- [ ] Rate limits on login, register, password reset, write-heavy endpoints
- [ ] Security headers: CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy
- [ ] Logging includes auth events; no PII in logs (or redacted)
- [ ] DB backups exist and have been restore-tested in the last 90 days
- [ ] Incident response contact and runbook documented

## When to load references
- Backend (FastAPI) security work → `references/fastapi-security.md`
- Frontend (SvelteKit/React) security work → `references/frontend-security.md`
- Infra, secrets, deployment hardening → `references/infra-secrets.md`
- Pre-deploy audit or incident triage → `references/audit-checklist.md`
