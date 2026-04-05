# System Defaults & Configuration

## Default Configs Moved to /usr

In SUSE 16, default configuration files live in `/usr`; `/etc` is reserved for admin overrides only.

### How It Works

1. System defaults are shipped in `/usr/etc/`, `/usr/lib/systemd/`, etc.
2. To customize, copy or create the file in the corresponding `/etc/` location
3. To restore a default, simply remove the `/etc` override file

```bash
# Customize systemd service settings (drop-in snippet)
mkdir -p /etc/systemd/system/myservice.service.d/
cat >/etc/systemd/system/myservice.service.d/override.conf <<EOF
[Service]
LimitNOFILE=65536
EOF
systemctl daemon-reload

# Restore default: remove the override
rm /etc/systemd/system/myservice.service.d/override.conf
systemctl daemon-reload

# For systemd global settings, create drop-ins in:
# /etc/systemd/system.conf.d/
# /etc/systemd/journald.conf.d/
# /etc/systemd/logind.conf.d/
```

## sudo: Wheel Group and Auth Changes

The first user created by the installer is added to the `wheel` group. The `sudo-policy-wheel-auth-self` package (installed by default) changes sudo behavior:

- Users in `wheel` group: prompted for **their own** password (not root's)
- Users NOT in `wheel`: prompted for root password

This replaces the SLE 15 behavior where `sudo` always prompted for the target user's password.

## /etc/hostname No Longer Strips FQDN

Previously, if a FQDN was stored in `/etc/hostname`, the domain part was silently stripped. In SUSE 16, the name is applied as-is. Storing a FQDN in `/etc/hostname` is discouraged (non-RFC-compliant); use DNS or `/etc/hosts` for FQDN resolution.

## No Zypper Modules or Split Repos

The module system (basesystem, server-apps, development, etc.) is gone. No separate `pool`/`update` channels. Minor releases (16.1, 16.2) get separate repositories. This simplifies `zypper` operations and improves update performance.

## /tmp Is Now tmpfs

`/tmp` is RAM-backed (tmpfs), no longer persistent across reboots.

**Impact**: Applications that write persistent data to `/tmp` will lose it on reboot.

**Migration**: Use `/var/cache`, `/var/tmp`, or application-specific directories for persistent temporary data. `/var/tmp` is still persistent.

## Cgroup v2 Only

Only cgroups v2 is supported. Cgroups v1 is no longer available.

**Impact**: Tools or scripts that reference `/sys/fs/cgroup/cpu/`, `/sys/fs/cgroup/memory/`, etc. (v1 hierarchy) will break.

```bash
# v1 paths (broken on SUSE 16):
/sys/fs/cgroup/cpu/
/sys/fs/cgroup/memory/

# v2 unified hierarchy:
/sys/fs/cgroup/
```

Container runtimes (`runc`, Podman, etc.) already support cgroup v2. Older container tooling may need updates.

## Per-User Primary Groups

`USERGROUPS_ENAB` is enabled in `/etc/login.defs`: each new user gets their own primary group (matching their username) instead of the shared `users` group.

**Impact**: Scripts or sudoers rules referencing the `users` group (e.g., `%users ALL=(ALL) ALL` or `@users`) may no longer match expected users.

```bash
# Old behavior (SUSE 15): useradd creates user in group "users" (GID 100)
# New behavior (SUSE 16): useradd creates user with their own group

# Check a user's groups
id username
```

## mountfd API in util-linux

`mount` now uses the new kernel mountfd API. This changes behavior for read-only mounts:

```bash
# If the first mount is read-only and you need the physical layer read-write:
mount -oro=vfs /dev/sda1 /mnt # Correct: VFS-level read-only
mount -oro /dev/sda1 /mnt     # Changed behavior with mountfd
```

## Python 3.13

`/usr/bin/python3` points to Python 3.13. Future minor SUSE 16 releases may bump this version.

## Kernel Module Compilation

The SUSE 16 kernel is built with gcc 13, not the system default compiler. To build kernel modules:

```bash
# Install gcc 13
zypper install gcc13

# Build kernel module with correct compiler
make CC=gcc-13
```

## QEMU CPU Requirement

SUSE 16 requires x86-64-v2 minimum. Running in QEMU requires a v2-capable CPU:

```bash
# Use host CPU passthrough
qemu-system-x86_64 -cpu host ...

# Or specify a v2-capable model (e.g., Nehalem or newer)
qemu-system-x86_64 -cpu Nehalem ...

# Using just "-cpu qemu64" may cause kernel crashes
```
