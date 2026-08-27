# Release and platform

## Architecture support and ABI boundaries

These architecture changes are from `13-whats-new` and `13-known-issues`.

### Treat i386 as legacy-only

Do not upgrade an existing i386 installation to Trixie. Debian retains `i386` for
legacy uses such as chroots and multiarch on amd64, and deliberately keeps its legacy
time ABI.

### Retired and restricted architectures

`mipsel` and `mips64el` are removed. Trixie provides no armel installer and supports
only Raspberry Pi 1, Zero, and Zero W with Debian kernels. It is the last armel
release, although supported installed systems may still upgrade.

### Audit the 64-bit time transition

Every architecture except `i386` now uses a 64-bit `time_t`. On `armel` and `armhf`,
this changes many library ABIs without changing sonames. Rebuild third-party software
for those architectures and test data handling for silent corruption.

## Platform defaults

The platform changes in this section are from `13-whats-new`.

### Temporary filesystems and merged `/usr`

Systemd creates `/tmp` as tmpfs by default. Fresh installations enable automatic
cleanup of `/tmp` and `/var/tmp`; upgraded systems must opt in. Fully merged `/usr` is
assumed, leaving `usrmerge` and `usr-is-merged` as removable dummy packages.

### Core and desktop baselines

The principal platform versions are Linux 6.12, glibc 2.41, GCC 14.2, LLVM/Clang 19,
OpenJDK 21, OpenSSH 10.0p1, OpenSSL 3.5, Perl 5.40, PHP 8.4, PostgreSQL 17, Python
3.13, Rust 1.85, MariaDB 11.8, Samba 4.22, and systemd 257.

Desktop choices include GNOME 48, Plasma 6.3, LXDE 13, LXQt 2.1, and Xfce 4.20.
Use these versions when checking compatibility with third-party modules, packages, or
local build scripts.

## Boot and hardware capabilities

### Firmware HTTP Boot

Debian Installer and Live images can boot directly from a full ISO URL through
firmware HTTP Boot on supported UEFI and U-Boot systems. In TianoCore, configure the
URL under Device Manager → Network Device List → the interface → HTTP Boot
Configuration.

### arm64 hardening

On supported arm64 hardware, Pointer Authentication is applied automatically to
mitigate return-oriented programming, and Branch Target Identification mitigates
call- and jump-oriented attacks.

## Virtualization

The ppc64el constraint below is from `13-known-issues`.

### Match PowerPC page sizes

QEMU requests 64 KiB pages for PowerPC virtual machines, which conflicts with KVM
acceleration on the default kernel. For a guest that supports 4 KiB pages, run:

```bash
kvm -machine pseries,cap-hpt-max-page-size=4096 ...
```

A guest requiring 64 KiB pages needs `linux-image-powerpc64le-64k` on the host.

## Support lifecycle

### Trixie

The lifecycle dates here are from `13.0`. Full Debian support continues through
August 9, 2028, followed by Long Term Support through June 30, 2030. The set of
supported architectures is reduced during the LTS phase.

### Bookworm

The transition here is from `12.15`. Debian 12.15 is Bookworm's final point release,
ending support from the Debian Release, Security, and Backports teams. Supported
architectures move to Debian LTS coverage through June 30, 2028.
