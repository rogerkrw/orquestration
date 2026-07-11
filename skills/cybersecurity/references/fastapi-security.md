# FastAPI Security

## Auth pattern — JWT with httpOnly cookies (preferred)

```python
from datetime import datetime, timedelta, UTC
from fastapi import Depends, FastAPI, HTTPException, Response, Cookie
import jwt
from jwt import PyJWTError
from pwdlib import PasswordHash
from pydantic import BaseModel

SECRET = settings.jwt_secret  # from pydantic-settings, never hardcoded
ALGO = "HS256"
pwd = PasswordHash.recommended()  # argon2id — NOT bcrypt (72-byte truncation)

def hash_pw(p: str) -> str: return pwd.hash(p)
def verify_pw(p: str, h: str) -> bool: return pwd.verify(p, h)

def make_token(sub: str) -> str:
    payload = {"sub": sub, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, SECRET, algorithm=ALGO)

async def current_user(session: str | None = Cookie(default=None)) -> User:
    if not session:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = jwt.decode(session, SECRET, algorithms=[ALGO])
    except PyJWTError:
        raise HTTPException(401, "Invalid token")
    user = await User.get(payload["sub"])
    if not user:
        raise HTTPException(401, "User not found")
    return user

@app.post("/login")
async def login(body: LoginBody, response: Response):
    user = await User.get_by_email(body.email)
    if not user or not verify_pw(body.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    response.set_cookie(
        "session", make_token(str(user.id)),
        httponly=True, secure=True, samesite="lax", max_age=3600
    )
    return {"ok": True}
```

## CORS — done right

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],  # explicit, never "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Never** `allow_origins=["*"]` with `allow_credentials=True` — browsers silently reject it but devs assume it works.

## Rate limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, body: LoginBody):
    ...
```

For distributed/multi-instance: back slowapi with Redis (`storage_uri="redis://..."`).

## Input validation — Pydantic at the boundary

```python
from pydantic import BaseModel, EmailStr, Field, field_validator

class CreateUser(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    name: str = Field(min_length=1, max_length=100)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a digit")
        return v
```

Never accept `dict` past a route boundary. Models are the contract.

## Exception handling — don't leak stack traces

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def safe_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
```

Specific handlers for known exceptions, this fallback for everything else. **Never** return `str(exc)` in production responses.

## Security headers

```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        r = await call_next(request)
        r.headers["X-Content-Type-Options"] = "nosniff"
        r.headers["X-Frame-Options"] = "DENY"
        r.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        r.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        r.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return r

app.add_middleware(SecurityHeaders)
```

CSP belongs at the frontend (SvelteKit hooks) where you know which scripts/styles are legitimate.

## SQL injection prevention

```python
# ✅ Parametrized — safe
result = await session.execute(
    text("SELECT * FROM users WHERE email = :email"),
    {"email": email}
)

# ❌ f-string — vulnerable
result = await session.execute(text(f"SELECT * FROM users WHERE email = '{email}'"))
```

Use SQLAlchemy ORM (`select(User).where(User.email == email)`) or raw SQL with `text()` + bindparams. Never string-format SQL.

## Docs in production

```python
app = FastAPI(
    docs_url=None if settings.env == "production" else "/docs",
    redoc_url=None if settings.env == "production" else "/redoc",
    openapi_url=None if settings.env == "production" else "/openapi.json",
)
```

Or auth-gate them. Public OpenAPI tells attackers your entire surface.

## Webhook verification

```python
import hmac, hashlib

def verify_webhook(body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.post("/webhook")
async def webhook(request: Request, x_signature: str = Header()):
    body = await request.body()
    if not verify_webhook(body, x_signature, settings.webhook_secret):
        raise HTTPException(403, "Invalid signature")
    # process body
```

`hmac.compare_digest` is constant-time; `==` is not (timing attack).
