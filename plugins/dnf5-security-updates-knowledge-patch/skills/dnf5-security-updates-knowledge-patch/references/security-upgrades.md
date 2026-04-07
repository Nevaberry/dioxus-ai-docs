# Security Upgrades

## Security Upgrade Flags

```bash
# Apply only security updates
dnf5 upgrade --security

# Minimal upgrade — lowest version that fixes the advisory
dnf5 upgrade --minimal --security
dnf5 upgrade --minimal --advisory-severities=critical

# Target specific CVE or advisory
dnf5 upgrade --cves=CVE-2024-1234
dnf5 upgrade --advisories=FEDORA-2024-abc123

# Check without applying (exit code 100 = updates available, 0 = none)
dnf5 check-upgrade --security --json
```

`--strict` is deprecated — split into `--skip-broken` (dependency issues) and `--skip-unavailable` (missing packages). `best` now defaults to `true`.

## Automatic Security Updates

Config paths changed. Defaults: `/usr/share/dnf5/dnf5-plugins/automatic.conf`. Overrides: `/etc/dnf/automatic.conf`.

**One timer replaces three** — `dnf-automatic-download.timer`, `dnf-automatic-install.timer`, and `dnf-automatic-notifyonly.timer` are all gone. Only `dnf5-automatic.timer` exists.

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

### Configuration Keys

| Section | Key | Values | Notes |
|---|---|---|---|
| `[commands]` | `upgrade_type` | `default`, `security` | Filter by update type |
| `[commands]` | `apply_updates` | `true`, `false` | Whether to install updates |
| `[commands]` | `reboot` | `never`, `when-changed`, `when-needed` | `when-needed` is new in DNF5 |
| `[commands]` | `reboot_command` | shell command | Custom reboot command |
| `[emitters]` | `emit_via` | `stdio`, `email`, `motd`, `command`, `command_email` | Notification method |

## Offline Security Upgrades

Any transactional command accepts `--offline` to defer execution to a minimal boot environment:

```bash
dnf5 upgrade --security --offline
dnf5 offline status          # check pending transaction
dnf5 offline reboot          # reboot and apply
dnf5 offline log --number=-1 # view last offline transaction log
```

The `--offline` flag works with any transactional command (`upgrade`, `install`, `remove`, etc.), not just security upgrades.
