---
name: fastapi-knowledge-patch
description: "FastAPI changes since training cutoff (latest: 0.135.3) — SSE with EventSourceResponse, JSON Lines streaming with yield, strict Content-Type, dependency scope, security 401. Load before working with FastAPI."
version: "0.135.3"
license: MIT
metadata:
  author: Nevaberry
---

# FastAPI Knowledge Patch

Covers FastAPI 0.116.0–0.135.3 (2025-07 through 2026-04). Claude Opus 4.6 knows FastAPI through 0.115.12 with Pydantic v2, dependency injection, async/sync endpoints, OpenAPI generation, middleware, security, CORS, background tasks, WebSockets, and lifespan events. It is **unaware** of the streaming APIs, strict Content-Type enforcement, and breaking changes below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Streaming | [references/streaming.md](references/streaming.md) | `EventSourceResponse`, `ServerSentEvent`, JSON Lines with `yield`, `AsyncIterable[Model]` |
| Breaking changes & migration | [references/breaking-changes-and-migration.md](references/breaking-changes-and-migration.md) | Strict Content-Type, security 401, dependency `scope`, Python/Pydantic version drops, ORJSON deprecated |

---

## Breaking Changes Summary

| What changed | Before | After | Version |
|---|---|---|---|
| Content-Type enforcement | Any/missing header accepted | Rejects missing `Content-Type` on JSON endpoints | 0.132.0 |
| Security class status | `403` when credentials missing | `401` when credentials missing | 0.122.0 |
| Python support | 3.8+ | 3.10+ (3.8 dropped 0.125.0, 3.9 dropped 0.129.0) | 0.125–0.129 |
| Pydantic support | v1 + v2 | v2 only (min `>=2.9.0`) | 0.126–0.128 |
| `fastapi-slim` | Separate package | Dropped — use `fastapi` or `fastapi[standard]` | 0.129.2 |
| Starlette | `<1.0` | `>=0.46.0` (Starlette 1.0+ supported) | 0.133.0 |
| ORJSON/UJSON responses | Needed for fast JSON | Deprecated — Pydantic Rust serialization is faster | 0.131.0 |

See [references/breaking-changes-and-migration.md](references/breaking-changes-and-migration.md) for details and migration patterns.

## New APIs

| API | Version | Description |
|---|---|---|
| `fastapi.sse.EventSourceResponse` | 0.135.0 | Response class for Server-Sent Events endpoints |
| `fastapi.sse.ServerSentEvent` | 0.135.0 | SSE event with `data`, `event`, `id`, `retry`, `raw_data` fields |
| `yield` streaming (JSON Lines) | 0.134.0 | Return `AsyncIterable[Model]` / `Iterable[Model]` to stream JSONL |
| `FastAPI(strict_content_type=)` | 0.132.0 | Toggle Content-Type enforcement (default `True`) |
| `Depends(..., scope=)` | 0.121.0 | `"function"` runs cleanup before response; `"request"` (default) runs after |

## Server-Sent Events (0.135.0)

New `EventSourceResponse` and `ServerSentEvent` in `fastapi.sse`:

```python
from collections.abc import AsyncIterable
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


# Simple: yield models directly
@app.get("/stream", response_class=EventSourceResponse)
async def sse_items() -> AsyncIterable[Item]:
    for item in get_items():
        yield item


# Advanced: control event/id/retry fields
@app.get("/events", response_class=EventSourceResponse)
async def sse_events() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(data=item, event="update", id="1", retry=5000)
    yield ServerSentEvent(raw_data="[DONE]")  # raw_data skips JSON encoding
```

Read `Last-Event-ID` header for reconnection resume. Works with POST too.

## Stream JSON Lines with `yield` (0.134.0)

Use `yield` in path operations to stream JSON Lines (`application/jsonl`). Declare return type as `AsyncIterable[Model]` for Pydantic validation and Rust-speed serialization:

```python
from collections.abc import AsyncIterable
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/items/stream")
async def stream_items() -> AsyncIterable[Item]:
    for item in get_items():
        yield item
```

Works with sync `def` too (use `Iterable[Model]`). No `StreamingResponse` wrapper needed.

See [references/streaming.md](references/streaming.md) for complete streaming patterns.

## Strict Content-Type Checking (0.132.0)

FastAPI now rejects JSON requests without a valid `Content-Type` header (e.g. `application/json`). Protects against CSRF on localhost apps. Disable if your clients don't send it:

```python
app = FastAPI(strict_content_type=False)
```

## Dependency `scope` Parameter (0.121.0)

Dependencies with `yield` now support `scope="function"` to run cleanup **before** the response is sent (default `scope="request"` runs after):

```python
@app.get("/users/me")
def get_user(db: Annotated[Session, Depends(get_db, scope="function")]):
    return db.query(User).first()
    # db.close() runs here, before response is sent
```

## Complete Example — AI Chat with SSE

Combines SSE, dependency scope, and strict Content-Type in a realistic pattern:

```python
from collections.abc import AsyncIterable
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

app = FastAPI(strict_content_type=True)

class ChatRequest(BaseModel):
    message: str

class ChatChunk(BaseModel):
    text: str
    done: bool

def get_llm_client():
    client = create_client()
    yield client
    client.close()

@app.post("/chat", response_class=EventSourceResponse)
async def chat(
    req: ChatRequest,
    llm: Annotated[LLMClient, Depends(get_llm_client, scope="request")],
) -> AsyncIterable[ServerSentEvent]:
    async for chunk in llm.stream(req.message):
        yield ServerSentEvent(
            data=ChatChunk(text=chunk.text, done=False),
            event="chunk",
        )
    yield ServerSentEvent(
        data=ChatChunk(text="", done=True),
        event="done",
    )
```

## Reference Files

| File | Contents |
|---|---|
| [streaming.md](references/streaming.md) | EventSourceResponse, ServerSentEvent, JSON Lines streaming, yield-based streaming |
| [breaking-changes-and-migration.md](references/breaking-changes-and-migration.md) | Strict Content-Type, security 401, dependency scope, Python/Pydantic drops, ORJSON deprecation |
