# Pydantic Updates (2.9-2.12) for FastAPI

FastAPI 0.135.3 requires Pydantic >=2.9.0. These are the key Pydantic changes affecting FastAPI code.

## MISSING Sentinel (2.12) -- Experimental

Canonical solution for PATCH endpoints -- distinguish "field not provided" from "field set to None":

```python
from pydantic import BaseModel
from pydantic.experimental.missing_sentinel import MISSING

class UpdateItem(BaseModel):
    name: str | None | MISSING = MISSING
    price: float | None | MISSING = MISSING

# Field not provided at all:
item = UpdateItem()
item.model_dump()  # {} -- MISSING fields excluded from output

# Field explicitly set to None:
item = UpdateItem(name=None)
item.model_dump()  # {'name': None}
```

`MISSING` values are excluded from JSON Schema output. No longer requires filtering `PydanticExperimentalWarning` as of 2.12.

## exclude_if Field Option (2.12)

Conditional field exclusion during serialization:

```python
from pydantic import BaseModel, Field

class Transaction(BaseModel):
    id: int
    value: int = Field(ge=0, exclude_if=lambda v: v == 0)

Transaction(id=1, value=0).model_dump()  # {'id': 1}
Transaction(id=1, value=5).model_dump()  # {'id': 1, 'value': 5}
```

## exclude_computed_fields Option (2.12)

Exclude all `@computed_field` fields from serialization:

```python
model.model_dump(exclude_computed_fields=True)
```

## extra Per-Validation Override (2.12)

Override `extra` config at validation call time, not just class definition:

```python
class Model(BaseModel):
    x: int

# Allow extra fields for this one call:
Model.model_validate({'x': 1, 'y': 'extra'}, extra='ignore')

# Forbid extra fields even if class allows them:
Model.model_validate({'x': 1, 'y': 'extra'}, extra='forbid')
```

## Temporal Configuration (2.12)

### val_temporal_unit -- Force Timestamp Interpretation

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class Model(BaseModel):
    d: datetime
    model_config = ConfigDict(val_temporal_unit='milliseconds')

# Previously Pydantic guessed seconds vs milliseconds
# Now you can force explicit interpretation
Model(d=1704067200000)  # interpreted as milliseconds
```

### ser_json_temporal -- Control JSON Serialization

Controls how `timedelta` and datetime values are serialized to JSON.

## url_preserve_empty_path (2.12)

Fixes Pydantic adding trailing slash to URLs with empty paths:

```python
from pydantic import AnyUrl, BaseModel, ConfigDict

class Model(BaseModel):
    u: AnyUrl
    model_config = ConfigDict(url_preserve_empty_path=True)

Model(u='https://example.com').u  # 'https://example.com' (not 'https://example.com/')
```

Will likely become the default in Pydantic v3.

## @model_validator(mode='after') -- Instance Method Required (2.12)

Using `@classmethod` with `@model_validator(mode='after')` is now deprecated:

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

## Field Metadata Warnings (2.12)

Using field-specific metadata in contexts where it has no effect now warns:

```python
# WRONG -- alias on type alias has no effect:
type AliasedInt = Annotated[int, Field(alias='b')]

# WRONG -- exclude must be outermost Annotated layer:
c: Optional[Annotated[int, Field(exclude=True)]]
# CORRECT:
c: Annotated[Optional[int], Field(exclude=True)]
```
