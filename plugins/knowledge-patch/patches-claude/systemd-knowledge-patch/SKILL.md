---
name: systemd-knowledge-patch
description: systemd
version: "260"
license: MIT
metadata:
  author: Nevaberry
---


# systemd Knowledge Patch

Load this skill before changing units, boot images, service sandboxes, networkd
configuration, image workflows, user sessions, or systemd-facing C and shell code.
Check the installed version and prefer observed behavior when backports differ.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Boot, UKIs, and TPM Policy](references/boot-uki-and-tpm.md) | UKI profiles, firmware, Secure Boot, PCR-lock, NvPCRs, and early boot |
| [Compatibility, Builds, and Administration](references/compatibility-build-and-administration.md) | Removed interfaces, platform requirements, runtime-loaded libraries, configuration search, and OS metadata |
| [Containers and Virtual Machines](references/containers-and-virtual-machines.md) | nspawn, vmspawn, capsules, per-user daemons, SSH transports, and MStacks |
| [Credentials and Enrollment](references/credentials-and-enrollment.md) | User credentials, null-key policy, cryptenroll, FIDO2, storage keys, and certificates |
| [Devices and Administrative Tools](references/devices-and-administration.md) | Udev testing and ACLs, device identity, tmpfiles, sysusers, and factory reset |
| [Homed, Users, and Sessions](references/homed-users-and-sessions.md) | Homed records and areas, PAM classes, pidfd sessions, inhibitors, sleep, and run0 |
| [Images, Storage, and Extensions](references/images-storage-and-extensions.md) | Image transfer, DDIs, repart, integrity, sysext/confext, portable services, and sysupdate |
| [Network Configuration](references/networking.md) | Forwarding, bridge VLANs, DHCP, cellular links, routes, offloads, and networkd Varlink |
| [Resolution, Observability, and IPC](references/resolution-observability-and-ipc.md) | Journal and coredumps, DNS delegation, JSON/Varlink APIs, reports, and event loops |
| [Resource Control and Sandboxing](references/resource-control-and-sandboxing.md) | Cgroup accounting, namespaces, BPF delegation, private filesystems, quotas, and oomd |
| [Units and Activation](references/units-and-activation.md) | Mount dependencies, sockets, timers, transient services, reload, readiness, and gettys |

## Breaking Changes and Required Migrations

### Use cgroup v2 exclusively

- Legacy and hybrid cgroup v1 hierarchies are unsupported.
- Remove boot overrides and build logic intended to retain cgroup v1.
- Expect HugeTLB memory to contribute to cgroup memory accounting on supporting
  kernels.

### Replace SysV and rc.local logic

- Convert SysV scripts and `/etc/rc.local` work into native service, socket,
  timer, path, or target units.
- Compatibility targets do not restore script loading.
- Explicitly enable every getty instance the system needs:

```sh
systemctl enable --now getty@tty1.service
```

### Account for changed defaults

- Journald defaults to persistent storage even when `/var/log/journal` was not
  pre-created.
- TTY and PTY nodes default to `0600`; do not assume group-write access.
- Networkd and nspawn require nftables for NAT.
- Systemd-boot and systemd-stub require TPM 2.0 for TPM integration.
- Automatically dissected XBOOTLDR partitions must use VFAT.
- Main configuration files may come from `/etc`, `/run`, `/usr/local/lib`, or
  `/usr/lib`, in that priority order.
- A drop-in ending in `.ignore` is installed but inactive.

### Repair udev ACL rules

Rules granting `uaccess` must survive `change` events and sort before rule 73:

```udev
ACTION!="remove", SUBSYSTEM=="hidraw", TAG+="uaccess"
```

Test rules without applying their side effects:

```sh
udevadm verify /etc/udev/rules.d/60-example.rules
udevadm test --verbose /sys/class/hidraw/hidraw0
```

### Treat tmpfiles purge as explicit destruction

Purge requires named configuration files and affects only entries marked with
`$`:

```text
d$ /var/lib/example 0755 root root -
```

Always preview the exact invocation first:

```sh
systemd-tmpfiles --dry-run --purge example.conf
systemd-tmpfiles --purge example.conf
```

### Declare runtime-loaded package dependencies

ELF scanners may miss compression, crypto, kmod, PAM, ACL, blkid, seccomp,
SELinux, and libmount integrations loaded at runtime. Declare package feature
dependencies explicitly; missing libkmod can prevent boot.

```sh
systemd-analyze dlopen-metadata /usr/lib/systemd/systemd
```

## Units and Service Sandboxing

### Prefer current namespace modes

