---
name: debian-knowledge-patch
description: Debian changes since training cutoff (latest: 13) — systemd run0, apt deb822 format, /tmp tmpfs default, wtmpdb/lastlog2, OpenSSH DSA removal, curl HTTP/3. Load before working with Debian.
license: MIT
metadata:
  author: Nevaberry
  version: "13"
---

# Debian Knowledge Patch

Claude's baseline knowledge covers Debian 12 (Bookworm). This skill provides changes in Debian 13 "Trixie" (August 2025).

## Breaking Changes Quick Reference

| Change | Impact | Details |
|--------|--------|---------|
| /tmp is tmpfs | Large temp files may exhaust RAM | [system-changes](references/system-changes.md) |
| last/lastb/lastlog removed | Use wtmpdb, lastlog2, lslogins | [system-changes](references/system-changes.md) |
| OpenSSH DSA keys removed | No workaround; use Ed25519 | [system-changes](references/system-changes.md) |
| ~/.pam_environment ignored | Set vars in shell init files | [system-changes](references/system-changes.md) |
| systemd-cryptsetup split | Install before reboot if encrypted | [system-changes](references/system-changes.md) |
| dm-crypt defaults changed | Record cipher/hash in crypttab | [system-changes](references/system-changes.md) |
| RabbitMQ HA queues removed | Switch to quorum queues; no direct upgrade | [server-changes](references/server-changes.md) |
| MariaDB 10.11 -> 11.8 | Clean shutdown required before upgrade | [server-changes](references/server-changes.md) |
| i386 legacy-only | No kernel/installer; do NOT upgrade | [architecture-changes](references/architecture-changes.md) |

## New Features

### systemd run0

Privilege escalation tool that replaces `sudo`. Checks for "sudo" group membership, asks for user's password (not root's).

### apt modernize-sources

```bash
apt modernize-sources  # convert old SourcesList format to deb822
```

### curl HTTP/3 and wcurl

```bash
curl --http3 https://example.com # HTTP/3 support
curl --http3-only https://example.com
wcurl https://example.com/file.tar.gz # simple wget alternative
```

## System Changes

### /tmp as tmpfs

Default: up to 50% of RAM. Customize:

```bash
systemctl edit tmp.mount
# Add: Options=mode=1777,nosuid,nodev,size=2G
```

Revert: `systemctl mask tmp.mount && reboot`

### Login Tracking Replacements

| Old Command | Replacement | Packages Needed |
|-------------|-------------|-----------------|
| `last` | `wtmpdb` | wtmpdb, libpam-wtmpdb |
| `lastlog` | `lastlog2` | lastlog2, libpam-lastlog2 |
| `lastb` | `lslogins --failed` | util-linux (included) |

Also new: `lslogins` for account last-used info. `exch` and `waitpid` added to util-linux-extra. `mesg` and `write` removed.

### OpenSSH Changes

- **DSA keys completely removed** (OpenSSH 9.8p1). Use `openssh-client-ssh1` for legacy devices.
- **~/.pam_environment no longer read**. Move variables to `~/.bash_profile` or `~/.bashrc`.

### Encrypted Filesystem Changes

- Install `systemd-cryptsetup` before rebooting (split from systemd).
- Plain-mode dm-crypt new defaults: `cipher=aes-xts-plain64`, `hash=sha256`. For old devices, add `cipher=aes-cbc-essiv:sha256,size=256,hash=ripemd160` to `/etc/crypttab`.
- LUKS devices unaffected (settings stored on device).

### /usr Merge Complete

`usrmerge` and `usr-is-merged` are now removable dummy packages.

See [references/system-changes.md](references/system-changes.md) for full details.

## Server Changes

### RabbitMQ

HA queues removed. Must switch to quorum queues. No direct upgrade from bookworm -- wipe `/var/lib/rabbitmq/mnesia` and restart.

### MariaDB 10.11 -> 11.8

Ensure clean shutdown before upgrade. Crash recovery across major versions not supported:

```bash
systemctl stop mariadb  # ensure clean shutdown before upgrading
```

See [references/server-changes.md](references/server-changes.md) for full details.

## Architecture Changes

- **i386**: Legacy-only (multiarch/chroot on amd64). No kernel, no installer. Do NOT upgrade i386 systems.
- **riscv64**: First official Debian support for 64-bit RISC-V.
- **armel**: Last supported release. Migrate to armhf or arm64.
- **mipsel/mips64el**: Removed entirely.
- **/boot**: Needs at least 768 MB with ~300 MB free for upgrade.

See [references/architecture-changes.md](references/architecture-changes.md) for details.

## Desktop

### Plasma 6 (First in Debian)

- Plasma 6.3.6 (replaces 5.27.5)
- Qt 6.8.2 (from 6.4.2)
- KDE Frameworks 6.13
- Qt 5.15.15 and KF5 5.116 for compatibility (deprecated, removal in forky)
- GNOME 48

### 64-bit time_t Transition

All architectures except i386 use 64-bit `time_t` (Y2038-safe). On 32-bit arches (armel, armhf), library ABIs changed without soname changes. Third-party software needs recompilation.

## Key Package Versions

| Package | Bookworm (12) | Trixie (13) |
|---------|--------------|-------------|
| Kernel | 6.1 | 6.12 |
| Python | 3.11 | 3.13 |
| GCC | 12.2 | 14.2 |
| OpenSSH | 9.2p1 | 10.0p1 |
| OpenSSL | 3.0 | 3.5 |
| systemd | 252 | 257 |
| PostgreSQL | 15 | 17 |
| MariaDB | 10.11 | 11.8 |
| PHP | 8.2 | 8.4 |
| Perl | 5.36 | 5.40 |
| Rustc | 1.63 | 1.85 |
| LLVM | 14 default | 19 default |
| Samba | 4.17 | 4.22 |
| GIMP | 2.10 | 3.0 |
| curl | 7.88 | 8.14 |
| LibreOffice | 7.x | 25 |
| GNOME | 43 | 48 |
| Emacs | 28.2 | 30.1 |

## Reference Files

| File | Contents |
|------|----------|
| [system-changes.md](references/system-changes.md) | tmpfs /tmp, login tracking, OpenSSH, encryption, systemd changes |
| [server-changes.md](references/server-changes.md) | RabbitMQ, MariaDB, package version details |
| [architecture-changes.md](references/architecture-changes.md) | i386, riscv64, armel, mips removal, /boot sizing |
