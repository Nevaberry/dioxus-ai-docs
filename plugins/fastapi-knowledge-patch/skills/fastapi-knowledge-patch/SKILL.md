---
name: fastapi-knowledge-patch
description: "FastAPI changes since training cutoff (0.112-0.135.3) -- native SSE, yield streaming, strict_content_type, dependency scopes, Pydantic v1 dropped, Starlette 1.0, Pydantic 2.12 MISSING sentinel/exclude_if, security 401 fix. Load before working with FastAPI."
license: MIT
version: "0.135.3"
metadata:
  author: Nevaberry
---

# FastAPI Knowledge Patch (0.112 to 0.135.3)

Claude's baseline knowledge covers FastAPI through 0.111, Pydantic v2.7, Starlette 0.37, Uvicorn 0.29. This skill covers changes from 0.112 through 0.135.3 (2024-09 to 2026-04).

## Version Compatibility

| Dependency | Minimum | Notes |
|-----------|---------|-------|
| Python | 3.10 | Dropped 3.8 in 0.125.0, 3.9 in 0.129.0. Python 3.14 supported |
| Pydantic | 2.9.0 | v1 fully dropped (0.126.0-0.128.0). No `pydantic.v1` compat |
| Starlette | >=0.46.0 | Supports Starlette 1.0.0+ |
| `fastapi-slim` | -- | Dropped in 0.129.2. Use `fastapi` or `fastapi[standard]` |

## Key Changes Timeline

| Version | Change | Impact |
|---------|--------|--------|
| 0.135.0 | Native SSE via `fastapi.sse` | New API |
| 0.134.0 | `yield` streaming (JSON lines, binary) | New pattern |
| 0.133.0 | Starlette 1.0 support | `on_event` removed |
| 0.132.0 | `strict_content_type=True` default | **Breaking** |
| 0.131.0 | ORJSONResponse/UJSONResponse deprecated | Deprecation |
| 0.130.0 | Pydantic Rust JSON serializer auto-used | Performance |
| 0.129.1 | `bytes` JSON Schema: `contentMediaType` | **Breaking** |
| 0.126.0 | Pydantic v1 support fully dropped | **Breaking** |
| 0.122.0 | Security classes return 401, not 403 | **Breaking** |
| 0.121.0 | Dependency `scope="request"` | New API |
| 0.117.0 | `-> None` return type for no-body responses | New pattern |

## Server-Sent Events (0.135.0)

Native SSE via `fastapi.sse`. No third-party packages needed:

```python
from collections.abc import AsyncIterable
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/items/stream", response_class=EventSourceResponse)
async def stream_items() -> AsyncIterable[Item]:
    for item in items:
        yield item  # auto-serialized as JSON in data: field
```

For SSE fields (`event`, `id`, `retry`, `comment`), yield `ServerSentEvent` objects:

```python
yield ServerSentEvent(data=item, event="item_update", id=str(i), retry=5000)
yield ServerSentEvent(raw_data="[DONE]", event="done")  # raw_data skips JSON encoding
yield ServerSentEvent(comment="keep-alive")  # comment-only event
```

- `data` and `raw_data` are **mutually exclusive** on `ServerSentEvent`
- Works with `def` (sync) too -- use `Iterable[T]` return type
- Auto keep-alive ping every 15s, `Cache-Control: no-cache`, `X-Accel-Buffering: no` set by default
- Works with **any HTTP method** (not just GET) -- relevant for MCP-style POST SSE

See [`sse.md`](references/sse.md) for `Last-Event-ID` resumption pattern and advanced usage.

## strict_content_type (0.132.0) -- Breaking Change

FastAPI now checks `Content-Type` header on JSON requests by default. Requests without `application/json` are rejected with 422. Disable per-route:

```python
@app.post("/legacy", strict_content_type=False)
async def legacy_endpoint(data: MyModel):
    ...
```

## Dependency Scopes (0.121.0)

`scope="request"` makes yield dependency exit code run **before** the response is sent:

```python
@app.get("/items/")
async def read_items(db: Annotated[Session, Depends(get_db, scope="request")]):
    ...
```

Without `scope="request"` (default), exit code runs **after** the response is fully sent -- correct for `StreamingResponse` where the dep must stay alive during streaming.

See [`dependency-injection.md`](references/dependency-injection.md) for `functools.partial()` support and `Response` as dependency annotation.

## Security Classes Return 401 (0.122.0) -- Breaking Change

`HTTPBearer`, `OAuth2`, `HTTPBasic` etc. now raise **401** (not 403) when credentials are missing. Tests asserting `status_code == 403` will break.

