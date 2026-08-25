# Revisions, CLI, and extensions

Use this reference when organizing revision files, validating graph state,
creating merge revisions, or extending Alembic's public command and operation
surfaces.

## Revision identifiers and file layout

### Do not use colons in custom revision IDs

Custom revision identifiers cannot contain `:` because Alembic reserves the
character for revision-range syntax. Replace an ID such as `REV:1` with a form
such as `REV_1`. (since 1.17.0)

### Organize generated revisions into dated directories

`file_template` accepts directory separators and creates the required
directories automatically. Enable recursive version locations whenever a
template nests revision files, or later commands will not discover them.
(since 1.18.0)

```toml
[tool.alembic]
file_template = "%(year)d/%(month).2d/%(day).2d_%(rev)s_%(slug)s"
recursive_version_locations = true
```

Treat the template and recursive-discovery flag as one configuration change.
Creating nested files without recursive lookup can make valid revisions appear
missing to later commands.

## Head validation and lookup

### Verify that every head is applied

`command.current()` accepts `check_heads=True`, exposed as `--check-heads` by
`alembic current`. If any head revision is not applied, the API raises
`DatabaseNotAtHead` and the CLI exits nonzero. (since 1.17.0)

```console
alembic current --check-heads
```

This is a direct deployment or readiness check; it is stricter than merely
printing the current revision.

### Resolve effective heads through dependencies

`ScriptDirectory.get_heads(consider_depends_on=True)` removes nominal heads
that are dependencies of another revision through `depends_on`. Its result
matches the effective heads stored in `alembic_version` after all upgrades.
(since 1.18.0)

```python
heads = script.get_heads(consider_depends_on=True)
```

Use the default lookup when the nominal script heads are the desired view, and
the dependency-aware form when comparing with fully upgraded database state.

## Merge revision placement

### Splice a merge revision from non-head revisions

The merge command accepts `--splice`, and `command.merge()` accepts the matching
`splice` parameter. This permits a merge revision to be created from revisions
that are not currently heads. (since 1.18.0)

```console
alembic merge --splice rev_a rev_b
```

Use splicing deliberately: it changes where the merge revision joins the graph
rather than requiring all merge points to be current heads.

## Public CLI extension

### Register custom commands

Use `CommandLine.register_command()` to register an application command with
Alembic's command-line tool. The registration mechanism is public; extensions
no longer need to depend on its former internal implementation. (since 1.16.0)

```python
command_line.register_command(my_command)
```

Keep the command callable and its arguments compatible with the command-line
wrapper used by the application.

## Operation implementation extension

### Replace an existing implementation

`Operations.implementation_for(..., replace=True)` lets an extension replace
an already registered operation implementation, including the implementation
for an operation such as `CreateTableOp`. Without `replace=True`, registration
remains suitable for adding new operation types rather than overriding existing
ones. (since 1.17.0)

Make replacement scope explicit and cover both online execution and offline SQL
generation if the implementation participates in both modes.
