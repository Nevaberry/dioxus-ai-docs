# Playbooks, CLI, Inventory, and Galaxy

## Cache and inventory command options

The `ansible`, `ansible-console`, and `ansible-pull` commands accept
`--flush-cache` (`2.19-2.20`). Use it when the requested operation requires
invalidating cached facts or inventory data.

Prefer `--inventory`; the `--inventory-file` alias is deprecated.

## Inventory file discovery

`INVENTORY_IGNORE_EXTS` no longer contains `ini` by default. A file such as
`inventory.ini` is therefore parsed unless `ini` is explicitly restored to the
ignore list. Audit repositories that previously left unrelated `.ini` files in
inventory search paths.

## Tracebacks, warnings, and deprecations

`DISPLAY_TRACEBACK` controls traceback display. `-vvv` increases verbosity but
is not the switch that enables tracebacks.

Task results expose emitted `warnings` and `deprecations`. Diagnostic tools and
wrappers should consume those result fields rather than scraping display text.

## Deprecated playbook syntax

Replace these surfaces:

- `play_hosts` with `ansible_play_batch`.
- `DEFAULT_MANAGED_STR` with an ordinary `ansible_managed` variable.
- Mapping-form `action` with standard module task syntax.

Remove empty `args` mappings. Do not combine `key=value` module arguments with
an `args` mapping in one task.

## Play argument-spec validation

Ansible 2.20 introduced tech-preview play validation through
`validate_argspec`. The value `true` selects the play's required `name`; a
string selects another entry in `<playbook_name>.meta.yml`.

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

## Collection server compatibility

Collection Galaxy servers must support API v3; v2 support was removed in 2.20.
Upgrade private Galaxy-compatible servers before upgrading controllers.

In `2.21.3`, `ansible-galaxy` retries a collection download when the response
is shorter than expected. A truncated first response no longer fails
immediately as an artifact-hash mismatch.

## Vault filter compatibility

The `vault` and `unvault` filters no longer accept `vaultid`. Remove that
argument from filters and select vault identities through supported vault
configuration and CLI mechanisms.
