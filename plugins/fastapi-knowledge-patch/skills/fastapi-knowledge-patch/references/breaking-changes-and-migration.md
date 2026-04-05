# Breaking Changes & Migration

Covers all breaking changes and deprecations in FastAPI 0.116.0–0.135.3.

## Strict Content-Type Checking (0.132.0) — BREAKING

FastAPI now rejects JSON requests without a valid `Content-Type` header (e.g. `application/json`). This protects against CSRF on localhost apps.

Disable if your clients don't send it:

```python
app = FastAPI(strict_content_type=False)
```

This affects all endpoints that accept JSON body parameters. Clients must include `Content-Type: application/json` (or compatible media type) or the request will be rejected.

## Security Classes Return 401 (0.122.0) — BREAKING

`HTTPBearer`, `OAuth2PasswordBearer`, and other security classes now raise `401 Unauthorized` (not `403 Forbidden`) when credentials are missing. This aligns with HTTP spec — 401 means "not authenticated", 403 means "authenticated but not authorized".

Override the classes if you need the old `403` behavior.

## Dependency `scope` Parameter (0.121.0)

Dependencies with `yield` now support `scope="function"` to run cleanup **before** the response is sent. The default `scope="request"` runs cleanup after the response is sent (existing behavior).

```python
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()


@app.get("/users/me")
def get_user(db: Annotated[Session, Depends(get_db, scope="function")]):
    return db.query(User).first()
    # db.close() runs here, before response is sent
```

Use `scope="function"` when you need the resource cleaned up before the response starts streaming, for example to release database connections back to the pool promptly.

## `ORJSONResponse` / `UJSONResponse` Deprecated (0.131.0)

Pydantic now serializes JSON responses in Rust when a return type or `response_model` is declared — 2x+ faster than orjson. Custom response classes like `ORJSONResponse` and `UJSONResponse` are no longer needed and are deprecated.

Migration: remove `response_class=ORJSONResponse` and ensure your endpoints declare a return type or `response_model` to get automatic Rust-speed serialization.

## Python Version Drops

- **Python 3.8 dropped** (0.125.0)
- **Python 3.9 dropped** (0.129.0)

Minimum supported Python version is now **3.10**.

## Pydantic v1 Dropped (0.126.0–0.128.0)

Pydantic v1 compatibility was removed in stages:
- 0.126.0: minimum `pydantic>=2.7.0`
- 0.128.0: minimum `pydantic>=2.9.0`

All Pydantic v1 patterns (`from pydantic.v1 import ...`, `class Config:`, `.dict()`, `.json()`) must be migrated to v2.

## `fastapi-slim` Dropped (0.129.2)

The `fastapi-slim` package (FastAPI without CLI dependencies) is no longer published. Use `fastapi` or `fastapi[standard]` instead.

## Starlette 1.0+ Supported (0.133.0)

Minimum Starlette version bumped to `>=0.46.0`, with full Starlette 1.0 support. This shouldn't require code changes unless you depend on removed Starlette internals.
