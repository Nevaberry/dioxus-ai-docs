# Python, ORM, and Typing

## Python 3.14 and free-threaded runtimes

As of 2.0.51, Python 3.14 installs `greenlet` automatically through
SQLAlchemy's dependency metadata. PEP 649 handling covers deferred relationship
targets in `MappedAsDataclass` and unresolved annotation names encountered
during ORM introspection.

Free-threaded Python 3.13t and 3.14t receive initial runtime fixes in this line,
but free-threaded PyPI wheels are a 2.1-only feature. Validate the artifact that
actually exists for the deployment environment instead of assuming a 2.0 wheel
is published.

## Python 3.15

SQLAlchemy 2.0.52 adds and tests Python 3.15 support, including the
compatibility changes required to run on that interpreter.

## Exact union keys in annotation maps

In 2.0.51, `registry.type_annotation_map` treats a union as an exact key. A map
entry for `float | Decimal` does not also apply to `Mapped[float]`. PEP 604 and
`typing.Union` forms resolve consistently, so do not duplicate a union entry
only because its spelling differs.

A PEP 695 alias may resolve from:

- an explicit map entry for the alias;
- an entry for its immediate target; or
- a generic alias whose target wraps `Annotated[..., mapped_column(...)]`.

Do not depend on recursive alias-chain traversal or implicit `NewType`
resolution. Those behaviors remain deprecated in 2.0 and are disallowed in
2.1. Add an explicit map entry or flatten the alias chain before upgrading.

## Dataclass field metadata

ORM attribute constructors that accept dataclass options accept
`dataclass_metadata` as of 2.0.51. The mapping is forwarded to the generated
dataclass field's `metadata`:

```python
from sqlalchemy.orm import Mapped, mapped_column

name: Mapped[str] = mapped_column(
    dataclass_metadata={"ui": "label"},
)
```

Inspect the result with `dataclasses.fields()`. Dataclass field metadata is
separate from `Column.info`, which belongs to the SQLAlchemy schema object.

## Deferred composite attributes

`defer()`, `undefer()`, and `load_only()` accept composite attributes in
2.0.51. Pass the mapped attribute rather than a string:

```python
from sqlalchemy import select
from sqlalchemy.orm import load_only

stmt = select(Location).options(load_only(Location.point))
```

This lets the loading plan address a composite at the ORM attribute level.

## Loader-option wildcard validation

In 2.0.52, a dotted string ending in `"*"`, such as
`Load(A).joinedload("bs.*")`, raises `ArgumentError`. It no longer silently
matches nothing because loader options reject string attribute names. Use
mapped attributes to spell the path.

The bare wildcard remains valid as a special token:

```python
Load(A).lazyload("*")
```

## Explicit subqueries for `aliased()`

Passing a `select()` or `union()` directly to `aliased()` emits a deprecation
warning in 2.0.52 while retaining implicit subquery coercion. SQLAlchemy 2.1
raises instead. Build the subquery explicitly:

```python
user_alias = aliased(User, select(User).subquery())
```
