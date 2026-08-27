# Starlette

## Migrate registration APIs before Starlette 1.0

Starlette 1.0 removes these deprecated APIs:

- `on_startup`, `on_shutdown`, `on_event()`, and `add_event_handler()`
- router `startup()` and `shutdown()`
- route, WebSocket-route, exception-handler, and middleware decorators
- the `method` argument to `FileResponse`

Use an async lifespan context manager and declarative `routes`, `middleware`,
and `exception_handlers`. Starlette requires Python 3.10 or newer from 0.50.

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

app = Starlette(
    routes=[Route("/", home)],
    lifespan=lifespan,
)
```

FastAPI 0.128.3 reimplements `on_event` across the accepted pre-1.0 Starlette
range, but that compatibility layer does not restore the removed API in
Starlette 1.0.

## Update Jinja template setup and calls

Starlette 1.0 no longer accepts arbitrary `**env_options` in
`Jinja2Templates`. Construct a `jinja2.Environment` and pass it through `env`.
Call `TemplateResponse(request, name, ...)`, not the former name-first
signature. Autoescaping is enabled by default, and importing
`Jinja2Templates` requires Jinja2 to be installed.

```python
from jinja2 import Environment, FileSystemLoader
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(
    env=Environment(
        loader=FileSystemLoader("templates"),
        autoescape=True,
    )
)

async def page(request):
    return templates.TemplateResponse(
        request, "index.html", {"name": "Ada"}
    )
```

## Private Network Access CORS

Starlette 0.51 adds `allow_private_network` to `CORSMiddleware`. Starlette 1.0
also returns an explicit origin, rather than `*`, when credentials are allowed.

```python
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

app = Starlette()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboard.example"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_private_network=True,
)
```

## Set partitioned cookies

Since Starlette 0.47, `Response.set_cookie()` accepts `partitioned=True` for
cookies that should use partitioned storage:

```python
from starlette.responses import Response

response = Response()
response.set_cookie(
    "session", "token", secure=True, partitioned=True
)
```

## Keep multipart limits distinct

`Request.form(max_part_size=...)` limits each multipart part. In direct
`MultiPartParser` configuration, Starlette 0.46 renames the former
`max_file_size` setting to `spool_max_size`.

```python
from starlette.responses import PlainTextResponse

async def submit(request):
    form = await request.form(max_part_size=2 * 1024 * 1024)
    return PlainTextResponse(str(form["value"]))
```

Do not treat the per-part limit and the in-memory spool threshold as the same
control.

## Handle streaming disconnects

Since Starlette 0.42, `StreamingResponse` raises `ClientDisconnect` when the
client drops. Middleware and code wrapping response transmission can catch and
handle that explicit outcome rather than assuming the stream ended normally.
