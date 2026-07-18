---
name: arch-knowledge-patch
description: Arch Linux
license: MIT
version: null
metadata:
  author: Nevaberry
---

# Arch Linux Knowledge Patch

Baseline: Arch Linux through mid-2024 and pacman 6.x; covers changes through 2026-07-12, including pacman 7.1.0.

## Reference index

| Reference | Topics |
|---|---|
| [Package management](references/package-management.md) | pacman 7.0.0 and 7.1.0 sandboxing and signatures, makepkg and PKGBUILD changes, repositories, repo-add, firmware packaging, package-source licensing |
| [Service migrations](references/service-migrations.md) | OpenSSH and rsync interventions, Redis to Valkey, Zabbix accounts, Dovecot 2.4, nft-backed iptables, Kea ownership, Vinyl Cache |
| [Runtime and desktop transitions](references/runtime-and-desktop-transitions.md) | glibc and Discord, Wine WoW64, Plasma X11, Waydroid, .NET 10, NVIDIA 590 |
| [Operations and security](references/operations-and-security.md) | Arch service outage fallbacks, AUR package auditing |

## Use this patch

1. Read the package-management reference before changing `pacman.conf`, maintaining PKGBUILDs, running private repositories, or automating pacman 7.0.0 or 7.1.0.
2. Check the intervention tables before a full system upgrade, especially on remote hosts, servers, and graphical workstations.
3. Read the relevant migration reference before accepting renamed packages, accounts, directories, units, or configuration formats.
4. Review `.pacnew` and `.pacsave` files instead of assuming package upgrades preserve local configuration.
5. Perform Arch upgrades as full upgrades; do not turn an intervention into a partial-upgrade workflow.

## Breaking changes and required interventions

### Restart OpenSSH after the 9.8p1 upgrade

Restart the daemon immediately after upgrading `openssh` to 9.8p1 because the old daemon cannot accept new connections:

```sh
systemctl try-restart sshd
```

On a remote host, preserve an existing session until the restarted daemon accepts a new connection.

### Upgrade rsync everywhere

Upgrade every rsync daemon and client to Arch package `3.4.0-1` or newer, then reboot. Treat public mirrors as urgent: vulnerable anonymous servers can permit remote code execution, and hostile servers can attack connecting clients and sensitive files.

### Remove retired pacman repositories

Remove `[community]`, `[community-testing]`, `[testing]`, `[testing-debug]`, `[staging]`, and `[staging-debug]` from `/etc/pacman.conf`. Merge the `.pacnew` from `pacman>=6.0.2-7`; stale entries cause database synchronization to fail.

### Resolve the split linux-firmware upgrade

For upgrades from `linux-firmware` `20250508.788aadc8-2` or earlier to `20250613.12fe085f-5` or newer, remove the old package without dependency checks and reinstall it during the full upgrade:

```sh
pacman -Rdd linux-firmware
pacman -Syu linux-firmware
```

Expect `linux-firmware` to become an empty dependency package backed by hardware-specific firmware packages.

### Prepare Plasma X11 before Plasma 6.4

Install `plasma-x11-session` before upgrading an X11 workstation. Plasma 6.4 installs only the Wayland session by default after `kwin` splits into `kwin-wayland` and `kwin-x11`.

### Rebuild 32-bit Wine prefixes

Recreate existing 32-bit prefixes and reinstall their applications after `wine` and `wine-staging` move to pure WoW64. Do not expect `[multilib]` to remain a dependency; anticipate slower direct OpenGL from some 32-bit applications.

### Migrate Dovecot or pin the maintained 2.3 branch

Do not start Dovecot 2.4 with a 2.3-or-earlier configuration. Migrate it first, or install `dovecot23` and the matching `pigeonhole23` or `dovecot23-fts-*` packages when replication or delayed migration is required.

### Handle transition-specific package conflicts

- Overwrite stale Waydroid `.pyc` files below `/usr/lib/waydroid/tools/` when upgrading from before `1.5.4-3`.
- Install the required `-9.0` .NET package during the .NET 10 full upgrade, then remove its unversioned counterpart if version 9 must remain.
- Move Pascal, Maxwell, and older NVIDIA GPUs to AUR package `nvidia-580xx-dkms` before NVIDIA 590 replaces the closed modules with open kernel-module packages.
- Let Turing and newer GPUs transition automatically; do not apply the legacy-driver intervention to them.

