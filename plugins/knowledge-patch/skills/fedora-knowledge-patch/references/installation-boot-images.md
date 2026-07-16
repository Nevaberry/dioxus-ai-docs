# Installation, Boot, and Installation Images

## Contents

- Anaconda interfaces and configuration
- Storage layout and encryption
- Boot loaders and early boot
- Live media, images, and architectures

## Anaconda interfaces and configuration

### Workstation's new installer flow (42)

Workstation uses Anaconda's PatternFly web UI and ordered wizard. Its storage
flow includes goal-based guided partitioning, a **Reinstall Fedora** path,
improved dual-boot handling, and an advanced storage editor under **Installation
Method**.

### Remote installation moves from VNC to RDP (42)

Anaconda is Wayland-native. TigerVNC support, `inst.vnc`, `inst.vncpassword`,
`inst.vncconnect`, and the Kickstart `vnc` interface are removed. Use an
RDP-capable client with `inst.rdp`, `inst.rdp.username`, and
`inst.rdp.password`.

### Anaconda's web UI expands to Fedora Spins (43)

The PatternFly web UI is the default for most Spins and Editions, although an
individual Spin can defer the transition. Automation and user guidance should
not assume the former GTK installer flow.

### Anaconda stops creating profiles for untouched network devices (44)

Anaconda creates NetworkManager profiles only for devices configured through
boot options, Kickstart, or the installer UI. A merely present wired device no
longer receives a default connection profile.

### KDE setup moves out of Anaconda (44)

Fedora KDE variants perform post-install configuration in Plasma Setup;
redundant setup choices are disabled in Anaconda.

## Storage layout and encryption

### OPAL2 drive encryption in Anaconda (41)

Anaconda can configure native hardware encryption on TCG OPAL2-compliant
self-encrypting drives as an installer option, in addition to software-backed
disk encryption.

### GPT is the installer default on every architecture (42)

Anaconda creates GPT partition tables by default on ppc64le and s390x as well
as x86_64. Provisioning that assumed MBR on those architectures must request or
handle GPT.

### The default `/boot` partition is 2 GiB (43)

Anaconda's default layout allocates 2 GiB rather than 1 GiB to `/boot`. Give
custom partitioning and image definitions enough space.

### x86 UEFI installations require GPT (43)

Anaconda does not install Fedora in UEFI mode to an MBR-partitioned x86 disk;
use GPT. This restriction does not apply to ARM or RISC-V installations.

### Fedora Cloud makes `/boot` a Btrfs subvolume (44)

Fedora Cloud images no longer use a separate `/boot` partition. `/boot` is a
subvolume in the Btrfs layout, so image and provisioning tools must not depend
on the old partition boundary.

### TPM-backed LUKS unlock on Atomic Desktops (41)

Atomic Desktop initramfs images contain the early-boot components required to
unlock LUKS volumes through the TPM. TPM enrollment no longer requires
layering those missing components.

## Boot loaders and early boot

### bootupd and static GRUB on Atomic Desktops (41)

UEFI Atomic Desktops apply boot-loader updates automatically with `bootupd`.
New installations use a static GRUB configuration driven by Boot Loader
Specification entries instead of regenerating GRUB configuration on every
update.

### Plymouth uses simpledrm early in boot (42)

Plymouth draws through the EFI framebuffer before the full GPU driver loads
and estimates HiDPI scaling from resolution. Restore the former timing when
the splash behaves poorly:

```console
sudo grubby --update-kernel=ALL --args="plymouth.use-simpledrm=0"
```

### Initramfs images use zstd (43)

Dracut compresses initramfs images with zstd by default across Fedora
variants. Custom inspection, unpacking, and repacking tools must support zstd.

### Boot-loader updates are decoupled from package transactions (44)

The first boot-loader unification phase moves GRUB and shim toward one updater,
likely `bootupd`, instead of writing `/boot` or `/boot/efi` directly during RPM
transactions. zipl and systemd-boot are unchanged.

### `mkosi-initrd` is packaged as an alternative initrd builder (44)

Fedora packages `mkosi-initrd` for local initrd generation and supplies a
`kernel-install` plugin that can rebuild the initrd when a kernel package is
installed.

## Installation security

### FIPS mode becomes an install-time choice (42)

`fips-mode-setup` is removed. Create a FIPS-mode system by booting Anaconda
with `fips=1`, selecting an Image Builder customization, or preparing a bootc
image. Post-install switching can leave LUKS and host keys noncompliant. The
kernel `fips=1` flag is the source of truth and crypto policy follows it;
compliance-oriented disabling requires reinstallation.

```toml
[customizations]
fips = true
```

## Live media, images, and architectures

### Live media switch to EROFS (42)

Fedora live environments store their read-only filesystem as EROFS rather than
SquashFS. Custom live-media inspection and repacking tools must recognize the
new format.

### AArch64 live media selects DTBs automatically (44)

AArch64 live images select the correct device tree at boot, enabling direct
boot on supported Windows-on-Arm laptops.

### Atomic Desktops drop ppc64le images (42)

Fedora no longer publishes Atomic Desktop images for ppc64le. Use a
package-mode installation or build an Atomic image from the available ppc64le
Bootable Containers.

### Kickstart assets are available as OCI artifacts (42)

Fedora publishes network and bare-metal bootc installation files in a
versioned OCI repository. Deployments can obtain both the bootable container
and Kickstart assets from registries without extracting the assets from an RPM
repository.
