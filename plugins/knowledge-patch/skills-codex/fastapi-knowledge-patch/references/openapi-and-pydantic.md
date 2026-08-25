# OpenAPI and Pydantic

## Pydantic model construction and validation

### Dynamic models with a base and configuration

Pydantic 2.11.2 (`pydantic-2.11.2`) lets `create_model()` receive `__base__`
and `__config__` in the same call. Pass both directly; do not fake
`model_config` as a field.

```python
from pydantic import BaseModel, ConfigDict, create_model

class Base(BaseModel):
    id: int

Configured = create_model(
    "Configured",
    __base__=Base,
    __config__=ConfigDict(extra="forbid"),
    name=(str, ...),
)
```

Pydantic 2.11.2 also stops coercing decimal constraint metadata during schema
construction. Supply constraints in their intended form.

### Mapping arguments and private attributes

Parameterized mapping annotations validate key and value arguments, not only
the outer mapping shape (`pydantic-2.11.2`). Pydantic also initializes
`__pydantic_private__` before private-attribute assignment in construction
paths where the backing state did not already exist.

### Per-call extra handling

Pydantic 2.12 lets `model_validate()` override the configured extra-field
policy for one call (`pydantic-2.12-guide`):

```python
Model.model_validate({"x": 1, "y": 2}, extra="forbid")
```

### `ValidateAs` for custom classes

`ValidateAs(from_type, factory)` validates an `Annotated` custom class through
a natively supported intermediate type, then calls the factory
(`pydantic-2.12.0`).

```python
from typing import Annotated
from pydantic import TypeAdapter, ValidateAs

LabelValue = Annotated[Label, ValidateAs(str, Label)]
label = TypeAdapter(LabelValue).validate_python("ready")
```

### Model completion hook

Override `__pydantic_on_complete__()` for work requiring fully initialized
fields (`pydantic-2.12.0`). It normally runs during class creation, but can run
after `model_rebuild()` when unresolved forward annotations delay completion.

## Pydantic annotations and typing

Pydantic 2.12 supports Python 3.14 PEP 649/749 lazy annotations, including a
reference to a later type without quoting it (`pydantic-2.12-guide`). Python
3.14 requires Pydantic V2 (`pydantic-2.12.0`).

FastAPI 0.124.2 and 0.128.1 resolve string annotations, `TYPE_CHECKING`
imports, and Python 3.14 deferred annotations more reliably (`2025-12`).
FastAPI 0.128.2 also accepts PEP 695 `TypeAliasType` values made by the Python
3.12 `type` statement in endpoint annotations.

Pydantic's mypy plugin preserves a model used as a variable annotation rather
than expanding it to the model's root type (`pydantic-2.11.2`). Starting with
Pydantic 2.12, the plugin explicitly supports only the latest released mypy
(`pydantic-2.12-guide`).

Fields on `@validate_call` parameters honor `validation_alias`, including an
alias supplied as a keyword (`pydantic-2.12.0`).

Field metadata such as `alias` or `exclude` warns when placed where it would be
ignored, including on a type alias or only the inner member of an optional type
(`pydantic-2.12-guide`). Put metadata on the field annotation as a whole.

## Serialization controls

### Omission and conditional exclusion

Pydantic 2.12's experimental `MISSING` sentinel distinguishes omission from
`None`; a `MISSING` value is excluded from serialization and JSON Schema
(`pydantic-2.12-guide`). `Field(exclude_if=predicate)` conditionally excludes a
field, while `exclude_computed_fields=True` omits every computed field
(`pydantic-2.12.0`).

### JSON and temporal configuration

JSON serialization methods accept `ensure_ascii=True`; the default remains
`False`. `val_temporal_unit` explicitly selects seconds, milliseconds, or
inference for numeric temporal inputs, and `ser_json_temporal` is the general
serialization setting for temporal types (`pydantic-2.12-guide`).

Set `url_preserve_empty_path=True` in model configuration, or
`UrlConstraints(preserve_empty_path=True)` on a field, to prevent an empty URL
path from normalizing to `/` (`pydantic-2.12-guide`).

### Duck-typed serialization

Global `serialize_as_any=True` now behaves like `SerializeAsAny`, including
exposing subclass-only fields and surfacing the same errors. Prefer
`SerializeAsAny[T]` on selected fields when a global policy is too broad
(`pydantic-2.12-guide`).

## Validators and dynamic fields

Define `@model_validator(mode="after")` as an instance method; using a class
method is deprecated in Pydantic 2.12 (`pydantic-2.12-guide`).

From Pydantic 2.12.3, `FieldInfo.asdict()` returns separate `annotation`,
`metadata`, and `attributes` entries. Use that structured export to rebuild
dynamic fields; mutating a reused `FieldInfo` remains unsupported
(`pydantic-2.12.0`).

Importing `pydantic.experimental` no longer emits
`PydanticExperimentalWarning`, so filters used only for that import can be
removed. Normal `isinstance()` and `issubclass()` behavior is restored for
models, but `ABCMeta.register()` virtual-subclass registration warns
(`pydantic-2.12-guide`).

## Typed dictionaries and JSON Schema

Pydantic 2.12 supports PEP 728 `closed` and `extra_items` on
`typing_extensions.TypedDict`: `closed` can prohibit unknown keys, while
`extra_items` types their values. These constraints drive generated
`additionalProperties` (`pydantic-2.12-guide`).

Schema generation accepts `union_format="primitive_type_array"` for eligible
primitive unions and falls back to `anyOf` for constrained or non-primitive
members (`pydantic-2.12.0`). Pydantic 2.12 also emits decimal regex patterns,
respects custom function-schema titles, and maps manually created typed-dict
`extra_behavior` to `additionalProperties` (`pydantic-2.12-guide`). Update
schema snapshots and consumers.

Discriminated-union schema generation can resolve branches that already exist
in the definitions map (`pydantic-2.11.2`). FastAPI 0.118.2 recognizes tagged
discriminated unions as request bodies (`2025-09`).

## FastAPI OpenAPI behavior

FastAPI accepts array-valued OpenAPI `type`, enabling custom OpenAPI 3.1
fragments such as `{"type": ["string", "null"]}` (`2025-09`). It also accepts
`external_docs` on `FastAPI` and emits top-level `externalDocs`.

Pydantic V2 model docstrings honor a form feed: text after `\f` is omitted from
the public schema description (`2025-06`).

FastAPI 0.121.2 preserves literal JSON Schema attributes named `$ref`, with a
related Pydantic V2 remapping fix in 0.123.1. FastAPI 0.123.10 supports computed
fields when `separate_input_output_schemas=False` (`2025-11`).

FastAPI 0.128.1 adds `input` and `ctx` to the OpenAPI `ValidationError` schema
and removes duplicate `anyOf` references from app-level union responses that
specify both `content` and `model`. FastAPI 0.128.2 validates
`Json[list[str]]` correctly (`2025-12`).

Top-level application security schemes render correctly from FastAPI 0.120.4
(`2025-10`).
