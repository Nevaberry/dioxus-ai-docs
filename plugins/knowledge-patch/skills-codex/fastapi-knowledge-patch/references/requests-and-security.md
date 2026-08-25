# Requests and security

## Forms and parameter models

### Union-valued forms

FastAPI 0.115.14 (`2025-06`) validates a `Form()` field directly against a
union instead of requiring a manual parser:

```python
from typing import Annotated
from fastapi import FastAPI, Form

app = FastAPI()

@app.post("/values")
async def create_value(value: Annotated[int | float, Form()]):
    return {"value": value}
```

### Aliases, optional sequences, and missing values

FastAPI 0.123.3 (`2025-11`) honors aliases on Pydantic models used with
`Query`, `Header`, and `Cookie`, and accepts optional sequences such as
`list[str] | None`. Related fixes apply missing-value semantics to an empty
HTML form control whose default is `None`, and preserve extra list-valued form
or non-body parameters.

```python
from typing import Annotated
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

class Filters(BaseModel):
    tags: list[str] | None = Field(default=None, alias="tag")

@app.get("/items")
def items(filters: Annotated[Filters, Query()]):
    return filters
```

### Tagged unions are request bodies

FastAPI 0.118.2 (`2025-09`) classifies a Pydantic tagged discriminated union as
a request body, so it is parsed and validated from the body rather than as a
different parameter kind.

### Strict JSON media types

FastAPI 0.132 (`2026-02`) requires a valid JSON media type, normally
`application/json`, before parsing a JSON request. Fix clients to send the
header. During a compatibility migration only, restore headerless parsing with:

```python
from fastapi import FastAPI

app = FastAPI(strict_content_type=False)
```

The strict default protects a narrow trust boundary described by
`frontend-cli-and-protocol`: a credential-free browser request with a
headerless `Blob` body cannot bypass CORS preflight and reach an unauthenticated
localhost or internal-network endpoint merely because that endpoint trusts its
network location. Disabling strict content types removes this barrier and is
not a substitute for authentication.

## Authentication behavior

### Missing credentials return `401`

Built-in security dependencies return `401 Unauthorized`, not `403 Forbidden`,
for missing credentials from FastAPI 0.122 (`2025-11`). Tests and clients that
encoded the old status must be updated or use an explicit compatibility class.

Override `make_not_authenticated_error()` to preserve a `403` contract. Return
the exception; do not raise inside the hook (`frontend-cli-and-protocol`).

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

### Authorization values are normalized

FastAPI 0.128.1 (`2025-12`) strips surrounding whitespace from credentials
parsed from `Authorization`. Built-in authentication dependencies therefore
receive the normalized credential value.

### Nested scopes propagate

FastAPI 0.122.1 (`2025-11`) propagates security scopes through dependency
hierarchies. Fixes through 0.123.9 correct OAuth2 scope declarations and avoid
duplicate schemes when parents and children use different scopes. Remove
workarounds that manually copied nested scopes or schemes.

### Top-level schemes

FastAPI 0.120.4 (`2025-10`) correctly renders OpenAPI security schemes added at
the top-level application.

## OAuth2 password flow metadata

`OAuth2PasswordBearer` accepts `refreshUrl` (`2025-06`) and emits it on the
generated password-flow definition:

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    refreshUrl="/token/refresh",
)
```

The `password` and `client_secret` fields on `OAuth2PasswordRequestForm` now
carry the `password` schema format (`2025-06`), allowing interactive
documentation to render protected inputs.

## Exception headers

FastAPI 0.128.7 (`2025-12`) types `HTTPException.headers` as `Mapping` rather
than only `dict`, so any string-to-string mapping is accepted:

```python
from collections.abc import Mapping
from fastapi import HTTPException

headers: Mapping[str, str] = {"Retry-After": "30"}
raise HTTPException(status_code=429, headers=headers)
```
