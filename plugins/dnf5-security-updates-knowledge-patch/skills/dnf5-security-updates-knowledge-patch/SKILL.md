---
name: dnf5-security-updates-knowledge-patch
description: "DNF5 security and package management changes since training cutoff — advisory command (replaces updateinfo), security upgrade flags, automatic updates, offline upgrades, versionlock TOML, config-manager subcommands, needs-restarting defaults, Ansible dnf5 module, replay command. This skill should be used when writing DNF5 commands, Ansible dnf5 playbooks, or configuring dnf5-automatic."
version: "2026.04.07"
license: MIT
metadata:
  author: Nevaberry
---

# DNF5 Knowledge Patch

Claude knows DNF4 commands and basic yum/dnf heritage. This skill covers DNF5 changes that affect command syntax, configuration files, and automation workflows.

## Index

| Topic | Reference | Key changes |
|---|---|---|
| Advisory command | [references/advisory-command.md](references/advisory-command.md) | Replaces `updateinfo`, mandatory subcommands, JSON output, `--advisory-severities` |
| Security upgrades | [references/security-upgrades.md](references/security-upgrades.md) | `--security`/`--minimal` flags, CVE targeting, automatic updates timer+config, offline upgrades |
| Configuration | [references/configuration-changes.md](references/configuration-changes.md) | Versionlock TOML format, config-manager subcommands, needs-restarting default change |
| Automation | [references/automation-and-replay.md](references/automation-and-replay.md) | Ansible `dnf5` module, `replay` command (split from `history`) |

---

## Breaking Changes

| DNF4 | DNF5 | Notes |
|---|---|---|
| `dnf updateinfo` | `dnf5 advisory <subcommand>` | Bare `advisory` fails — subcommand required |
| `--sec-severity` | `--advisory-severities=SEVERITY,...` | Accepts: critical, important, moderate, low, none |
| `--strict` | `--skip-broken` / `--skip-unavailable` | Split into two flags; `best` defaults to `true` |
| `dnf-automatic-download.timer` | `dnf5-automatic.timer` | One timer replaces three |
| `/etc/dnf/automatic.conf` (flat) | `/etc/dnf/automatic.conf` (new keys) | `reboot = when-needed` option added |
| `versionlock.list` (flat) | `/etc/dnf/versionlock.toml` | TOML with conditions |
| `config-manager --add-repo` | `config-manager addrepo` | All flags replaced by subcommands |
| `config-manager --enable` | `config-manager enable` | Original repo files never modified |
| `needs-restarting` (process scan) | `needs-restarting` (reboothint) | Process scan requires explicit `-p` |
| `history redo/undo` | `replay <dir>` | Standalone command; takes directory, not file |

---

## Quick Reference

### Advisory queries

`dnf5 advisory` subcommands: `list`, `summary`, `info`. Bare `dnf5 advisory` fails.

```bash
dnf5 advisory list --security
dnf5 advisory summary --advisory-severities=critical,important
dnf5 advisory info FEDORA-2024-abc123
dnf5 advisory list --json                  # basic JSON
dnf5 advisory list --json --with-cve       # adds references array
```

Severity values for `--advisory-severities`: `critical`, `important`, `moderate`, `low`, `none` (comma-separated).

### Security upgrades

```bash
# Apply only security updates
dnf5 upgrade --security

# Minimal upgrade — lowest version that fixes the advisory
dnf5 upgrade --minimal --security
dnf5 upgrade --minimal --advisory-severities=critical

# Target specific CVE or advisory
dnf5 upgrade --cves=CVE-2024-1234
dnf5 upgrade --advisories=FEDORA-2024-abc123

# Check without applying
dnf5 check-upgrade --security --json
```

Exit codes: `100` = updates available, `0` = none. `--strict` is gone — use `--skip-broken` (dependency issues) and `--skip-unavailable` (missing packages). `best` defaults to `true`.

### Automatic security updates

Config defaults: `/usr/share/dnf5/dnf5-plugins/automatic.conf`. Overrides: `/etc/dnf/automatic.conf`.

One timer replaces three (`dnf-automatic-download.timer`, `dnf-automatic-install.timer`, `dnf-automatic-notifyonly.timer` are all gone).

```ini
# /etc/dnf/automatic.conf
[commands]
upgrade_type = security     # "default" or "security"
apply_updates = true
reboot = when-needed        # never | when-changed | when-needed (new)
reboot_command = shutdown -r +5 'Rebooting after applying package updates'

[emitters]
emit_via = stdio            # stdio, email, motd, command, command_email
```

```bash
systemctl enable --now dnf5-automatic.timer
```

### Offline upgrades

Any transactional command accepts `--offline` to defer execution to a minimal boot environment:

```bash
dnf5 upgrade --security --offline
dnf5 offline status          # check pending transaction
dnf5 offline reboot          # reboot and apply
dnf5 offline log --number=-1 # view last offline transaction log
```

### Versionlock (TOML)

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

```bash
dnf5 versionlock add openssl                       # lock to installed version
dnf5 versionlock exclude openssl-3.1.5-1.fc41      # skip specific version
dnf5 versionlock list
```

### Config-manager

Old flags (`--add-repo`, `--save --setopt`, `--enable/--disable`) are gone. Uses subcommands. Original repo files are **never modified** — overrides go to `/etc/dnf/repos.override.d/99-config_manager.repo`.

```bash
dnf5 config-manager enable updates-testing
dnf5 config-manager disable fedora
dnf5 config-manager setopt fedora.enabled=0
dnf5 config-manager addrepo --set=baseurl=https://example.com/repo --id=myrepo
```

### Needs-restarting

Default is now **reboothint** (was process scanning in DNF4). Process scan requires explicit `-p`.

```bash
dnf5 needs-restarting              # exit 1 = reboot needed (reboothint only)
dnf5 needs-restarting -s           # list services needing restart
dnf5 needs-restarting -p           # list processes needing restart
dnf5 needs-restarting -p -e        # exclude systemd-managed processes
dnf5 needs-restarting --json       # structured JSON output
```

### Ansible dnf5 module

`ansible.builtin.dnf5` (since ansible-core 2.15) requires `python3-libdnf5` on managed hosts. As of ansible-core 2.19, `auto_install_module_deps: true` (default) installs it automatically.

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

### Replay

`history replay` moved to standalone `dnf5 replay`. Takes a directory (not file). Create with `--store`:

```bash
dnf5 upgrade --security --store=./my-transaction
dnf5 replay ./my-transaction --skip-unavailable
```

---

## Reference Files

| File | Contents |
|---|---|
| [advisory-command.md](references/advisory-command.md) | Full advisory subcommand reference, JSON output formats, severity filtering |
| [security-upgrades.md](references/security-upgrades.md) | All security upgrade flags, automatic.conf configuration, timer setup, offline upgrade workflow |
| [configuration-changes.md](references/configuration-changes.md) | Versionlock TOML schema, config-manager subcommands and override paths, needs-restarting behavior change |
| [automation-and-replay.md](references/automation-and-replay.md) | Ansible dnf5 module usage and dependencies, replay command syntax |