### Switch iptables backends deliberately

Treat `iptables` as the nft-backed package. Use `iptables-legacy` only for legacy-only behavior, inspect both rules `.pacsave` files when switching packages, restore rules as needed, and test uncommon xtables extensions.

### Re-own Kea runtime state

After upgrading to `kea>=1:3.0.3-6`, assign existing state to the dedicated `kea` account and restart the services:

```sh
chown kea: /var/lib/kea/* /var/log/kea/* /run/lock/kea/logger_lockfile
systemctl try-restart kea-ctrl-agent.service kea-dhcp{4,6,-ddns}.service
```

Add interactive or service accounts to the `kea` group only when they require access to Kea leases, logs, or configuration.

### Rename Varnish installations to Vinyl Cache

Migrate directories, accounts, commands, and systemd units from `varnish` names to `vinyl` names. Disable `varnish.service` and `varnishncsa.service`; enable `vinyl-cache.service` and `vinylncsa.service` after correcting state ownership.

## Deprecations and platform migrations

### Replace Redis with Valkey

Plan to move Arch-managed deployments from `redis` to Valkey. The Redis package was deprecated after its brief April 2025 transition in `[extra]`, moved to the AUR, and stopped receiving Arch updates.

### Move custom Zabbix files to the shared account

Change ownership and embedded account names in custom PSK files, scripts, sudoers rules, and configuration to the shared `zabbix` account introduced by `zabbix-common`. Complete this before deleting the old component-specific accounts.

### Audit AUR changes before every update

During the ongoing malicious-package incident, inspect every change to each AUR package's `PKGBUILD` and install scripts before updating. Report suspicious commits for packages in use through the `aur-general` mailing list.

## Pacman 7.0.0 and 7.1.0 defaults and sandboxing

### Apply privilege-separated downloads

Merge pacman's `.pacnew` so Arch's `DownloadUser` default can take effect. Make each local repository traversable by the `alpm` group:

```sh
chown :alpm -R /path/to/local/repo
find /path/to/local/repo -type d -exec chmod g+x {} +
```

On Linux, expect the downloader to be unable to write outside its download directory. Prefer the fine-grained pacman 7.1.0 sandbox controls when one restriction is incompatible; use `DisableSandbox` or `--disable-sandbox` only when wholesale disablement is necessary.

### Require signatures explicitly

Expect pacman 7.1.0's default `SigLevel` to be `Required` for packages and databases. Configure an intentional exception for unsigned local content; do not rely on the previous permissive default.

## makepkg and PKGBUILD quick reference

### Remove obsolete overrides

- Remove `GITFLAGS`; makepkg no longer supports it.
- Do not override `BUILDENV` or `OPTIONS` from a PKGBUILD.
- Do not use `options=(!buildenv)` to suppress `MAKEFLAGS` or `CHOST`.
- Expect Git operations to use `/etc/makepkg.d/gitconfig` while ignoring system Git configuration.

### Use new packaging controls

- Set makepkg's own parallel-operation limit with `NPROC`; keep build-system parallelism separate.
- Store generic tracked data in `xdata`.
- Set per-architecture options with `options_$arch`.
- Use architecture-specific split packages where appropriate.
- Update Git-source checksums once when the stable, configuration-independent checksum logic changes an existing value, including for repositories using `.gitattributes`.

### Serialize repository maintenance

Use `repo-add --wait-for-lock` when multiple writers may update a repository. Use `repo-add --remove` when the update should also delete old package files.

## Detailed guidance

Load only the reference that matches the task:

- Read [Package management](references/package-management.md) for complete pacman, makepkg, repository, licensing, and firmware details.
- Read [Service migrations](references/service-migrations.md) for service-specific impact, package alternatives, account changes, directories, and unit names.
- Read [Runtime and desktop transitions](references/runtime-and-desktop-transitions.md) before upgrading affected graphical applications or language runtimes.
- Read [Operations and security](references/operations-and-security.md) during Arch infrastructure outages or before any AUR update.
