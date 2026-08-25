# Python, ORM, and Typing

## Python runtime compatibility

### Python 3.14 and free-threaded builds

Python 3.14 automatically receives `greenlet` through SQLAlchemy's dependency
metadata. PEP 649 handling supports deferred relationship targets in
`MappedAsDataclass` and unresolved annotation names encountered during ORM
introspection.

Free-threaded Python 3.13t and 3.14t have initial runtime fixes. Do not infer
wheel availability from runtime support: free-threaded PyPI wheels remain a
SQLAlchemy 2.1 feature. This guidance is from 2.0.51.

### Python 3.15

SQLAlchemy 2.0.52 adds and tests Python 3.15 support, including the runtime
compatibility changes needed for that interpreter.

## Declarative annotations

### Union keys are exact

`registry.type_annotation_map` matches a union entry only to that exact union.
For example, a `float | Decimal` entry does not also map `Mapped[float]`.
PEP 604 union syntax and `typing.Union` resolve consistently, so duplicate
entries are not needed merely because the spelling differs.

### PEP 695 aliases and `NewType`

A PEP 695 alias can resolve from:

- an explicit map entry for the alias;
- an entry for its immediate target; or
- a generic alias whose target wraps
  `Annotated[..., mapped_column(...)]`.

Recursive alias-chain traversal and implicit `NewType` resolution remain
deprecated in the 2.0 line and are disallowed in 2.1. Add explicit annotation
map entries or flatten alias chains before upgrading.

## Dataclass integration

ORM attribute constructors that accept dataclass options also accept
`dataclass_metadata`. SQLAlchemy forwards the mapping to the generated
dataclass field's `metadata`:

```python
from sqlalchemy.orm import Mapped, mapped_column

name: Mapped[str] = mapped_column(
    dataclass_metadata={"ui": "label"},
)
```

Read the value from the generated dataclass field metadata.

## Composite loading

`defer()`, `undefer()`, and `load_only()` support mapped composite attributes:

```python
from sqlalchemy import select
from sqlalchemy.orm import load_only

stmt = select(Location).options(load_only(Location.point))
```

Pass the composite attribute, not a string name, so the loading plan addresses
the composite at the ORM level.

## Loader-option wildcard validation

A dotted string ending in `"*"`, such as
`Load(A).joinedload("bs.*")`, raises `ArgumentError` rather than silently
matching nothing. Loader options reject string attribute names, so express
paths with mapped attributes.

The bare wildcard remains valid:

```python
Load(A).lazyload("*")
```

This validation behavior is from 2.0.52.

## Explicit subqueries for `aliased()`

Passing a `select()` or `union()` directly to `aliased()` emits a deprecation
warning in 2.0 while retaining implicit subquery coercion. SQLAlchemy 2.1
raises instead. Construct the subquery explicitly:

```python
alias = aliased(User, select(User).subquery())
```

Apply the same explicit conversion to union constructs before passing them to
`aliased()`.
