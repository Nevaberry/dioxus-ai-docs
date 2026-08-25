# Upgrading and compatibility

## Runtime floors

- FastAPI 0.125 requires Python 3.9 or newer. On Python 3.8, installers are
  capped at FastAPI 0.124.4 (`2025-12`).
- FastAPI 0.129 requires Python 3.10 or newer (`2026-02`).
- FastAPI 0.118.3 added Python 3.14 support (`2025-09`), but Python 3.14
  requires Pydantic V2; the bundled Pydantic V1 compatibility implementation
  does not support it.
- SQLModel 0.0.35, Starlette 0.50, and Uvicorn 0.40 also require Python 3.10
  or newer. Align the entire serving stack rather than checking FastAPI alone.

## Pydantic floors and the V1 migration bridge

FastAPI 0.118.1 supports Pydantic 2.12.0 (`2025-09`). FastAPI 0.126 requires
Pydantic 2.7 or newer, and FastAPI 0.135.2 raises that floor to Pydantic 2.9
or newer (`2026-03`).

FastAPI 0.119 temporarily allows `pydantic.v1` and Pydantic V2 models in the
same application (`2025-10`). Treat this strictly as a migration bridge:

```python
from fastapi import FastAPI
from pydantic import BaseModel as BaseModelV2
from pydantic.v1 import BaseModel as BaseModelV1

app = FastAPI()

class LegacyItem(BaseModelV1):
    name: str

class Item(BaseModelV2):
    title: str

@app.post("/items", response_model=Item)
def create_item(item: LegacyItem):
    return {"title": item.name}
```

FastAPI 0.126 drops standalone Pydantic V1 but temporarily retains
`pydantic.v1`; 0.127 emits `FastAPIDeprecationWarning` for the bridge; 0.128
removes it. Finish the migration before FastAPI 0.128 or Python 3.14.

Pydantic 2.12 also requires the exact matching `pydantic-core`; a mismatch
fails explicitly during startup. Update the two packages together. Its mypy
plugin supports only the latest released mypy, rather than the rolling
six-month range previously supported.

## Starlette compatibility

Use a Starlette version inside the FastAPI release's declared range:

| FastAPI | Accepted Starlette range |
| --- | --- |
| 0.116.1 | `>=0.40.0,<0.48.0` (`2025-07`) |
| 0.116.2 | `>=0.40.0,<0.49.0` |
| 0.120.1 | `<0.50.0` |
| 0.121.3 | `<0.51.0` (`2025-11`) |
| 0.128.3 | `>=0.40.0,<1.0.0` |
| 0.133 | Starlette 1.0 and newer supported |
| 0.134 | Starlette minimum raised to 0.46.0 |

FastAPI 0.128.3 reimplements `on_event` across its pre-1.0 Starlette range,
preserving existing callback behavior. That does not change Starlette 1.0's
removal of the underlying registration APIs; migrate to lifespan before
adopting Starlette 1.0. FastAPI 0.134's higher minimum supplies the needed
exception-group behavior.

## Other dependency and packaging changes

- FastAPI 0.117 pins HTTPX to `>=0.23.0,<1.0.0` (`2025-09`).
- FastAPI 0.126's `standard` dependencies include
  `pydantic-settings>=2.0.0` and `pydantic-extra-types>=2.0.0`.
- The `all` extra later raises its optional JSON floors to `ujson>=5.8.0`
  and `orjson>=3.9.3`.
- `fastapi[standard]` includes `fastapi-cloud-cli`; use
  `fastapi[standard-no-fastapi-cloud-cli]` to keep the other standard
  dependencies without that CLI.
- Depend on `fastapi` directly. FastAPI 0.128.8 turns `fastapi-slim` into a
  deprecated wrapper around the main package.
- Depend on `sqlmodel` directly; `sqlmodel-slim` is discontinued.

## Response and adapter deprecations

FastAPI 0.130 serializes JSON through Pydantic when an operation declares a
Pydantic return annotation or `response_model`. `ORJSONResponse` and
`UJSONResponse` are deprecated from FastAPI 0.131; prefer the ordinary typed
response path.

The built-in WSGI adapter is deprecated. Replace it with `a2wsgi`:

```python
from a2wsgi import WSGIMiddleware

app.mount("/legacy", WSGIMiddleware(legacy_wsgi_app))
```

## Annotation compatibility

FastAPI 0.124.2 resolves unevaluated string annotations and types imported
only under `TYPE_CHECKING`; 0.128.1 extends that correction to Python 3.14's
PEP 649 behavior. FastAPI 0.124.1 also handles fields correctly when Pydantic
uses `arbitrary_types_allowed=True`.

FastAPI 0.128.2 accepts PEP 695 `TypeAliasType` objects made by Python 3.12's
`type` statement in path-operation annotations:

```python
from fastapi import FastAPI

app = FastAPI()
type ItemId = int

@app.get("/items/{item_id}")
def read_item(item_id: ItemId):
    return {"item_id": item_id}
```

## Upgrade verification

After changing versions, run schema snapshot tests and endpoint tests that
cover dependency teardown, authentication failures, strict request content
types, streaming cancellation, and custom documentation. Recheck application
startup for dependency-pair errors and import-time deprecation warnings.
