---
name: alembic-knowledge-patch
description: Alembic
version: 1.18.0
license: MIT
metadata:
  author: Nevaberry
---


# Alembic Knowledge Patch

Use this skill when changing an Alembic project, reviewing generated migrations,
upgrading Alembic, extending its CLI or operation system, or diagnosing revision
graph and backend-specific DDL behavior.

Inspect the project's pinned Alembic, Python, and SQLAlchemy versions before
applying version-dependent advice. Prefer the project's code, tests, and observed
database behavior when they disagree with general guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Compatibility and configuration](references/compatibility-and-configuration.md) | Runtime and build requirements, the yanked wheel, TOML configuration, path parsing, and path APIs |
| [Autogenerate and rendering](references/autogenerate-and-rendering.md) | Indexes, constraints, operation rendering, comparators, filtering, and plugins |
| [Operations and DDL](references/operations-and-ddl.md) | Conditional DDL, comments, inline keys and references, and offline version-table behavior |
| [Revisions, CLI, and extensions](references/revisions-cli-and-extensions.md) | Revision paths and identifiers, head checks, merge splicing, command registration, and operation implementations |

## Upgrade triage

### Avoid the yanked 1.15.0 wheel

Do not deploy Alembic 1.15.0. Its wheel omitted migration template files after
the packaging move to PEP 621. Use 1.15.1 or later in that series.

### Enforce the applicable runtime floor

- Alembic 1.15 requires Python 3.9+ and SQLAlchemy 1.4+.
- Alembic 1.17 requires Python 3.10+.
- Alembic 1.18 requires SQLAlchemy 1.4.23+.

Check source-build environments separately: the 1.16 series raised its
setuptools build requirement to 77.0.3.

### Update path parsing deliberately

For new or updated INI files, set:

```ini
[alembic]
path_separator = os
```

`path_separator` replaces `version_path_separator`, applies to both
`version_locations` and `prepend_sys_path`, and uses `os.pathsep` when set to
`os`. An omitted setting preserves legacy splitting with a deprecation warning.

### Remove colons from custom revision identifiers

Revision IDs cannot contain `:` because Alembic reserves it for revision-range
syntax. Replace identifiers such as `REV:1` with an unambiguous form such as
`REV_1` before creating or resolving revisions.

## Configuration quick reference

### Put source-generation settings in TOML

`pyproject.toml` can hold source paths, generation settings, local paths, and
post-write hooks. TOML lists are preferred for `version_locations` and
`prepend_sys_path`, and `%(here)s` resolves from the TOML file's parent.

Keep database connectivity and logging in `alembic.ini` or `env.py`. When
`env.py` supplies both, the `pyproject` initialization template can operate
without an INI file.

### Enable discovery for date-organized revision files

`file_template` can contain directory separators and Alembic creates the
directories. Always enable recursive version locations with a nested template:

```toml
[tool.alembic]
file_template = "%(year)d/%(month).2d/%(day).2d_%(rev)s_%(slug)s"
recursive_version_locations = true
```

The key rule is that nested files require recursive discovery.

### Pass path objects only through public APIs

Public command, configuration, and script path parameters accept `os.PathLike`
objects. Their public path-returning accessors still return strings. Do not rely
on private underscored APIs returning strings; the path refactor permits them to
return `pathlib.Path` values.

## Migration safety quick reference

### Fail deployment checks when any head is missing

Use the CLI:

```console
alembic current --check-heads
```

Or call `command.current(config, check_heads=True)`. A database missing any head
causes `DatabaseNotAtHead`; the CLI exits nonzero.

### Add backend-guarded DDL

On supporting backends, use:

```python
op.add_column("account", sa.Column("nickname", sa.String()), if_not_exists=True)
op.drop_column("account", "legacy", if_exists=True)
op.drop_constraint("uq_account_name", "account", type_="unique", if_exists=True)
```

The flags render `IF NOT EXISTS` or `IF EXISTS`, and custom autogenerate
rewriters can attach the same flags to generated operations.

### Opt in to inline keys and references

`Column(primary_key=True)` alone does not inline a primary key in `ADD COLUMN`.
Pass `inline_primary_key=True` to `Operations.add_column()` when the backend
supports that syntax and inline behavior is intended.

Pass `inline_references=True` to render a column's `REFERENCES` clause within
`ADD COLUMN` instead of emitting a separate constraint. See the DDL reference
for supported backends and included foreign-key actions.

### Preserve the offline version table at `base`

In `--sql` mode, `stamp base` and `downgrade base` retain `alembic_version`,
matching online behavior. Alembic still creates the version table if absent.
Do not expect these offline commands to emit `DROP TABLE alembic_version`.

## Autogenerate correctness quick reference

### Treat named CHECK comparison as name-only

Named `CHECK` additions and removals are detected by default through the
`alembic.autogenerate.checkconstraint_byname` plugin. Expression changes under
an unchanged name do not produce a diff. Disable that comparator by excluding
the plugin from `autogenerate_plugins` when name-based detection is unwanted.

### Select comparison plugins per environment

Third-party `Plugin` implementations can register operations, implementations,
and comparators. Select built-in and third-party comparison plugins with:

```python
context.configure(autogenerate_plugins=[...])
```

Existing extensions do not need plugin entry points, but new plugins can use
`Plugin.add_autogenerate_comparator()` for automatic loading.

### Preserve finalized database names

Rendered reflected constraint and index names use `Operations.f()` so active
naming conventions do not transform final names twice. Keep wrappers such as:

```python
op.drop_constraint(op.f("uq_account_name"), "account", type_="unique")
```

This is especially important for conventions using `%(constraint_name)s`.

### Account for filtered foreign-key placeholders

Foreign keys whose targets were excluded by `include_name` or omitted from the
reflected schemas no longer abort autogenerate. An `include_object` callback can
receive placeholder target tables carrying only the table name, schema, and
referenced columns. Do not assume those targets are fully reflected.

## Revision and extension quick reference

### Create a merge revision away from a head

Use `alembic merge --splice rev_a rev_b`, or pass `splice=True` to
`command.merge()`, when the merge revision must be based on non-head revisions.

### Ask for dependency-aware effective heads

Call:

```python
heads = script.get_heads(consider_depends_on=True)
```

This excludes nominal heads that another revision names through `depends_on`,
matching the effective heads recorded after all upgrades.

### Extend public surfaces explicitly

- Register application CLI commands with `CommandLine.register_command()`.
- Replace an existing operation implementation with
  `Operations.implementation_for(..., replace=True)`.
- When a rewriter represents a column rename, set
  `AlterColumnOp.modified_name`; Alembic does not infer the rename itself.

## Review workflow

1. Confirm the pinned Alembic, Python, SQLAlchemy, and backend versions.
2. Check the compatibility reference before changing packaging or configuration.
3. Review autogenerate output against naming conventions and filtered schemas.
4. Review backend-specific DDL flags and inline behavior before execution.
5. Validate the revision graph with head checks and dependency-aware lookup.
6. Test both online and `--sql` workflows when release tooling emits SQL.

Open the indexed reference matching the task for the complete edge cases and
version attributions; the quick reference intentionally focuses on the most
failure-prone upgrade and migration paths.
