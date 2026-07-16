# Upgrading and compatibility

Use this reference when selecting FastAPI, Python, Pydantic, Starlette, or httpx versions, or when removing deprecated packages and integrations.

## Contents

- [Runtime floors](#runtime-floors)
- [FastAPI and Pydantic migration](#fastapi-and-pydantic-migration)
- [FastAPI and Starlette compatibility](#fastapi-and-starlette-compatibility)
- [Package extras and distributions](#package-extras-and-distributions)
- [Removed and deprecated response integrations](#removed-and-deprecated-response-integrations)
- [Upgrade diagnostics](#upgrade-diagnostics)

## Runtime floors

### FastAPI

- FastAPI 0.118.3 supports Python 3.14 (`2025-09`).
- FastAPI 0.125 drops Python 3.8. On Python 3.8, installers remain on FastAPI 0.124.4 (`2025-12`).
- FastAPI 0.129 drops Python 3.9 and therefore requires Python 3.10 or newer (`2026-02`).

### Pydantic

- Pydantic 2.12 initially supports Python 3.14 and its PEP 649/749 lazy-annotation semantics. A type declared later can be referenced without a string on Python 3.14 (`pydantic-2.12-guide`).
- The Pydantic V1 compatibility implementation does not support Python 3.14. Migrate `pydantic.v1` code before upgrading the interpreter (`pydantic-2.12.0`).
- Pydantic 2.12 requires its one matching `pydantic-core` version and raises at import/startup on a mismatch. Upgrade the pair together and retain exact core constraints in dependency automation.

## FastAPI and Pydantic migration

### Use the V1/V2 bridge only temporarily

FastAPI 0.119 permits a Pydantic V1 request model and a Pydantic V2 response model in one application. This supports incremental migration, but Pydantic V1 support is deprecated:

```python
from fastapi import FastAPI
from pydantic import BaseModel as BaseModelV2
from pydantic.v1 import BaseModel as BaseModelV1

class LegacyInput(BaseModelV1):
    name: str

class Output(BaseModelV2):
    title: str

app = FastAPI()

@app.post("/items", response_model=Output)
def create_item(item: LegacyInput):
    return {"title": item.name}
```

Plan the removal in stages (`2025-10`, `2025-12`):

1. FastAPI 0.126 no longer supports a separately installed Pydantic V1; only the `pydantic.v1` module bundled with V2 remains.
2. FastAPI 0.127 warns on that compatibility module. FastAPI 0.127.1 categorizes the warning as `FastAPIDeprecationWarning`.
3. FastAPI 0.128 removes `pydantic.v1` support entirely.

### Meet Pydantic floors

- FastAPI 0.118.1 adds Pydantic 2.12 compatibility.
- FastAPI 0.126 requires `pydantic>=2.7.0`.
- FastAPI 0.135.2 requires `pydantic>=2.9.0`; upgrade any older Pydantic 2.x pin before adopting it (`2026-03`).

## FastAPI and Starlette compatibility

Use these constraints when resolving or pinning the framework pair:

| FastAPI release | Supported Starlette range or change |
| --- | --- |
| 0.116.1 | `>=0.40.0,<0.48.0` |
| 0.116.2 | Upper bound raised to `<0.49.0`, admitting 0.48.x (`2025-07`) |
| 0.120.1 | Upper bound raised to `<0.50.0`, admitting 0.49.x (`2025-10`) |
| 0.121.3 | Upper bound raised to `<0.51.0`, admitting 0.50.x (`2025-11`) |
| 0.128.3 | `>=0.40.0,<1.0.0` |
| 0.133 | Starlette 1.0 and newer supported |
| 0.134 | Minimum raised from 0.40 to 0.46 for streaming support |

FastAPI 0.128.3 reimplements `on_event` so existing FastAPI behavior continues with newer pre-1.0 Starlette. FastAPI 0.128.6 also restores `APIRouter(on_startup=..., on_shutdown=...)`. These compatibility shims do not reverse Starlette 1.0's own removals; use lifespan for code intended to work directly with Starlette 1.0.

FastAPI 0.117 constrains `httpx` to `>=0.23.0,<1.0.0` (`2025-09`). Retain a compatible httpx constraint when constructing a test environment.

## Package extras and distributions

- FastAPI 0.126 adds `pydantic-settings>=2.0.0` and `pydantic-extra-types>=2.0.0` to the standard dependencies.
- The FastAPI 0.128 `all` extra raises its floors to `ujson>=5.8.0` and `orjson>=3.9.3`.
- `fastapi-slim` becomes a compatibility package depending only on `fastapi` in FastAPI 0.128.8. Use `fastapi` directly in new or updated manifests.
- The `fastapi[standard]` extra installs the FastAPI Cloud CLI as of FastAPI 0.116. Use `fastapi[standard-no-fastapi-cloud-cli]` to keep the other standard dependencies without that CLI.

## Removed and deprecated response integrations

### Specialized JSON responses

FastAPI 0.130 automatically routes JSON serialization through Pydantic when an endpoint declares a Pydantic return type or `response_model`. FastAPI 0.131 deprecates `ORJSONResponse` and `UJSONResponse`; use the standard model-backed path:

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str

app = FastAPI()

@app.get("/items/{name}", response_model=Item)
def read_item(name: str):
    return {"name": name}
```

### WSGI adapter

The built-in `fastapi.middleware.wsgi.WSGIMiddleware` is deprecated. Use `a2wsgi.WSGIMiddleware` when mounting a WSGI application:

```python
from a2wsgi import WSGIMiddleware

app.mount("/legacy", WSGIMiddleware(wsgi_app))
```

## Upgrade diagnostics

- FastAPI 0.124 adds endpoint metadata to route tracebacks, providing handler context without application changes.
- FastAPI 0.120.2 fixes the nested-model input/output schema-separation regression introduced in 0.119.0. Avoid affected 0.119.x versions when accurate nested schemas are required; see [openapi-and-pydantic.md](openapi-and-pydantic.md).
