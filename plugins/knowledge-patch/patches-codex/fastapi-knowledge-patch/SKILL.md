---
name: fastapi-knowledge-patch
description: FastAPI
version: "0.135.3"
license: MIT
metadata:
  author: Nevaberry
---


# FastAPI Knowledge Patch

Use this skill when changing a FastAPI application or its Pydantic, SQLModel,
Starlette, or Uvicorn integration. Inspect the project's pinned versions before
applying version-dependent guidance, and trust its code and tests when they
demonstrate different behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrading-and-compatibility.md](references/upgrading-and-compatibility.md) | Runtime and dependency floors, package extras, migration bridges, removals, and deprecations |
| [dependency-injection.md](references/dependency-injection.md) | `yield` scopes and teardown, caching, callable dependencies, annotations, and injected responses |
| [requests-and-security.md](references/requests-and-security.md) | Forms and parameter models, strict JSON requests, authentication, OAuth2 scopes, and exception headers |
| [responses-and-streaming.md](references/responses-and-streaming.md) | Typed JSON, JSON Lines, raw streams, SSE, iterable responses, and disconnects |
| [openapi-and-pydantic.md](references/openapi-and-pydantic.md) | Pydantic validation and serialization, dynamic models, annotations, and OpenAPI schema generation |
| [frontend-cli-and-docs.md](references/frontend-cli-and-docs.md) | Static frontends and fallbacks, dependencies, CLI discovery and deployment, Vibe, and documentation UIs |
| [sqlmodel.md](references/sqlmodel.md) | SQLModel compatibility, fields, typing, relationships, and cascades |
| [starlette.md](references/starlette.md) | Starlette migration, lifespan, templates, CORS, cookies, multipart forms, and files |
| [uvicorn.md](references/uvicorn.md) | Uvicorn runtime, workers, reload, protocols, proxies, ASGI scopes, and logging |

## Breaking changes and deprecations

### Meet the runtime and dependency floors

Check FastAPI, Python, Pydantic, Starlette, HTTPX, and optional serializer pins
together. Python 3.14 applications must use Pydantic V2, and FastAPI 0.129+
requires Python 3.10. Upgrade `pydantic` and `pydantic-core` together because
Pydantic 2.12 rejects a mismatched core at startup. Starlette compatibility has
changed repeatedly, so confirm the range supported by the pinned FastAPI
release rather than upgrading it independently. Read
[upgrading-and-compatibility.md](references/upgrading-and-compatibility.md)
before changing dependency constraints.

### Finish Pydantic V1 migration

FastAPI 0.119 allowed V1 and V2 models together only as a migration bridge.
Move every `pydantic.v1` import to V2 before FastAPI 0.128 and before Python
3.14. Do not plan new mixed-model designs around the removed bridge.

### Replace deprecated integrations

- Replace `fastapi.middleware.wsgi.WSGIMiddleware` with
  `a2wsgi.WSGIMiddleware`.
- Depend on `fastapi`, not the deprecated `fastapi-slim` wrapper.
- Replace `ORJSONResponse` and `UJSONResponse` with an ordinary typed return or
  `response_model`; FastAPI's standard JSON path now serializes with Pydantic.
- Replace Starlette registration decorators and startup/shutdown callbacks with
  lifespan plus declarative routes, middleware, and exception handlers.
- Stop calling removed Uvicorn `Config.setup_event_loop()` and migrate away
  from the deprecated `uvicorn.workers` module.

### Send an explicit JSON media type

FastAPI 0.132 rejects a JSON request without a valid JSON `Content-Type` by
default. Fix clients to send `application/json`. Use the compatibility switch
only while migrating clients:

```python
from fastapi import FastAPI

app = FastAPI(strict_content_type=False)
```

The strict default also blocks a narrow class of credential-free, headerless
browser requests from bypassing CORS preflight; it does not replace
authentication for privileged endpoints.

### Update schema consumers

- Expect `bytes` schemas to use
  `contentMediaType: application/octet-stream`, not `format: binary`, from
  FastAPI 0.129.1.
- Expect validation-error schemas to include `input` and `ctx`.
- Expect Pydantic 2.12 changes for decimal patterns, function titles,
  typed-dictionary `additionalProperties`, and configurable primitive-union
  type arrays.
- Preserve literal schema attributes named `$ref` and accept OpenAPI `type`
  arrays.

## Dependency lifecycles

FastAPI 0.118 keeps default `yield` dependencies alive until the response has
finished, including streaming responses. FastAPI 0.121 makes cleanup timing
explicit:

| Scope | Cleanup timing | Allowed scoped children |
| --- | --- | --- |
| `"function"` | After the operation returns, before sending the response | Function or request scope |
| `"request"` | After the response is sent | Request scope only |

