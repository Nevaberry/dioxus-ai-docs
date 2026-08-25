# Virtualization, Routing, and Hardware Platforms

## Kernel and host capabilities

Linux 6.14 in Ubuntu 25.04 supports hot-swappable `sched_ext` schedulers written
as eBPF programs and adds NTSYNC for Wine and Proton workloads.

On Ubuntu 25.10 arm64, `linux-generic` uses `stubble` for broader UEFI desktop
compatibility. Linux 6.17 adds early kexec and kdump support on Intel TDX hosts.

Ubuntu Livepatch supports Arm systems in Ubuntu 26.04, allowing kernel security
fixes without reboot downtime.

## Libvirt

### Domain capabilities in libvirt 10.6

Ubuntu 24.10 libvirt adds clustered CPU topology, `dynamicMemslots` for
`virtio-mem`, MTP filesystem devices, USB network devices, SSH proxying, pstore
devices, and the `virDomainGraphicsReload` API.

### Packaging, networking, and migration

Ubuntu 25.04 splits libvirt drivers and storage backends into separate binary
packages. `libvirt-daemon-system` is a convenience metapackage for a typical QEMU
host.

An open-forwarded network can omit a host-side bridge IP and select a firewalld
zone. `virsh migrate --migrate-disks-detect-zeroes` can sparsify non-shared
disks. UEFI guests can use internal snapshots when their NVRAM is `qcow2`.

Libvirt accepts versioned QEMU CPU models, automatically enables an EIM-capable
IOMMU above 255 vCPUs, and exposes SEV-SNP. In a nested installation, install
`libvirt-daemon-config-network` before other libvirt components so the
default-network adjustment has a file to modify.

### URI overrides and libvirt 11.6

Ubuntu 25.10 no longer forces `qemu:///system` through
`/etc/profile.d/libvirt-uri.sh`. That URI remains the fallback, but
`LIBVIRT_DEFAULT_URI`, `/etc/libvirt/libvirt.conf`, or
`~/.config/libvirt/libvirt.conf` can override it.

Libvirt 11.6 adds NVMe disks, AMD IOMMU and Intel TDX guests, opt-in guest
shutdown with the host, parallel save and restore, and multiple virtio-scsi
iothreads. EDK2 provides secure-boot firmware for TDX guests.

## QEMU

### Serial and storage behavior

With multiple serial options in QEMU 9 on Ubuntu 24.10, `-serial none` suppresses
the first serial port instead of being ignored. Remove an accidental
`-serial none` to keep the former effective layout. `virtio-blk` adds
`iothread-vq-mapping`; `mapped-ram` provides fixed-size, multithreaded snapshot
save and load.

### Removed QEMU 9.2 interfaces

QEMU 9.2 in Ubuntu 25.04 removes:

- the `scsi` property from `virtio-blk`; use `virtio-scsi`;
- monitor and QMP block-migration options; use block jobs with NBD;
- the `compress` migration capability; use `multifd` compression; and
- the 9pfs `proxy` backend and `virtfs-proxy-helper`; use the 9pfs `local`
  backend or `virtio-fs`.

### QEMU 10.1 compatibility

QEMU 10.1 in Ubuntu 25.10 removes x86 machine types through 2.5 and s390x
machine types through 4.1. Move affected guests to newer machine types before
upgrading. It also prevents running 64-bit guests on a 32-bit host.

New capabilities include true multiqueue for `virtio-scsi`, Intel TDX, starting
TDX or SEV-SNP guests from IGVM files, and VFIO support for those confidential
guests.

## OVN routing and policy

OVN 25.03 in Ubuntu 25.04 adds dynamic route exchange controlled by
`dynamic-routing-redistribute`, IPv4 routing across IPv6 underlays, addressless
IPv4 logical router ports, `switch` logical switch ports, and transit routers for
interconnect deployments.

Established flows can bypass subsequent ACL matching with `persist-established`.
Logical-router policies add chains and the `jump`, `chain`, and `jump_chain`
actions.

## Raspberry Pi

