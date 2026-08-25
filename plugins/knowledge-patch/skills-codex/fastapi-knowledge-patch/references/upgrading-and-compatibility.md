# Upgrading and compatibility

## Runtime and dependency floors

### FastAPI compatibility transitions

The `2025-09` changes pin HTTPX to `>=0.23.0,<1.0.0`, add Pydantic 2.12.0
support, and add Python 3.14 support. Later transitions are cumulative:

| FastAPI release | Requirement or compatibility change |
| --- | --- |
| 0.116.1 | Starlette `>=0.40.0,<0.48.0` |
| 0.116.2 | Starlette upper bound raised to `<0.49.0` |
| 0.120.1 | Starlette 0.49.x accepted through `<0.50.0` |
| 0.121.3 | Starlette 0.50.x accepted through `<0.51.0` |
| 0.125 | Python 3.9+; Python 3.8 remains capped at 0.124.4 |
| 0.126 | Pydantic 2.7+; standalone Pydantic V1 removed |
| 0.128.3 | Starlette `>=0.40.0,<1.0.0` |
| 0.129 | Python 3.10+ |
| 0.133 | Starlette 1.x accepted |
| 0.134 | Starlette 0.46+ required for exception groups and streaming |
| 0.135.2 | Pydantic 2.9+ |

These changes come from `2025-07`, `2025-10`, `2025-11`, `2025-12`,
`2026-02`, and `2026-03`. Check all relevant pins before upgrading.

### Pydantic V1 migration bridge

FastAPI 0.119 (`2025-10`) temporarily permits models imported from
`pydantic.v1` alongside Pydantic V2 models in one application. It is a
migration bridge, not a stable mixed-model architecture, and does not work on
Python 3.14.

FastAPI 0.126 (`2025-12`) removes standalone Pydantic V1 but briefly retains
the bundled `pydantic.v1` path. FastAPI 0.127 emits
`FastAPIDeprecationWarning` for that path, and 0.128 removes it. Migrate every
V1 import before upgrading to 0.128.

### Dependency extras

FastAPI 0.126 (`2025-12`) includes `pydantic-settings>=2.0.0` and
`pydantic-extra-types>=2.0.0` in its standard dependency set. Its `all` extra
later requires `ujson>=5.8.0` and `orjson>=3.9.3`.

Installing `fastapi[standard]` includes the FastAPI Cloud CLI. Use
`fastapi[standard-no-fastapi-cloud-cli]` when the normal standard dependencies
are wanted without that CLI (`2025-07`).

## Package and integration migrations

### Standard JSON serialization

FastAPI 0.130 (`2026-02`) sends typed returns and `response_model` values
through Pydantic's JSON serialization path. `ORJSONResponse` and
`UJSONResponse` are deprecated from FastAPI 0.131. Prefer a typed model return
or `response_model`; only specify a JSON response class when its distinct
encoding path is intentional.

### WSGI adapter

The built-in WSGI adapter is deprecated (`2025-12`). Replace it with `a2wsgi`:

```python
from a2wsgi import WSGIMiddleware

app.mount("/legacy", WSGIMiddleware(legacy_wsgi_app))
```

### Package names

`fastapi-slim` is only a deprecated wrapper around `fastapi` as of 0.128.8
(`2025-12`). Depend directly on `fastapi`.

## Operational upgrade checks

FastAPI 0.124 (`2025-12`) adds path-operation metadata to tracebacks, making
failures easier to associate with endpoints. Remove log-processing assumptions
that endpoint context is unavailable.

ReDoc moved to 2.x in `2025-06`; recheck custom integrations and UI snapshots.

Python 3.14 requires Pydantic V2 (`pydantic-2.12.0`). Upgrade `pydantic` and
`pydantic-core` together because Pydantic 2.12 validates the exact core version
at startup (`pydantic-2.12-guide`).
