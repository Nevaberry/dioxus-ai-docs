# Release and platform

Use this reference to assess architecture eligibility, ABI compatibility,
filesystem behavior, boot methods, virtual-machine constraints, and support
timelines.

## Architecture support

### Treat i386 as legacy-only

The `13-whats-new` guidance retains `i386` only for legacy uses such as chroots
and multiarch on `amd64`. Do not plan an in-place upgrade of an existing i386
installation. Unlike all other architectures, `i386` deliberately keeps the
legacy `time_t` ABI.

### Account for removed and restricted architectures

The `13-known-issues` guidance removes `mipsel` and `mips64el` entirely.
Debian provides no `armel` installer and limits Debian-kernel support to
Raspberry Pi 1, Zero, and Zero W. Supported existing armel systems can still
upgrade, but this is the final armel release.

### Rebuild for the 64-bit time ABI

All architectures except `i386` now use a 64-bit `time_t`. On `armel` and
`armhf`, many library ABIs changed without soname changes. Rebuild third-party
software for these architectures and audit it for silent data corruption;
package names and dynamic-linker success do not prove ABI compatibility.

## Filesystem and accounting defaults

### Distinguish fresh installs from upgrades

Systemd mounts `/tmp` as tmpfs by default. Fresh installations enable automatic
cleanup of `/tmp` and `/var/tmp`; upgraded installations must opt in to that
cleanup policy. Decide deliberately whether existing applications tolerate the
tmpfs capacity and cleanup behavior.

The system assumes a fully merged `/usr`. The `usrmerge` and `usr-is-merged`
packages are removable dummies rather than active migration tools.

### Replace unsafe utmp and wtmp consumers

The Y2038-unsafe utmp/wtmp databases are being displaced. Use:

- `lastlog2` instead of `lastlog`;
- `wtmpd` instead of `last`;
- util-linux `lslogins` for login-account inspection.

`util-linux-extra` removes `mesg` and `write`, while adding tools including
`exch` and `waitpid`. Audit scripts that invoke removed commands and select an
alternative based on the intended behavior.

## Boot and hardware capabilities

### Use firmware HTTP Boot with full ISO URLs

On supported UEFI and U-Boot systems, Debian Installer and Live images can boot
directly from a full ISO URL through firmware HTTP Boot. In TianoCore, configure
the URL through Device Manager, Network Device List, the selected interface,
and HTTP Boot Configuration.

### Expect arm64 control-flow hardening

Supported arm64 hardware automatically uses Pointer Authentication to mitigate
return-oriented programming and Branch Target Identification to mitigate call-
and jump-oriented attacks. Treat this as platform behavior rather than an
application opt-in.

## Virtual machines

### Match ppc64el page sizes

QEMU requests 64 KiB pages for PowerPC virtual machines, which conflicts with
KVM acceleration on the default host kernel.

For a guest that supports 4 KiB pages, cap the requested page size:

```bash
kvm -machine pseries,cap-hpt-max-page-size=4096 ...
```

For a guest that requires 64 KiB pages, install
`linux-image-powerpc64le-64k` on the host. Verify both the guest requirement and
host kernel before enabling acceleration.

## Support lifecycle

### Debian 13

Batch `13.0` states that full Debian support continues through August 9, 2028,
followed by Long Term Support through June 30, 2030. The architecture set is
reduced during the LTS phase, so verify architecture eligibility separately.

### Debian 12

Batch `12.15` is Bookworm's final point release and ends support from the Debian
Release, Security, and Backports teams. Supported architectures move to Debian
LTS coverage through June 30, 2028.
