# Dependency injection

Use this reference for dependency teardown, scope constraints, caching, callable forms, forward annotations, and response injection.

## `yield` teardown timing

FastAPI 0.118 defers a `yield` dependency's exit code until after the response has been sent. This restores request-lifetime behavior needed by streaming handlers: a `StreamingResponse` can continue using a yielded session, file, or client, and uploaded files close only after transmission completes (`2025-09`).

FastAPI 0.121 makes scope selectable at the dependency declaration (`2025-11`):

- `scope="function"`: run exit code after the path operation returns but before sending the response.
- `scope="request"`: run exit code after sending the response. This is the default lifecycle when the resource must remain live during streaming.

Scopes work anywhere a dependency is declared, including application-level parameterless dependencies. FastAPI 0.121.1 fixes `scope="function"` for that top-level parameterless case:

```python
from fastapi import Depends, FastAPI

async def lifecycle():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        release_resource(resource)

app = FastAPI(dependencies=[Depends(lifecycle, scope="function")])
```

## Scope constraints in dependency trees

Preserve teardown ordering when nesting scoped `yield` dependencies:

- A request-scoped dependency may have only request-scoped sub-dependencies.
- A function-scoped dependency may have function- or request-scoped sub-dependencies.

The rule ensures that a dependency's exit code runs before its children are cleaned up, allowing the parent to use child resources during teardown. Reorganize any tree in which a request-scoped parent depends on a function-scoped child (`dependency-lifecycle`).

## Caching with scopes

FastAPI 0.123.0 restores normal caching for a dependency tree containing no scopes. A dependency that declares a scope, or has any scoped sub-dependency, is excluded from that unscoped cache path. Do not assume that adding a scope preserves the same within-request reuse behavior (`2025-11`).

## Supported callable forms

FastAPI 0.123.5 recognizes `functools.partial()` as a dependable and follows `functools.wraps()` while resolving forward references and wrapped dependencies. FastAPI 0.123.10 completes support for combinations involving:

- Partial and wrapped synchronous functions.
- Partial and wrapped asynchronous functions.
- Classes and asynchronous callable objects.
- Callable classes passed directly rather than instantiated first.

Upgrade to 0.123.10 or newer before removing wrapper workarounds. Preserve `functools.wraps()` metadata in custom decorators so FastAPI can reach the original annotations.

## Deferred and nonstandard annotations

Several fixes remove the need to rewrite valid annotations merely for FastAPI inspection:

- FastAPI 0.123.7 evaluates Python 3.10 stringified and postponed annotations correctly (`2025-11`).
- FastAPI 0.124.1 handles models configured with `arbitrary_types_allowed=True`.
- FastAPI 0.124.2 resolves unevaluated string annotations whose imports are guarded by `TYPE_CHECKING`.
- FastAPI 0.128.1 extends guarded-import handling to Python 3.14 PEP 649 semantics.
- FastAPI 0.128.2 correctly handles fields declared as `Json[list[str]]` and endpoint types declared with Python 3.12 PEP 695 `type` aliases (`2025-12`).

Prefer upgrading over replacing these types with runtime-only annotations or duplicating imports outside `TYPE_CHECKING`.

## Injecting a `Response`

FastAPI 0.128.2 accepts `Response` as the type of an `Annotated` dependency parameter. A dependency may construct and supply the response without triggering an annotation conflict:

```python
from typing import Annotated
from fastapi import Depends, FastAPI, Response

app = FastAPI()

def make_response() -> Response:
    return Response("ok", media_type="text/plain")

@app.get("/")
def root(response: Annotated[Response, Depends(make_response)]) -> Response:
    return response
```

## Frontend dependencies

FastAPI 0.139.0 allows `app.frontend()` to receive dependencies (`2026-07`). Use them for checks that should apply to the whole static frontend, such as automatic cookie authentication, while retaining normal API-route precedence. See [frontend-cli-and-docs.md](frontend-cli-and-docs.md) for frontend routing behavior.
