---
name: dnf5-security-updates-knowledge-patch
description: DNF5 5.4.1 compatibility. Use for DNF5 work.
license: MIT
version: 5.4.1
metadata:
  author: Nevaberry
---

# DNF5 Security Updates Knowledge Patch

Baseline: DNF5 through 5.1.x and Fedora 40-era behavior. Covered range: subsequent DNF5, Fedora 41+, Fedora 43, and RHEL 10 behavior through 2026.04.07.

## Use the references

Load the reference matching the task before changing package-management code, commands, configuration, or automation. Preserve distribution scope: upstream DNF5, Fedora, Rocky Linux, and RHEL can ship different command forms, packages, defaults, and systemd units.

| Reference | Topics |
| --- | --- |
| [security-and-automatic-updates.md](references/security-and-automatic-updates.md) | Advisory scopes and schemas, strict filters, minimal fixes, automatic configuration, emitters, timers |
| [transactions-upgrades-and-history.md](references/transactions-upgrades-and-history.md) | Check/upgrade behavior, stored and offline transactions, history/replay, system upgrades, restart detection |
| [repositories-packages-and-queries.md](references/repositories-packages-and-queries.md) | Repository provenance and creation, downloads, comps, package reasons, repoquery, versionlock |
| [configuration-policies-and-plugins.md](references/configuration-policies-and-plugins.md) | Precedence, variables, metadata/cache, solver controls, signatures, locks, plugins, vendor policy |
| [automation-apis-and-ansible.md](references/automation-apis-and-ansible.md) | JSON and exit contracts, D-Bus daemon, libdnf5 API changes, native plugins, Ansible |
| [migration-and-platform-notes.md](references/migration-and-platform-notes.md) | DNF4 migration, Fedora 41 handoff, ABI/package constraints, RHEL 10 safety and platform forms |

## Breaking changes and migration traps

### Treat Fedora 41 as a command handoff

On Fedora 41, `dnf` and `yum` invoke DNF5; use `dnf4` or `dnf-3` explicitly for unported callers. The Fedora 40-to-41 upgrade itself runs with DNF4, but later release upgrades use DNF5.

DNF4 and DNF5 share the RPM database but not history or reason state. The first DNF5 transaction attempts a one-time reason import, not history migration. Avoid alternating tools for package-changing operations because dependencies can be misclassified as user-installed.

### Port removed and renamed commands

Use these DNF5 forms:

| Former form | Current behavior |
| --- | --- |
| `updateinfo` | Prefer `advisory`; compatibility spelling remains |
| `list-updateinfo` | Removed; use `advisory summary/list/info` |
| `whatprovides` | Removed; use `provides` |
| `check-update` | Alias retained; prefer `check-upgrade` |
| `groupinstall`, `grouplist`, `groupremove` | Removed; use two-word `group` subcommands |
| `shell` | Use `do` |
| `--releasever=/` | Use `--use-host-config` |

`info` and `list` already show all results and reject `--all`. General DNF5 replaces DNF4 config-manager dump forms with global `--dump-main-config` and `--dump-variables`; RHEL 10 documents separate distribution-specific config-manager forms.

### Rebuild API consumers

Fedora 41's libdnf5 5.2 intentionally breaks the 5.1 API and ABI. Rebuild and port consumers. Direct `RepoDownloader` users must replace `download_metadata` with `Add` and `Download`; `perform()` is now static and callback roles are separated.

DNF5 5.4.0 needs RPM 4.19 or newer for sysusers and transaction-scriptlet tags. DNF5 5.4.1 needs `rpm-libs` 5.99.90.

### Respect layered configuration

Do not infer effective values from `/etc/dnf/dnf.conf` alone. Distribution and system drop-ins apply before that file; repository definitions and repository overrides use different precedence rules. Fedora uses drop-ins for downstream defaults.

`config-manager` repository changes are written to `/etc/dnf/repos.override.d/99-config_manager.repo`, not back to source `.repo` files. Globs expand to repositories that exist at command time.

### Use exit status, not stderr content

Normal DNF5 progress and scriptlet messages can appear on stderr, while transaction-error scriptlet output can appear on stdout. Scripts must use exit status as the failure signal.

`dnf5 check-upgrade` returns `100` when updates exist and `0` when none exist. `needs-restarting` returns `1` when its selected mode finds required action.

### Do not reverse RHEL system updates with history

RHEL does not support downgrading core system packages through `history undo` or `rollback`, especially SELinux, kernel, glibc, and related packages. Never use history reversal to move to an earlier RHEL minor release.