Ubuntu 25.04 Raspberry Pi images add libcamera/libpisp camera support, replace
`libraspberry-bin` utilities with `raspi-utils`, and seed `nbd-client`. Desktop
images use `gnome-initial-setup`, enabling cloud-init for automated first-user
creation, package installation, and customization.

Ubuntu 25.10 Raspberry Pi images use a transactional boot-partition layout that
tests new boot assets before committing them as the known-good set. Raspberry Pi
4 firmware must be dated 2022-11-25 or later. Check and update it with:

```sh
sudo rpi-eeprom-update
sudo rpi-eeprom-update -a
```

Reboot after applying the update.

The 25.10 desktop images use the `desktop-minimal` seed and omit the former
backup, archive, calendar, camera, office, remote-desktop, media, scanning, mail,
and BitTorrent applications. Upgraded installations retain a manually installed
`ubuntu-desktop` metapackage and its applications. Cloud-init creates the desktop
swap file; set its size in boot-partition user-data before first boot.

## RISC-V and POWER

Ubuntu 25.04 uses one preinstalled RISC-V image across JH7110 boards and adds
Pine64 Star64 support. On POWER, the new `secvarctl` package manages Secure Boot
artifacts and keys.

Ubuntu 25.10 `linux-riscv` supports only systems implementing the RVA23S64 ISA
profile. RVA20-class hardware must remain on Ubuntu 24.04 LTS.

Ubuntu 24.10 adds POWER Book3S HV nestedv2 support. An Ubuntu 25.04 ppc64el guest
inside a PowerVM LPAR must reboot before an interface added with
`virsh attach-interface` becomes visible, even when `--live` is used.

## IBM Z

### Ubuntu 24.10 cryptography

OpenCryptoki 3.23 adds protected-key support for extractable keys used with EP11
tokens.

### Secure Execution and administration tools

In Ubuntu 25.04, `s390-tools` 2.37 adds `pvimg` and rewrites `genprotimg` in
Rust. It supports image inspection, host-compatibility validation, unencrypted
Secure Execution images, extended attestation, and retrievable guest secrets.
`scsi_logging_level` moves to `sg3_utils`. The new `cpacfinfo`, `zpwr`, and
`chpstat` commands report crypto facilities, LPAR power use, and channel
measurements.

IBM Z also gains eight-device KVM boot fallback, `virtio-mem`, and live updates
to mediated `vfio-ap` crypto-device configuration. The cryptographic stack adds
MSA 10 XTS, MSA 11 HMAC, MSA 12 SHA-3, and Secure Execution retrieved protected
keys. OpenCryptoki 3.24 adds CCA SHA-3, RSA OAEP 2.1, Dilithium, and
`CKM_RSA_AES_KEY_WRAP` mechanisms.

### z17 and key administration

In Ubuntu 25.10, `s390-tools` 2.38 adds topology-map data, conversion of LUKS2
AES keys to retrievable PAES keys, and hardened Control Program Identification
for SEL guests. The virtualization stack enables z17/LinuxONE 5 and reports
mediated `vfio-ap` configuration changes.

OpenCryptoki 3.25 adds EP11 secure-key import and export plus basic AES-GCM for
CCA tokens. The new `p11kmip` tool transfers PKCS #11 keys to and from a KMIP
server.

## Architecture-specific constraints and workarounds

The OpenStack 2025.1 Nova Compute package shipped in Ubuntu 25.04 is
nonfunctional with Python 3.13. The Ubuntu Cloud Archive build for Ubuntu 24.04
is unaffected.

On s390x Ubuntu 25.04, an AppArmor regression can make `lsblk` show no devices
or crash in a container. `aa-disable lsblk` is the temporary mitigation.

POWER installations to SAN disks with old metadata may require `wipefs` before
retrying. A ppc64el PowerVM guest must reboot to see an interface hot-attached
with `virsh attach-interface`, even with `--live`.

GTK4 desktop applications can render incorrectly under VirtualBox or VMware when
3D acceleration is enabled; distinguish that presentation issue from a guest
boot or device failure.
