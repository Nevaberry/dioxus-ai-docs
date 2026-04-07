# Breaking Changes (FastAPI 0.112-0.135.3)

## strict_content_type Default (0.132.0)

FastAPI now checks `Content-Type` header on JSON requests by default. Requests without a valid JSON content type (e.g., `application/json`) are rejected with 422.

Disable per-route if clients don't send proper headers:

```python
@app.post("/legacy", strict_content_type=False)
async def legacy_endpoint(data: MyModel):
    ...
```

## Security Classes Return 401 (0.122.0)

`HTTPBearer`, `OAuth2`, `HTTPBasic`, and other security classes now raise **401** (not 403) when credentials are missing. This is the correct HTTP standard behavior.

If tests or client code relied on 403:

```python
# Old behavior (before 0.122.0):
# Missing credentials -> 403 Forbidden

# New behavior (0.122.0+):
# Missing credentials -> 401 Unauthorized
```

## bytes Field JSON Schema Change (0.129.1)

The `bytes` field JSON Schema representation changed:
- **Before**: `"format": "binary"`
- **After**: `"contentMediaType": "application/octet-stream"`

This breaks any code making assertions on generated OpenAPI schemas that include `bytes` fields.

## Pydantic v1 Fully Dropped (0.126.0-0.128.0)

No more `pydantic.v1` compatibility shim. All code must use Pydantic v2 APIs.

- 0.119.0 temporarily added mixed v1/v2 model support as a migration bridge
- 0.128.0 removed that bridge entirely
- Minimum Pydantic version: 2.9.0

## Python Version Drops

- **0.125.0**: Dropped Python 3.8
- **0.129.0**: Dropped Python 3.9
- Minimum: Python 3.10. Python 3.14 supported.

## fastapi-slim Dropped (0.129.2)

The `fastapi-slim` package is no longer published. Use `fastapi` or `fastapi[standard]`.

## Starlette 1.0 Hard Removals (via FastAPI 0.133.0+)

These are **not deprecation warnings** -- they are hard removals that raise errors:

| Removed API | Replacement |
|------------|-------------|
| `@app.on_event("startup")` | `lifespan=` context manager |
| `@app.on_event("shutdown")` | `lifespan=` context manager |
| `on_startup` parameter | `lifespan=` parameter |
| `on_shutdown` parameter | `lifespan=` parameter |
| `app.add_event_handler()` | `lifespan=` context manager |
| `@app.route()` decorator | `routes=` parameter with `Route()` |
| `@app.websocket_route()` | `routes=` with `WebSocketRoute()` |
| `@app.exception_handler()` | `exception_handlers=` parameter |
| `@app.middleware()` | `middleware=` parameter |
| `TemplateResponse(name, context)` | `TemplateResponse(request, name, ...)` |
| `Jinja2Templates(**env_options)` | `env=` with pre-configured `jinja2.Environment` |
| `FileResponse(method=...)` | Removed entirely |

### Jinja2Templates Behavioral Changes (Starlette 1.0)

- **Autoescape enabled by default** -- security improvement but behavioral change for templates with HTML content
- `jinja2` must now be installed to even `import Jinja2Templates` (not just when instantiating)

### Lifespan Migration Pattern

```python
# BROKEN in Starlette 1.0:
app = FastAPI()

@app.on_event("startup")  # AttributeError
async def startup():
    ...

# CORRECT:
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code
    yield
    # shutdown code

app = FastAPI(lifespan=lifespan)
```

## Pydantic 2.12 Breaking Changes

### @model_validator(mode='after') Must Be Instance Method

Using `@classmethod` with `@model_validator(mode='after')` now emits a deprecation warning:

```python
# DEPRECATED:
class Model(BaseModel):
    @model_validator(mode='after')
    @classmethod
    def validate(cls, model, info): ...

# CORRECT:
class Model(BaseModel):
    @model_validator(mode='after')
    def validate(self, info): ...
```

### Field Metadata Warning in Invalid Contexts

Using field-specific metadata like `alias` or `exclude` where it has no effect now warns:

```python
# WRONG -- alias can't be used on type aliases:
type AliasedInt = Annotated[int, Field(alias='b')]

# WRONG -- exclude must be outermost:
c: Optional[Annotated[int, Field(exclude=True)]]
# CORRECT:
c: Annotated[Optional[int], Field(exclude=True)]
```

## ORJSONResponse / UJSONResponse Deprecated (0.131.0)

No longer needed. FastAPI 0.130.0+ uses Pydantic's Rust-based JSON serializer automatically when a Pydantic return type annotation or `response_model` is declared. Without either, falls back to `jsonable_encoder`.

## HTTPException.headers Accepts Mapping (0.128.7)

`HTTPException.headers` parameter type changed from `dict` to `Mapping`, allowing any mapping type.
