---
name: alembic-knowledge-patch
description: Alembic
version: "1.18.0"
license: MIT
metadata:
  author: Nevaberry
---


# Alembic Knowledge Patch

Use this skill when upgrading Alembic, reviewing generated migrations, writing
operation extensions, or diagnosing configuration and revision-graph behavior.
Check the installed Alembic, Python, and SQLAlchemy versions before applying
version-dependent guidance. Treat project configuration, migration history,
and backend behavior as authoritative.

## Reference index

| Reference | Topics |
| --- | --- |
| [Compatibility and configuration](references/compatibility-and-configuration.md) | Runtime and build requirements, packaging, TOML and INI configuration, path APIs |
| [Autogenerate and rendering](references/autogenerate-and-rendering.md) | Indexes, constraints, defaults, dialect arguments, rename rewriters, custom writers |
| [Operations and DDL](references/operations-and-ddl.md) | Conditional DDL, inline keys and references, SQL Server comments, offline base moves |
| [Revisions, CLI, and extensions](references/revisions-cli-and-extensions.md) | Revision identifiers and paths, head checks, merge splicing, commands, plugins, operation implementations |

## Upgrade blockers first

### Match the runtime floor

- Alembic 1.15 requires Python 3.9+ and SQLAlchemy 1.4+.
- Alembic 1.17 requires Python 3.10+.
- Alembic 1.18 requires SQLAlchemy 1.4.23+.

Do not select an Alembic version independently of its application runtime and
SQLAlchemy dependency. For the complete packaging notes, read
[Compatibility and configuration](references/compatibility-and-configuration.md).

### Avoid the yanked 1.15.0 wheel

The 1.15.0 wheel omitted migration templates after the packaging move to PEP
621. Use 1.15.1 or later in that series so `alembic init` and template-driven
workflows have the required files.

### Remove colons from custom revision identifiers

Custom revision IDs cannot contain `:` because it denotes revision ranges.
Replace values such as `REV:1` with an unambiguous form such as `REV_1` before
creating or resolving revisions.

### Adopt cross-platform path separation

Use the shared `path_separator` option for both `version_locations` and
`prepend_sys_path`:

```ini
[alembic]
path_separator = os
```

This selects `os.pathsep`. The older `version_path_separator` is superseded;
omitting the new option retains legacy splitting only with a deprecation
warning.

## Autogenerate safety checks

### Preserve finalized names

Reflected constraint and index names are rendered through `Operations.f()`.
Keep that wrapper when reviewing or editing generated migrations, especially
when a naming convention uses `%(constraint_name)s`:

```python
op.drop_constraint(op.f("uq_account_name"), "account", type_="unique")
```

Removing `op.f()` can cause a convention to transform a final database name a
second time.

### Understand named `CHECK` detection

Named `CHECK` additions and removals are detected by default. The comparison
is name-only, so changing an expression without renaming the constraint does
not create a diff. The behavior comes from the
`alembic.autogenerate.checkconstraint_byname` plugin and can be disabled via
`autogenerate_plugins`.

### Treat filtered foreign-key targets as placeholders

If `include_name` or reflected schema selection excludes a referenced table,
autogenerate no longer fails merely because of the missing target. An
`include_object` callback can instead receive a placeholder target containing
only its name, schema, and referenced columns. Do not assume that object is a
fully reflected table.

### Review dialect-sensitive comparisons

- PostgreSQL sequence defaults with server-added `::regclass` casts should not
  recur as changes on non-primary-key columns.
- MySQL `ENUM` comparison detects value membership changes but ignores value
  order.
- Sequence-valued dialect arguments such as `postgresql_include` render
  `Column` objects as string column names.

See [Autogenerate and rendering](references/autogenerate-and-rendering.md) for
all rendering corrections, including labeled indexes, boolean deferrability,
rewriter-driven renames, and configured operation prefixes.

## Safer operation authoring

### Use conditional DDL explicitly

On supporting backends, request conditional syntax directly:

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

Custom `Rewriter` recipes can set the same flags for generated migrations.

### Opt in to inline primary keys

`Column(primary_key=True)` alone does not make `ADD COLUMN` emit `PRIMARY KEY`.
Pass `inline_primary_key=True` when inline syntax is intended and supported:

```python
op.add_column(
    "account",
    sa.Column("id", sa.Integer, primary_key=True),
    inline_primary_key=True,
)
```

The explicit opt-in preserves PostgreSQL `SERIAL` behavior by default.

### Opt in to inline foreign-key references

Pass `inline_references=True` to render `REFERENCES` inside `ADD COLUMN` rather
than as a separate `ADD CONSTRAINT` on PostgreSQL, Oracle, MySQL 5.7+, and
MariaDB 10.5+:

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

Inline rendering also carries `ON DELETE`, `ON UPDATE`, `DEFERRABLE`,
`INITIALLY`, and `MATCH`. Consult
[Operations and DDL](references/operations-and-ddl.md) for backend details and
offline version-table behavior.

## Revision and extension workflows

### Verify deployment state against every head

Use the CLI when a deployment gate must fail unless all heads are applied:

```console
alembic current --check-heads
```

Programmatically, call `command.current(..., check_heads=True)`. A mismatch
raises `DatabaseNotAtHead`; the CLI exits nonzero.

### Create nested date-based revision paths correctly

`file_template` can contain directory separators and creates those directories:

```toml
[tool.alembic]
file_template = "%(year)d/%(month).2d/%(day).2d_%(rev)s_%(slug)s"
recursive_version_locations = true
```

Always enable recursive version locations for this layout so later commands
can discover nested revisions.

### Distinguish nominal and effective heads

Call `ScriptDirectory.get_heads(consider_depends_on=True)` when dependencies
must affect head calculation. It excludes nominal heads used as another
revision's `depends_on`, matching effective heads stored after upgrades.

### Choose the supported extension point

- Register application CLI commands with `CommandLine.register_command()`.
- Replace an existing operation implementation with
  `Operations.implementation_for(..., replace=True)`.
- Use the `Plugin` interface for automatically loaded third-party operations,
  implementations, and autogenerate comparators.
- Select comparison plugins per environment with
  `EnvironmentContext.configure(autogenerate_plugins=...)`.

Existing add-ons can continue without plugin entry points. See
[Revisions, CLI, and extensions](references/revisions-cli-and-extensions.md)
for merge splicing and full extension details.

## Review checklist

1. Confirm the runtime and dependency floors before changing the Alembic pin.
2. Check path parsing and recursive revision discovery after configuration
   changes.
3. Run autogenerate and review names, dialect arguments, defaults, constraints,
   and filtered objects rather than accepting output blindly.
4. Test conditional and inline DDL on every supported database backend.
5. Exercise online and `--sql` paths separately when migration state handling
   matters.
6. Verify all effective heads in deployment checks, including `depends_on`
   relationships.
7. Test custom commands, writers, rewriters, and plugins through their public
   extension APIs.
