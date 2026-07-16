# Architecture-Specific Platforms

Use this reference for architecture floors, firmware, boot, cryptography, capacity, and platform-specific constraints on IBM Z, POWER, Arm, and x86-64.

## Contents

- [Architecture floors](#architecture-floors)
- [IBM Z and LinuxONE](#ibm-z-and-linuxone)
- [POWER](#power)
- [Arm64](#arm64)
- [Virtual firmware retirement](#virtual-firmware-retirement)

## Architecture floors

Leap 16 requires x86-64-v2 on AMD64/Intel 64, POWER10 on supported POWER systems, Armv8.0-A on Arm64, and z14 on IBM Z. POWER9 may work but is unsupported. Legacy BIOS still works, but TPM-backed full-disk encryption requires UEFI and legacy BIOS support is planned for removal.

SLES 16 has a higher IBM Z support floor: z15. It may run on z14, but that configuration is unsupported.

## IBM Z and LinuxONE

### Enablement and cryptography

Leap 16 adds z17 and LinuxONE 5 enablement across the kernel, toolchain, KVM, and libraries, plus MSA 10 XTS, MSA 11 HMAC, and MSA 12 SHA-3 support. Replace `openssl-ibmpkcs11` with `openssl-pkcs11`; use `cpacinfo` to report CPACF capabilities.

SLES 16 `openssl-pkcs11` supports programs that fork. openCryptoki's CCA token is available on x86-64 and ppc64le as well as IBM Z. The kernel `pkey` module can derive AES-XTS and HMAC keys from clear keys, create keys identified by Secure Execution retrievable-key identifiers, and use EP11 API ordinal 6 in secure guests.

### Secure IPL and Secure Boot

For SLES 15 SP6, Secure IPL from NVMe requires LinuxONE III or later; FC-attached SCSI requires LinuxONE III, z15, or later; and ECKD DASD with CDL requires z16, LinuxONE 4, or later. Older hardware can IPL only in non-secure mode.

After SLES 16 installation, `/etc/sysconfig/bootloader` contains `SECURE_BOOT=yes`. Secure Boot is unsupported with the combination of an ECKD DASD disk and LinuxONE III.

### Protected-key disk encryption

On SLES 15 SP7 IBM Z, the YaST partitioner can select `paes-xts-plain64` when a Crypto Express adapter is configured. CCA and EP11 modes are supported, but EP11 needs CEX7S or newer. LUKS2 can use an AES data key or AES cipher key.

### Secure Execution management

SLES 16 IBM Z KVM adds host-key-hash discovery, host-specific `genprotimg` validation, encrypted and unencrypted inspection with `pvimg info`, retrievable-secret passthrough, and unencrypted Secure Execution images for generic-image workflows. It also exposes `virsh hypervisor-cpu-models` and complete boot ordering across multiple targets.

### Agama `parmfile`

For Leap 16 IBM Z, point `root=` to a loop-mounted ISO and explicitly describe installation networking and disks after the `linuxrc`-to-`dracut` transition. A Leap online layout uses:

```conf
root=live:ftp://$SERVER_URL/install/agama-online.iso
agama.install_url=ftp://$SERVER_URL/install/agama
```

For an SLES 16 online installation, `root=` must name the ISO and the former `agama.install_url` entry must be absent. On z/VM, describe networking and disks explicitly, for example:

```text
root=live:http://$SERVER_URL/install/online.iso
ip=$IP_ADDRESS::$IP_GATEWAY:24:SLES16-system:enc800:none
rd.zdev=qeth,0.0.0800:0.0.0801:0.0.0802,layer2=1,portno=0
cio_ignore=all,!condev,!0.0.0160 nameserver=$NAMESERVER_IP
rd.zdev=dasd,0.0.0160
```

### Deprecated IBM Z interfaces

Move IBM Z network automation away from `netiucv` and `lcs`; SLES 15 SP7 deprecates both drivers for SLES 16 removal. HMC now supplies most `snIPL` capabilities; replace remaining deprecated command-line automation with `zhmccli` against the HMC Web Services API.

## POWER

### Nested KVM in PowerVM

On PowerVM firmware 1060.10, Leap 16 can host KVM guests inside a dedicated-core, KVM-enabled LPAR and manage them with tools such as `virsh`. If GNOME login through an HMC virtual terminal times out, add `plymouth.enable=0` to the kernel command line.

### Capacity

SLES 16 supports up to 8192 logical CPUs on POWER. User-space addressing defaults to 128 TiB; an application can explicitly request mappings as large as 4 PiB.

### Emulex DLPAR risk

On POWER9 and POWER10 under SLES 15 SP6, DLPAR removal of any Emulex FC adapter can leave it attached; re-adding it can cause an EEH error, kernel oops, and crash. No fix or live workaround exists, so shut down the LPAR before changing the adapter.

If GRUB exhausts memory while loading the large installer ramdisk with Secure Boot and vTPM enabled, disable vTPM for installation.

## Arm64

### Boot requirements

Leap 16 enables SoCs across Ampere, AWS Graviton, Broadcom, Fujitsu, Huawei, Marvell, NVIDIA, NXP, Rockchip, Socionext, and Xilinx families, but board-level external chips can require extra drivers. Require SBBR or EBBR using UEFI with ACPI or a Flat Device Tree. When both ACPI and a device tree exist, the kernel chooses the tree unless booted with `acpi=force`.

### Memory tagging and IOMMU

SLES 15 SP6 Arm glibc 2.38 enables Armv8.5 Memory Tagging Extension. The Arm kernel changes its IOMMU default from passthrough to translated mode; restore the former mode with `iommu.passthrough=1` only when required.

### 64 KiB kernel

SLES 15 SP6 supports `kernel-64kb` on selected systems such as NVIDIA Grace, but KVM with this flavor remains a technology preview. Use the default kernel for supported virtualization. Four-KiB-block Btrfs works with the 64 KiB kernel, but reinitialize swap after changing page size, destroying suspend data:

```sh
swapon --fixpgsz /dev/sdc1
```

RAID 5 stripe size is bounded by `PAGE_SIZE`; avoid RAID 5 for 4 KiB versus 64 KiB performance comparisons.

### Graphics

Integrated GH200 graphics need `nvidia-open-driver-G06-signed-kmp-default` and `kernel-firmware-nvidia-gspx-G06` version 545.29.02 or later; discrete H100 cards are unaffected. SLES supplies no graphics drivers for Jetson, IGX, or DRIVE. NXP LS1028A/LS1018A has no DisplayPort output because no HDP-TX PHY driver exists, and its `etnaviv` driver is only a preview.

### Additional previews

SLES 15 SP7 on a BlueField-2 DPU remains a preview, distinct from using BlueField as a SmartNIC; obtain `rshim` from Package Hub. The `lima`/`Mesa-dri` stack for Mali Utgard GPUs is a preview and needs a matching Device Tree. Raspberry Pi's preview `u-boot-rpiarm64` Btrfs driver lets U-Boot `ls` and `load` read Btrfs and adds `btrsubvol` for listing subvolumes.

Additional SLES 15 SP7 Arm technology previews are documented by the release but remain unsupported; verify preview status before relying on them.

## Virtual firmware retirement

The 2 MB OVMF image is deprecated in SLES 15 SP7 for removal in SLES 16.1. Update VM definitions before that minor release.
