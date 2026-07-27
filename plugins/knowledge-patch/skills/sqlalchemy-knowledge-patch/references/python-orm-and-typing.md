# Python, ORM, and Typing

The behaviors below are attributed to the `2.0.51` extraction batch.

## Python 3.14 dependency and annotation behavior

Python 3.14 environments now receive `greenlet` automatically when installing
SQLAlchemy. Installation logic should not retain a Python-3.14-specific
workaround that separately adds the ordinary `greenlet` dependency.

PEP 649 deferred-annotation handling covers two ORM cases:

- deferred relationship targets used by `MappedAsDataclass`; and
- unresolved annotation names encountered while the ORM introspects a mapped
  class.

Keep annotations as annotations rather than eagerly evaluating them in an
application workaround. When diagnosing a remaining failure, establish which
Python annotation semantics are active and inspect the exact class namespace.

SQLAlchemy also includes initial runtime corrections for free-threaded Python
3.13t and 3.14t. These fixes do not mean that the 2.0 release line publishes
free-threaded wheels on PyPI: those wheels are a 2.1-only feature. A deployment
on a free-threaded interpreter must account for the artifact it can actually
install or build.

## Exact union matching in `type_annotation_map`

A key in `registry.type_annotation_map` that is a union matches that complete
union, not each member:

```python
from decimal import Decimal
from sqlalchemy import Numeric
from sqlalchemy.orm import registry

mapper_registry = registry(
    type_annotation_map={
        float | Decimal: Numeric(),
    }
)
```

The entry above applies to an annotation of `float | Decimal`; it does not
cause `Mapped[float]` to use `Numeric`. Add a separate `float` entry if that is
the desired mapping.

PEP 604 spelling (`A | B`) and `typing.Union[A, B]` spelling resolve
consistently. Treat them as equivalent forms of the same union rather than
maintaining parallel mappings.

## PEP 695 aliases and deprecations

A PEP 695 type alias can resolve from an explicit annotation-map entry for the
alias or from an entry for its immediate target. Resolution also supports a
generic alias around an `Annotated` target containing
`mapped_column(...)`.

Keep the resolution path shallow and explicit. Recursive alias chains and
implicit `NewType` resolution are deprecated in SQLAlchemy 2.0 and disallowed
in 2.1. Migrate either by flattening the alias or by adding a direct
`type_annotation_map` entry for the public annotation used by the mapped
attribute.

When preparing for 2.1, search mapped annotations for:

- aliases whose target is another alias;
- a chain with more than one implicit target lookup; and
- `NewType` annotations that have no explicit annotation-map key.

## Dataclass field metadata

ORM attribute constructors that accept dataclass options accept
`dataclass_metadata`. The value is forwarded to the generated
`dataclasses.Field.metadata` mapping:

```python
from dataclasses import fields
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column

class Customer(MappedAsDataclass, Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(
        dataclass_metadata={"ui": "label"},
    )

metadata = fields(Customer)[1].metadata
```

This metadata belongs to the Python dataclass field. Do not substitute
`Column.info` when a dataclass-aware consumer reads `Field.metadata`, and do
not assume `dataclass_metadata` changes emitted DDL.

## Deferred and selective loading of composites

Composite attributes can be passed directly to `defer()`, `undefer()`, and
`load_only()`:

```python
from sqlalchemy import select
from sqlalchemy.orm import defer, load_only, undefer

only_point = select(Location).options(load_only(Location.point))
without_point = select(Location).options(defer(Location.point))
with_point = select(Location).options(undefer(Location.point))
```

Use the mapped composite attribute (`Location.point`) as the option target.
This lets a loading policy operate on the composite as one ORM attribute
instead of requiring callers to spell out its component columns.
