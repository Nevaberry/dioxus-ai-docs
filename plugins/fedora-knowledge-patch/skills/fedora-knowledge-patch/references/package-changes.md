# Fedora Package & Tool Changes

## Redis → Valkey (Fedora 41)

Redis removed due to license change from BSD-3 to RSALv2/SSPLv1. **Valkey 7.2** is the wire-compatible, BSD-licensed fork maintained by the Linux Foundation.

### Migration

```bash
# Existing Redis installation — use compat package for seamless transition:
dnf install valkey-compat-redis --allowerasing

# Fresh install:
dnf install valkey
```

The `valkey-compat` sub-package provides `Obsoletes: redis` and systemd aliases (`redis.service` → `valkey.service`).

### Path Changes

| Redis (old) | Valkey (new) |
|-------------|-------------|
| `redis-server` / `redis-cli` | `valkey-server` / `valkey-cli` |
| `systemctl start redis` | `systemctl start valkey` |
| `/etc/redis/redis.conf` | `/etc/valkey/valkey.conf` |
| `/var/lib/redis/` | `/var/lib/valkey/` |
| Port 6379 | Port 6379 (unchanged) |

Data files (RDB/AOF) are compatible. RESP protocol is identical.

**Caution:** Check `shutdown-on-sigterm` setting in your config. If set to `nosave` or `force`, unsaved data may be lost during the migration restart.

## Python 2.7 Fully Removed (Fedora 41)

The `python2.7` package is removed. `dnf install python2` fails. Only PyPy2 remains as an optional package.

- `/usr/bin/python2` no longer exists
- Build scripts referencing `python2` will fail
- No `python2-*` library packages available

## Setuptools Removes setup.py install (Fedora 42)

Setuptools 74+ removes the `setup.py install` command (deprecated since 2019).

```bash
# Old (breaks on F42+)
python setup.py install

# New
pip install .                    # for local installs
pip install -e .                 # for editable/development
python -m build && pip install dist/*.whl  # for wheel builds
```

The `%py3_build` and `%py3_install` RPM macros that use `setup.py` are deprecated in F43.

## RPM 6.0 (Fedora 43)

Major RPM version bump with significant breaking changes for package builders.

### Key Changes

- **Enforced signature checking** by default. Unsigned packages may be rejected.
- **v6 package format** is the new default for building. To keep v4: `%_rpmformat 4` in rpmmacros.
- **v3 packages** can no longer be installed (very old format).
- **MD5 and SHA1 digests** disabled by default in verification.
- **C++ rewrite** — adds `libstdc++` as a dependency.

### Signing Changes

```rpm
# Old signing config (custom gpg command — deprecated)
%__gpg_sign_cmd  %{__gpg} gpg --batch ...

# New signing config
%_openpgp_sign_id  FINGERPRINT_HERE
```

Use `%_openpgp_sign_id` with the full key fingerprint. `rpmkeys` is the official keyring management tool.

### Key Management

Keys are now referenced by **full fingerprint** (not short keyid). `rpmkeys --import` and `rpmkeys --list` are the canonical commands.

## CMake 4.0 (Fedora 44)

**Breaking:** Projects with `cmake_minimum_required(VERSION X)` where X < 3.5 will fail:

```
CMake Error: Compatibility with CMake < 3.5 has been removed from CMake 4.0.
```

**Fixes:**

```cmake
# Update minimum version (preferred)
cmake_minimum_required(VERSION 3.12...4.0)

# Quick unblock (for third-party code you can't modify)
cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5 ...
```

**Fedora RPM macro change:** The `%cmake` macro now uses the **ninja** generator instead of make. Build scripts that assume `make` output or use `make -j$(nproc)` after `%cmake` will break. Use `%cmake_build` and `%cmake_install` macros instead.

## Podman 6 (Fedora 44/45)

Major Podman version with multiple breaking removals.

### Migration Prerequisite

**Must upgrade to Podman 5.8+ and reboot before upgrading to Podman 6.** This triggers the BoltDB → SQLite database migration. Jumping directly from older Podman to 6 will lose container state.

### Breaking Changes

- **BoltDB backend removed** — SQLite is the only option
- **slirp4netns removed** — pasta is the only rootless network backend
- **cgroups v1 removed** — cgroups v2 only
- **Netavark drops iptables** — nftables only for container networking
- **Config file rework** — split into client config and server (containers.conf) config

### Compatibility

```bash
# Check current database backend before upgrading
podman info --format '{{.Host.DatabaseBackend}}'
# Must show "sqlite" before upgrading to Podman 6
```
