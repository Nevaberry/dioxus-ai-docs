# Revisions, CLI, and Extensions

## Revision identifiers and files

### Colons are reserved in revision IDs (1.17.0)

Custom revision identifiers cannot contain `:` because Alembic reserves the
character for revision-range syntax. Use an identifier such as `REV_1` rather
than `REV:1`. Update generators that derive revision IDs from external names
before creating new revisions.

### Date-organized revision paths (1.18.0)

`file_template` accepts directory separators and automatically creates the
required directories:

```toml
[tool.alembic]
file_template = "%(year)d/%(month).2d/%(day).2d_%(rev)s_%(slug)s"
recursive_version_locations = true
```

Enable `recursive_version_locations`; without it, later commands will not find
the nested revision files.

## Head validation and graph traversal

### Require every head to be applied (1.17.0)

`command.current()` accepts `check_heads=True`. The equivalent CLI option is:

```console
alembic current --check-heads
```

When any head revision is not applied, the API raises `DatabaseNotAtHead` and
the CLI exits with a nonzero status. Use this as a deployment or health-check
gate when all branches must be current.

### Dependency-aware head lookup (1.18.0)

`ScriptDirectory.get_heads(consider_depends_on=True)` removes nominal heads
that another revision references through `depends_on`:

```python
heads = script.get_heads(consider_depends_on=True)
```

The result matches the effective heads stored in `alembic_version` after all
upgrades. Leave the option off only when callers specifically need nominal
revision-graph heads.

## Creating merge revisions

### Splice from non-head revisions (1.18.0)

The merge command accepts `--splice`, and `command.merge()` accepts the
corresponding `splice` parameter. This permits creation of a merge revision
whose selected revisions are not currently heads:

```console
alembic merge --splice rev_a rev_b
```

Use the option deliberately: the resulting graph is a splice rather than a
normal merge of current branches.

## Command extensions

### Public custom-command registration (1.16.0)

Applications extending the Alembic CLI can register a command through the
public mechanism:

```python
command_line.register_command(my_command)
```

`CommandLine.register_command()` replaces reliance on the previously internal
registration path.

## Operation implementation extensions

### Replace an existing implementation (1.17.0)

Pass `replace=True` to `Operations.implementation_for()` when an extension must
replace the registered implementation for an existing operation such as
`CreateTableOp`. Without the flag, registration remains suited to new
operation types rather than overriding an existing handler.

## Automatically loaded plugins

### Plugin interface and autogenerate comparators (1.18.0)

The `Plugin` interface supports automatically loaded third-party extensions.
A plugin can register operations, implementations, and autogenerate
comparators; use `Plugin.add_autogenerate_comparator()` for comparator
registration.

Built-in and third-party comparison plugins can be selected for each migration
environment:

```python
context.configure(autogenerate_plugins=[...])
```

The underlying API is
`EnvironmentContext.configure(autogenerate_plugins=...)`. Existing add-ons do
not have to adopt plugin entry points and can continue using their established
registration mechanisms.
