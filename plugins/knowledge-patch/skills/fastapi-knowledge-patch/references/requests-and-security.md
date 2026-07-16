# Requests and security

Use this reference for request classification and parsing, strict JSON media types, authentication failures, OAuth2 metadata, and security-scope generation.

## JSON request media types

FastAPI 0.132 validates JSON `Content-Type` by default (`2026-02`). A request carrying JSON without a valid JSON media type is rejected rather than parsed permissively. Update clients to send a valid value such as `Content-Type: application/json`.

Temporarily retain the older behavior at application construction while migrating clients:

```python
from fastapi import FastAPI

app = FastAPI(strict_content_type=False)
```

Prefer correcting clients; the compatibility flag weakens a useful request-boundary check.

## Form parsing

### Union annotations

FastAPI handles union-typed form inputs correctly as of the `2025-06` batch. Keep the intended union annotation instead of widening the field or manually parsing the submitted value.

### Empty and list-valued controls

FastAPI 0.123.2 treats an empty string from an HTML form control as missing. When the parameter default is `None`, an empty control consequently resolves to `None`. The same release correctly handles extra list-valued values in `Form` and other non-body parameters (`2025-11`).

## Query, header, and cookie parameter models

FastAPI 0.123.3 honors aliases on Pydantic parameter models passed through `Query`, `Header`, or `Cookie`. It also fixes Pydantic V2 serialization of optional sequences. FastAPI 0.123.5 completes parsing support for Python 3.10 union syntax such as `list[str] | None`.

Remove manual alias translation and sequence-normalization workarounds when the minimum FastAPI version includes these fixes.

## Request-body classification

FastAPI 0.118.2 recognizes tagged discriminated unions as request bodies (`2025-09`). A parameter using a tagged union no longer needs an explicit workaround to prevent it being classified as a query parameter.

Callable discriminators on PEP 695 aliases are also supported by Pydantic 2.12; see [openapi-and-pydantic.md](openapi-and-pydantic.md).

## Missing authentication credentials

Starting with FastAPI 0.122.0, built-in security classes raise `401 Unauthorized` for absent credentials instead of `403 Forbidden` (`2025-11`). Update response assertions, generated-client expectations, and any middleware keyed to the previous status.

To retain custom behavior, subclass the security implementation and override `make_not_authenticated_error()`. Return the exception; the implementation raises it:

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

FastAPI 0.128.1 strips surrounding whitespace from credentials extracted from the `Authorization` header (`2025-12`). Authentication dependencies therefore receive the normalized credential rather than the original padded substring.

## OAuth2 password flows

`OAuth2PasswordBearer` accepts `refreshUrl` and emits it in the OpenAPI password flow. Use the OpenAPI spelling shown by the constructor:

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    refreshUrl="/auth/refresh",
)
```

`OAuth2PasswordRequestForm` marks both `password` and `client_secret` with OpenAPI's `password` format. Documentation UIs and generated forms can render them as password controls without application schema customization (`2025-06`).

## Nested security scopes and OpenAPI schemes

FastAPI 0.122.1 fixes hierarchical security-scope propagation. FastAPI 0.123.9 fixes the corresponding OpenAPI scope declarations and scheme deduplication for combinations such as a scoped parent dependency with an unscoped child security scheme.

FastAPI 0.120.4 also fixes omission of security schemes added at the top-level application (`2025-10`). Upgrade instead of patching the generated document or duplicating schemes manually.

## Exception header mappings

FastAPI 0.128.7 types `HTTPException.headers` as any `Mapping`, not only `dict`. Read-only and custom mappings are accepted without a static type error:

```python
from types import MappingProxyType
from fastapi import HTTPException

raise HTTPException(
    status_code=404,
    headers=MappingProxyType({"X-Reason": "missing"}),
)
```