Choose the shortest scope that still covers resource use:

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
def items(
    resource: Annotated[Resource, Depends(session, scope="function")],
):
    return read_items(resource)
```

A request-scoped dependency cannot use a function-scoped child because it may
need that child during teardown. Scoped dependency trees also do not use the
ordinary unscoped cache path. Re-raise exceptions caught after `yield`; merely
swallowing them can hide useful server logging.

Read [dependency-injection.md](references/dependency-injection.md) before
changing scopes, wrappers, partials, callable classes, or forward annotations.

## Streaming response selection

Choose the response path deliberately:

| Goal | Declaration | Behavior |
| --- | --- | --- |
| JSON Lines | Yield normally and annotate `Iterable[Item]` or `AsyncIterable[Item]` | Each item is validated, filtered, documented, and encoded as `application/jsonl` |
| Raw chunks | Set `response_class=StreamingResponse` | Strings and bytes bypass Pydantic; the generator annotation is for typing only |
| Server-Sent Events | Set `response_class=EventSourceResponse` | Plain values become JSON in `data:`; `ServerSentEvent` controls metadata and raw data |

```python
from collections.abc import AsyncIterable
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent

app = FastAPI()

@app.get("/events", response_class=EventSourceResponse)
async def events() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(
        data={"status": "ready"}, event="status", id="1", retry=5000
    )
    yield ServerSentEvent(raw_data="[DONE]", event="done")
```

`data` is JSON encoded; mutually exclusive `raw_data` carries preformatted
text. SSE defaults include a 15-second keepalive, `Cache-Control: no-cache`,
and `X-Accel-Buffering: no`. Read
[responses-and-streaming.md](references/responses-and-streaming.md) for status
codes, model filtering, cancellation, router inclusion, and multiline events.

## Requests and security

Built-in authentication dependencies return `401 Unauthorized`, rather than
`403 Forbidden`, when credentials are missing. Preserve an old `403` contract
by overriding `make_not_authenticated_error()` and returning an exception
instance. Credentials from `Authorization` have surrounding whitespace
removed, and nested security scopes now propagate into runtime checks and
OpenAPI.

Parameter parsing now handles union-valued forms, empty controls, extra list
values, aliases on `Query`, `Header`, and `Cookie` models, optional sequences,
and tagged discriminated-union bodies. Read
[requests-and-security.md](references/requests-and-security.md) before keeping
compatibility workarounds.

## Pydantic and OpenAPI essentials

For Pydantic 2.12:

- Define `@model_validator(mode="after")` as an instance method.
- Use `MISSING` to distinguish omission from `None`.
- Use `Field(exclude_if=...)` and `exclude_computed_fields=True` for selective
  serialization.
- Use `model_validate(data, extra="forbid")` for a one-call extra-field policy.
- Use `union_format="primitive_type_array"` where a consumer prefers eligible
  primitive unions as a `type` array.
- Rebuild dynamic fields from `FieldInfo.asdict()` instead of mutating reused
  `FieldInfo` objects.
- Use `ValidateAs` to validate a custom class through a supported intermediate
  type.

FastAPI accepts OpenAPI `type` arrays and `external_docs`, emits top-level
security schemes correctly, and supports PEP 695 aliases in endpoint types.
Read [openapi-and-pydantic.md](references/openapi-and-pydantic.md) before
changing validation, serialization, dynamic models, discriminators, or schema
generation.

## Static frontends and CLI

`app.frontend()` and `router.frontend()` serve already-built static output
after API route matching. They are not server-side rendering. Normal routes win,
and frontend responses remain inside middleware and inherit dependencies.
`fallback="auto"` prefers `404.html`; otherwise it uses `index.html` only for
missing browser navigations, not missing assets.

Persist application discovery for `fastapi dev`, editors, and deployment:

```toml
[tool.fastapi]
entrypoint = "backend.main:app"
```

Read [frontend-cli-and-docs.md](references/frontend-cli-and-docs.md) before
changing fallback selection, directory checks, frontend dependencies, CLI
extras, deployment, Vibe, or ReDoc customization.

## Ecosystem checks

- Read [sqlmodel.md](references/sqlmodel.md) before changing SQLModel package
  pins, Pydantic field forms, DML execution, relationships, or cascades.
- Read [starlette.md](references/starlette.md) before adopting Starlette 1.0 or
  changing lifespan, templates, CORS, cookies, multipart limits, files, or
  response transmission.
- Read [uvicorn.md](references/uvicorn.md) before changing workers, reload,
  custom protocols, proxy trust, Unix sockets, root paths, WebSockets,
  environment configuration, or logging.
