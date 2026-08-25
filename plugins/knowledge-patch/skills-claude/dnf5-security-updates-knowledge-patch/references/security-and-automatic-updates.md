# Security Advisories and Automatic Updates

## Contents

- Advisory scopes and filters
- Advisory output and strict transaction matching
- Applying security fixes
- Automatic-update configuration and run modes
- Reboot, timing, and result emitters
- Distribution timer differences

## Advisory scopes and filters

DNF5 advisory queries default to `--available`: advisories containing a package version newer than an installed version. Choose the scope deliberately:

| Scope | Meaning |
| --- | --- |
| `--available` | Advisory package versions newer than an installed version; the default |
| `--all` | Any advisory version for an installed package |
| `--installed` | Advisory versions equal to or older than the installed version |
| `--updates` | Newer advisory versions whose packages currently have an available update |

An installed package can therefore appear in multiple installed advisories.

~~~console
dnf5 advisory list --installed --security
dnf5 advisory summary --updates
~~~

`--contains-pkgs` accepts globs but matches installed package names only. Classification filters are `--security`, `--bugfix`, `--enhancement`, and `--newpackage`. `--advisory-severities` accepts `critical`, `important`, `moderate`, `low`, or `none`.

Filters of different kinds are not necessarily intersections. In particular, combining `--security` with `--advisory-severities=important` selects security advisories **or** advisories with important severity.

~~~console
dnf5 advisory list --contains-pkgs='kernel*' --security
dnf5 advisory list --security --advisory-severities=important
~~~

`--with-cve` and `--with-bz` restrict results to advisories carrying the selected reference type. In text `list` output they replace the advisory-ID column with the reference ID. Advisory queries can also filter by package NEVRA.

## Advisory output and strict transaction matching

`advisory list --json` has two schemas:

- Normally each record has `name`, `type`, `severity`, `nevra`, and `buildtime`.
- With `--with-cve` or `--with-bz`, records instead have `advisory_name`, `advisory_type`, `advisory_severity`, `advisory_buildtime`, `nevra`, and a `references` array.

`advisory info --json` uses capitalized detail keys and a `collections` object containing package NEVRAs and module NSVCAs. Advisory JSON uses standardized timestamps and suppresses ordinary error text to keep stdout machine-readable.

Transaction filters `--advisories`, `--bzs`, and `--cves` are strict. If a filter removes a requested package specification, resolution can fail with `NOT_FOUND_IN_ADVISORIES`; do not treat these filters as best-effort selectors.

## Applying security fixes

On RHEL 10, `dnf update --security` applies every available security update. Use `--advisory` for one advisory. Use `upgrade-minimal` when the goal is the smallest available version change that contains the fix.

~~~console
dnf update --security
dnf update --advisory=RHSA-2019:0997
dnf upgrade-minimal --advisory=RHSA-2019:0997
~~~

`dnf5 upgrade --minimal` and `dnf5 check-upgrade --minimal` select the lowest versions that fix matching bugfix, enhancement, security, or new-package advisories rather than simply selecting the newest builds. Additional advisory filters restrict the fixes considered.

## Automatic-update configuration and run modes

`dnf5 automatic` reads distribution defaults from `/usr/share/dnf5/dnf5-plugins/automatic.conf`, then host overrides from `/etc/dnf/automatic.conf`. The host file may contain only settings that differ.

Conservative defaults are:

~~~ini
[commands]
download_updates = True
apply_updates = False
~~~

Enabling `apply_updates` implies downloading. Downloaded but unapplied packages remain cached until the next successful DNF transaction.

Per-run switches override the file:

- `--downloadupdates` and `--no-downloadupdates` control downloads.
- `--installupdates` and `--no-installupdates` control installation.
- Forcing installation also forces downloading.
- `dnf5 automatic --no-downloadupdates` is a notification-only test.
- `dnf5 automatic --installupdates` forces download and installation without editing configuration.

`upgrade_type` accepts `default`, `security`, or `distro-sync`. The last mode aligns packages to enabled repositories like `dnf5 distro-sync`.

## Reboot, timing, and result emitters

`reboot` accepts `never` (default), `when-changed`, or `when-needed`. `reboot_command` defaults to a five-minute delayed `shutdown -r`. `network_online_timeout` defaults to 60 seconds; set it to `0` to disable network detection. `random_sleep` is honored only when automatic runs with `--timer`, in addition to any systemd timer random delay.

~~~ini
[commands]
upgrade_type = distro-sync
apply_updates = True
reboot = when-needed
~~~

`emit_via` selects `stdio`, `command`, `command_email`, direct-SMTP `email`, or `motd`. The MOTD emitter writes `/etc/motd.d/dnf5-automatic`. `emit_no_updates` defaults to false and `system_name` to the hostname.

The command emitter formats `{body}` and normally passes it on stdin. For `command_email`, `emit_via` expands the command into individual arguments. Direct email accepts TLS modes `no`, `yes`, or `starttls` and reads SMTP credentials from `~/.netrc`. It now fails explicitly if libcurl lacks SMTP support, although the package does not require the `libcurl-full` variant.

~~~ini
[emitters]
emit_via = motd
emit_no_updates = True
system_name = web-01
~~~

## Distribution timer differences

Use the unit installed and documented by the target distribution:

- Upstream DNF5 documents `dnf5-automatic.timer`.
- Fedora 41+ and Rocky Linux 10 package guidance uses `dnf-automatic.timer`.
- RHEL 10 installs `dnf-automatic`, reads `/etc/dnf/automatic.conf`, and uses `dnf-automatic-install.timer` for automatic installation. Set `upgrade_type = security` under `[commands]` for security-only runs; `default` means all upgrades.

~~~console
systemctl enable --now dnf5-automatic.timer
systemctl enable --now dnf-automatic-install.timer
~~~

RHEL 10 also supplies mode-specific units:

- `dnf-automatic-download.timer` forces download without installation.
- `dnf-automatic-notifyonly.timer` refreshes metadata and reports updates without downloading RPMs.
- `dnf-automatic.timer` honors the configured `download_updates` and `apply_updates` values.

The mode-specific units override those two `[commands]` settings.
