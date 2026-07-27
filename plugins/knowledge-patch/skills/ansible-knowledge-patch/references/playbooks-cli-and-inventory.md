# Playbooks, CLI, Inventory, and Galaxy

These user-facing and compatibility changes are attributed to batch
`2.19-2.20`.

## Cache and CLI Options

`ansible`, `ansible-console`, and `ansible-pull` support `--flush-cache`.
Use it when a run must invalidate cached facts or inventory-derived data.

The `--inventory-file` alias is deprecated; use `--inventory`.
The `oneline` and `tree` callbacks and their `-o` and `-t` arguments are
deprecated.

## Inventory Parsing

The default `INVENTORY_IGNORE_EXTS` no longer includes `ini`. A file such as
`inventory.ini` is therefore considered for inventory parsing unless `ini` is
explicitly restored to the ignore list.

Audit repositories that keep non-inventory `.ini` files beside inventory
sources. Either move those files, narrow inventory paths, or deliberately
configure the ignore extension.

## Diagnostics

`-vvv` no longer enables tracebacks. Control traceback display with
`DISPLAY_TRACEBACK`.

Task results expose emitted `warnings` and `deprecations`. Tools that inspect,
serialize, or redact task results should preserve and handle these fields.

## Deprecated Playbook Surfaces

Replace `play_hosts` with `ansible_play_batch`.

The following playbook forms are deprecated:

- An empty `args` keyword.
- Mapping-form `action`.
- Combining `key=value` arguments with `args`.

Normalize tasks to a module's YAML mapping form. `DEFAULT_MANAGED_STR` is also
deprecated; define `ansible_managed` as an ordinary variable.

## Play Argument-Spec Validation

The `validate_argspec` play keyword is a tech preview added in 2.20. Setting
it to `true` uses the required play `name` as the argument-spec name. A string
selects a different spec. Specs live in `<playbook_name>.meta.yml`.

```yaml
# deploy.yml
- name: deploy
  hosts: all
  validate_argspec: true
```

```yaml
# deploy.meta.yml
argument_specs:
  deploy:
    options:
      environment:
        type: str
        required: true
```

Keep the play name stable when it is also the spec selector, or use an
explicit string selector.

## Galaxy Collection Servers

Collection servers used by Galaxy must implement API v3. API v2 support was
removed in 2.20. Validate private Galaxy-compatible servers before upgrading
controllers or execution environments.
