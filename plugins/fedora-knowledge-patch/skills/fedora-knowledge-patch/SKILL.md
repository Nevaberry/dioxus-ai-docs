---
name: fedora-knowledge-patch
description: Fedora Linux changes since training cutoff (latest: 44) — DNF5 replaces DNF4, /usr/sbin merged, ifcfg removed, Redis→Valkey, SHA-1 distrusted, cert.pem dropped, RPM 6.0, Podman 6, CMake 4.0, lastlog2, nftables default. Load before writing Fedora scripts, Dockerfiles, or system automation.
license: MIT
metadata:
  author: Nevaberry
  version: "44"
---

# Fedora Linux Knowledge Patch

Claude's baseline knowledge covers Fedora Linux through Fedora 40. This skill provides breaking changes from Fedora 41–44 (2024-10 through 2026-04) that affect scripts, automation, Dockerfiles, and system administration.

## Breaking Changes Quick Reference

| Version | Change | Impact | Details |
|---------|--------|--------|---------|
| F41+ | DNF5 replaces DNF4 | Commands renamed/restructured; config paths changed | [dnf5](references/dnf5.md) |
| F41 | Redis → Valkey | Package/binary/service names changed | [package-changes](references/package-changes.md) |
| F41 | NetworkManager drops ifcfg | `/etc/sysconfig/network-scripts/` removed | [system-changes](references/system-changes.md) |
| F41 | OpenSSL distrusts SHA-1 | TLS to SHA-1 cert servers fails | [crypto-changes](references/crypto-changes.md) |
| F41 | OpenSSL ENGINE API deprecated | Must use provider API instead | [crypto-changes](references/crypto-changes.md) |
| F41 | Python 2.7 removed | `python2`/`python2.7` packages gone | [package-changes](references/package-changes.md) |
| F41 | nftables default for Podman/libvirt | iptables rules don't show container/VM rules | [system-changes](references/system-changes.md) |
| F42 | `/usr/sbin` → `/usr/bin` | Sbin removed from `$PATH`; all binaries in `/usr/bin` | [system-changes](references/system-changes.md) |
| F42 | `fips-mode-setup` removed | Use `fips=1` kernel arg instead | [crypto-changes](references/crypto-changes.md) |
| F42 | `setup.py install` removed | Use `pip install .` or pyproject.toml builds | [package-changes](references/package-changes.md) |
| F42 | Anaconda WebUI + VNC→RDP | `inst.vnc` replaced by `inst.rdp` | [system-changes](references/system-changes.md) |
| F43 | RPM 6.0 | Enforced signatures, v6 format, new signing config | [package-changes](references/package-changes.md) |
| F43 | lastlog → lastlog2 | `/var/log/lastlog` gone, sqlite-based replacement | [system-changes](references/system-changes.md) |
| F43 | Wayland-only GNOME | X11 session packages removed | [system-changes](references/system-changes.md) |
| F44 | CA cert.pem files dropped | Hardcoded CA bundle paths break | [crypto-changes](references/crypto-changes.md) |
| F44 | CMake 4.0 | `cmake_minimum_required` < 3.5 fails | [package-changes](references/package-changes.md) |
| F44 | Podman 6 | BoltDB removed, nftables only, config rework | [package-changes](references/package-changes.md) |

## DNF5 Quick Reference (Fedora 41+)

`dnf` is now DNF5 (C++ rewrite). Scripts using DNF4 syntax will break.

**Most common command changes:**

| DNF4 | DNF5 |
|------|------|
| `dnf history <id>` | `dnf history info <id>` |
| `dnf updateinfo` | `dnf advisory summary` |
| `dnf groupinstall <grp>` | `dnf group install <grp>` |
| `dnf config-manager --add-repo URL` | `dnf config-manager addrepo --from-repofile=URL` |
| `dnf config-manager --save --setopt=..` | `dnf config-manager setopt key=value` |
| `dnf shell` | `dnf do install pkg1 remove pkg2` |
| `dnf mark install pkg` | `dnf mark user pkg` |
| `dnf mark remove pkg` | `dnf mark dependency pkg` |
| `dnf download --source pkg` | `dnf download --srpm pkg` |
| `dnf rq --resolve --requires pkg` | `dnf rq --providers-of=requires pkg` |

**Dropped options:** `-4`/`-6` (use `ip_resolve` config), `--verbose`, `--downloaddir` (use `--destdir`), `--skip-broken` on upgrade (use `--no-best`).

**Config changes:** Cache dir is `/var/cache/libdnf5` (root) / `~/.cache/libdnf5` (user). `best=true` by default. Timer: `dnf5-makecache.timer`. Auto-updates: `dnf5-automatic.timer`. `strict` option split into `skip_broken` and `skip_unavailable`.

See [references/dnf5.md](references/dnf5.md) for full details.

## Redis → Valkey (Fedora 41+)

