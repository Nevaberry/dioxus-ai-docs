# Installation and Image Mode

Consult this reference for Anaconda and Kickstart, image building, bootc deployment, image-mode updates, recovery, and installation-specific caveats.

## Contents

- [Installer interfaces, automation, and device discovery](#installer-interfaces-automation-and-device-discovery)
- [Installation caveats and remote media](#installation-caveats-and-remote-media)
- [Image Builder and output formats](#image-builder-and-output-formats)
- [Bootc and image-mode deployment](#bootc-and-image-mode-deployment)

## Installer interfaces, automation, and device discovery

### Anaconda account, certificate, and remote-access changes (10.0)

New users created in the graphical installer are administrators by default. Graphical remote installation uses RDP through `inst.rdp`, `inst.rdp.username`, and `inst.rdp.password` instead of the removed VNC boot options; Kickstart gains `%certificate` for importing Base64 CA certificates needed by encrypted DNS, and the installer can select NVMe-over-Fabrics devices.

### Removed installer interfaces (10.0)

Kickstart removes `auth`/`authconfig` (use `authselect`), `%anaconda`, `pwpolicy`, logging `--level`, team options (use bonds), and the camel-case `%packages` options (use `--exclude-weakdeps` and `--inst-langs`). `timezone --isUtc|--ntpservers|--nontp` become `--utc` or `timesource` options; extra GUI repositories move to Kickstart or `inst.addrepo`, and LUKS2 is the GUI default.

### Installer FIPS, scripting, and mount identity (10.1)

DVD, Boot ISO, and `image-installer` media add a boot-menu entry that starts installation with `fips=1`. The installer environment now includes `rpm` for uses such as Kickstart `%post`, and installed logical volumes are written to `/etc/fstab` by filesystem UUID rather than device-mapper path.

### Installer network and IBM Z behavior (10.1)

Anaconda now honors `BOOTIF=<MAC>` and activates only the designated interface rather than every interface. The `ostreecontainer` Kickstart command can deploy image-mode systems on s390x, although the release still notes Anaconda limitations for image mode on s390x and ppc64le.

### Removed installation and directory interfaces (10.1)

`cockpit-composer` is removed in favor of `cockpit-image-builder`, and `gdisk` is absent from `boot.iso` but remains usable from Kickstart. Directory Server removes server-wide referral mode and `nsslapd-subtree-rename-switch` (use an ACI to prevent subtree moves), and `virsh dump --live` is no longer supported.

### Installer Flatpak delivery (10.2)

Anaconda now preinstalls environment-selected Flatpaks from CDN, DVD, LAN, or Satellite sources through `preinstall.d`; Firefox and Thunderbird use Flatpaks by default, although their AppStream RPMs remain supported. To select the Firefox RPM instead:

```kickstart
%packages
@^graphical-server-environment
-redhat-flatpak-preinstall-firefox
firefox
%end
```

### Installer control and partition defaults (10.2)

Kickstart adds `rdp [--username USERNAME] [--password PASSWORD]` for headless graphical installation, and the automatically created `/boot` partition grows from 1 GiB to 2 GiB.

### Corrected installer ordering and rescue behavior (10.2)

Kickstart now resolves iSCSI and zFCP devices regardless of whether `ignoredisk` appears before their attachment commands, and `inst.dd` console input is visible again. Anaconda rescue mode recognizes image-based systems, mounts them at `/mnt/sysroot`, and limits meaningful manual changes to `/etc` and `/var`.


## Installation caveats and remote media

### Installation ordering and image-mode caveats (10.0)

Kickstart must place `iscsi` before an `ignoredisk` that names the iSCSI device, use `firewall --disabled` instead of the broken `services --disabled=firewalld`, and add `--no-activate` when duplicate LACP configuration would disrupt `rhsm`. `ostreecontainer` still requires a dedicated `/boot`, and signed-container ISO builds require removing the signature or deriving an unsigned image.

### Installer and image-mode caveats (10.1)

With composefs, cloud-init growpart does not enlarge the root filesystem, so set its final size in the image; on Azure, use RAW rather than LVM-labelled images with `system-reinstall-bootc` or `bootc install`. For encrypted-DNS remote installs put the source in Kickstart rather than `inst.repo`/`inst.stage2`, use `harddrive --partition=sdX --dir=/` for a USB CD-ROM restricted by `ignoredisk`, and note that `inst.dd` accepts invisible console input after Enter.


## Image Builder and output formats

### Image Builder and disk-image defaults (10.0)

Image Builder and `bootc-image-builder` can describe custom mount options, LVM partitions, and LVM swap, and `[customization.installer]` can inject a Kickstart into installer artifacts. Public cloud and KVM disk images use predictable interface names, `C.UTF-8`, UTC, and no separate `/boot`; AWS images boot with UEFI by default, while newly partitioned Power and IBM Z disks default to GPT except for DASD.

### Image Builder sources and formats (10.1)

File customizations in blueprints can reference external content with a `URI` field. Image Builder also adds `vagrant-libvirt` output, whose `vagrant` user has sudo access, and a `wsl` output that produces directly deployable WSL2 images.

### New installer and recovery previews (10.1)

The Technology Preview `image-builder-cli` package provides a one-command, container-capable successor path for `osbuild-composer` and `composer-cli`. For preview Sequoia RPM signing, install `rpm-sign sequoia-sq` and copy `/usr/share/doc/rpm/macros.rpmsign-sequoia` into `/etc/rpm/`; ReaR ISO/USB/PXE output and 4-KB/64-KB real-time kernels on ARM64 are also previews.

### RHEL image builder outputs (10.2)

The image-builder web app and `image-builder-cli` can create bootable images that subscribe on first boot; the CLI also creates stateless PXE systems, while network-installer ISO images can embed activation keys. Stateless container-derived PXE output consists of `kernel`, `initrd`, and `squashfs` artifacts.


## Bootc and image-mode deployment

### Bootc deployment and image construction (10.0)

`system-reinstall-bootc` installs an image onto an existing root, and `bootc-base-imgectl` can build from scratch or `rechunk` images, but scratch-derived images do not inherit base updates automatically. Image mode supports FIPS by setting the FIPS policy in the Containerfile and supplying `fips=1` through `/usr/lib/bootc/kargs.d/*.toml` when Anaconda is involved.

### Image-mode filesystem and build behavior (10.1)

Image mode can create root-level directories and symlinks after deployment, restore the filesystem to read-only, and now creates `/var/lib/tftpboot` automatically. `bootc-image-builder` uses local container storage by default, so workflows must preload the base image instead of relying on a registry pull; default image-mode installations also need an explicit `crashkernel=` argument to produce crash dumps.

### Package and image-mode caveats (10.1)

PostgreSQL, MariaDB, and MySQL cannot initialize in image mode because required users and working directories are not populated, with no documented workaround. `ansible-core` does not pull in `sshpass`, so password-based SSH management requires installing it explicitly.

### Staged bootc updates and VM conversion (10.2)

`bootc upgrade --download-only` stages an update without applying it on reboot, and `bootc upgrade --from-downloaded` later deploys that exact staged image without checking the registry. The new `bcvk` utility runs boot-container images as ephemeral VMs or converts them to persistent disk images.

### Image-mode service corrections (10.2)

PostgreSQL now initializes in `podman-bootc` and BIND installs in image mode after its essential state moved under `/etc/named`. MySQL still cannot initialize in image mode because it does not populate the required users and working directories, and has no workaround.

### Bootc installation and sealing previews (10.2)

The Technology Preview Kickstart command `bootc --source-imgref=TRANSPORT:IMAGE --target-imgref=IMAGE` provisions bootable containers but cannot express multi-device or nonstandard mount layouts. Integrity Image Sealing is also a preview, embedding a root-filesystem digest in an organization-signed UKI to cover the boot path and host OS.

### Unified bootc storage developer preview (10.2)

The unified-storage developer preview lets bootc keep the host image in bootc-owned container storage so Podman can reuse it for running or layering images, including zstd-chunked data where available.

### Bootc installation caveat (10.2)

UEFI installation with the new `bootc` path fails without both an EFI System Partition and a separate `/boot`. This is distinct from `ostreecontainer`, whose separate-`/boot` requirement is fixed in 10.2.

