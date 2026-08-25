# Operations and DDL

## Conditional schema changes

### Conditional columns and constraints (1.16.0)

On backends that support the syntax, operation flags render the corresponding
condition directly:

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

`Operations.add_column(..., if_not_exists=True)` emits `IF NOT EXISTS`.
`drop_column(..., if_exists=True)` and
`drop_constraint(..., if_exists=True)` emit `IF EXISTS`. Custom autogenerate
`Rewriter` recipes can put these flags into rendered operations as well. Test
the migration against each target dialect because support remains
backend-dependent.

## Inline keys and references

### Opt-in inline primary keys (1.18.0)

Pass `inline_primary_key=True` to render `PRIMARY KEY` inside `ADD COLUMN`:

```python
op.add_column(
    "account",
    sa.Column("id", sa.Integer, primary_key=True),
    inline_primary_key=True,
)
```

`Column(primary_key=True)` by itself does not opt in. Requiring a separate flag
preserves PostgreSQL `SERIAL` behavior while allowing inline primary-key syntax
when the target backend supports it.

### Inline foreign-key references (1.18.0)

Pass `inline_references=True` to render `REFERENCES` within `ADD COLUMN` instead
of issuing a separate `ADD CONSTRAINT`:

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

This form is supported on PostgreSQL, Oracle, MySQL 5.7+, and MariaDB 10.5+.
Inline rendering includes referential actions and attributes such as
`ON DELETE`, `ON UPDATE`, `DEFERRABLE`, `INITIALLY`, and `MATCH`.

## Backend-specific alteration

### SQL Server column comments (1.18.0)

On Microsoft SQL Server, `Operations.alter_column(comment=...)` emits DDL to
add, update, or delete a column comment rather than raising
`UnsupportedCompilationError`:

```python
op.alter_column("account", "name", comment="Display name")
```

Use `comment=None` when the intended alteration is removal, consistent with
the operation's comment semantics.

## Offline migration state

### Moving to `base` retains the version table (1.19.1)

In `--sql` mode, `stamp base` and `downgrade base` do not emit
`DROP TABLE alembic_version`. This matches online behavior. The version table
is still created when it does not exist, so offline scripts can establish
migration state without dropping the state table when moving back to `base`.
