# Requests and security

## Form and parameter parsing

FastAPI 0.115.14 validates union-typed `Form()` fields directly (`2025-06`):

```python
from typing import Annotated
from fastapi import FastAPI, Form

app = FastAPI()

@app.post("/values")
async def create_value(value: Annotated[int | float, Form()]):
    return {"value": value}
```

FastAPI 0.123.3 applies aliases in `Query`, `Header`, and `Cookie` parameter
models and accepts optional sequences such as `list[str] | None` (`2025-11`).

```python
from typing import Annotated
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

class Filters(BaseModel):
    tags: list[str] | None = Field(default=None, alias="tag")

@app.get("/items")
def items(filters: Annotated[Filters, Query()]):
    return filters
```

Related fixes give empty HTML form controls missing-value semantics when the
default is `None` and preserve extra list-valued form or non-body parameters.
FastAPI 0.140.10 correctly handles sequence types containing nested
`Annotated` metadata (`2026-08`); upgrade instead of flattening the annotation.

FastAPI 0.118.2 recognizes tagged discriminated-union annotations as request
bodies (`2025-09`). Keep the discriminator metadata intact and let FastAPI
parse the union from the body rather than forcing it through a query parameter.

## Require a JSON content type

FastAPI 0.132 validates the JSON media type by default. Clients must send a
valid JSON `Content-Type`, normally `application/json`; headerless or
incorrectly typed JSON is rejected (`2026-02`).

Use the compatibility switch only during a controlled client migration:

```python
from fastapi import FastAPI

app = FastAPI(strict_content_type=False)
```

The strict behavior also blocks a narrow trust-boundary bypass: a browser can
send a credential-free, headerless `Blob` without CORS preflight to a localhost
or internal-network API that trusts network location. Disabling strict content
types removes this barrier. It is not a substitute for authenticating
privileged endpoints.

## Missing credentials return 401

From FastAPI 0.122, built-in security utilities return `401 Unauthorized`, not
`403 Forbidden`, when credentials are absent. If an established client
contract requires `403`, override the compatibility hook and return the
exception instance:

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

Do not raise inside `make_not_authenticated_error()`; the hook's contract is
to return an exception.

## OAuth2 metadata and nested scopes

`OAuth2PasswordBearer` accepts `refreshUrl`, which appears on the generated
password-flow definition. The password request form's `password` and
`client_secret` fields use the password schema format so interactive
documentation masks them (`2025-06`).

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    refreshUrl="/token/refresh",
)
```

FastAPI 0.122.1 propagates security scopes through dependency hierarchies.
Follow-up fixes through 0.123.9 correct OAuth2 declarations and deduplicate
schemes when parents and sub-dependencies use different scopes. Remove
workarounds that repeat nested scopes or schemes manually.

FastAPI 0.120.4 also emits top-level application security schemes correctly
in OpenAPI (`2025-10`).

## Authorization and exception headers

FastAPI 0.128.1 strips surrounding whitespace from credentials parsed from
the `Authorization` header, so built-in dependencies receive the normalized
token (`2025-12`). Avoid depending on preserved leading or trailing spaces.

FastAPI 0.128.7 accepts any string-to-string `Mapping` for
`HTTPException.headers`, not only a concrete dictionary:

```python
from collections.abc import Mapping
from fastapi import HTTPException

headers: Mapping[str, str] = {"Retry-After": "30"}
raise HTTPException(status_code=429, headers=headers)
```

## Public and internal schema descriptions

With Pydantic V2, a form-feed character in a model docstring ends the portion
published in generated API documentation. Keep internal notes after `\f`:

```python
from pydantic import BaseModel

class Item(BaseModel):
    """Public schema description.\fInternal documentation."""

    name: str
```
