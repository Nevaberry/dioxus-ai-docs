# Migration and Platform Notes

## Contents

- Fedora 41 command handoff
- DNF4/DNF5 state and CLI migration
- API and packaging compatibility
- Fedora plugin and configuration transition
- RHEL 10 repository and plugin behavior
- RHEL 10 update safety boundaries

## Fedora 41 command handoff

On Fedora 41, package `dnf5` obsoletes `dnf`. `/usr/bin/dnf` and compatibility path `/usr/bin/yum` invoke DNF5. DNF4 remains available as `/usr/bin/dnf-3` and `/usr/bin/dnf4`.

The Fedora 40-to-41 upgrade itself runs under DNF4. Afterward, invoke `dnf4` explicitly for callers not yet ported and use DNF5 for later release upgrades.

## DNF4/DNF5 state and CLI migration

DNF4 and DNF5 share the RPM database but keep transaction history and installed-package reasons in different formats. Neither sees the other's history. A dependency installed with one can appear user-installed to the other and escape autoremove.

The first DNF5 transaction attempts to import DNF4 reason state, but it does not migrate history. Avoid alternating tools for package-changing operations.

Command migrations include:

| DNF4 form | DNF5 form or status |
| --- | --- |
| `updateinfo` | `advisory`; `updateinfo` remains a compatibility spelling |
| `list-updateinfo` | Removed; use structured `advisory` subcommands |
| `whatprovides` | Removed; use `provides` |
| `check-update` | Retained alias; prefer `check-upgrade` |
| `groupinstall`, `grouplist`, `groupremove` | Removed; use `group install/list/remove` |
| `shell` | Use `do` |
| `--releasever=/` | Use `--use-host-config` |

`info` and `list` no longer accept `--all` because all results are already the default.

~~~console
dnf5 advisory summary
dnf5 advisory list
dnf5 advisory info FEDORA-2024-24fbd327e3
dnf5 provides /usr/bin/example
dnf5 check-upgrade
dnf5 group install 'Development Tools'
~~~

General DNF5 does not carry over DNF4 `config-manager --dump` or `config-manager --dump-variables`. Use `dnf5 --dump-main-config` and `dnf5 --dump-variables`. Also, `makecache` is not guaranteed to refresh metadata each time; request `--refresh` when required.

## API and packaging compatibility

Fedora 41's libdnf5 5.2 intentionally breaks the 5.1 API and ABI. Rebuild consumers and port them from 5.1 to 5.2; do not assume source or binary compatibility.

Direct `RepoDownloader` users also need the newer `Add`/`Download` API described in the automation reference.

DNF5 5.4.0 requires RPM 4.19 or newer for sysusers and transaction-scriptlet tags. DNF5 5.4.1 raises the `rpm-libs` requirement to 5.99.90. Systemd service files are installed only when the build enables `WITH_SYSTEMD`.

## Fedora plugin and configuration transition

Fedora 41 upgrades replace `dnf-automatic` with `dnf5-plugin-automatic`. Installed DNF4 plugins remain usable through `dnf4` when no DNF5 port exists. DNF5 replaces the Snapper plugin with the Actions plugin.

DNF5 supports distribution-specific default drop-ins, and Fedora supplies them to retain downstream defaults. Diagnose effective settings across the drop-in layers instead of inspecting only `/etc/dnf/dnf.conf`.

Fresh Fedora 41 installations can omit `python3-libdnf5`, which breaks Ansible DNF5 tasks until bootstrapped; upgraded Fedora 40 systems install the binding.

~~~console
sudo dnf5 install python3-libdnf5
~~~

DNF5 does not reserve stderr for failures. Successful transaction progress and scriptlet messages can appear there. Use exit status, not a nonempty stderr capture, as the automation failure signal.

## RHEL 10 repository and plugin behavior

RHEL 10 documentation exposes these `dnf config-manager` forms:

~~~console
dnf config-manager --dump
dnf config-manager --add-repo https://packages.example.com/example.repo
dnf config-manager --disable example
dnf config-manager --enable example
~~~

`--dump` includes effective global defaults omitted from `/etc/dnf/dnf.conf`. `--add-repo URL` is the documented custom-repository form, and a newly added repository is enabled by default. These distribution forms are distinct from the general DNF5 commands described above.

The `product-id` and `subscription-manager` plugins are required to install or update from the RHEL content network. Disable all plugins only for diagnosis. Disable one persistently in `/etc/dnf/plugins/<plugin_name>.conf`:

~~~ini
[main]
enabled=False
~~~

Or disable it for one command:

~~~console
dnf update --disableplugin=<plugin_name>
~~~

## RHEL 10 update safety boundaries

After updating GRUB boot-loader packages on BIOS or IBM Power, reinstall GRUB. This applies to ordinary and security-focused upgrades.

RHEL does not support downgrading system packages through `dnf history undo` or `rollback`, especially:

- `selinux` and `selinux-policy-*`
- `kernel`
- `glibc`
- `glibc` dependencies such as `gcc`

Do not use history reversal to move to an earlier RHEL minor release. Undo also fails when the required older package is no longer available.

For RHEL 10 automatic-update timer overrides and security-only configuration, read [Security Advisories and Automatic Updates](security-and-automatic-updates.md).
