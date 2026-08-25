# Dependency injection

## Yield cleanup and scopes

### Response-lifetime cleanup

FastAPI 0.118.0 (`2025-09`) defers default `yield` dependency teardown and
`UploadFile` closure until after the response is sent. Streaming code can use a
yielded database session or similar resource for the full response.

### Explicit scopes

FastAPI 0.121 (`2025-11`) adds `scope` to `Depends()` for dependencies that
yield. `scope="function"` cleans up after the operation returns but before the
response is sent. `scope="request"` keeps the resource alive until after the
response. FastAPI 0.121.1 also fixes top-level function-scoped dependencies.

```python
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()

def session():
    value = open_session()
    try:
        yield value
    finally:
        value.close()

@app.get("/items")
def items(value: Annotated[Session, Depends(session, scope="function")]):
    return read_items(value)
```

### Scope nesting

A request-scoped dependency may use only request-scoped children. A
function-scoped dependency may use function- or request-scoped children. This
rule preserves reverse-order teardown: a parent can still use its children in
its exit code (`dependency-lifecycle`).

Do not put a function-scoped child below a request-scoped parent.

### Caching

FastAPI 0.123 (`2025-11`) restores ordinary dependency caching only for an
unscoped dependency tree with no scoped descendants. A dependency that has a
scope, or has a scoped descendant, does not follow the normal unscoped cache
path.

### Exceptions after `yield`

An operation exception is thrown back into its `yield` dependencies. Since
FastAPI 0.110.0, catching and swallowing it does not forward it automatically;
this can produce a `500` without useful server logging. Re-raise the original
or raise a replacement HTTP exception (`dependency-lifecycle`).

```python
def guard():
    try:
        yield
    except InternalError:
        logger.exception("request failed")
        raise
```

## Callable dependencies and annotations

FastAPI 0.123.5 (`2025-11`) supports `functools.partial()` and wrapped
dependables, including forward-reference annotations. Follow-up 0.123.x fixes
cover combined partial/wrapped synchronous and asynchronous callables and a
callable class supplied as the class itself rather than an instance.

```python
from functools import partial
from typing import Annotated
from fastapi import Depends, FastAPI

def require_role(role: str) -> str:
    return role

require_admin = partial(require_role, "admin")

@app.get("/admin")
def admin(role: Annotated[str, Depends(require_admin)]):
    return {"role": role}
```

FastAPI 0.124.2 (`2025-12`) resolves unevaluated string annotations and types
imported only under `TYPE_CHECKING`. FastAPI 0.128.1 extends the fix to Python
3.14's PEP 649 annotation behavior. FastAPI 0.124.1 also handles fields when
Pydantic enables `arbitrary_types_allowed=True`.

## Injected responses

FastAPI 0.128.2 (`2025-12`) lets a dependency-bound parameter retain the
precise `Response` annotation:

```python
from typing import Annotated
from fastapi import Depends, FastAPI, Response

def text_response() -> Response:
    return Response("ready", media_type="text/plain")

@app.get("/ready")
def ready(response: Annotated[Response, Depends(text_response)]):
    return response
```
