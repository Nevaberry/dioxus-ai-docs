# Platform, Architecture, and Installation

Use this reference when selecting an AlmaLinux release or architecture, building
installation media, planning storage, or checking hardware and lifecycle
constraints.

## Release and kernel matrix

| Coverage batch | Release facts |
| --- | --- |
| `9.4` (2024-05-06) | AlmaLinux 9.4 supports `x86_64`, `aarch64`, `ppc64le`, and `s390x` and initially distributed kernel `5.14.0-427.13.1.el9_4`. |
| `9.5` (2024-11-18) | AlmaLinux 9.5 distributed kernel `5.14.0-503.11.1.el9_5`. |
| `9.6` (2025-05-20) | AlmaLinux 9.6 distributed kernel `5.14.0-570.12.1.el9_6`. |
| `9.7` (2025-11-17) | AlmaLinux 9.7 distributed kernel `5.14.0-611.5.1.el9_7`. |
| `9.8-10.2-ga` (2026-05-26) | AlmaLinux 9.8 ships kernel `5.14.0-687.5.3.el9_8`; AlmaLinux 10.2 ships kernel `6.12.0-211.7.3.el10_2`. |
| `10.0` (2025-05-27) | AlmaLinux 10.0 supports `x86_64`, `x86_64_v2`, `aarch64`, `ppc64le`, and `s390x` and initially distributed kernel `6.12.0-55.9.1.el10_0`. |
| `10.1` (2025-11-24) | AlmaLinux 10.1 distributed kernel `6.12.0-124.8.1.el10_1`. |

The `release-catalog` also records two adjacent baselines:

- AlmaLinux 8.10 was released on 2024-05-28 with kernel `4.18.0-553`
  for `x86_64`, `aarch64`, `ppc64le`, and `s390x`, plus userspace-only
  `i686`.
- AlmaLinux OS Kitten 10 was released on 2024-10-22 with kernel
  `6.11.0-25` for `x86_64`, `x86_64_v2`, `aarch64`, `ppc64le`, and
  `s390x`, plus userspace-only `i686`. Its active-support lifetime ends
  with CentOS Stream 10.

## x86 compatibility and 32-bit userspace

### AlmaLinux 10 CPU baseline

The normal AlmaLinux 10 `x86_64` build targets the x86-64-v3 CPU baseline.
AlmaLinux additionally publishes an `x86_64_v2` build for older CPUs
(`10.0`). Packages from RHEL 10 third parties target v3, so use the v2 build
only when the default OS package set is sufficient or when extra packages can
be rebuilt. Rebuilding EPEL 10 for v2 was separately approved.

### i686 removal and restoration

AlmaLinux 10.0 published no i686 package set (`10.0`). AlmaLinux 10.2 restores
i686 userspace packages for legacy applications, CI, and containers
(`9.8-10.2-ga`), with these constraints (`10.2`):

- There is no bootable i686 installer and no 32-bit kernel.
- Packages are published at `vault.almalinux.org`.
- Official Docker images use the `linux/386` platform selection.
- The i686 architecture stream is maintained through 2035.

## Installer, repositories, and storage

### AlmaLinux 10 media and signing key

AlmaLinux 10.0 media use
`AlmaLinux-10.0-$arch-{boot,minimal,dvd}.iso` (`10.0`). Only the boot image
needs a network package source. If mirror discovery fails, point the installer
at a selected mirror's `10.0/BaseOS/$arch/kickstart/` repository. Minimal and
DVD media need no additional installation source.

AlmaLinux 10 uses `RPM-GPG-KEY-AlmaLinux-10`, fingerprint
`EE6D B7B9 8F5B F5ED D9DA 0DE5 DEE5 C11C C2A1 E572`:

~~~console
wget https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux-10
gpg --import RPM-GPG-KEY-AlmaLinux-10
gpg --verify CHECKSUM
sha256sum AlmaLinux-10.0-$(uname -m)-boot.iso
~~~

### Repository and filesystem defaults

- New AlmaLinux 10.1 installations enable CRB by default (`10.1`).
- AlmaLinux 10.1 enables Btrfs in the kernel and userspace, and its installer
  can create a system that boots from Btrfs (`10.1`). Initial support covers
  installation and the storage-management stack; broad support throughout the
  software collection was still forthcoming.
- On x86_64, AlmaLinux 9.8 shim 16.1 binaries are dual-signed with the
  Microsoft 2011 and 2023 UEFI Secure Boot certificates for the certificate
  transition (`9.8`).

## Legacy hardware support

AlmaLinux 9.4 re-enables upstream-disabled PCI IDs for older storage, Fibre
Channel, iSCSI, and network hardware through these drivers (`9.4`):

`aacraid`, `be2iscsi`, `be2net`, `hpsa`, `lpfc`, `megaraid_sas`,
`mlx4_core`, `mpt3sas`, `mptsas`, `qla2xxx`, and `qla4xxx`.

The affected families include older Dell PERC, Adaptec, HP and IBM RAID
devices; LSI SAS; QLogic and Emulex adapters; and Mellanox
Gen2/ConnectX-2. Listed `be2net` devices require kernel
`5.14.0-427.18.1.el9_4` or newer, not the initially distributed
`5.14.0-427.13.1.el9_4` kernel.

AlmaLinux 10.2 likewise re-enables older storage and networking drivers for
Adaptec, Dell PERC, HP, Mellanox, QLogic, Emulex, LSI, and Broadcom hardware
(`9.8-10.2-ga`).

## Lifecycle rules

The `release-catalog` records:

| Major | Active support through | Security support through |
| --- | --- | --- |
| AlmaLinux 10 | 2030-05-31 | 2035-05-31 |
| AlmaLinux 9 | 2027-05-31 | 2032-05-31 |
| AlmaLinux 8 | 2024-05-31 | 2029-05-31 |

Within a major line, each minor release reaches end of life when the next minor
release ships. Do not infer continued minor-release support from the major
version's lifecycle.
