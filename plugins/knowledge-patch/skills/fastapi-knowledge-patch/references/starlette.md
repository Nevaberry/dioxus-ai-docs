# Starlette

Use this reference when FastAPI code directly uses Starlette lifespan, state, templates, middleware, requests, responses, tests, or WebSockets (`starlette-release-history`).

## Contents

- [Starlette 1.0 migration](#starlette-10-migration)
- [Typed lifespan and connection state](#typed-lifespan-and-connection-state)
- [Templates in Starlette 1.0](#templates-in-starlette-10)
- [Middleware and configuration](#middleware-and-configuration)
- [Cookies](#cookies)
- [Multipart forms](#multipart-forms)
- [`TestClient`](#testclient)
- [File responses and ranges](#file-responses-and-ranges)
- [Streaming responses](#streaming-responses)
- [WebSocket denial responses](#websocket-denial-responses)

## Starlette 1.0 migration

### Replace imperative lifecycle registration

Starlette 1.0 removes these lifecycle APIs:

- `on_startup` and `on_shutdown` constructor arguments on `Starlette` and `Router`.
- `on_event()` and `add_event_handler()`.
- `Router.startup()` and `Router.shutdown()`.

Supply an async-context-manager `lifespan` instead.

### Replace registration decorators

Starlette 1.0 removes route, WebSocket-route, exception-handler, and middleware decorators. Pass `routes`, `exception_handlers`, and `middleware` to constructors. This is a Starlette change even though FastAPI retains or reimplements some compatibility APIs on its own classes.

Starlette 1.0 also removes the `method=` argument from `FileResponse`.

## Typed lifespan and connection state

Starlette 0.52 supports dictionary-style state access. A `TypedDict` yielded from lifespan remains precisely typed through `Request[State]`. Starlette 1.0 extends the state generic to `WebSocket`:

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import TypedDict
import httpx
from starlette.applications import Starlette
from starlette.requests import Request

class AppState(TypedDict):
    client: httpx.AsyncClient

@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[AppState]:
    async with httpx.AsyncClient() as client:
        yield {"client": client}

async def endpoint(request: Request[AppState]):
    client = request.state["client"]
```

Use item access when retaining the `TypedDict`'s key-level type information matters.

## Templates in Starlette 1.0

`Jinja2Templates` changes in several ways:

- Autoescaping is enabled by default.
- `jinja2` must be installed when the templates integration is imported.
- Arbitrary `**env_options` are no longer accepted; construct a `jinja2.Environment` and pass it with `env=`.
- The legacy `TemplateResponse(name, context)` form is removed. Pass the request first: `templates.TemplateResponse(request, "index.html", context)`.

Review rendered output for newly escaped values and update both template construction and response call sites during migration.

## Middleware and configuration

### Private-network CORS

Starlette 0.51 adds `allow_private_network` to `CORSMiddleware`. Enable browser private-network access explicitly:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin],
    allow_private_network=True,
)
```

Retain the usual origin controls; this flag opts into an additional browser access mode.

### Environment-file encoding

Starlette 0.49 adds `encoding` to `Config`:

```python
from starlette.config import Config

config = Config(".env", encoding="utf-8")
```

Use it when environment files are not safely decoded by an implicit platform default.

## Cookies

Starlette 0.47 adds `partitioned` to `Response.set_cookie()`:

```python
response.set_cookie("session", token, partitioned=True)
```

Partitioned cookies are scoped by the browser's top-level site. Python 3.14 supplies the underlying cookie support; setting `partitioned=True` raises on older Python versions.

## Multipart forms

Starlette 0.40 adds `max_part_size` to `MultiPartParser`, and Starlette 0.44 exposes it through `Request.form()`:

```python
async with request.form(max_part_size=2 * 1024 * 1024) as form:
    process(form)
```

Use the limit to bound individual multipart parts. In Starlette 0.46, the parser customization point named `max_file_size` is renamed to `spool_max_size`; update subclasses and configuration that controlled the in-memory spool threshold.

## `TestClient`

- Starlette 0.44 adds `client=(host, port)` to set the ASGI client address.
- Starlette 0.43 removes deprecated `allow_redirects`; use `follow_redirects`.
- Passing `timeout` is deprecated as of Starlette 0.46.

```python
with TestClient(
    app,
    client=("203.0.113.10", 50000),
    follow_redirects=False,
) as client:
    response = client.get("/")
```

## File responses and ranges

`FileResponse` handles HTTP `Range` requests, including multiple ranges, from Starlette 0.39. Do not remain on the initial affected range-handling releases:

- Starlette 0.49.1 fixes a security vulnerability in range parsing.
- Starlette 1.0 fixes additional multi-range response details.

Test satisfiable, unsatisfiable, single-range, and multi-range requests when serving user-accessible files.

## Streaming responses

Starting in Starlette 0.42, a client disconnect while sending a `StreamingResponse` raises `ClientDisconnect`. Account for it in cleanup, middleware, error monitoring, and stream tests instead of assuming the send loop ends silently.

Starlette 0.38 accepts `memoryview` in both `Response` and `StreamingResponse`. Return or yield an existing buffer view without first converting it to `bytes`.

## WebSocket denial responses

Starlette 0.37 supports the ASGI WebSocket Denial Response extension:

```python
await websocket.send_denial_response(
    PlainTextResponse("Unauthorized", status_code=401)
)
```

Starlette 0.41 additionally permits raising `HTTPException` before `websocket.accept()`. Starlette 1.0 allows `StreamingResponse` and `FileResponse` themselves to serve as denial responses.
