---
name: fastapi-knowledge-patch
description: FastAPI
version: 0.135.3
license: MIT
metadata:
  author: Nevaberry
---


# FastAPI Knowledge Patch

Use this patch before changing a FastAPI application or its Pydantic,
SQLModel, Starlette, or Uvicorn integration. Check the project's pinned
versions first and apply only guidance introduced at or below those versions.
Prefer the project's manifests, code, tests, and observed behavior whenever
they disagree with compatibility guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrading-and-compatibility.md](references/upgrading-and-compatibility.md) | Python, Pydantic, Starlette, and HTTPX requirements; package extras; migration bridges; removals and deprecations |
| [dependency-injection.md](references/dependency-injection.md) | `yield` lifetimes, scope constraints, cleanup, caching, wrapped callables, annotation resolution, injected responses |
| [requests-and-security.md](references/requests-and-security.md) | Forms and parameter models, strict JSON media types, tagged unions, authentication errors, OAuth2 scopes |
| [responses-and-streaming.md](references/responses-and-streaming.md) | Typed serialization, JSON Lines, raw streaming, SSE, iterable responses, byte schemas |
| [openapi-and-pydantic.md](references/openapi-and-pydantic.md) | Pydantic validation and serialization, dynamic models, annotations, JSON Schema, FastAPI OpenAPI fixes |
| [frontend-cli-and-docs.md](references/frontend-cli-and-docs.md) | Static frontends and fallbacks, frontend dependencies, CLI entrypoints and deployment, Vibe, ReDoc, tracebacks |
| [sqlmodel.md](references/sqlmodel.md) | Runtime compatibility, field declarations, DML typing, relationships, cascade controls |
| [starlette.md](references/starlette.md) | Starlette 1.0 migration, templates, CORS, cookies, multipart parsing, streaming disconnects |
| [uvicorn.md](references/uvicorn.md) | Runtime and reload changes, workers, protocols, proxy trust, ASGI scopes, logging |

## Upgrade blockers and removals

Align the runtime and dependency floors before changing FastAPI versions:

| FastAPI release | Requirement or behavior |
| --- | --- |
| 0.125 | Python 3.9+; Python 3.8 is capped at 0.124.4 |
| 0.126 | Pydantic 2.7+; standalone Pydantic V1 is unsupported |
| 0.128 | The temporary `pydantic.v1` migration bridge is removed |
| 0.129 | Python 3.10+ |
| 0.133 | Starlette 1.x is supported |
| 0.134 | Starlette 0.46+ is required |
| 0.135.2 | Pydantic 2.9+ |

Python 3.14 requires Pydantic V2. If using the temporary Pydantic V1/V2
bridge added in FastAPI 0.119, finish migrating all `pydantic.v1` imports
before FastAPI 0.128 or Python 3.14.

Replace deprecated integrations:

- Prefer typed Pydantic returns or `response_model` over `ORJSONResponse` and
  `UJSONResponse`; standard JSON responses use Pydantic directly, and those
  specialized classes are deprecated.
- Replace `fastapi.middleware.wsgi.WSGIMiddleware` with
  `a2wsgi.WSGIMiddleware`.
- Depend on `fastapi`, not the deprecated `fastapi-slim` wrapper; depend on
  `sqlmodel`, not the discontinued `sqlmodel-slim` package.
- Before adopting Starlette 1.0, replace startup and shutdown registration,
  event-handler APIs, and decorators removed by that release with lifespan
  and declarative configuration.
- Stop calling Uvicorn's removed `Config.setup_event_loop()` and avoid new
  imports from the deprecated `uvicorn.workers` module.

Read [upgrading-and-compatibility.md](references/upgrading-and-compatibility.md)
before upgrading Python, FastAPI, Pydantic, or Starlette.

## Require explicit JSON media types

FastAPI 0.132 rejects JSON request bodies without a valid JSON
`Content-Type` by default. Correct clients to send `application/json`. Use the
compatibility switch only while migrating clients:

```python
from fastapi import FastAPI

app = FastAPI(strict_content_type=False)
```

The strict default also blocks a narrow browser-to-local-network path in which
a headerless `Blob` can avoid CORS preflight. It does not replace authentication
for privileged endpoints.

## Choose dependency lifetimes deliberately

A `yield` dependency defaults to request scope: its exit code runs after the
response is sent, so a stream can continue using its resource. Use
`scope="function"` when cleanup should run after the path operation returns but
before response transmission.

```python
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()

def session():
    resource = open_resource()
    try:
        yield resource
    finally:
        resource.close()

@app.get("/items")
def items(resource: Annotated[Resource, Depends(session, scope="function")]):
    return read_items(resource)
```

A request-scoped dependency may use only request-scoped sub-dependencies. A
function-scoped dependency may use either scope. This keeps children alive
until their parent finishes teardown. Scoped dependency trees also do not use
the ordinary unscoped cache path.

If a `yield` dependency catches an exception thrown by the endpoint, re-raise
the original or raise a replacement exception; swallowing it can produce an
unhelpful `500` without a useful server log.

Read [dependency-injection.md](references/dependency-injection.md) before
changing scopes, wrappers, partials, callable classes, or deferred annotations.