## ORJSONResponse / UJSONResponse Deprecated (0.131.0)

No longer needed. FastAPI 0.130.0+ uses Pydantic's Rust-based JSON serializer automatically when a **Pydantic return type annotation or `response_model`** is declared. Without either, falls back to `jsonable_encoder`.

## Pydantic 2.12 Highlights

**`MISSING` sentinel** -- canonical solution for PATCH endpoints (distinguish "not provided" from `None`):

```python
from pydantic.experimental.missing_sentinel import MISSING

class UpdateItem(BaseModel):
    name: str | None | MISSING = MISSING
    price: float | None | MISSING = MISSING

item = UpdateItem()
item.model_dump()  # {} -- MISSING fields excluded
```

**`exclude_if`** -- conditional field exclusion:

```python
value: int = Field(ge=0, exclude_if=lambda v: v == 0)
```

**`@model_validator(mode='after')`** must now be an instance method (not `@classmethod`). See [`pydantic-updates.md`](references/pydantic-updates.md) for all Pydantic 2.9-2.12 changes.

## Starlette 1.0 Removals (0.133.0+)

Hard removals (not just deprecated -- will raise errors):

| Removed | Replacement |
|---------|-------------|
| `@app.on_event("startup"/"shutdown")` | `lifespan=` context manager |
| `on_startup`/`on_shutdown` params | `lifespan=` context manager |
| `@app.route()` | `routes=` parameter |
| `@app.exception_handler()` | `exception_handlers=` parameter |
| `@app.middleware()` | `middleware=` parameter |
| `TemplateResponse(name, context)` | `TemplateResponse(request, name, ...)` |

Jinja2Templates: **autoescape enabled by default**. `jinja2` must be installed to import.

### Lifespan Migration Pattern

```python
# BROKEN in Starlette 1.0:
@app.on_event("startup")  # AttributeError -- hard removed
async def startup():
    ...

# CORRECT:
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown

app = FastAPI(lifespan=lifespan)
```

### Typed Lifespan State (Starlette 0.52.0)

Access lifespan state with type safety via `TypedDict`:

```python
from typing import AsyncIterator, TypedDict
from contextlib import asynccontextmanager
import httpx

class AppState(TypedDict):
    http_client: httpx.AsyncClient

@asynccontextmanager
async def lifespan(app) -> AsyncIterator[AppState]:
    async with httpx.AsyncClient() as client:
        yield {"http_client": client}

# In route handler -- typed access:
async def handler(request: Request[AppState]):
    client = request.state["http_client"]  # typed as httpx.AsyncClient
```

See [`starlette-changes.md`](references/starlette-changes.md) for CORSMiddleware, FileResponse range, ClientDisconnect.

## `None` Return Type (0.117.0)

Valid return annotation for endpoints with no body (204, 304):

```python
@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int) -> None:
    ...
```

## Streaming with yield (0.134.0)

Path operations can `yield` to stream responses directly -- no manual `StreamingResponse` needed. Requires Starlette >=0.46.0.

## functools.partial() Dependencies (0.123.5)

Dependencies now fully support `functools.partial()` and `functools.wraps()`:

```python
from functools import partial

def get_db(engine: Engine, read_only: bool = False):
    ...

get_prod_db = partial(get_db, engine=prod_engine)

@app.get("/items")
async def read_items(db=Depends(get_prod_db)):
    ...
```

See [`dependency-injection.md`](references/dependency-injection.md) for full details.

## Reference Files

| File | Contents |
|------|----------|
| [`sse.md`](references/sse.md) | SSE Last-Event-ID resumption, advanced ServerSentEvent usage |
| [`breaking-changes.md`](references/breaking-changes.md) | All breaking changes: strict_content_type, 401 security, bytes schema, Starlette 1.0 removals |
| [`pydantic-updates.md`](references/pydantic-updates.md) | Pydantic 2.9-2.12: MISSING sentinel, exclude_if, temporal config, model_validator changes |
| [`dependency-injection.md`](references/dependency-injection.md) | Scopes, functools.partial/wraps, Response as dep, PEP 695 TypeAliasType |
| [`starlette-changes.md`](references/starlette-changes.md) | Starlette 0.39-1.0: typed lifespan state, CORSMiddleware, FileResponse range, ClientDisconnect |
| [`ecosystem.md`](references/ecosystem.md) | SQLModel 0.0.25-0.0.36, Uvicorn changes, FastAPI Cloud CLI |
