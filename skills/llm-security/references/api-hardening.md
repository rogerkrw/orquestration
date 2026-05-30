# API Hardening — FastAPI + Chainlit LLM Harness

## Authentication for LLM endpoints

LLM endpoints must be authenticated. They consume expensive compute and expose
sensitive data — unauthenticated endpoints are both a data risk and a cost risk.

### JWT middleware (FastAPI)

```python
import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

_secret = os.environ.get("JWT_SECRET", "")
assert len(_secret) >= 32, "JWT_SECRET must be at least 32 characters"

security = HTTPBearer()

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    try:
        payload = jwt.decode(
            creds.credentials,
            _secret,
            algorithms=["HS256"],  # always specify; never allow 'none'
            options={"require": ["exp", "sub"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

JWT tokens: store **access tokens in memory** (SPA) or `HttpOnly Secure SameSite=Strict`
cookies. Never localStorage.

---

## Rate limiting (per-user and per-IP)

LLM endpoints must be rate-limited at two levels:
1. **IP-level**: protect against unauthenticated abuse
2. **User-level**: protect against authenticated over-consumption and cost bombs

```python
# slowapi — Redis-backed, FastAPI-native
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat")
@limiter.limit("10/minute")          # IP-level
async def chat(request: Request, user=Depends(get_current_user)):
    ...
```

For user-level limits, key on `user_id` from JWT, backed by Redis counters.

Token-length limits (separate from request-rate limits):
```python
MAX_PROMPT_CHARS = 4_000

@app.post("/chat")
async def chat(body: ChatRequest, user=Depends(get_current_user)):
    if len(body.message) > MAX_PROMPT_CHARS:
        raise HTTPException(status_code=422, detail="Message too long")
    ...
```

---

## HTTP security headers

Apply via middleware on every response:

```python
from starlette.middleware.base import BaseHTTPMiddleware

SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "  # relax only if needed for Chainlit
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "object-src 'none';"
    ),
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "X-XSS-Protection": "0",  # explicitly disable broken XSS Auditor; rely on CSP
}

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

## CORS configuration

```python
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",")
# e.g. CORS_ORIGINS="https://app.yourdomain.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,         # never ["*"] for LLM endpoints
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

`allow_origins=["*"]` with `allow_credentials=True` is both an error (FastAPI will
reject it) and a vulnerability. Explicitly list known frontend origins.

---

## Exception handling — never expose stack traces

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error", exc_info=exc, extra={
        "path": request.url.path,
        "method": request.method,
    })
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
```

Stack traces, model names, prompt content, and internal paths must never appear in
error responses returned to clients.

---

## Chainlit-specific hardening

Chainlit exposes WebSocket connections for streaming. Additional considerations:

1. **Auth callback**: implement `@cl.oauth_callback` or `@cl.password_auth_callback`
   — Chainlit's built-in auth hooks. Do not leave unauthenticated.

2. **Session isolation**: each Chainlit session gets its own user context. Never
   share agent state across sessions.

3. **File uploads**: if enabled, validate MIME type, size, and scan for malware
   before passing to RAG pipeline.

```python
# Chainlit auth example
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    user = authenticate_user(username, password)  # your auth logic
    if user:
        return cl.User(identifier=user.id, metadata={"roles": user.roles})
    return None
```

---

## Arize Phoenix (observability) security notes

Phoenix logs traces including prompts and responses. In production:

1. Deploy Phoenix on internal network — never publicly exposed
2. Enable Phoenix authentication if on shared infrastructure
3. Configure PII redaction before traces reach Phoenix:

```python
# In PydanticAI instrumentation setup
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
# Apply a PII-scrubbing span processor before the Phoenix exporter
```

4. Set data retention policies — traces containing user data have LGPD/GDPR
   implications in Brazil.
