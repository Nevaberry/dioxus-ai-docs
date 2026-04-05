---
name: arch-knowledge-patch
description: Arch Linux changes since training cutoff (latest: 2025.12) — pacman 7.0 alpm user, Valkey replacing Redis, Plasma 6.4 Wayland-only, NVIDIA 590 open modules, Dovecot 2.4, linux-firmware split. Load before working with Arch Linux.
license: MIT
metadata:
  author: Nevaberry
  version: "2025.12"
---

# Arch Linux Knowledge Patch

Claude's baseline knowledge covers Arch Linux through mid-2024, pacman 6.x. This skill provides breaking changes and major package transitions from late 2024 onwards.

## Breaking Changes Quick Reference

| Date | Change | Impact | Details |
|------|--------|--------|---------|
| 2024-09 | pacman 7.0 — `alpm` user | Downloads run unprivileged; local repos need `chown :alpm` | [pacman-7](references/pacman-7.md) |
| 2025-04 | Redis → Valkey | `redis` removed from [extra]; use `valkey-cli`, `valkey.service` | [server-packages](references/server-packages.md) |
| 2025-06 | Wine WoW64 build | Multilib no longer needed; existing 32-bit prefixes must be recreated | [desktop-graphics](references/desktop-graphics.md) |
| 2025-06 | Plasma 6.4 Wayland-only | X11 session removed by default; install `plasma-x11-session` first | [desktop-graphics](references/desktop-graphics.md) |
| 2025-06 | linux-firmware split | Vendor packages; NVIDIA symlink conflict requires `pacman -Rdd` workaround | [desktop-graphics](references/desktop-graphics.md) |
| 2025-08 | Zabbix unified user | Per-component users removed; all run as `zabbix` | [server-packages](references/server-packages.md) |
| 2025-10 | Dovecot 2.4 | Configs incompatible with 2.3; service won't start until migrated | [server-packages](references/server-packages.md) |
| 2025-12 | .NET 10.0 default | Unversioned packages jump to 10.0; install `dotnet-sdk-9.0` to keep 9.0 | [server-packages](references/server-packages.md) |
| 2025-12 | NVIDIA 590 open modules | Pascal (GTX 10xx) and older dropped; use `nvidia-580xx-dkms` from AUR | [desktop-graphics](references/desktop-graphics.md) |

## pacman 7.0 (2024-09)

pacman 7.0 introduced privilege-separated downloads via a dedicated `alpm` system user. Packages are no longer downloaded as root.

**Fix local repo access** after upgrading:

```bash
chown :alpm -R /path/to/local/repo
# Ensure +x on directories so alpm user can traverse
```

After upgrading, merge `.pacnew` files (`/etc/pacman.conf`, `/etc/makepkg.conf`) to pick up new defaults.

Git source checksums may change for repos using `.gitattributes` — one-time `PKGBUILD` checksum update may be needed.

See [references/pacman-7.md](references/pacman-7.md) for details.

## Valkey Replacing Redis (2025-04)

Redis was dropped from [extra] due to its license change (BSD-3-Clause to RSALv2/SSPLv1). Valkey is the BSD-licensed, API-compatible drop-in replacement.

| Old | New |
|-----|-----|
| `redis` | `valkey` |
| `redis-cli` | `valkey-cli` |
| `redis-server` | `valkey-server` |
| `redis.service` | `valkey.service` |

```bash
pacman -S valkey
systemctl enable --now valkey.service
```

The old `redis` package is in the AUR only. Update all scripts and configs referencing old names.

## Wine WoW64 Transition (2025-06)

`wine` and `wine-staging` switched to a pure WoW64 build. The multilib repository is no longer needed for Wine.

**Breaking**: Existing 32-bit Wine prefixes must be recreated:

```bash
rm -rf ~/.wine
# Then reinstall your applications
```

Known limitation: 32-bit apps using OpenGL directly may have reduced performance under WoW64 mode.

## Plasma 6.4 — Wayland-Only Default (2025-06)

Plasma 6.4 split `kwin` into `kwin-wayland` and `kwin-x11`. Only Wayland is installed by default. X11 users who don't act will lose their login session.

```bash
# Install BEFORE upgrading to Plasma 6.4:
pacman -S plasma-x11-session
```

## linux-firmware Split (2025-06)

`linux-firmware` was split into vendor packages (`linux-firmware-nvidia`, `linux-firmware-intel`, etc.). The meta-package depends on a default set of these.

**Breaking**: Upgrading from `20250508` or earlier fails due to NVIDIA firmware symlink conflicts:

```bash
pacman -Rdd linux-firmware
pacman -Syu linux-firmware
```

## Zabbix Unified User (2025-08)

Per-component users (`zabbix-server`, `zabbix-proxy`, `zabbix-agent`, `zabbix-web-service`) are removed. All components now run as a single `zabbix` user from `zabbix-common`.

Main configs and systemd units migrate automatically. **Manual fix needed** for custom files:

```bash
chown zabbix:zabbix /etc/zabbix/zabbix_agentd.psk
# Update sudoers: "zabbix-agent ALL=..." → "zabbix ALL=..."
```

After migrating, remove obsolete accounts (`userdel zabbix-server`, etc.).

## Dovecot 2.4 — Breaking Config (2025-10)

Dovecot 2.4 configs are **incompatible** with 2.3. The service will not start until migrated. The replication feature was removed.

See [upstream migration guide](https://doc.dovecot.org/latest/installation/upgrade/2.3-to-2.4.html).

Legacy fallback packages in [extra]:

```bash
pacman -S dovecot23 pigeonhole23
# Also: dovecot23-fts-elastic, dovecot23-fts-xapian
```

## .NET 10.0 Default (2025-12)

Unversioned packages (`dotnet-sdk`, `dotnet-runtime`, `aspnet-runtime`) jumped to .NET 10.0. pacman may fail with dependency errors during upgrade.

Keep 9.0 alongside 10.0:

```bash
pacman -Syu aspnet-runtime-9.0
pacman -Rs aspnet-runtime
# Same pattern for dotnet-sdk-9.0, dotnet-runtime-9.0
```

## NVIDIA 590 — Open Kernel Modules (2025-12)

Package mapping:

| Old | New |
|-----|-----|
| `nvidia` | `nvidia-open` |
| `nvidia-dkms` | `nvidia-open-dkms` |
| `nvidia-lts` | `nvidia-lts-open` |

Turing (RTX 20xx / GTX 1650) and newer transition automatically on upgrade.

**Breaking for Pascal (GTX 10xx) and older** — the 590 driver drops support entirely. Upgrading will break your graphical environment:

```bash
pacman -R nvidia # or nvidia-dkms / nvidia-lts
yay -S nvidia-580xx-dkms
```

## Reference Files

| File | Contents |
|------|----------|
| [pacman-7.md](references/pacman-7.md) | Privilege-separated downloads, `alpm` user, git source checksum changes |
| [desktop-graphics.md](references/desktop-graphics.md) | Plasma 6.4 Wayland-only, linux-firmware split, NVIDIA 590 open modules, Wine WoW64 |
| [server-packages.md](references/server-packages.md) | Valkey (Redis replacement), Zabbix unified user, Dovecot 2.4 migration, .NET 10.0 |
