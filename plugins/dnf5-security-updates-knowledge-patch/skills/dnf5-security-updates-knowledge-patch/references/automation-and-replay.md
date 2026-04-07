# Automation and Replay

## Ansible dnf5 Module

`ansible.builtin.dnf5` (since ansible-core 2.15) requires `python3-libdnf5` on managed hosts. As of 2.19, `auto_install_module_deps: true` (default) will install it automatically.

```yaml
- name: Apply security updates only
  ansible.builtin.dnf5:
    name: "*"
    state: latest
    security: true

- name: Apply bugfix updates only
  ansible.builtin.dnf5:
    name: "*"
    state: latest
    bugfix: true
```

### Key Parameters

| Parameter | Purpose |
|---|---|
| `security: true` | Apply only security updates |
| `bugfix: true` | Apply only bugfix updates |
| `name: "*"` | Target all packages |
| `state: latest` | Upgrade to latest available |
| `auto_install_module_deps: true` | Auto-install `python3-libdnf5` (default since 2.19) |

### Requirements

- `python3-libdnf5` must be present on managed hosts
- ansible-core >= 2.15 for `ansible.builtin.dnf5`
- ansible-core >= 2.19 for automatic dependency installation

## Replay Command

`history replay` moved to standalone `dnf5 replay`. Takes a directory (not file). Create with `--store`:

```bash
# Store a transaction for later replay
dnf5 upgrade --security --store=./my-transaction

# Replay the stored transaction
dnf5 replay ./my-transaction --skip-unavailable
```

### Key Differences from DNF4

- Standalone `replay` command instead of `history redo`/`history undo`
- Takes a **directory** path, not a file
- Transaction stored with `--store=<dir>` flag on any transactional command
- `--skip-unavailable` handles packages no longer in repos
