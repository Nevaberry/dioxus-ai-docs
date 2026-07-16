# Release and platform

## Architecture availability (`13-known-issues`)

### i386

Debian retains `i386` only for legacy uses such as chroots and multiarch on `amd64`.
Upgrading an existing i386 system to Trixie is not supported.

### armel and MIPS

Trixie has no armel installer. Debian kernels support only the Raspberry Pi 1, Zero,
and Zero W in this architecture. This is the last armel release, although supported
existing systems can still upgrade.

The `mipsel` and `mips64el` architectures have been removed entirely.

## Time ABI on 32-bit systems (`13-whats-new`)

All architectures except `i386` now use a 64-bit `time_t`. On `armel` and `armhf`, this
changes many library ABIs without changing their sonames. Rebuild third-party software
for those architectures and check it for silent data loss. `i386` deliberately retains
its legacy ABI.

## Temporary filesystems and merged `/usr`

Systemd now creates `/tmp` as a tmpfs by default. Fresh installations also enable
automatic cleanup of `/tmp` and `/var/tmp`; upgraded systems must opt in to that cleanup
regime.

A fully merged `/usr` is assumed. The `usrmerge` and `usr-is-merged` packages are only
removable dummy packages.

## Login and accounting tools

The Y2038-unsafe utmp and wtmp databases are being displaced:

- Replace `lastlog` with the `lastlog2` package.
- Replace `last` with `wtmpd`.
- Use `lslogins` from util-linux where appropriate.
- Account for `util-linux-extra` removing `mesg` and `write`; replace scripts that
  invoke them.
- Note that `util-linux-extra` adds tools including `exch` and `waitpid`.

## arm64 hardening

On supported arm64 hardware, Trixie automatically uses Pointer Authentication to
mitigate return-oriented programming and Branch Target Identification to mitigate
call- and jump-oriented attacks.

## Firmware HTTP Boot

The Debian Installer and Debian Live images can boot directly from a full ISO URL by
using firmware HTTP Boot on supported UEFI and U-Boot systems.

With TianoCore, configure the URL under **Device Manager → Network Device List → the
interface → HTTP Boot Configuration**.

## ppc64el virtual-machine page sizes

QEMU requests 64 KiB pages for PowerPC virtual machines, which conflicts with KVM
acceleration on the default kernel.

For a 4 KiB-capable guest, use:

```bash
kvm -machine pseries,cap-hpt-max-page-size=4096 ...
```

Guests that require 64 KiB pages need `linux-image-powerpc64le-64k` on the host.

## Support lifecycle (`13.0`)

Trixie receives full Debian support through August 9, 2028, followed by Long Term
Support through June 30, 2030. The supported architecture set is reduced during the
Long Term Support phase.
