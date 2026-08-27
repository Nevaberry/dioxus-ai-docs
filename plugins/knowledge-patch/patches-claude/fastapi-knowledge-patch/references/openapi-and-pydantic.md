# OpenAPI and Pydantic

## Dynamic models and completion hooks

`create_model()` accepts `__config__` together with `__base__`
(`pydantic-2.11.2`). Pass both directly; do not disguise `model_config` as a
field to work around the former restriction.

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

Override `__pydantic_on_complete__()` when class work requires fully
initialized fields (`pydantic-2.12.0`). It normally runs during class creation,
but may run after `model_rebuild()` if unresolved forward annotations delayed
completion.

```python
from pydantic import BaseModel

registry = []

class Registered(BaseModel):
    @classmethod
    def __pydantic_on_complete__(cls) -> None:
        registry.append(cls)
```

From Pydantic 2.12.3, `FieldInfo.asdict()` returns separate `annotation`,
`metadata`, and `attributes` entries. Use this structured form when rebuilding
dynamic fields; mutating a reused `FieldInfo` remains unsupported.

## Validation and annotation semantics

Parameterized mapping annotations validate both key and value arguments, not
only the outer mapping shape (`pydantic-2.11.2`):

```python
from collections.abc import Mapping
from pydantic import BaseModel

class Payload(BaseModel):
    values: Mapping[str, int]

Payload(values={"count": []})  # ValidationError
```

Pydantic 2.12 supports Python 3.14's PEP 649/749 lazy annotations, allowing a
later definition to be referenced without quoting it (`pydantic-2.12-guide`):

```python
from pydantic import BaseModel

class Model(BaseModel):
    value: Later

type Later = int
```

Python 3.14 requires Pydantic V2; the bundled V1 compatibility implementation
does not support that runtime.

Use `ValidateAs(from_type, factory)` to validate a custom class through an
intermediate Pydantic-supported type and construct the desired class from the
validated value:

```python
from typing import Annotated
from pydantic import TypeAdapter, ValidateAs

class Label:
    def __init__(self, value: str):
        self.value = value

LabelValue = Annotated[Label, ValidateAs(str, Label)]
label = TypeAdapter(LabelValue).validate_python("ready")
```

`@validate_call` honors a parameter field's `validation_alias`, including an
alias supplied as a keyword:

```python
from typing import Annotated
from pydantic import Field, validate_call

@validate_call
def double(value: Annotated[int, Field(validation_alias="number")]) -> int:
    return value * 2

assert double(number="3") == 6
```

Pass `extra=` to `model_validate()` to override a model's configured
extra-field policy for one call:

```python
from pydantic import BaseModel, ConfigDict

class Model(BaseModel):
    x: int
    model_config = ConfigDict(extra="allow")

Model.model_validate({"x": 1, "y": 2}, extra="forbid")  # ValidationError
```

Define `@model_validator(mode="after")` as an instance method. A class method
now produces a deprecation warning:

```python
from pydantic import BaseModel, model_validator

class Model(BaseModel):
    @model_validator(mode="after")
    def validate_model(self):
        return self
```

Field-specific metadata such as `alias` and `exclude` now warns when placed
where it would be ignored, including on a type alias or only on an optional
type's inner member. Place it on the complete field annotation:

```python
from typing import Annotated
from pydantic import BaseModel, Field

class Model(BaseModel):
    value: Annotated[int | None, Field(exclude=True)]
```

Normal `isinstance()` and `issubclass()` behavior is restored for Pydantic
models. Registering a virtual subclass through `ABCMeta.register()` now warns.

## Represent missing and excluded values

The experimental `MISSING` singleton distinguishes an omitted field from
explicit `None`. A field whose value is `MISSING` is omitted during
serialization, and the sentinel is excluded from JSON Schema.

```python
from pydantic import BaseModel
from pydantic.experimental.missing_sentinel import MISSING

class Configuration(BaseModel):
    timeout: int | None | MISSING = MISSING

assert Configuration().model_dump() == {}
```

`Field(exclude_if=...)` conditionally omits a value during serialization:

```python
from pydantic import BaseModel, Field

class Transaction(BaseModel):
    value: int = Field(ge=0, exclude_if=lambda value: value == 0)
```

Pass `exclude_computed_fields=True` to omit every computed field and retain
only stored data (`pydantic-2.12.0`):

```python
from pydantic import BaseModel, computed_field

class Value(BaseModel):
    number: int

    @computed_field
    @property
    def doubled(self) -> int:
        return self.number * 2

assert Value(number=2).model_dump(exclude_computed_fields=True) == {"number": 2}
```

