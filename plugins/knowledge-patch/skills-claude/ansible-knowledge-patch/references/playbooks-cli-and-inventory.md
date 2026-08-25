# Playbooks, CLI, Inventory, and Galaxy

## Cache control and inventory discovery

The `ansible`, `ansible-console`, and `ansible-pull` commands in `2.19-2.20`
accept `--flush-cache` when cached facts or inventory data must be invalidated.

`INVENTORY_IGNORE_EXTS` no longer includes `ini` by default. A file such as
`inventory.ini` is therefore parsed as inventory unless `ini` is explicitly
restored to the ignore list. Audit repositories that used an `.ini` suffix for
unrelated configuration.

Prefer `--inventory`; the `--inventory-file` alias is deprecated.

## Tracebacks and result diagnostics

Use `DISPLAY_TRACEBACK` to control traceback display in `2.19-2.20`. `-vvv`
does not enable tracebacks. Diagnostic tooling can consume the `warnings` and
`deprecations` values emitted in task results; preserve these fields when
wrapping or relaying results.

## Deprecated play and task syntax

Replace `play_hosts` with `ansible_play_batch` in `2.19-2.20`. Also remove:

- an empty `args` keyword;
- mapping-form `action`;
- task syntax that combines `key=value` arguments with `args`.

`DEFAULT_MANAGED_STR` is deprecated. Define `ansible_managed` as a normal
variable instead.

## Play argument-spec validation

Play argument validation is a tech preview in `2.19-2.20`. Add
`validate_argspec: true` to use the play's required `name` as the argument-spec
name. Supply a string instead to select another entry from
`<playbook_name>.meta.yml`.

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

## Galaxy server and download behavior

Collection Galaxy servers must support API v3 in `2.19-2.20`; API v2 support
is removed.

In `2.21.3`, `ansible-galaxy` retries a collection download when the response
body is shorter than expected. A truncated first response no longer causes an
immediate terminal artifact-hash mismatch.

## Explicit test-target versions

Target filtering in `2.21.3` preserves a user-specified version even if that
version is absent from completion configuration. Do not treat completion data
as the authoritative allowlist for explicit target versions.
