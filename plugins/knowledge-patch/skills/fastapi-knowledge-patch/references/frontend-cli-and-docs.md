# Frontend, CLI, and documentation

Use this reference for serving static frontend builds, configuring the FastAPI CLI, deploying through the CLI, using Vibe support, and accounting for documentation-UI changes.

## Serve an existing frontend build

Use `app.frontend()` or `router.frontend()` to serve an already-built static directory (`frontend-cli-and-protocol`):

```python
from fastapi import FastAPI

app = FastAPI()
app.frontend("/", directory="dist")
```

This facility serves static build output; it does not execute server-side rendering.

FastAPI checks ordinary path operations before frontend files. If an API route and a frontend asset resolve to the same path, the API route wins. This makes a root frontend compatible with separately declared API endpoints.

## Choose fallback behavior

The default `fallback="auto"` distinguishes browser navigation from missing assets:

1. If the build contains `404.html`, serve it with status `404` for a missing path.
2. Otherwise, serve `index.html` for a missing `GET` or `HEAD` browser-navigation path.
3. Return `404` for missing assets and for other HTTP methods.

Select the policy explicitly when required:

- `fallback="index.html"`: choose the single-page-application entrypoint.
- `fallback="404.html"`: choose the static not-found page.
- `fallback=None`: disable frontend fallback.

## Defer directory checks

FastAPI validates the frontend directory when constructing the application by default. If a later build step creates it, set `check_dir=False`:

```python
app.frontend("/", directory="dist", check_dir=False)
```

If the directory is still missing when first requested, the request raises the directory error; deferral does not make an absent build valid.

## Apply frontend-wide dependencies

FastAPI 0.139.0 lets `app.frontend()` receive dependencies (`2026-07`). Use them for frontend-wide checks such as cookie authentication. The dependencies run before the frontend is served, while normal API-route precedence remains intact.

## Configure the CLI entrypoint

Store the application import string in `pyproject.toml` so `fastapi dev`, integrations, and editors can locate the app without a path argument:

```toml
[tool.fastapi]
entrypoint = "backend.main:app"
```

This is persistent project configuration rather than a per-invocation discovery hint.

## Deploy from the FastAPI CLI

FastAPI 0.116 adds `fastapi deploy`, targeting FastAPI Cloud (`2025-07`):

```console
$ fastapi deploy
```

`fastapi[standard]` installs `fastapi-cloud-cli`, which provides the command. To retain the other standard dependencies without installing the Cloud CLI, use:

```console
$ pip install "fastapi[standard-no-fastapi-cloud-cli]"
```

## Vibe support

FastAPI 0.135.3 adds the application `@app.vibe()` decorator and Vibe Coding support (`2026-03`):

```python
from fastapi import FastAPI

app = FastAPI()

@app.vibe()
def vibe():
    return {"message": "hello"}
```

## ReDoc version

The default FastAPI ReDoc UI uses ReDoc 2.x as of the `2025-06` batch. Update markup-sensitive tests, visual expectations, plugins, and customizations that were written for the earlier major version.
