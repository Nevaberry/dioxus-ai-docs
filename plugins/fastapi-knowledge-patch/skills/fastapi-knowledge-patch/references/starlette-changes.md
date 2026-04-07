# Starlette Changes (0.39-1.0) Affecting FastAPI

FastAPI 0.135.3 supports Starlette >=0.46.0 including Starlette 1.0.0+.

## Starlette 1.0 -- Hard Removals

See [breaking-changes.md](breaking-changes.md) for the full table of removed APIs. The most impactful: `@app.on_event()`, `on_startup`/`on_shutdown` params, old decorator-based middleware/exception handlers, and old `TemplateResponse` signature.

## Typed Lifespan State (0.52.0)

Typed access to lifespan state via `TypedDict` and `Request[State]`:

```python
from typing import AsyncIterator, TypedDict
from contextlib import asynccontextmanager
import httpx
from starlette.requests import Request

class AppState(TypedDict):
    http_client: httpx.AsyncClient

@asynccontextmanager
async def lifespan(app) -> AsyncIterator[AppState]:
    async with httpx.AsyncClient() as client:
        yield {"http_client": client}

async def handler(request: Request[AppState]):
    client = request.state["http_client"]  # typed as httpx.AsyncClient
```

## CORSMiddleware: allow_private_network (0.51.0)

New parameter for apps accessed from private network contexts (e.g., localhost UIs calling local APIs):

```python
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_private_network=True,  # new parameter
)
```

## Partitioned Cookies (0.47.0)

Supports CHIPS (Cookies Having Independent Partitioned State) for third-party cookies in embedded iframes:

```python
response.set_cookie("key", "value", partitioned=True)
```

## MultiPartParser Rename (0.46.0)

`max_file_size` parameter renamed to `spool_max_size`. Also: `TestClient(timeout=...)` is deprecated.

## max_part_size on Request.form() (0.44.0)

Limit individual form part size when processing multipart data:

```python
form = await request.form(max_part_size=1024 * 1024)  # 1MB limit per part
```

## ClientDisconnect from StreamingResponse (0.42.0)

`StreamingResponse` now raises `ClientDisconnect` when the client disconnects during streaming:

```python
from starlette.exceptions import ClientDisconnect

async def generate():
    try:
        while True:
            yield await get_next_chunk()
    except ClientDisconnect:
        # client left early -- cleanup
        pass
```

## HTTPException Before WebSocket Accept (0.41.0)

Raising `HTTPException` before `websocket.accept()` now correctly returns an HTTP response instead of failing the WebSocket handshake.

## FileResponse Range Requests (0.39.0)

`FileResponse` now supports HTTP Range requests for partial content delivery. Important for video/audio streaming and resumable large file downloads -- no application code changes needed.

## Jinja2Templates Changes (1.0)

- **Autoescape enabled by default** -- behavioral change for templates containing HTML
- `jinja2` must be installed to `import Jinja2Templates` (not just when instantiating)
- `**env_options` removed -- use `env=` with pre-configured `jinja2.Environment`
