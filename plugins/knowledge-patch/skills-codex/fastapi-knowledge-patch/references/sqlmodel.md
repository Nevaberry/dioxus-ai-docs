# SQLModel

## Runtime and dependency compatibility

The `sqlmodel-release-history` guidance includes these floors and transitions:

- SQLModel 0.0.19 requires SQLAlchemy 2.0.14 or newer.
- SQLModel 0.0.27 adds Python 3.14 support.
- SQLModel 0.0.31 removes Pydantic V1 support.
- SQLModel 0.0.35 requires Python 3.10 or newer.

SQLModel 0.0.29 fixes field aliases with Pydantic V2. SQLModel 0.0.32 fixes
`Annotated` fields with Pydantic 2.12+. Upgrade to at least the corresponding
release before relying on either combination.

Starting with SQLModel 0.0.36, no further `sqlmodel-slim` releases are planned.
Install `sqlmodel` directly.

## Typed DML execution

SQLModel 0.0.25 adds `Session.exec()` overloads for SQLAlchemy `insert`,
`update`, and `delete` statements, so static type checkers accept DML calls.

```python
from sqlalchemy import update

statement = update(Hero).where(Hero.id == 1).values(name="Updated")
session.exec(statement)
session.commit()
```

## Relationship deletion controls

SQLModel 0.0.21 adds `cascade_delete`, `ondelete`, and `passive_deletes`. Use
`cascade_delete` for ORM-managed relationship deletion. For database-managed
deletion, put `ondelete` on the foreign key and `passive_deletes` on the
collection relationship.

```python
from sqlmodel import Field, Relationship, SQLModel

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(
        back_populates="team",
        passive_deletes="all",
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

## SQLAlchemy column configuration

Since SQLModel 0.0.11, `Field(sa_type=...)` accepts a SQLAlchemy type directly.
A complete `sa_column` is mutually exclusive with column-building options such
as `sa_column_args`, `primary_key`, and `nullable`; invalid combinations raise
an error rather than being ignored.

```python
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel

class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    payload: dict = Field(sa_type=JSON)
```
