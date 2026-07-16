---
name: fastapi-knowledge-patch
description: FastAPI 0.135.3 compatibility. Use for FastAPI work.
license: MIT
version: 0.135.3
metadata:
  author: Nevaberry
---

# FastAPI Knowledge Patch

Baseline: FastAPI through 0.115.12 with established Pydantic v2 integration, dependency injection, endpoints, OpenAPI, middleware, security, CORS, background tasks, WebSockets, and lifespan events; covered range: included changes through the `2026-07` batch.

Use this patch before changing a FastAPI application or its Pydantic, SQLModel, Starlette, or Uvicorn integration. Read only the references relevant to the task, but always check the compatibility and deprecation notes before upgrading.

Coverage IDs: `pydantic-2.11.2`, `2025-06`, `2025-07`, `2025-09`, `pydantic-2.12-guide`, `pydantic-2.12.0`, `2025-10`, `2025-11`, `2025-12`, `2026-02`, `2026-03`, `2026-07`.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrading-and-compatibility.md](references/upgrading-and-compatibility.md) | Python, Pydantic, Starlette, and httpx constraints; package extras; migration bridges; removals and deprecations |
| [dependency-injection.md](references/dependency-injection.md) | `yield` scopes and teardown, caching, callable dependencies, annotation resolution, injected responses |
| [requests-and-security.md](references/requests-and-security.md) | Forms and parameter models, strict JSON media types, tagged unions, authentication status and OpenAPI scopes |
| [responses-and-streaming.md](references/responses-and-streaming.md) | Model serialization, JSON Lines, raw streaming, SSE, response annotations, byte schemas |
| [openapi-and-pydantic.md](references/openapi-and-pydantic.md) | Pydantic 2.11/2.12 validation and serialization, dynamic models, JSON Schema, FastAPI OpenAPI fixes |
| [frontend-cli-and-docs.md](references/frontend-cli-and-docs.md) | Static frontends and fallbacks, CLI entrypoints and deployment, Vibe support, ReDoc |
| [sqlmodel.md](references/sqlmodel.md) | SQLModel compatibility, field forms, typing, relationships, indexes |
| [starlette.md](references/starlette.md) | Starlette 1.0 migration, typed state, templates, CORS, cookies, multipart, testing, files, WebSockets |
| [uvicorn.md](references/uvicorn.md) | Uvicorn runtime and reload changes, workers, protocols, proxy trust, ASGI scopes, logging |

## Breaking changes and migrations

### Meet the runtime and dependency floors

Before upgrading, align the environment:

| Release | Requirement or behavior |
| --- | --- |
| FastAPI 0.125 | Python 3.9+; Python 3.8 remains capped at 0.124.4 |
| FastAPI 0.126 | Pydantic 2.7+; standalone Pydantic V1 no longer works |
| FastAPI 0.128 | The bundled `pydantic.v1` bridge is removed |
| FastAPI 0.129 | Python 3.10+ |
| FastAPI 0.133 | Starlette 1.x is accepted |
| FastAPI 0.134 | Starlette 0.46+ is required for streaming support |
| FastAPI 0.135.2 | Pydantic 2.9+ |

Use Pydantic V1 and V2 together only as the temporary FastAPI 0.119 migration bridge. Migrate all `pydantic.v1` imports before FastAPI 0.128 and before Python 3.14.

### Replace deprecated integrations

- Replace `ORJSONResponse` and `UJSONResponse` with ordinary Pydantic return annotations or `response_model`; FastAPI 0.130 serializes these through Pydantic and 0.131 deprecates the specialized classes.
- Replace `fastapi.middleware.wsgi.WSGIMiddleware` with `a2wsgi.WSGIMiddleware`.
- Depend on `fastapi`, not `fastapi-slim`; depend on `sqlmodel`, not `sqlmodel-slim`.
- Replace Starlette startup/shutdown callbacks and registration decorators with an async-context-manager `lifespan` before Starlette 1.0.
- Stop calling removed Uvicorn `Config.setup_event_loop()` and stop importing the deprecated `uvicorn.workers` namespace.

### Send explicit JSON content types

FastAPI 0.132 rejects a JSON body without a valid JSON `Content-Type` by default. Fix clients to send `application/json`. Use the compatibility switch only while migrating clients:

```python
from fastapi import FastAPI

app = FastAPI(strict_content_type=False)
```

### Update schema consumers

- Expect `bytes` schemas to use `contentMediaType: application/octet-stream`, not `format: binary`, from FastAPI 0.129.1.
- Expect Pydantic 2.12 schema changes for `Decimal`, function titles, typed-dict `additionalProperties`, and configurable primitive-union type arrays.
- Update snapshots for the OpenAPI `ValidationError` fields `input` and `ctx`.

## Yield dependency lifecycles

FastAPI 0.118 restored response-lifetime cleanup: a default `yield` dependency exits after the response is sent, so streaming code may keep using its resource. FastAPI 0.121 makes the lifecycle explicit.

| Scope | Exit timing | Allowed scoped sub-dependencies |
| --- | --- | --- |
| `"function"` | After the path operation returns, before the response is sent | Function or request scope |
| `"request"` | After the response is sent | Request scope only |

Choose the shortest scope that still covers resource use:

