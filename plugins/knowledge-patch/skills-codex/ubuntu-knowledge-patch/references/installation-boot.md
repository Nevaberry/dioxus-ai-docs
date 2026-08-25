# Installation, Boot, Filesystems, and Recovery

## Boot and early userspace

### Crash dumps are pre-enabled

Kernel crash dumps are enabled by default on both desktop and server
installations in Ubuntu 24.10. Capacity planning, storage cleanup, and operational
checks must treat kdump as active rather than opt-in.

### systemd boot and filesystem defaults

Ubuntu 24.10 ships systemd 256.5 with several operational changes:

- Boot with cgroup v1 is refused unless the kernel command line contains
  `SYSTEMD_CGROUP_ENABLE_LEGACY_FORCE=1`.
- The shipped `tmp.mount` makes `/tmp` a tmpfs by default.
- Cryptsetup-related systemd tools are in the merely-suggested
  `systemd-cryptsetup` package; install it when those tools are required.
- `systemd-ssh-generator` can arrange socket-activated SSH over local `AF_VSOCK`
  and `AF_UNIX` sockets.

In Ubuntu 25.04, systemd is built without utmp support and does not create
`/run/utmp`. Do not depend on that record. System V service scripts are
deprecated ahead of removal in systemd 258; convert local services and packages
to native units.

### Dracut on desktop systems

Ubuntu Desktop 25.10 builds its initramfs with Dracut and systemd instead of
`initramfs-tools`. This enables facilities such as Bluetooth and NVMe-oF in the
initramfs. Ubuntu Server and Raspberry Pi desktop images continue to use
`initramfs-tools`, and an ordinary desktop installation can switch back. Install
hooks and recovery logic for the actual generator in use.

### GRUB and iPXE

Ubuntu 25.10 ships a pre-release beta of GRUB 2.14, which is relevant when
triaging new boot regressions.

For physical boot through GRUB, install `grub-ipxe` and use `ipxe.efi` for UEFI
or `ipxe.lkrn` for x86 BIOS. UEFI ROMs in `ipxe-qemu` contain only network
drivers; an x86-64 QEMU guest that runs iPXE scripts must chainload `ipxe.efi`
from the `ipxe` package.

## Installer automation

### Local autoinstall input

The Ubuntu 24.10 desktop installer can import an autoinstall configuration from
a local file path; a remote source is no longer required for that workflow.

### Offline package-mirror fallback

When installation may proceed without a reachable mirror, make the fallback
explicit:

```yaml
apt:
  fallback: offline-install
```

In Ubuntu 25.10, choosing NVIDIA drivers during an offline installation installs
Nouveau instead. Install with network access or update the graphics driver after
installation.

### Network-dependent installation

The Ubuntu 24.10 installer assumes otherwise-unconfigured interfaces use DHCPv4.
Remove disconnected interfaces from `/etc/netplan/50-cloud-init.conf` or mark
them `optional: true`. A Raspberry Pi server image whose cloud-init data depends
on networking instead needs at least one interface marked `optional: false`.

### Desktop installation layouts and Arm media

The Ubuntu 25.04 desktop installer can replace an existing Ubuntu installation
and can install beside BitLocker-protected Windows where suitable free or
resizable space exists. Encrypted and other advanced layouts are available for
dual boot.

Its generic arm64 desktop ISO targets virtual machines, ACPI/EFI hardware, and
Snapdragon Windows-on-Arm devices, with initial Snapdragon X Elite enablement.

## Encryption and storage constraints

### Desktop encryption restrictions

For the Ubuntu 24.10 desktop installer:

- OEM installations are unsupported.
- ZFS encryption fails to activate cryptoswap on new installations and upgrades.
- TPM-backed full-disk encryption cannot boot while Absolute/Computrace is
  enabled.
- TPM-backed encryption can omit hardware-specific modules such as `vmd`, making
  NVMe RAID unavailable unless the conflicting BIOS feature is disabled.

Ubuntu 25.10 expands TPM-backed full-disk encryption with passphrase management,
recovery-key regeneration, and improved firmware-update integration. Security
Center can manage the recovery key after installation.

### NVMe-over-TCP installation

An Ubuntu 25.10 installation to a remote NVMe drive through NVMe-over-TCP
firmware can leave the target unbootable. Use the dedicated autoinstall
workaround or correct the installed system manually before its first reboot.

### Existing SAN metadata on POWER

An Ubuntu 25.04 POWER installation to SAN disks with existing metadata can fail.
Run `wipefs` as appropriate before retrying the installation.

## Architecture and firmware prerequisites

On U-Boot systems, update U-Boot to the Ubuntu 25.04 version before installation.
Subiquity does not run `flash-kernel` or `update-grub` on those systems, so an
older bootloader can leave the installation unusable.

The Ubuntu 24.10 `arm64+largemem` ISO uses a kernel with 64 KiB pages for
throughput-oriented workloads. Check application and driver page-size
compatibility before selecting it.

## Installation sizing

Ubuntu 26.04 Desktop lists a 2 GHz dual-core processor, at least 6 GB RAM, and
25 GB storage for a comfortable experience. Ubuntu Server starts at 1.5 GB RAM
and 4 GB storage, with actual needs determined by the workload. Internet access
is recommended but not required for the initial installation.
