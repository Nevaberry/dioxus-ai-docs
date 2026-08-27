---
name: systemd-knowledge-patch
description: systemd
version: "260"
license: MIT
metadata:
  author: Nevaberry
---


# systemd Knowledge Patch

Load this skill before changing units, boot images, service sandboxes, networkd configuration, image workflows, user sessions, or systemd-facing C and shell code. Start with the project or host's actual systemd version and use only guidance that applies to it.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Boot, UKIs, and TPM Policy](references/boot-uki-and-tpm.md) | UKI profiles, DeviceTree and firmware selection, Secure Boot, PCR-lock, NvPCRs, early boot |
| [Compatibility, Builds, and Administration](references/compatibility-build-and-administration.md) | Removed interfaces, platform requirements, runtime-loaded libraries, configuration search, OS metadata |
| [Containers and Virtual Machines](references/containers-and-virtual-machines.md) | nspawn, vmspawn, capsules, unprivileged containers, per-user daemons, SSH transports, MStacks |
| [Credentials and Enrollment](references/credentials-and-enrollment.md) | User-bound credentials, null-key policy, cryptenroll, FIDO2, storage keys, certificates |
| [Devices and Administrative Tools](references/devices-and-administration.md) | Udev testing, ACLs, device identity, tmpfiles purge, sysusers, factory reset |
| [Homed, Users, and Sessions](references/homed-users-and-sessions.md) | Homed records and areas, PAM classes, pidfd sessions, inhibitors, sleep, run0 |
| [Images, Storage, and Extensions](references/images-storage-and-extensions.md) | Image transfer and pulls, DDIs, repart, integrity, sysext/confext, sysupdate |
| [Network Configuration](references/networking.md) | Forwarding, bridge VLANs, DHCP, cellular links, routes, offloads, networkd Varlink |
| [Resolution, Observability, and IPC](references/resolution-observability-and-ipc.md) | Journal and coredumps, DNS delegation, JSON/Varlink APIs, transactions, event loops |
| [Resource Control and Sandboxing](references/resource-control-and-sandboxing.md) | Cgroup accounting, namespaces, BPF delegation, private filesystems, quotas, oomd |
| [Units and Activation](references/units-and-activation.md) | Mount dependencies, socket descriptors, timers, transient services, reload, readiness |

## Breaking Changes and Required Migrations

### Use cgroup v2 exclusively

- Remove legacy and hybrid cgroup v1 boot and build configuration.
- Do not depend on `SYSTEMD_CGROUP_ENABLE_LEGACY_FORCE=1`; it was transitional
  and cgroup v1 support was subsequently removed.
- Account for HugeTLB memory in cgroup memory use on supporting kernels.

### Replace SysV and rc.local logic

- Convert SysV scripts and `/etc/rc.local` work into native service, socket, timer, path, or target units.
- Compatibility targets do not restore script loading.
- Explicitly enable each required getty instance:

```sh
systemctl enable --now getty@tty1.service
```

### Account for changed defaults

- Journald uses persistent storage by default even without a pre-created
  `/var/log/journal`.
- TTY and PTY nodes default to mode `0600`; do not assume group-write access.
- Networkd and nspawn require nftables for NAT.
- Systemd-boot and systemd-stub TPM integration requires TPM 2.0.
- Main configuration files may be selected from `/etc`, `/run`, `/usr/local/lib`, or `/usr/lib`, in that order.
- A drop-in ending in `.ignore` remains installed but is inactive.

### Repair udev ACL rules

Rules granting `uaccess` must survive `change` events and sort before rule 73:

```udev
ACTION!="remove", SUBSYSTEM=="hidraw", TAG+="uaccess"
```

Verify and test rules without side effects:

```sh
udevadm verify /etc/udev/rules.d/60-example.rules
udevadm test --verbose /sys/class/hidraw/hidraw0
```

Use exact builtin names; prefix abbreviations are rejected. Do not assign
v258 device ownership to non-system accounts without checking whether the
local release contains the later partial revert.

### Treat tmpfiles purge as explicit destruction

Purge requires named configuration files and affects only entries marked `$`:

```text
d$ /var/lib/example 0755 root root -
```

Preview precisely the same invocation first:

```sh
systemd-tmpfiles --dry-run --purge example.conf
systemd-tmpfiles --purge example.conf
```

### Declare runtime-loaded package dependencies

ELF scanners may not discover compression, crypto, kmod, PAM, ACL, blkid, seccomp, SELinux, or most libmount integrations because they are loaded at runtime. Add explicit feature dependencies; missing libkmod can prevent boot.

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

- `PrivateUsers=managed` obtains a transient 65,536-ID range from nsresourced; `identity` maps the first 65,536 IDs and `full` the complete 32-bit range.
- `PrivateTmp=disconnected` gives `/tmp` and `/var/tmp` separate tmpfs mounts.
- Delegate namespaces and BPF operations only when the workload needs them.

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

