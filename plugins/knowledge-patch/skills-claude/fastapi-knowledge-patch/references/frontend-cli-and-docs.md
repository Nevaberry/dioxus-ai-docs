# Frontend, CLI, and documentation

## Mount built static frontends

`app.frontend()` and `router.frontend()` serve previously built static output;
they do not perform server-side rendering. Frontend matching happens after
ordinary path operations, so API routes win. Responses remain inside
application middleware and inherit dependencies from the application, router,
and `include_router()`.

```python
from fastapi import APIRouter, FastAPI

app = FastAPI()
router = APIRouter()
router.frontend("/", directory="dist")
app.include_router(router, prefix="/app")
```

## Choose fallback behavior

The default `fallback="auto"` prefers `404.html` and keeps status `404`. If
that file does not exist, it uses `index.html` only for missing `GET` or `HEAD`
browser navigations. Missing assets and other methods remain `404`.

Pass `"index.html"` or `"404.html"` to choose explicitly, or `None` to disable
fallback handling:

```python
app.frontend("/", directory="dist", fallback="index.html")
```

## Control directory checks

By default, `frontend()` verifies its directory when the application is
created and fails early when build output is absent. Set `check_dir=False`
when a later build step creates the directory. A request still raises an error
if the directory remains missing.

```python
app.frontend("/", directory="dist", check_dir=False)
```

FastAPI 0.141.0 adds development-oriented `check_dir="auto"` for projects run
with `fastapi dev` (`2026-08`):

```python
from fastapi import FastAPI

app = FastAPI()
app.frontend("/", directory="dist", check_dir="auto")
```

## Protect a whole frontend

FastAPI 0.139.0 allows `app.frontend()` dependencies, enabling frontend-wide
checks such as cookie authentication (`2026-07`):

```python
from fastapi import Depends, FastAPI

app = FastAPI()

def require_frontend_session():
    ...

app.frontend(
    "/",
    directory="dist",
    dependencies=[Depends(require_frontend_session)],
)
```

From FastAPI 0.141.1, those dependencies can also add response headers and
schedule background tasks. Earlier releases execute the dependencies but lose
those effects on the frontend response.

## Persist application discovery

Store the import target in `pyproject.toml` so `fastapi dev`, editor
integration, and deployment tooling discover the same application without a
repeated path argument:

```toml
[tool.fastapi]
entrypoint = "backend.main:app"
```

## Deployment CLI and extras

FastAPI 0.116.0 adds `fastapi deploy` for FastAPI Cloud (`2025-07`). Installing
`fastapi[standard]` includes `fastapi-cloud-cli`. Use
`fastapi[standard-no-fastapi-cloud-cli]` to retain the other standard
dependencies without that deployment CLI.

```console
pip install "fastapi[standard]"
fastapi deploy
```

## Vibe support

FastAPI 0.135.3 adds `@app.vibe()` and its accompanying Vibe Coding support
(`2026-03`). Account for this application-level decorator when inspecting or
generating application configuration.

## Documentation and diagnostics

FastAPI's bundled documentation UI uses ReDoc 2.x (`2025-06`). Recheck custom
ReDoc integration, styling, and UI snapshots after upgrading.

For Pydantic V2 model descriptions, a form feed (`\f`) ends the public part
included in generated API documentation. Put internal prose after it.

FastAPI 0.124 adds endpoint metadata to tracebacks (`2025-12`), making a
failure easier to associate with the path operation that triggered it. Preserve
that context when wrapping or formatting exceptions for development tools.