```ini
[Service]
PrivateUsers=managed
PrivatePIDs=yes
PrivateTmp=disconnected
ProtectControlGroups=strict
ProtectHostname=private:worker
PrivateBPF=yes
```

- `PrivateUsers=managed` obtains a transient 65,536-ID range from nsresourced.
- `PrivateUsers=identity` maps the first 65,536 IDs; `full` maps the complete
  32-bit range.
- `PrivateTmp=disconnected` creates separate tmpfs mounts for `/tmp` and `/var/tmp`.
- Use `DelegateNamespaces=` and `BPFDelegate*=` only for capabilities the
  workload must own.

### Use current activation and reload controls

```ini
[Service]
ExecReload=/usr/bin/example reload
ExecReloadPost=/usr/libexec/example-reload-finished
RefreshOnReload=yes
MemoryTHP=never

[Socket]
ListenStream=/run/example.sock
PassFileDescriptorsToExec=yes
PassPIDFD=yes
AcceptFileDescriptors=yes
```

- Validate both `LISTEN_PID` and `LISTEN_PIDFDID` where PID identity matters.
- `RefreshOnReload=` governs attached extensions and credentials.
- A leading `|` on `Exec*=` invokes a shell; otherwise shell syntax is not interpreted.

### Avoid timer stampedes

```ini
[Timer]
OnCalendar=hourly
RandomizedOffsetSec=10min
DeferReactivation=yes
```

`RandomizedOffsetSec=` is stable across activations, while
`DeferReactivation=` discards an expiration that occurred while the service
was still active.

## Images, Boot, and TPM

### Use DDI and version-pick workflows

- Put UAPI-versioned alternatives in `.v/` and select them with `systemd-vpick`.
- Use `importctl` for tar, raw, filesystem, extension, portable, nspawn, and VM images.
- Use `root=dissect` or `mount.usr=dissect` for automatic DDI discovery and
  Verity metadata.

### Build and update partition images carefully

- The last duplicate partition definition wins in image mount options.
- `AddValidateFS=` records filesystem-use constraints; an
  `x-systemd.validatefs` mismatch causes an immediate reboot.
- Use `systemd-repart -` to calculate minimum required image size without
  modifying a device.
- Repart can configure dm-integrity and volume-key pinning for encrypted
  images.

### Refresh extensions intentionally

Extension refresh is a no-op when the image set is unchanged. Use
`--always-refresh=yes` to force it and `RefreshOnReload=` to couple it to reload.

### Build multi-profile UKIs

- Use `.profile` sections for normal, debug, and recovery variants.
- Use `.dtbauto`, `.hwids`, and the system hardware-ID catalog for automatic
  DeviceTree selection.
- Keep offline PCR signing and Secure Boot signing as separate prepare, sign,
  and join workflows.
- New TPM enrollments use an empty PCR mask; add managed PCR-lock and signed
  PCR 11 policy when required.
- PCR-lock omits PCR 12 by default because a UKI credential is measured there.

## Networking and Name Resolution

### Replace broad forwarding settings

```ini
[Network]
IPv4Forwarding=yes
IPv6Forwarding=yes
```

`IPForward=` is deprecated. Once `[BridgeVLAN]` has any valid setting, it is
authoritative and undeclared VLAN IDs are removed from the interface.

### Preserve dynamic configuration deliberately

Use `KeepConfiguration=dynamic` or `dynamic-on-stop`; the old DHCP-only names
are obsolete. A networkd restart preserves DHCPv4, DHCPv6, NDISC, and IPv4LL
state regardless. Mutable netdev and traffic-control changes reload in place;
immutable identifiers still require recreation.

### Use DNS delegates for scoped resolution

Files below `/etc/systemd/dns-delegate.d/` define domain-specific servers,
search or routing domains, and an optional `FirewallMark=`.

## Observability, Users, and Privilege

### Query one service invocation

```sh
journalctl --list-invocation -u example.service
journalctl --invocation=ID -u example.service
```

For reliable streaming shutdown, use
`journalctl --follow --synchronize-on-exit=yes`. Programmatic clients can
retrieve entries through the journal Varlink interface.

### Choose PAM session classes explicitly

Lightweight background classes do not start a user manager. Set PAM `class=`
or `XDG_SESSION_CLASS` when a full manager is required; use `class=none` when
no logind session should be created. A pidfd-tied session ends as soon as its
leader exits; the legacy `CreateSession()` descriptor no longer anchors it.

### Treat inhibitors as effective for privileged callers

Ordinary `block` locks affect root and the lock holder. Bypass them explicitly
with `--force` or `--check-inhibitors=no`; use `block-weak` only for the older
weaker semantics.
