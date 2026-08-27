# Platform, installation, and upgrades

## Contents

- [Platform baseline and lifecycle](#platform-baseline-and-lifecycle)
- [In-place upgrades](#in-place-upgrades)
- [Installer behavior](#installer-behavior)
- [Image Builder and image mode](#image-builder-and-image-mode)
- [Repositories, recovery, and known limits](#repositories-recovery-and-known-limits)

## Platform baseline and lifecycle

### Hardware baseline and lifecycle

CentOS Stream 10 requires x86-64-v3 on x86_64. Other build targets are ARMv8.0-A, POWER9, and IBM z14. Its lifecycle is roughly five years, with maintenance expected until 2030, subject to the end of the corresponding enterprise release's Full Support phase. (10.0)

### Secure Boot status

The launch-time Secure Boot incompatibility was fixed by the 2025-07-07 update. Current CentOS Stream 10 installations can run with Secure Boot enabled. (10.0)

## In-place upgrades

### Supported in-place upgrades

Leapp supports direct 8.10-to-9.8 upgrades on x86-64-v2, ARMv8.0-A, POWER9 or newer, and IBM z14 or newer systems, including SAP HANA hosts. A release 7 host cannot upgrade directly to 9; upgrade to 8 first. (9.8)

### Supported RHEL 10.2 upgrade path

Leapp supports 9.8-to-10.2 upgrades on x86-64-v3, ARMv8.0-A, POWER10 or newer, and IBM z15 or newer systems. A release 8 host cannot upgrade directly to 10; upgrade through 9. (10.2)

### Secure Boot upgrade prerequisites

Before upgrading a Secure Boot release 9 host, run at least release 9.2 with `shim-15.8-3` or later so shim trusts the CA 5- and CA 8-signed GRUB and kernel. Firmware must enroll at least one certificate used by the 10.2 shim: Microsoft Windows UEFI Driver Publisher 2011, Microsoft UEFI CA 2023, or Red Hat UEFI Publisher 2024.

## Installer behavior

### RDP-based Kickstart installation

The Kickstart command `rdp [--username <USERNAME>] [--password <PASSWORD>]` starts a remote graphical installer for automated headless deployment over RDP. (10.2)

### Boot partition sizing and image-mode requirement

Anaconda's default `/boot` size increases from 1 GiB to 2 GiB. A boot-container installation in UEFI mode requires separate EFI System, `/boot`, and root partitions; installation fails if `/boot` is omitted. (10.2)

### Flatpak installation defaults

For applicable graphical installations, Anaconda preinstalls Firefox and Thunderbird as Flatpaks from CDN, DVD, LAN, and Satellite sources. To choose the Firefox RPM instead, suppress the preinstall package in Kickstart: (10.2)

```kickstart
%packages
@^graphical-server-environment
-redhat-flatpak-preinstall-firefox
firefox
%end
```

### Installer security and storage defaults

`initial-setup` is replaced by `gnome-initial-setup`. New storage defaults to LUKS2. GUI-created users are administrators unless that option is cleared. New logical volumes are recorded in `/etc/fstab` by file-system UUID rather than device-mapper path, so renaming an LV or VG does not require an fstab edit.

### Installer repository and remote-access interfaces

The installer GUI cannot add extra repositories; use Kickstart or the `inst.addrepo` boot option. RDP replaces VNC for remote graphical installation, using `inst.rdp`, `inst.rdp.username`, and `inst.rdp.password` kernel arguments.

### Removed installer boot options

Anaconda removes `inst.nompath`, `dmraid`, `nodmraid`, `inst.xdriver`, and `inst.usefbx`. GUI and Kickstart installation can no longer reconfigure NVDIMMs, although NVDIMMs remain usable in sector mode.

### Removed Kickstart commands

Kickstart removes `pwpolicy`, `%anaconda`, the logging command's `--level`, `auth`, and `authconfig`; configure authentication with `authselect`. `%addon com_redhat_oscap` and the installer Security Policy spoke are removed, so apply hardening in Kickstart or use a pre-hardened image.

### Kickstart option replacements

Replace `timezone --isUtc` with `timezone --utc`. Move `--ntpservers` and `--nontp` to `timesource --ntp-server` and `timesource --ntp-disable`. In `%packages`, use `--exclude-weakdeps` and `--inst-langs`. Network teaming options `--teamslaves` and `--teamconfig` are removed; define a bond with `--bondslaves` and `--bondopts`.

### Installer and GCC Toolset migrations

Replace `inst.gpt` with `inst.disklabel=gpt` or `inst.disklabel=mbr`, and remove the deprecated Kickstart `module` command. GCC Toolset 15 no longer supports `scl enable`; run `gcc-toolset-15-env <command>`, or invoke it without a command to enter a shell. (10.2)

## Image Builder and image mode

### Image Builder layouts and outputs

Image Builder supports advanced partitioning, Kickstart injection into ISO builds, and WSL2 images. Newly built AWS and KVM-style disk images no longer have a separate `/boot` partition. (9.8)

### Image Builder and bootc outputs

Image Builder can create Anaconda network-installer ISOs with embedded activation keys and stateless PXE artifacts that run from RAM. Its GUI and `image-builder-cli` create bootable container and disk images that subscribe on first boot. Use `bcvk` to launch boot containers as ephemeral VMs or convert them to persistent disk images. (10.2)

### Staged bootc updates

`bootc upgrade --download-only` stages an update without selecting it for the next reboot. Later, `bootc upgrade --from-downloaded` deploys exactly that staged image without checking the registry for a newer one. (10.2)

### `bootc` Kickstart command preview

The Technology Preview command `bootc --source-imgref=<transport>:<registry>/<namespace>/<name>:<tag> --target-imgref=<registry>/<namespace>/<name>:<tag>` provisions a bootable container and its boot loader. It does not support layouts spanning multiple disks or nonstandard custom mount points. (10.2)

### UKI entries in Boot Loader Specification snippets

BLS snippets under `/boot/efi/loader/entries` can use `efi` instead of `linux` to point to a unified kernel image under `/boot/efi/EFI/Linux`: (10.2)

```text
title Red Hat Enterprise Linux 10.2
version 6.12.0-197.el10.x86_64
efi /EFI/Linux/kernel-6.12.0-197.el10-UKI.efi
```

### Integrity Image Sealing preview

The Technology Preview sealing flow signs a boot-container UKI and embeds a digest of its container root file system, extending an organization's Secure Boot trust from firmware through the host operating system. (10.2)

### `bootc-image-builder` deprecation

`bootc-image-builder` remains supported for release 10 but is deprecated. Use the AppStream `image-builder` command for new bootable-container and disk-image workflows. (10.2)

### RHEL for Edge image-mode migration

Release 10 Edge artifacts use image mode rather than the older Image Builder flow. Ignition injection for Simplified Installer, AMI, and VMDK Edge images is removed without replacement. When converting a release 9 `simplified-installer` or raw image whose root uses null-cipher LUKS, include the required Clevis packages and regenerate the `initramfs` directories during the container build.

### Image Builder migration points

The web-console package changes from `cockpit-composer` to `cockpit-image-builder`. On-premises Image Builder replaces the `openstack` type with `qcow2`. Public disk images use predictable interface names because `net.ifnames=0` is removed. `gdisk` is absent from `boot.iso`, but remains usable from Kickstart.

## Repositories, recovery, and known limits

### EUS repositories require a pinned release

Release 10 containers do not enable EUS repositories automatically. Set `/etc/dnf/vars/releasever` to the intended EUS minor, disable standard repositories, and enable their EUS counterparts to avoid major-version URLs and metadata 404 errors. (10.2)

### `kdump` limitations with UKI and Secure Boot

`kdump` fails on UKI-based confidential Azure VMs; the documented workaround is to disable SELinux and reboot. It also cannot run with Secure Boot on 64-bit ARM; disable Secure Boot there. (9.8)

### ReaR output migration

On IBM Z, replace deprecated `OUTPUT=IPL` with `OUTPUT=RAMDISK`. Outputs become `kernel-$RAMDISK_SUFFIX` and `initramfs-$RAMDISK_SUFFIX.img`, with the host name as the default suffix. ISO output now defaults `ISO_VOLID` to `REAR-ISO` rather than `RELAXRECOVER`; update label-based mounts or set the old value explicitly in `/etc/rear/local.conf`.