Redis removed due to license change (BSD → RSALv2/SSPL). Valkey 7.2 is the wire-compatible BSD-licensed replacement.

```bash
# Migration on existing systems:
dnf install valkey-compat-redis --allowerasing

# Fresh install:
dnf install valkey
```

| Redis (old) | Valkey (new) |
|-------------|-------------|
| `redis-server` / `redis-cli` | `valkey-server` / `valkey-cli` |
| `systemctl start redis` | `systemctl start valkey` |
| `/etc/redis/redis.conf` | `/etc/valkey/valkey.conf` |
| `/var/lib/redis/` | `/var/lib/valkey/` |

Data files (RDB/AOF) are compatible. Port 6379 unchanged. The `valkey-compat` package provides `redis.service` → `valkey.service` systemd alias.

**Caution:** Check `shutdown-on-sigterm` setting — if set to `nosave` or `force`, data may be lost during migration restart.

## Crypto & TLS Changes Summary

- **F41**: OpenSSL distrusts SHA-1. Revert: `update-crypto-policies --set FEDORA40`. Per-process: `runcp FEDORA40 <command>`.
- **F41**: ENGINE API disabled. Use `pkcs11-provider` instead of `engine_pkcs11`.
- **F42**: `fips-mode-setup` removed. Enable FIPS at install with `fips=1` kernel arg. Post-install workaround: `grubby --update-kernel=ALL --args="fips=1"`.
- **F44**: `/etc/pki/tls/cert.pem` and CA bundle files removed. Use `/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem` instead.

See [references/crypto-changes.md](references/crypto-changes.md) for full details.

## nftables Default (Fedora 41)

Both Podman/Netavark and libvirt switch to nftables. `iptables -L` shows nothing for container/VM rules.

```bash
nft list ruleset   # see all firewall rules including containers/VMs
```

**Docker incompatibility:** Docker sets iptables FORWARD policy to DENY, which blocks nftables rules in libvirt's separate table. Workaround:

```ini
# /etc/libvirt/network.conf
firewall_backend = "iptables"
```

Then: `systemctl restart virtnetworkd`

## Anaconda Installer Changes (Fedora 42+)

- **F42**: New **WebUI installer** (PatternFly-based wizard) replaces GTK for Workstation. Guided partitioning with dual-boot support.
- **F42**: **VNC removed** from installer. Use RDP: `inst.rdp` and `inst.rdp.password=<pass>` boot options.
- **F43**: WebUI becomes default for all Spins and KDE edition.

## Other Breaking Changes

- **F41**: **Python 2.7** fully removed. `dnf install python2` fails.
- **F42**: **`/usr/sbin`** → symlink to `/usr/bin`. `/usr/sbin` removed from `$PATH`. Use `/usr/bin/` in new scripts.
- **F42**: **Setuptools 74+** removes `setup.py install`. Use `pip install .`.
- **F43**: **RPM 6.0**. Defaults to enforced signature checking and v6 format. Signing: use `%_openpgp_sign_id` (not custom `%__gpg_sign_cmd`). v3 packages can no longer be installed. MD5/SHA1 digests disabled. Control format: `%_rpmformat 4` to keep v4.
- **F43**: **lastlog → lastlog2** (sqlite-based, from util-linux). Automatic migration on upgrade.
- **F43**: **Wayland-only GNOME**. `gnome-session-xsession` and `gnome-classic-session-xsession` removed. XWayland still available for X11 apps.
- **F44**: **CMake 4.0**. `cmake_minimum_required` < 3.5 fails. Quick fix: `-DCMAKE_POLICY_VERSION_MINIMUM=3.5`. The `%cmake` RPM macro now uses ninja instead of make.
- **F44**: **Podman 6**. Removes BoltDB backend (must upgrade to Podman 5.8 first and reboot for SQLite migration), slirp4netns, cgroups v1. Netavark nftables-only. Config split into client/server files.

## Software Versions (Fedora 44)

Python 3.14, Ruby 4.0, Node.js 24, Go 1.26, GCC 16.1, glibc 2.43, LLVM 22, Rust 1.86, MariaDB 11.8, PostgreSQL 18, Valkey 8.1, Ansible 13 (core 2.20), CMake 4.0, RPM 6.0, Podman 6, Helm 4, kernel 6.19, GNOME 50, KDE Plasma 6.6.

## Reference Files

| File | Contents |
|------|----------|
| [dnf5.md](references/dnf5.md) | DNF5 command migration, config changes, dropped options |
| [system-changes.md](references/system-changes.md) | sbin/bin merge, NetworkManager, nftables, lastlog2, Anaconda, Wayland |
| [crypto-changes.md](references/crypto-changes.md) | SHA-1 distrust, ENGINE API removal, FIPS, CA cert paths |
| [package-changes.md](references/package-changes.md) | Redis→Valkey, Python 2 removal, setuptools, RPM 6.0, CMake 4.0, Podman 6 |
