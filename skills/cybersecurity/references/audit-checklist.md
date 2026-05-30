# Audit Checklist — Pre-Deploy & Diff Review

Binary pass / fail / warning. Run before any production deploy and on diff review of security-relevant changes.

## Authentication & Session

- [ ] All non-public endpoints require auth (no accidentally-public endpoint)
- [ ] Passwords hashed with Argon2 (not bcrypt, not SHA256)
- [ ] Session tokens are httpOnly + Secure + SameSite cookies (or justified deviation)
- [ ] Token expiration ≤ 24h for sessions; ≤ 1h for access tokens with refresh
- [ ] Rate limit on `/login`, `/register`, `/password-reset` (max 5/min/IP)
- [ ] Account lockout after N failed attempts (e.g., 10 in 15min)
- [ ] Password reset uses signed, single-use, time-limited tokens
- [ ] MFA available for admin accounts at minimum

## Authorization

- [ ] Every endpoint validates the caller has permission for the requested resource (not just authenticated)
- [ ] User IDs from request bodies/paths are checked against the session user
- [ ] Admin endpoints require explicit role check, not just "logged in"
- [ ] No IDOR (Insecure Direct Object Reference) — `/api/users/{id}/orders` checks `id == session.user.id` or admin
- [ ] Mass assignment prevented (Pydantic models filter by schema; never `**body` into ORM)

## Input Validation

- [ ] Pydantic / Zod schemas on every request body, query, path param
- [ ] No raw SQL with string interpolation (parametrized only)
- [ ] File uploads: size limit, MIME whitelist, virus scan if user-shared
- [ ] URLs the server fetches are validated against an allowlist (SSRF prevention)
- [ ] Numeric inputs have min/max bounds
- [ ] Strings have max length (DoS prevention)

## Output / Rendering

- [ ] No `{@html}` / `dangerouslySetInnerHTML` without sanitization
- [ ] User-controlled URLs in `href` validate scheme
- [ ] `target="_blank"` always with `rel="noopener noreferrer"`
- [ ] JSON responses never include sensitive fields (password_hash, internal IDs)
- [ ] Error responses generic in production (no stack traces, no SQL queries)

## Transport & Headers

- [ ] HTTPS-only (redirect HTTP → HTTPS at the edge)
- [ ] HSTS header set with `max-age >= 63072000`
- [ ] Security headers: X-Content-Type-Options, X-Frame-Options, Referrer-Policy
- [ ] CSP defined, no `'unsafe-inline'` for scripts
- [ ] CORS origins explicit, no `*` with credentials
- [ ] TLS 1.3 only at the edge (or 1.2+ minimum)

## Secrets & Config

- [ ] No secrets in repo (`gitleaks` clean)
- [ ] All env vars validated at startup (fail-fast)
- [ ] Production has `DEBUG=False`, `docs_url=None` (or auth-gated)
- [ ] Database credentials are read-only where possible (separate user for read/write)
- [ ] Backup credentials separate from runtime credentials

## Dependencies

- [ ] `pip-audit` / `npm audit` clean (no high/critical)
- [ ] Lockfiles committed (`uv.lock`, `package-lock.json`)
- [ ] Dependencies updated within last 90 days
- [ ] Subresource Integrity on third-party scripts
- [ ] Direct dependencies reviewed; no abandoned packages (last commit > 1y)

## Infrastructure

- [ ] Docker containers run as non-root user
- [ ] Database NOT publicly accessible
- [ ] Internal services on private network
- [ ] Firewall rules default-deny ingress
- [ ] SSH key-only auth on any VM (no password)
- [ ] Automated security updates on base images / OS

## Logging & Monitoring

- [ ] PII redacted in logs
- [ ] Auth events logged (login, logout, failed login, password change)
- [ ] Admin actions logged with actor + timestamp + before/after
- [ ] Error tracking configured (Sentry, Logfire)
- [ ] Alerts on error rate spike, auth failure spike, 5xx surge
- [ ] Log retention defined (compliance: GDPR = 30d default, justify longer)

## Data

- [ ] Backups automated, off-site
- [ ] Restore tested in last 90 days
- [ ] Encryption at rest (provider-side or app-side for sensitive fields)
- [ ] PII columns identified; consider encryption-at-application-layer
- [ ] Data retention policy defined (delete inactive users after N years)

## Incident Readiness

- [ ] Runbook exists and is findable (not buried in Slack)
- [ ] On-call rotation defined (or owner identified for solo)
- [ ] Status page or comms channel for users
- [ ] Postmortem template
- [ ] Contact for security disclosures (security.txt)

---

## Diff review (security focus)

For each changed file in the PR:

1. **New endpoints?** → check auth dependency, input validation, rate limit
2. **Auth changes?** → review token lifecycle, session handling, password code
3. **New dependencies?** → check `pip-audit` / `npm audit` for the new lib
4. **Env var changes?** → check `.env.example` updated and prod has the var set
5. **SQL changes?** → parametrized? Migration safe under concurrent load?
6. **Frontend `{@html}` / `dangerouslySetInnerHTML` introduced?** → sanitized?
7. **External URL fetched server-side?** → URL allowlisted?
8. **New cookies?** → httpOnly, Secure, SameSite set?
9. **Logging added?** → PII redacted?
10. **File upload added?** → size limit, MIME check, storage location secure?

## Incident triage flowchart

```
Suspected incident →
  ├─ Scope: which users? which data? time window?
  ├─ Severity: P0 (data loss/exposure) / P1 (auth/access) / P2 (degradation)
  ├─ Contain:
  │   ├─ Rotate compromised secrets immediately
  │   ├─ Revoke active sessions if needed
  │   └─ Disable affected endpoints if needed
  ├─ Investigate:
  │   ├─ Logs around the time window
  │   ├─ Affected user activity
  │   └─ Timeline of events
  ├─ Communicate:
  │   ├─ Internal: status update every 30min until resolved
  │   ├─ External: users within 72h if PII affected (GDPR)
  │   └─ Status page update
  └─ Postmortem within 7 days
```
