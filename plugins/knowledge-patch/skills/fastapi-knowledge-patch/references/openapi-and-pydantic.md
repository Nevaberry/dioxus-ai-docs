# OpenAPI and Pydantic

Use this reference for Pydantic 2.11/2.12 behavior and FastAPI's generated OpenAPI and JSON Schema.

## Contents

- [Pydantic 2.11 validation fixes](#pydantic-211-validation-fixes)
- [Pydantic 2.12 validation and field semantics](#pydantic-212-validation-and-field-semantics)
- [Serialization](#serialization)
- [Dynamic models and dataclasses](#dynamic-models-and-dataclasses)
- [JSON Schema](#json-schema)
- [FastAPI OpenAPI generation](#fastapi-openapi-generation)
- [Typing and tooling](#typing-and-tooling)

## Pydantic 2.11 validation fixes

These fixes are present in Pydantic 2.11.2 (`pydantic-2.11.2`):

- Before assigning a private attribute, Pydantic ensures `__pydantic_private__` exists. Setting a `PrivateAttr` no longer fails merely because private storage was not initialized.
- Discriminated-union schema generation receives definitions already available to the generator. Referenced union variants resolve correctly when building Pydantic or FastAPI schemas.
- The mypy plugin no longer expands a root type while processing variables, avoiding incorrect transformations of variable annotations.
- Parameterized mappings such as `Mapping[str, int]` validate their key and value type arguments. Do not rely on invalid entries being accepted or mishandled.

## Pydantic 2.12 validation and field semantics

### Distinguish omission with `MISSING`

The experimental singleton `pydantic.experimental.missing_sentinel.MISSING` distinguishes “not supplied” from `None` or an ordinary default. A value of `MISSING` is omitted from serialization, and the sentinel branch is omitted from JSON Schema (`pydantic-2.12-guide`):

```python
from pydantic import BaseModel
from pydantic.experimental.missing_sentinel import MISSING

class Config(BaseModel):
    timeout: int | None | MISSING = MISSING
```

Importing `pydantic.experimental` no longer emits `PydanticExperimentalWarning`. Remove warning filters used solely to suppress the import, but continue treating these APIs as experimental.

### Type or close `TypedDict` extras

Pydantic supports PEP 728 `closed` and `extra_items` through `typing_extensions.TypedDict`. Use `typing_extensions` until the active standard library exposes the feature. `TypeAdapter` validates the typed extras, and generated `additionalProperties` indicates closed, unrestricted, or type-constrained extras:

```python
from typing_extensions import TypedDict
from pydantic import TypeAdapter

class Payload(TypedDict, extra_items=int):
    name: str

TypeAdapter(Payload).validate_python({"name": "x", "count": 2})
```

### Override extra-field policy per call

Pass `extra="allow"`, `"ignore"`, or `"forbid"` to `model_validate()` to override the model configuration for one validation:

```python
StrictResult = Model.model_validate(data, extra="forbid")
```

Use this at a strict boundary instead of defining a duplicate model solely to change extra handling.

### Configure temporal units

Set `ConfigDict(val_temporal_unit="seconds")` to control how numeric inputs for `datetime`, `date`, and related temporal types are interpreted; the setting also accepts `"milliseconds"` or `"infer"`. `ser_json_temporal` generalizes `ser_json_timedelta` for temporal JSON output.

### Validate custom types through `ValidateAs`

`ValidateAs` lets a custom type validate through an intermediate Pydantic-supported type and then constructs the target:

```python
from typing import Annotated
from pydantic import TypeAdapter, ValidateAs

adapter = TypeAdapter(
    Annotated[Point, ValidateAs(PointModel, lambda value: Point(value.x, value.y))]
)
```

### Define after-model validators as instance methods

Combining `@classmethod` with `@model_validator(mode="after")` is deprecated and warns. Accept `self` and return the instance:

```python
from pydantic import BaseModel, model_validator

class Model(BaseModel):
    value: int

    @model_validator(mode="after")
    def validate_model(self, info):
        return self
```

### Avoid virtual-subclass registration

Registering a Pydantic model as an ABC virtual subclass with `register()` now warns and is not a reliable capability. Use real inheritance when `isinstance()` or `issubclass()` relationships matter.

## Serialization

### Preserve an empty URL path

Set `ConfigDict(url_preserve_empty_path=True)` to retain `https://example.com` instead of normalizing it to `https://example.com/`. For one field or adapter, use `Annotated[AnyUrl, UrlConstraints(preserve_empty_path=True)]`. This setting may become the Pydantic 3 default.

### Exclude fields conditionally

Use `Field(exclude_if=predicate)` to omit a field when its validated value matches the condition:

```python
from pydantic import BaseModel, Field

class Transaction(BaseModel):
    value: int = Field(ge=0, exclude_if=lambda value: value == 0)

assert Transaction(value=0).model_dump() == {}
```

Use `exclude_computed_fields=True` on serialization calls to omit all `@computed_field` values without listing them individually (`pydantic-2.12.0`):

```python
payload = model.model_dump(exclude_computed_fields=True)
```

### Escape non-ASCII JSON when required

`model_dump_json()` and `TypeAdapter.dump_json()` accept `ensure_ascii=True`. The default is `False`; enabling it emits Unicode escape sequences for non-ASCII characters.

### Scope duck-typed serialization

The `serialize_as_any=True` dump option now behaves like the `SerializeAsAny[T]` annotation and can expose serialization errors hidden by the old flag. Prefer annotating only fields that should include subclass fields, such as `user: SerializeAsAny[User]`, instead of enabling duck typing globally.

## Dynamic models and dataclasses

### Configure generated models

`create_model()` accepts `__base__` and `__config__` together, so a dynamic model can inherit fields and apply new configuration:

```python
from pydantic import ConfigDict, create_model

Dynamic = create_model(
    "Dynamic",
    __base__=Base,
    __config__=ConfigDict(extra="forbid"),
)
```

Pass `__qualname__="Container.Dynamic"` when the generated class needs a controlled qualified name.

Override `__pydantic_on_complete__()` for class-level setup that must run only after a model is fully ready, including after delayed completion of unresolved forward references.

### Rebuild fields through `FieldInfo.asdict()`

Use `FieldInfo.asdict()` to decompose a field for supported dynamic rebuilding or transformation. Do not mutate a `FieldInfo` reused as `Annotated` metadata. Compatibility for that mutation pattern was restored in 2.12.3, but the pattern remains unsupported.

Field-only metadata must be attached to the actual model field. Metadata such as `alias` on a type alias, or `exclude` on only one member inside `Optional`, now warns instead of being silently ignored. Prefer:

```python
Annotated[Optional[int], Field(exclude=True)]
```

The undocumented `FieldInfo.merge_field_infos()` is deprecated.

### Validation-call aliases

`@validate_call` honors `Field(validation_alias=...)` on parameters. Call an aliased keyword by its validation alias as declared instead of manually renaming it before validation.

### Dataclass integration

- Pydantic reads the native `doc` attribute on dataclass fields, preserving their documentation metadata.
- A Pydantic dataclass with `validate_assignment=True` can use property setters without bypassing or conflicting with assignment validation.

### Callable discriminators and type aliases

A callable discriminator can be attached to a union declared with Python 3.12's PEP 695 `type` syntax. Do not rewrite the alias into the older assignment form solely for Pydantic validation.

## JSON Schema

### Choose primitive-union representation

Pass `union_format="primitive_type_array"` to JSON Schema generation to emit eligible primitive unions as a `type` array rather than the default `anyOf`:

```python
from pydantic import TypeAdapter

schema = TypeAdapter(str | None).json_schema(
    union_format="primitive_type_array"
)
```

### Account for other Pydantic 2.12 schema changes

Generated schemas now:

- Include a pattern for `Decimal`.
- Preserve custom titles in function schemas.
- Derive `additionalProperties` from `extra_behavior` in manually constructed typed-dict core schemas.

Update schema snapshots and downstream generators that assert the previous representation.

## FastAPI OpenAPI generation

### Schema shapes and descriptions

- The OpenAPI schema model accepts an array in `type`, such as `{"type": ["string", "null"]}`, matching OpenAPI 3.1 union-style schemas (`2025-09`).
- FastAPI truncates a Pydantic V2 model description at `\f`, keeping trailing internal text out of generated documentation (`2025-06`).
- FastAPI 0.121.2 handles schema attributes literally named `$ref`; FastAPI 0.123.1 stops assuming every remapped Pydantic V2 schema has a `$ref` key (`2025-11`).
- When `separate_input_output_schemas=False`, computed fields generate correctly as of FastAPI 0.123.10, following the initial 0.123.4 correction.
- FastAPI 0.120.2 fixes the nested-model input/output schema-separation regression introduced in 0.119.0 (`2025-10`).

### Application metadata

Pass `external_docs` to `FastAPI` to add an OpenAPI External Documentation Object:

```python
from fastapi import FastAPI

app = FastAPI(external_docs={"url": "https://example.com/guide"})
```

FastAPI 0.120.4 includes security schemes registered at the top-level application. FastAPI 0.123.9 also declares and deduplicates schemes correctly for nested security-scope combinations; see [requests-and-security.md](requests-and-security.md).

### Validation and response schemas

FastAPI 0.128.1 adds `input` and `ctx` to the OpenAPI `ValidationError` schema (`2025-12`). The same release avoids duplicated `anyOf` references when an application-level response defines both `content` and a union `model`.

FastAPI 0.129.1 describes `bytes` with `contentMediaType: application/octet-stream` rather than `format: binary`; see [responses-and-streaming.md](responses-and-streaming.md).

## Typing and tooling

- Pydantic 2.12 supports Python 3.14 PEP 649/749 lazy annotations, so a model can reference a type declared later without quoting it. This support requires Pydantic V2.
- The Pydantic mypy plugin explicitly supports only the latest mypy version, rather than promising every release from the prior six months. Keep mypy current when diagnosing plugin behavior.
- FastAPI 0.128.2 understands PEP 695 aliases used for endpoint parameters and response types; see [dependency-injection.md](dependency-injection.md) for other deferred-annotation fixes.