```python
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()

async def session():
    resource = open_resource()
    try:
        yield resource
    finally:
        resource.close()

@app.get("/items")
def items(resource: Annotated[Resource, Depends(session, scope="function")]):
    return read_items(resource)
```

Do not place a function-scoped dependency beneath a request-scoped parent: the parent must remain able to use its children during teardown. Also account for scoped trees in caching; a dependency with a scope, or with a scoped descendant, does not use the normal unscoped cache path.

Read [dependency-injection.md](references/dependency-injection.md) before changing dependency scopes, wrappers, partials, callable classes, or forward annotations.

## Streaming response selection

FastAPI 0.134 lets a path operation stream by yielding. Select the response mode deliberately:

| Goal | Declaration | Serialization |
| --- | --- | --- |
| JSON Lines | Yield normally; annotate `Iterable[Item]` or `AsyncIterable[Item]` | Each item is Pydantic-validated, filtered, documented, and encoded; media type is `application/jsonl` |
| Raw chunks | Set `response_class=StreamingResponse` | Strings and bytes bypass Pydantic; the generator annotation is ignored at runtime |
| Server-Sent Events | Set `response_class=EventSourceResponse` | Plain values become JSON in `data:`; `ServerSentEvent` controls event metadata or raw data |

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

Use `data` for JSON-encoded values and mutually exclusive `raw_data` for preformatted text. SSE sends a keepalive comment every 15 seconds and defaults to `Cache-Control: no-cache` plus `X-Accel-Buffering: no`.

Give a raw `StreamingResponse` an explicit media type, normally through a subclass. Expect Starlette `ClientDisconnect` when the client drops during streaming.

Read [responses-and-streaming.md](references/responses-and-streaming.md) for validation, annotation, media-type, and disconnect details.

## Requests and security

### Treat missing credentials as `401`

Built-in security dependencies return `401 Unauthorized`, not `403 Forbidden`, from FastAPI 0.122. To retain a different response, override the hook and return an exception:

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

Credentials parsed from `Authorization` are stripped of surrounding whitespace. Nested security scopes now propagate into runtime checks and OpenAPI; remove workarounds that duplicated nested OAuth2 schemes.

### Rely on corrected parameter parsing

- Union-typed `Form` values work, empty form controls use missing-value semantics, and extra list-valued form fields are handled.
- `Query`, `Header`, and `Cookie` parameter models honor aliases; optional sequences accept `list[str] | None`.
- Tagged discriminated unions are classified as request bodies.

Read [requests-and-security.md](references/requests-and-security.md) for release-specific fixes and OAuth2 metadata.

## Pydantic and OpenAPI essentials

For Pydantic 2.12:

- Define `@model_validator(mode="after")` as an instance method, not a class method.
- Upgrade Pydantic and `pydantic-core` together; a mismatched core version fails at startup.
- Use `MISSING` to distinguish omission from `None`, `Field(exclude_if=...)` for conditional output, and `exclude_computed_fields=True` for computed fields.
- Use `model_validate(data, extra="forbid")` for a one-call extra-field override.
- Use `union_format="primitive_type_array"` when a consumer prefers eligible primitive unions as a `type` array.
- Use `FieldInfo.asdict()` rather than mutating reused `FieldInfo` metadata when rebuilding dynamic fields.

FastAPI now accepts OpenAPI `type` arrays and `external_docs`, preserves literal schema attributes named `$ref`, emits top-level security schemes, and supports PEP 695 aliases in endpoint types.

Read [openapi-and-pydantic.md](references/openapi-and-pydantic.md) before modifying validation, serialization, dynamic models, dataclasses, discriminators, or generated schemas.

## Static frontends, CLI, and documentation

Serve an already-built client after API routes; this is static hosting, not server-side rendering:

```python
from fastapi import FastAPI

app = FastAPI()
app.frontend("/", directory="dist", fallback="auto")
```

Normal API routes win over frontend files. With `fallback="auto"`, FastAPI prefers `404.html`; otherwise it uses `index.html` only for missing `GET` or `HEAD` browser navigations, not missing assets. Set `check_dir=False` when a later build creates the directory. Frontends may also declare dependencies for frontend-wide checks.

Persist the application target for `fastapi dev` and editor tooling:

```toml
[tool.fastapi]
entrypoint = "backend.main:app"
```

`fastapi deploy` targets FastAPI Cloud. The `fastapi[standard]` extra installs its CLI; use `fastapi[standard-no-fastapi-cloud-cli]` to opt out. Account for ReDoc 2.x when testing or customizing the default docs UI.

Read [frontend-cli-and-docs.md](references/frontend-cli-and-docs.md) for fallback, dependency, deployment, and Vibe details.

## Ecosystem checks

When the task touches adjacent layers:

- Read [sqlmodel.md](references/sqlmodel.md) before changing Pydantic field forms, DML execution, relationship cascades, or database indexes.
- Read [starlette.md](references/starlette.md) before adopting Starlette 1.0 or changing lifespan, templates, multipart limits, cookies, files, tests, or WebSocket denial behavior.
- Read [uvicorn.md](references/uvicorn.md) before changing workers, reload, custom protocols, trusted proxies, root paths, Unix sockets, environment configuration, or embedded logging.