## Serialization controls

JSON serialization methods accept `ensure_ascii=True`; the default remains
`False`:

```python
from pydantic import TypeAdapter

assert TypeAdapter(str).dump_json("🔥", ensure_ascii=True) == b'"\\ud83d\\udd25"'
```

The global `serialize_as_any=True` setting now matches the `SerializeAsAny`
annotation. Both can expose subclass-only fields and surface the same
serialization failures. Prefer `SerializeAsAny[T]` on selected fields when a
global duck-typed policy is too broad.

## URLs and temporal values

Set `url_preserve_empty_path=True` in configuration, or
`UrlConstraints(preserve_empty_path=True)` on a field, to keep an empty URL
path from becoming `/`:

```python
from pydantic import AnyUrl, BaseModel, ConfigDict

class Endpoint(BaseModel):
    url: AnyUrl
    model_config = ConfigDict(url_preserve_empty_path=True)
```

`val_temporal_unit` selects seconds, milliseconds, or the prior inference
behavior for numeric temporal inputs. `ser_json_temporal` provides the general
serialization setting for temporal types:

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class Event(BaseModel):
    at: datetime
    model_config = ConfigDict(val_temporal_unit="milliseconds")
```

## Typed dictionaries and union schemas

Pydantic 2.12 supports PEP 728 `TypedDict` parameters `closed` and
`extra_items` through `typing_extensions`. The same constraints determine
JSON Schema `additionalProperties`:

```python
from typing_extensions import TypedDict
from pydantic import TypeAdapter

class Payload(TypedDict, extra_items=int):
    name: str

TypeAdapter(Payload).validate_python({"name": "item", "count": 2})
```

Select `union_format="primitive_type_array"` to emit eligible primitive unions
as a JSON Schema `type` array. Unions with constraints or non-primitive
members fall back to `anyOf`:

```python
from pydantic import TypeAdapter

schema = TypeAdapter(int | str).json_schema(
    union_format="primitive_type_array"
)
assert schema == {"type": ["integer", "string"]}
```

FastAPI accepts array-valued OpenAPI schema `type` (`2025-09`), so custom
OpenAPI 3.1 fragments may also use values such as `["string", "null"]`.

## Schema-generation corrections

Pydantic no longer coerces `Decimal` constraint metadata while constructing
validation schemas (`pydantic-2.11.2`). Supply constraints in their intended
form. Pydantic 2.12 also emits regex patterns for `Decimal`, preserves custom
titles in function schemas, and maps manually created typed-dictionary
`extra_behavior` to `additionalProperties`. Update snapshots and downstream
schema tooling.

When applying discriminators, Pydantic now supplies definitions already
available to schema generation, so branches represented by existing
definitions resolve correctly. FastAPI 0.118.2 likewise classifies tagged
discriminated unions as request bodies.

FastAPI schema corrections include:

- `FastAPI(external_docs=...)` emits top-level OpenAPI `externalDocs`
  (`2025-09`).
- FastAPI 0.120.4 renders top-level application security schemes correctly.
- FastAPI 0.121.2 preserves schema attributes literally named `$ref`; 0.123.1
  adds the corresponding Pydantic V2 remapping fix.
- FastAPI 0.123.10 supports computed fields when
  `separate_input_output_schemas=False`.
- FastAPI 0.128.1 adds `input` and `ctx` to the OpenAPI `ValidationError`
  schema and removes duplicate `anyOf` references from app-level union
  responses that specify both `content` and `model` (`2025-12`).
- FastAPI 0.128.2 accepts `Json[list[str]]` as a validated type and PEP 695
  aliases in endpoint annotations.
- FastAPI 0.129.1 represents `bytes` with
  `contentMediaType: application/octet-stream`, not `format: binary`.

## Private state, static typing, and diagnostics

Pydantic ensures `__pydantic_private__` exists before storing a private
attribute, including construction paths where private backing state was not
initialized (`pydantic-2.11.2`).

The Pydantic mypy plugin preserves a model used as a variable annotation rather
than expanding it into the model's root type. Starting with Pydantic 2.12, the
plugin explicitly supports only the latest released mypy.

Importing from `pydantic.experimental` no longer emits
`PydanticExperimentalWarning`; remove warning filters added only for those
imports. Keep `pydantic` and `pydantic-core` at their exact compatible versions,
because Pydantic 2.12 reports a mismatch as a startup error.
