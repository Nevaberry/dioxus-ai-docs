# Frontend, CLI, and documentation

## Static frontend mounting

### Application and router frontends

`app.frontend()` and `router.frontend()` serve already-built static output
after normal path-operation matching (`frontend-cli-and-protocol`). API routes
therefore win. The feature does not perform server-side rendering.

Frontend responses remain inside application middleware and inherit
dependencies declared on the application, router, and `include_router()`.

```python
from fastapi import APIRouter, FastAPI

app = FastAPI()
router = APIRouter()
router.frontend("/", directory="dist")
app.include_router(router, prefix="/app")
```

### Fallback selection

The default `fallback="auto"` first prefers `404.html` and keeps status `404`.
Without that file, it uses `index.html` only for a missing `GET` or `HEAD`
browser navigation. Missing assets and other methods remain `404`. Pass
`"index.html"` or `"404.html"` to choose explicitly, or `None` to disable
fallbacks (`frontend-cli-and-protocol`).

### Directory checks

By default, `frontend()` checks its directory during application creation and
fails early if the build output is absent. Set `check_dir=False` when a later
build stage creates it; a request still errors if it remains missing
(`frontend-cli-and-protocol`).

FastAPI 0.141.0 adds development-oriented `check_dir="auto"` for projects run
with `fastapi dev` (`2026-08`):

```python
app.frontend("/", directory="dist", check_dir="auto")
```

### Dependencies and response effects

FastAPI 0.139.0 lets a frontend mount declare dependencies (`2026-07`), such
as a frontend-wide cookie-authentication check:

```python
from fastapi import Depends

app.frontend(
    "/",
    directory="dist",
    dependencies=[Depends(require_frontend_session)],
)
```

From FastAPI 0.141.1, those dependencies can also add response headers and
schedule background tasks on the frontend response (`2026-08`). Older releases
discard those response effects.

## CLI application discovery and deployment

Persist the import target in `pyproject.toml` so `fastapi dev`, editor
integration, and deployment tools discover the same application without a
repeated file path (`frontend-cli-and-protocol`):

```toml
[tool.fastapi]
entrypoint = "backend.main:app"
```

FastAPI 0.116.0 adds `fastapi deploy` for FastAPI Cloud (`2025-07`). The
`fastapi[standard]` extra installs `fastapi-cloud-cli`; use
`fastapi[standard-no-fastapi-cloud-cli]` to opt out while retaining the other
standard dependencies.

## Documentation and interactive tooling

The bundled ReDoc UI moved to 2.x (`2025-06`). Recheck custom ReDoc integration
code and visual snapshots.

FastAPI 0.135.3 adds `@app.vibe()` and its accompanying Vibe Coding support
(`2026-03`).
