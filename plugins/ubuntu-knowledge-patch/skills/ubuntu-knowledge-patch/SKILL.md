---
name: ubuntu-knowledge-patch
description: Ubuntu changes since training cutoff (latest: 25.10) — sudo-rs, rust-coreutils, APT 3.1, OpenSSH 10.0, OpenSSL 3.5 post-quantum crypto, Chrony NTS, Wayland-only GNOME. Load before working with Ubuntu.
license: MIT
metadata:
  author: Nevaberry
  version: "25.10"
---

# Ubuntu 25.10+ Knowledge Patch

Claude's baseline knowledge covers Ubuntu through 24.04 LTS Noble Numbat. This skill provides changes from 25.10 Questing Quokka (2025-10-09) onwards.

## Breaking Changes Quick Reference

| What Changed | Old | New (25.10+) |
|--------------|-----|--------------|
| sudo | GNU `sudo` | `sudo-rs` (Rust); originals renamed `.ws` |
| Core utilities | GNU coreutils | `rust-coreutils` v0.2.2; GNU as fallback |
| APT solver | Legacy solver | New solver default; `apt why` / `apt why-not` |
| wget on server | Pre-installed | Removed; use `wcurl $URL` instead |
| Time daemon | systemd-timesyncd | Chrony with NTS on port 4460/tcp |
| OpenSSH | 9.x | 10.0 — post-quantum key exchange, DSA removed |
| OpenSSL | 3.x | 3.5 — ML-KEM, ML-DSA, SLH-DSA; QUIC support |
| Valkey/Redis compat | `valkey-redis-compat` | Removed — swap to Valkey before upgrading |
| Desktop session | X.org + Wayland | Wayland-only; X.org session removed |
| Terminal multiplexers | `byobu` in main, `screen` in server seed | `byobu` demoted to universe, `screen` removed |

## sudo-rs Is the Default

`sudo-rs` (Rust rewrite) replaces GNU sudo. Original binaries renamed with `.ws` suffix:

```bash
sudo-rs   # now /usr/bin/sudo
sudo.ws   # original GNU sudo (if installed)
visudo    # now sudo-rs visudo
visudo.ws # original GNU visudo
```

**Breaking**: `sudo-ldap` package removed. Use LDAP authentication via PAM modules instead.

See [references/system-defaults.md](references/system-defaults.md) for migration details.

## rust-coreutils Is the Default

Core utilities now provided by `rust-coreutils` (v0.2.2). GNU coreutils remain as fallback.

**Not yet fully compatible** — if scripts break on edge cases, check the diversions list:

```bash
# See which commands have GNU fallbacks available
dpkg-divert --list | grep coreutils

# Explicitly call GNU version if needed
/usr/bin/gnu-<command>
```

## APT 3.1

New solver is now the default. New diagnostic commands:

```bash
apt why <pkg>           # explain why a package is installed/needed
apt why-not <pkg>       # explain why a package cannot be installed
apt history-list        # query apt history (preview)
apt history-info <id>   # detailed history entry
```

Repo restriction directives in DEB822 sources format:

```
Types: deb
URIs: http://security.ubuntu.com/ubuntu
Suites: questing-security
Components: main
Include: linux-image-*, openssl, openssh-*

Types: deb
URIs: http://ppa.launchpad.net/...
Suites: questing
Components: main
Exclude: python3-core, libc6
```

See [references/system-defaults.md](references/system-defaults.md) for full APT 3.1 details.

## wget Removed from Server

`wget` no longer pre-installed on server images. Use `wcurl` (ships with `curl`):

```bash
wcurl $URL              # drop-in replacement for simple wget downloads
```

For Dockerfiles and provisioning scripts, either install `wget` explicitly or migrate to `wcurl`/`curl`.

## Chrony Replaces systemd-timesyncd

Chrony is the new default time daemon with **NTS (Network Time Security)** enabled by default on port 4460/tcp.

If the network blocks NTS, revert to plain NTP:

```bash
# /etc/chrony/sources.d/ubuntu-ntp-pools.sources
# Remove NTS directives, use standard NTP pool entries:
pool ntp.ubuntu.com iburst
```

Verify NTS status:

```bash
chronyc -n authdata # show NTS authentication status per source
chronyc sources -v  # show time sources with verbose info
```

Ensure port 4460/tcp outbound is open for NTS. Fallback to NTP uses port 123/udp.

## OpenSSH 10.0

Key changes:

- Hybrid post-quantum key agreement enabled by default
- DSA signature algorithm **removed** entirely — migrate to Ed25519 or ECDSA
- Version string: `SSH-2.0-OpenSSH_10.0` — do NOT match on `OpenSSH_1*`

```bash
# Broken pattern (misses 10.0+):
grep 'OpenSSH_[0-9]\.'

# Fixed pattern:
grep 'OpenSSH_[0-9]\+\.'
```

New `sshd_config` features:

```
# Glob patterns in key/principal files
AuthorizedKeysFile /etc/ssh/authorized_keys.d/*.pub

# New Match criteria
Match version SSH-2.0-OpenSSH_10.*
Match sessiontype shell
Match command scp*
```

See [references/security-and-crypto.md](references/security-and-crypto.md) for full details.

## OpenSSL 3.5 — Post-Quantum Cryptography

| Algorithm | Type | Standard | Purpose |
|-----------|------|----------|---------|
| ML-KEM (Kyber) | KEM | FIPS 203 | Key encapsulation / key exchange |
| ML-DSA (Dilithium) | Signature | FIPS 204 | Digital signatures |
| SLH-DSA (SPHINCS+) | Signature | FIPS 205 | Stateless hash-based signatures |

- Default TLS groups include and prefer hybrid PQC KEM groups
- Server-side QUIC support (RFC 9000)
- No configuration needed — PQC is active out of the box

See [references/security-and-crypto.md](references/security-and-crypto.md) for algorithm details.

## Valkey No Longer a Redis Drop-In

Redis updated to 8.0. The `valkey-redis-compat` compatibility package is **removed**.

**Swap from Redis to Valkey before upgrading** to 25.10, or migrate to Redis 8.0 API directly. After the upgrade, the compatibility shim is gone and applications using Redis client libraries will not automatically connect to Valkey.

See [references/package-updates.md](references/package-updates.md) for migration options.

## Wayland-Only Desktop

X.org session removed entirely. GNOME Shell can no longer run as an X.org session. Applications relying on X11-specific features need XWayland (installed by default). Screen sharing, remote desktop, and accessibility tools should be verified for Wayland compatibility.

## Other Notable Changes

| Package | Version | Notes |
|---------|---------|-------|
| Nginx | 1.28 | HTTP/3 and QUIC improvements, SSL cert caching |
| Containerd | 2.1.3 | |
| Docker | 28.2 | |
| Zig | 0.14.1 | First time available in Ubuntu repos |

- `byobu` demoted to universe; `screen` removed from server seed — use `tmux` instead

## Reference Files

| File | Contents |
|------|----------|
| [security-and-crypto.md](references/security-and-crypto.md) | OpenSSH 10.0 config examples, OpenSSL 3.5 PQC algorithms, Chrony NTS verification |
| [system-defaults.md](references/system-defaults.md) | sudo-rs migration, rust-coreutils compatibility, APT 3.1 repo directives, wget removal, Wayland-only desktop |
| [package-updates.md](references/package-updates.md) | Valkey/Redis migration paths, Nginx 1.28, container runtime versions, Zig availability |