- Validate both `LISTEN_PID` and `LISTEN_PIDFDID` when PID identity matters.
- `RefreshOnReload=` governs attached extensions and credentials.
- A leading `|` on an `Exec*=` command invokes a shell; other shell syntax is not interpreted automatically.

### Avoid timer stampedes

```ini
[Timer]
OnCalendar=hourly
RandomizedOffsetSec=10min
DeferReactivation=yes
```

The randomized offset is stable, while deferred reactivation discards an expiration that happened while the service was still active.

## Images, Boot, and TPM

### Use DDI and version-pick workflows

- Put UAPI-versioned alternatives in a directory ending `.v/` and select them
  with `systemd-vpick`.
- Use `importctl` for tar, raw, filesystem, extension, portable-service, nspawn, and vmspawn image transfer.
- Use `root=dissect` or `mount.usr=dissect` for automatic DDI and Verity discovery; automatically dissected XBOOTLDR partitions must be VFAT.

### Build and update partition images carefully

- The last duplicate partition definition wins in image mount options.
- `AddValidateFS=` records filesystem-use constraints; a mismatch requested
  through `x-systemd.validatefs` causes an immediate reboot.
- Use `systemd-repart -` to calculate minimum image size without modifying a
  device.
- Repart can configure dm-integrity and volume-key pinning.

### Refresh extensions intentionally

System and configuration extension refresh is a no-op when the image set did not change. Use `--always-refresh=yes` only for a forced unmount/remount, and use `RefreshOnReload=` when service reload must refresh extensions and credentials too.

### Build multi-profile UKIs

- Use `.profile` sections for normal, debug, and recovery profiles in one UKI.
- Use `.dtbauto`, `.hwids`, and the system hardware-ID catalog for automatic DeviceTree selection.
- Keep offline PCR signing and Secure Boot prepare/sign/join phases distinct.
- New TPM enrollments use an empty PCR mask; add managed PCR-lock and signed
  PCR 11 policy when required.
- PCR-lock excludes PCR 12 by default because a UKI credential is measured
  there itself.

## Networking and Resolution

### Replace broad forwarding settings

```ini
[Network]
IPv4Forwarding=yes
IPv6Forwarding=yes
```

`IPForward=` is deprecated. Once `[BridgeVLAN]` has any valid setting, it is authoritative and undeclared VLAN IDs are removed from the interface.

### Preserve dynamic configuration deliberately

- Use `KeepConfiguration=dynamic` or `dynamic-on-stop`; DHCP-only names are
  obsolete.
- A networkd restart preserves DHCPv4, DHCPv6, NDISC, and IPv4LL state.
- Mutable netdev and traffic-control changes reload in place; immutable identifiers still require interface recreation.
- Treat `DNSOverTLS=yes` as strict certificate verification on affected point
  releases.

### Use scoped resolution and cellular links

DNS delegate files define independent domain-specific servers and routing or search domains, with optional `FirewallMark=`. Networkd can configure cellular links through `[MobileNetwork]`, including APN, authentication, roaming, PIN, operator, route metric, IP family, and gateway behavior.

## Observability, Sessions, and Privilege

### Query one service invocation

```sh
journalctl --list-invocation -u example.service
journalctl --invocation=ID -u example.service
```

Use `--follow --synchronize-on-exit=yes` for reliable streaming shutdown. Programmatic clients can retrieve journal entries over Varlink.

### Prefer public JSON and Varlink APIs

- `sd-json` and `sd-varlink` are public libsystemd APIs.
- Varlink supports descriptor passing, SSH execution, a public socket
  registry, and pluggable transport bridges.
- Manager APIs expose execution settings, unit filters, reload/reexecute, and
  transaction diagnostics.
- Unit counters distinguish kernel `OOMKills` from oomd `ManagedOOMKills`.

### Choose PAM session classes explicitly

Lightweight background classes do not start a user manager. Set PAM `class=` or `XDG_SESSION_CLASS` when a full user manager is required; use `class=none` when no logind session should be created. Logind ends pidfd-tied sessions as soon as their leader exits; the old returned descriptor is not a lifetime anchor.

### Use run0 and inhibitors deliberately

- Interactive `run0` defaults to late PTY attachment.
- `run0 --empower` preserves identity and home while granting capabilities
  and the Polkit `empower` group.
- `run0 --area=` enters a homed area; it changes `$HOME` and
  `$XDG_RUNTIME_DIR` but does not isolate files from the owning UID.
- Ordinary `block` inhibitors affect root and their holder. Bypass explicitly
  with `--force` or `--check-inhibitors=no`; use `block-weak` only when those
  older semantics are intended.
