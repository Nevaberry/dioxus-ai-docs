# SQLModel

## Runtime and dependency requirements

- SQLModel 0.0.27 adds Python 3.14 support.
- SQLModel 0.0.35 requires Python 3.10 or newer.
- SQLModel 0.0.19 raises the SQLAlchemy floor to 2.0.14.
- SQLModel 0.0.31 removes Pydantic V1 support.

For Pydantic V2 combinations, SQLModel 0.0.29 fixes field aliases and SQLModel
0.0.32 fixes `Annotated` fields with Pydantic 2.12 and newer. Upgrade to at
least the corresponding release before relying on either feature.

Starting with SQLModel 0.0.36, no more `sqlmodel-slim` releases are planned.
Install `sqlmodel` directly.

## Execute DML with typed `Session.exec()`

SQLModel 0.0.25 adds overloads for SQLAlchemy `insert`, `update`, and `delete`
statements passed to `Session.exec()`, so static type checkers accept DML calls:

```python
from sqlalchemy import update

statement = update(Hero).where(Hero.id == 1).values(name="Updated")
session.exec(statement)
session.commit()
```

## Choose ORM-managed or database-managed deletion

SQLModel 0.0.21 adds `cascade_delete`, `ondelete`, and `passive_deletes`.

- Use `cascade_delete` on a relationship for ORM-managed deletion.
- For database-managed deletion, set `ondelete` on the foreign key and
  `passive_deletes` on the collection relationship.

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

Ensure the database actually enforces foreign-key actions before choosing the
database-managed form.

## Supply SQLAlchemy column types

Since SQLModel 0.0.11, `Field(sa_type=...)` accepts a SQLAlchemy type directly:

```python
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel

class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    payload: dict = Field(sa_type=JSON)
```

A complete `sa_column` is mutually exclusive with options used to build a
column, including `sa_column_args`, `primary_key`, and `nullable`. Invalid
combinations raise an error rather than being silently ignored.
