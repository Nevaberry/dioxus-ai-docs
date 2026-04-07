# Configuration Changes

## Versionlock (TOML Format)

File moved from flat format to `/etc/dnf/versionlock.toml`:

```toml
version = "1.0"

[[packages]]
name = "openssl"
[[packages.conditions]]
key = "evr"
comparator = ">="
value = "0:3.1.0"
[[packages.conditions]]
key = "evr"
comparator = "<"
value = "0:3.2.0"
```

### Commands

```bash
dnf5 versionlock add openssl         # lock to installed version
dnf5 versionlock exclude openssl-3.1.5-1.fc41  # skip specific version
dnf5 versionlock list
```

### TOML Schema

Each entry in `[[packages]]` has:
- `name` — package name
- `[[packages.conditions]]` — one or more version constraints with:
  - `key` — comparison field (e.g., `evr` for epoch:version-release)
  - `comparator` — operator (`>=`, `<`, `=`, etc.)
  - `value` — version string (epoch:version-release format)

## Config-Manager Overhaul

Old `--add-repo`, `--save --setopt`, `--enable/--disable` flags are gone. Now uses subcommands. Original repo files are **never modified** — overrides go to `/etc/dnf/repos.override.d/99-config_manager.repo`.

```bash
dnf5 config-manager enable updates-testing
dnf5 config-manager disable fedora
dnf5 config-manager setopt fedora.enabled=0
dnf5 config-manager addrepo --set=baseurl=https://example.com/repo --id=myrepo
```

### Subcommand Reference

| Subcommand | Purpose | Example |
|---|---|---|
| `enable` | Enable a repository | `config-manager enable updates-testing` |
| `disable` | Disable a repository | `config-manager disable fedora` |
| `setopt` | Set a repository option | `config-manager setopt fedora.enabled=0` |
| `addrepo` | Add a new repository | `config-manager addrepo --set=baseurl=URL --id=myrepo` |

Override path: `/etc/dnf/repos.override.d/99-config_manager.repo`

## Needs-Restarting Changes

Default behavior is now **reboothint** (was process scanning in DNF4). Process scanning requires explicit `-p`.

```bash
dnf5 needs-restarting                  # exit 1 = reboot needed
dnf5 needs-restarting -s               # list services needing restart
dnf5 needs-restarting -p               # list processes needing restart
dnf5 needs-restarting -p -e            # exclude systemd-managed processes
dnf5 needs-restarting --json           # structured JSON output (new)
```

### Flag Reference

| Flag | Purpose |
|---|---|
| *(none)* | Reboothint only — exit 1 if reboot needed |
| `-s` | List services needing restart |
| `-p` | List processes needing restart |
| `-p -e` | Processes, excluding systemd-managed |
| `--json` | JSON output |
