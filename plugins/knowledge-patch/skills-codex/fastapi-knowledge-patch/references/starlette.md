# Starlette

## Starlette 1.0 migration

The `starlette-release-history` guidance says Starlette 1.0 removes these
deprecated registration APIs:

- `on_startup`, `on_shutdown`, `on_event()`, and `add_event_handler()`
- router `startup()` and `shutdown()`
- route, WebSocket-route, exception-handler, and middleware decorators
- `FileResponse(method=...)`

Use an async lifespan context manager and declarative `routes`, `middleware`,
and `exception_handlers`. Starlette requires Python 3.10+ from 0.50.

```python
from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

@asynccontextmanager
async def lifespan(app):
    yield

async def home(request):
    return PlainTextResponse("ok")

app = Starlette(routes=[Route("/", home)], lifespan=lifespan)
```

FastAPI compatibility progressed through Starlette 0.49 and 0.50 before
FastAPI 0.128.3 accepted `starlette>=0.40.0,<1.0.0`. FastAPI 0.133 accepts
Starlette 1.x; FastAPI 0.134 requires Starlette 0.46+ for correct exception-group
handling and streaming. Do not infer a compatible range without checking the
installed FastAPI version.

Across the pre-1.0 range, FastAPI 0.128.3 reimplements `on_event` so existing
callbacks keep their behavior. Treat that as compatibility support while
migrating to lifespan, because Starlette 1.0 removes the underlying registration
APIs (`2025-12`).

## Jinja templates

Starlette 1.0 removes `**env_options` from `Jinja2Templates`. Construct a
`jinja2.Environment` and pass it through `env`. Call
`TemplateResponse(request, name, ...)`, replacing the old name-first signature.
Autoescaping is on by default, and importing `Jinja2Templates` requires Jinja2
to be installed (`starlette-release-history`).

```python
from jinja2 import Environment, FileSystemLoader
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(
    env=Environment(loader=FileSystemLoader("templates"), autoescape=True)
)

async def page(request):
    return templates.TemplateResponse(request, "index.html", {"name": "Ada"})
```

## CORS and browser behavior

Starlette 0.51 adds `allow_private_network` to `CORSMiddleware`. Starlette 1.0
returns an explicit origin rather than `*` when credentials are allowed
(`starlette-release-history`).

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboard.example"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_private_network=True,
)
```

Since Starlette 0.47, `Response.set_cookie()` accepts `partitioned=True` to opt
a cookie into partitioned storage (`starlette-release-history`).

## Multipart controls

`Request.form(max_part_size=...)` limits each multipart part. For direct
`MultiPartParser` customization, the old `max_file_size` setting is named
`spool_max_size` from Starlette 0.46 (`starlette-release-history`). Do not
confuse the per-part request limit with the spool threshold.

```python
async def submit(request):
    form = await request.form(max_part_size=2 * 1024 * 1024)
    return PlainTextResponse(str(form["value"]))
```

## Streaming disconnects

From Starlette 0.42, `StreamingResponse` raises `ClientDisconnect` when the
client disconnects (`starlette-release-history`). Middleware and other code
wrapping response transmission can handle that exception explicitly.
