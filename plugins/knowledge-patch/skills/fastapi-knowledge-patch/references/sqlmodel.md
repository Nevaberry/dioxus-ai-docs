# SQLModel

Use this reference when a FastAPI project upgrades SQLModel or changes typed fields, DML execution, relationships, or indexes (`sqlmodel-release-history`).

## Runtime and Pydantic compatibility

- SQLModel 0.0.27 adds Python 3.14 support.
- SQLModel 0.0.30 drops Python 3.8.
- SQLModel 0.0.35 drops Python 3.9, so 0.0.35 and newer require Python 3.10 or later.
- SQLModel 0.0.31 removes Pydantic V1 support. Migrate all Pydantic V1 imports and behavior before adopting that line.
- No further `sqlmodel-slim` releases are published after SQLModel 0.0.36. Depend on `sqlmodel` directly.

## Pydantic V2 field forms

Choose a SQLModel version containing the fix for the field syntax in use:

- SQLModel 0.0.22 fixes nested `Optional[Annotated[T, ...]]`.
- SQLModel 0.0.29 fixes `Field(alias=...)` with Pydantic V2.
- SQLModel 0.0.32 fixes `Annotated` fields with Pydantic 2.12 and newer.

Projects below those releases can reject or mishandle otherwise valid declarations:

```python
from typing import Annotated
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Annotated[int, Field(primary_key=True)]
    display_name: str = Field(alias="displayName")
```

## Typed DML execution

SQLModel 0.0.25 adds `Session.exec()` overloads for `insert`, `update`, and `delete`. Static type checkers can understand data-changing statements instead of treating `exec()` as select-only:

```python
from sqlalchemy import update

statement = (
    update(Hero)
    .where(Hero.id == hero_id)
    .values(name="Deadpond")
)
session.exec(statement)
session.commit()
```

SQLModel 0.0.38 also removes the explicit `Any` return annotation from `SQLModel.__new__` and corrects the return annotation of `tuple_`. Upgrade when model construction or tuple expressions lose useful type information.

## Relationship deletion controls

SQLModel 0.0.21 adds:

- `cascade_delete` and `passive_deletes` on relationships.
- `ondelete` on foreign-key fields.

Use them to declare ORM cascades and database-level foreign-key actions directly:

```python
from sqlmodel import Field, Relationship, SQLModel

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(
        back_populates="team",
        cascade_delete=True,
    )

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team_id: int | None = Field(
        default=None,
        foreign_key="team.id",
        ondelete="CASCADE",
    )
    team: Team | None = Relationship(back_populates="heroes")
```

Coordinate ORM cascades with database constraints; the options control different layers.

## Indexes are opt-in

Since SQLModel 0.0.6, ordinary columns are not indexed automatically. Mark every required index explicitly:

```python
from sqlmodel import Field, SQLModel

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
```

Databases originally created by SQLModel 0.0.5 or older keep their automatically created indexes after upgrading the package. Inspect the actual database schema and explicitly drop unwanted legacy indexes; a library upgrade does not remove them.
