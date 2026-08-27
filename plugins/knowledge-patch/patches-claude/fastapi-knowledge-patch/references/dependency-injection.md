# Dependency injection

## Match cleanup to resource use

FastAPI 0.118.0 defers `yield` dependency teardown and `UploadFile` closure
until after the response is sent (`2025-09`). A default request-scoped
dependency therefore remains available to `StreamingResponse` for the whole
stream.

FastAPI 0.121 makes the lifetime explicit with `Depends(scope=...)`
(`2025-11`):

| Scope | Exit timing | Allowed scoped sub-dependencies |
| --- | --- | --- |
| `"function"` | After the path operation returns, before the response is sent | Function or request scope |
| `"request"` | After the response is sent | Request scope only |

Choose the shortest lifetime that still covers resource use:

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

FastAPI 0.121.1 fixes function-scoped top-level dependencies. Use a release
with that fix before depending on top-level function-scope cleanup timing.

## Scope constraints preserve teardown order

A request-scoped dependency may use only request-scoped sub-dependencies. A
function-scoped dependency may use function- or request-scoped children. Exit
code runs in reverse dependency order, so a parent must not outlive and then
attempt to use a child that has already closed.

```python
from typing import Annotated
from fastapi import Depends

def connection():
    resource = open_connection()
    try:
        yield resource
    finally:
        resource.close()

def repository(
    connection: Annotated[
        Connection, Depends(connection, scope="request")
    ],
):
    yield Repository(connection)
```

FastAPI 0.123 restores ordinary dependency caching only for unscoped trees
with no scoped descendants. A dependency that declares a scope, or contains a
scoped descendant, does not use the normal unscoped cache path.

## Re-raise caught endpoint exceptions

Exceptions from a path operation are thrown back into its `yield`
dependencies. Since FastAPI 0.110.0, catching and swallowing one no longer
forwards it automatically. Re-raise it or raise a deliberate replacement;
otherwise the client may receive a `500` without a useful server log.

```python
import logging
from typing import Annotated
from fastapi import Depends, FastAPI

logger = logging.getLogger(__name__)
app = FastAPI()

class InternalError(Exception):
    pass

def guard():
    try:
        yield
    except InternalError:
        logger.exception("request failed")
        raise

@app.get("/")
def read(_: Annotated[None, Depends(guard)]):
    raise InternalError("failed")
```

## Wrapped, partial, and callable dependencies

FastAPI 0.123.5 accepts `functools.partial()` and wrapped functions as
dependencies, including forward-reference annotations. Later 0.123.x fixes
cover combined partial/wrapped synchronous and asynchronous callables and a
callable class passed as the dependency instead of an instance.

```python
from functools import partial
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()

def require_role(role: str) -> str:
    return role

require_admin = partial(require_role, "admin")

@app.get("/admin")
def admin(role: Annotated[str, Depends(require_admin)]):
    return {"role": role}
```

FastAPI 0.124.2 also resolves non-evaluated strings and annotations referring
to types imported under `TYPE_CHECKING`; FastAPI 0.128.1 carries that behavior
into Python 3.14's PEP 649 annotation semantics (`2025-12`). Prefer upgrading
over manually evaluating annotations or stripping wrappers.

## Injecting a precise response type

FastAPI 0.128.2 permits a dependency-bound parameter to retain its concrete
`Response` annotation:

```python
from typing import Annotated
from fastapi import Depends, FastAPI, Response

app = FastAPI()

def text_response() -> Response:
    return Response("ready", media_type="text/plain")

@app.get("/ready")
def ready(response: Annotated[Response, Depends(text_response)]):
    return response
```

This keeps dependency injection and static typing aligned without weakening
the parameter annotation.
