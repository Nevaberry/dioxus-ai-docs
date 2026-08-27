# Operations and DDL

Use this reference when generating conditional schema changes, adding keys or
references with `ADD COLUMN`, managing SQL Server comments, or producing offline
SQL for moves to `base`.

## Conditional column and constraint DDL

### Render existence guards

The following operation flags render the corresponding clause on backends that
support it. (since 1.16.0)

```python
op.add_column(
    "account",
    sa.Column("nickname", sa.String()),
    if_not_exists=True,
)
op.drop_column("account", "legacy", if_exists=True)
op.drop_constraint(
    "uq_account_name",
    "account",
    type_="unique",
    if_exists=True,
)
```

- `Operations.add_column(..., if_not_exists=True)` renders `IF NOT EXISTS`.
- `Operations.drop_column(..., if_exists=True)` renders `IF EXISTS`.
- `Operations.drop_constraint(..., if_exists=True)` renders `IF EXISTS`.

Custom autogenerate `Rewriter` recipes can set the same flags on rendered
migration operations. Backend support still determines whether the resulting
clause is valid.

## Column comments on SQL Server

### Add, update, or delete a comment

`Operations.alter_column(comment=...)` emits Microsoft SQL Server DDL for
adding, updating, or deleting a column comment. It no longer fails with
`UnsupportedCompilationError` for that backend. (since 1.18.0)

```python
op.alter_column("account", "name", comment="Display name")
```

Use the same operation with the appropriate comment value when changing or
removing the comment; keep backend coverage in migration tests.

## Inline primary keys

### Require explicit opt-in

Pass `inline_primary_key=True` to `Operations.add_column()` to render
`PRIMARY KEY` inside `ADD COLUMN`. `Column(primary_key=True)` by itself does not
select inline rendering. (since 1.18.0)

```python
op.add_column(
    "account",
    sa.Column("id", sa.Integer, primary_key=True),
    inline_primary_key=True,
)
```

Explicit opt-in preserves PostgreSQL `SERIAL` behavior while allowing inline
primary-key syntax when supported by the target backend.

## Inline foreign-key references

### Render `REFERENCES` inside `ADD COLUMN`

Pass `inline_references=True` to `Operations.add_column()` to inline the
foreign-key `REFERENCES` clause instead of emitting a separate
`ADD CONSTRAINT`. (since 1.18.0)

```python
op.add_column(
    "child",
    sa.Column(
        "parent_id",
        sa.Integer,
        sa.ForeignKey("parent.id", ondelete="CASCADE"),
        nullable=True,
    ),
    inline_references=True,
)
```

Inline rendering is available on PostgreSQL, Oracle, MySQL 5.7 and newer, and
MariaDB 10.5 and newer. It includes foreign-key actions and attributes such as
`ON DELETE`, `ON UPDATE`, `DEFERRABLE`, `INITIALLY`, and `MATCH`.

## Offline moves to `base`

### Retain the version table

In `--sql` mode, `stamp base` and `downgrade base` do not emit
`DROP TABLE alembic_version`; this matches online behavior. The version table is
still created when it does not exist. (since 1.19.1)

Update SQL snapshot tests that expected a drop, and keep any explicit removal
of the version table separate from the Alembic move-to-base operation.