## Select the streaming mode

| Goal | Declaration | Item handling |
| --- | --- | --- |
| JSON Lines | Yield normally and annotate `Iterable[Item]` or `AsyncIterable[Item]` | Each item is Pydantic-validated, filtered, documented, and encoded as `application/jsonl` |
| Raw chunks | Set `response_class=StreamingResponse` | Strings and bytes bypass Pydantic; the generator annotation is ignored at runtime |
| Server-Sent Events | Set `response_class=EventSourceResponse` | Plain values become JSON in `data:`; `ServerSentEvent` controls metadata or raw data |

```python
from collections.abc import AsyncIterable
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent

app = FastAPI()

@app.get("/events", response_class=EventSourceResponse, status_code=202)
async def events() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(
        data={"status": "ready"}, event="status", id="1", retry=5000
    )
    yield ServerSentEvent(raw_data="[DONE]", event="done")
```

`data` is JSON-encoded; mutually exclusive `raw_data` is preformatted text.
SSE sends an idle keepalive comment every 15 seconds and defaults to
`Cache-Control: no-cache` and `X-Accel-Buffering: no`. Use releases containing
the corrected SSE line splitting and streaming status-code handling before
depending on multiline events or a non-default decorator status.

Use a regular `def` yielding `Iterable[bytes]` for blocking file-like sources,
and set an explicit media type for raw `StreamingResponse` data. Account for
Starlette `ClientDisconnect` when a streaming client drops.

Read [responses-and-streaming.md](references/responses-and-streaming.md) for
serialization paths, response-model options, router inclusion, and cancellation.

## Requests and authentication

Built-in security dependencies return `401 Unauthorized` rather than `403`
when credentials are absent. To preserve an established `403` contract,
subclass the security utility and return an exception from its hook:

```python
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer

class HTTPBearer403(HTTPBearer):
    def make_not_authenticated_error(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated",
        )
```

Nested OAuth2 scopes propagate through dependency trees and are deduplicated in
OpenAPI. Authorization credentials are stripped of surrounding whitespace.
Parameter models for `Query`, `Header`, and `Cookie` honor aliases and optional
sequences; union-typed forms and tagged discriminated-union request bodies are
handled directly.

Read [requests-and-security.md](references/requests-and-security.md) for form
edge cases, OAuth2 metadata, and the strict-content-type trust boundary.

## Pydantic and schema essentials

When using Pydantic 2.12:

- Define `@model_validator(mode="after")` as an instance method.
- Upgrade `pydantic` and `pydantic-core` together; mismatches fail at startup.
- Use `MISSING` to distinguish omission from `None`, `Field(exclude_if=...)`
  for conditional output, and `exclude_computed_fields=True` for computed data.
- Pass `extra="forbid"` to `model_validate()` for a one-call policy override.
- Use `union_format="primitive_type_array"` when eligible primitive unions
  should appear as an OpenAPI `type` array.
- Use `FieldInfo.asdict()` instead of mutating reused field metadata while
  rebuilding dynamic fields.

Expect schema snapshots to change for `Decimal`, function titles,
typed-dictionary `additionalProperties`, byte media metadata, and the OpenAPI
`ValidationError` fields `input` and `ctx`. FastAPI accepts array-valued
OpenAPI `type`, top-level `external_docs`, literal schema fields named `$ref`,
top-level security schemes, and PEP 695 endpoint aliases.

Read [openapi-and-pydantic.md](references/openapi-and-pydantic.md) before
changing validation, dynamic models, dataclasses, discriminators, annotation
resolution, serialization, or generated schemas.

## Serve a built frontend

Mount already-built static output after API routes; this feature does not
perform server-side rendering:

```python
from fastapi import Depends, FastAPI

app = FastAPI()
app.frontend(
    "/",
    directory="dist",
    fallback="auto",
    check_dir="auto",
    dependencies=[Depends(require_session)],
)
```

Normal API routes win. Automatic fallback prefers `404.html`; otherwise it
uses `index.html` only for missing browser `GET` or `HEAD` navigations, not
missing assets. Frontend dependencies can contribute headers and background
tasks on releases containing that response-effect fix.

Persist a shared application target for development and deployment tooling:

```toml
[tool.fastapi]
entrypoint = "backend.main:app"
```

`fastapi deploy` targets FastAPI Cloud. `fastapi[standard]` includes its CLI;
use `fastapi[standard-no-fastapi-cloud-cli]` to omit it. Read
[frontend-cli-and-docs.md](references/frontend-cli-and-docs.md) for frontend
fallbacks, directory checking, dependencies, Vibe, ReDoc, and tracebacks.

## Check adjacent integrations

- Read [sqlmodel.md](references/sqlmodel.md) before changing Pydantic field
  forms, DML execution, relationships, or deletion cascades.
- Read [starlette.md](references/starlette.md) before adopting Starlette 1.0 or
  changing lifespan, templates, CORS, multipart limits, cookies, or streaming.
- Read [uvicorn.md](references/uvicorn.md) before changing workers, reload,
  protocols, trusted proxies, root paths, Unix sockets, or logging.