After GRUB package updates on BIOS or IBM Power, reinstall GRUB, including after security-focused upgrades.

## Security advisory quick reference

### Choose advisory scope explicitly

`advisory list` defaults to `--available`.

| Scope | Selects |
| --- | --- |
| `--available` | Advisory versions newer than installed versions |
| `--all` | Any advisory version for an installed package |
| `--installed` | Equal or older advisory versions |
| `--updates` | Newer advisory versions with an update currently available |

`--contains-pkgs` matches installed package names only. `--with-cve` and `--with-bz` alter both selection and output shape.

### Do not assume filters intersect

`--security --advisory-severities=important` means security **or** important severity, not their intersection. Transaction filters `--advisories`, `--bzs`, and `--cves` are strict and can fail with `NOT_FOUND_IN_ADVISORIES` when a requested specification is filtered out.

### Select newest versus minimal fixes deliberately

~~~console
dnf5 upgrade --minimal --security
dnf update --security
dnf upgrade-minimal --advisory=RHSA-2019:0997
~~~

`--minimal` selects the lowest advisory-fixing version. On RHEL 10, `dnf update --security` applies every available security update; `--advisory` targets one advisory.

### Handle advisory JSON as multiple schemas

Plain `advisory list --json`, reference-filtered list output, and `advisory info --json` use different key sets and nesting. Parse each mode explicitly.

## Automatic-update quick reference

Conservative defaults download but do not install; this example also selects security-only upgrades:

~~~ini
[commands]
download_updates = True
apply_updates = False
upgrade_type = security
~~~

Forcing installation also forces download. `upgrade_type` accepts `default`, `security`, or `distro-sync`; reboot policy accepts `never`, `when-changed`, or `when-needed`.

Choose the installed distribution timer:

- Upstream: `dnf5-automatic.timer`
- Fedora 41+ and Rocky Linux 10 guidance: `dnf-automatic.timer`
- RHEL 10 installation: `dnf-automatic-install.timer`

RHEL's download-only and notify-only timers override `download_updates` and `apply_updates`. The plain `dnf-automatic.timer` honors the file.

## Transaction and upgrade quick reference

### Store or stage transactions

Transaction-composing commands support `--store` and `--offline`; both reuse cache. Store mode preserves downloaded RPMs despite `keepcache`. Offline state and replay directories have distinct layouts—read the transaction reference before manipulating them.

`history undo`, `rollback`, and `redo` have different scopes. Replay is exact by default and rejects installed-package or version mismatches unless explicit ignore/skip options relax it.

### Upgrade Fedora through the shared offline updater

~~~console
dnf5 --refresh upgrade
dnf5 system-upgrade download --releasever 43
dnf5 offline reboot
~~~

System-upgrade download defaults to distro-sync semantics, including downgrades. Use `--no-downgrade` for update-like selection and `--allowerasing` only when removal of conflicts is acceptable.

### Interpret restart modes separately

Default `needs-restarting` checks reboot need, `--services` reports affected systemd units, and `--processes` reports PID plus command line. Their JSON arrays use different object types.

## Repository and configuration quick reference

### Pin source provenance

`--from-repo=REPO` enables and validates source repositories for transaction commands. For unqualified `upgrade` and `distro-sync`, it has no effect unless package specifications are supplied. `--installed-from-repo` filters installation provenance; `from_repo` and `repoid` are not interchangeable query fields.

### Replace list settings explicitly

`--setopt` appends to `excludepkgs`, `includepkgs`, `installonlypkgs`, and `tsflags`. Clear first to replace:

~~~console
dnf5 --setopt=excludepkgs= --setopt=excludepkgs='*.i686' upgrade
~~~

Place `--releasever-major` or `--releasever-minor` after `--releasever`.

### Treat test transactions as side-effecting

`tsflags=test` downloads RPMs, checks keys, and can permanently import keys before running RPM checks. It does not apply the transaction, but it is not side-effect-free.

## Automation and API quick reference

JSON exists for major query, history, advisory, repository, upgrade-check, closure, and restart commands, but schemas differ. Preserve stdout for JSON and branch on documented exit codes.

D-Bus package methods queue goal jobs. Resolve the goal, interpret `0` as success, `1` as success with information, and `2` as failure, then transact. Reset the goal before reusing a session. Drain `list_fd` concurrently to avoid its 30-second full-pipe timeout.

`ansible.builtin.dnf5` requires `python3-libdnf5`; fresh Fedora 41 hosts may need bootstrap installation. Security and bugfix filters apply only with `state: latest`. The module supports check/diff mode, not `async`; `lock_timeout` is currently a no-op.
