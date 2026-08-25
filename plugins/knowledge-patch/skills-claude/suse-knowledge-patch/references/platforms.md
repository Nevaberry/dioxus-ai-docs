# Architecture-Specific Platforms

## x86-64 and NVIDIA

### Turing and Ampere on Leap 15.6 (`leap-15.6`)

`nouveau` is disabled by default. The recommended openGPU path installs the
signed G06 module and GSP firmware:

```sh
zypper install nvidia-open-driver-G06-signed-kmp-default kernel-firmware-nvidia-gsp-G06
```

Then enable unsupported-GPU support in
`/etc/modprobe.d/50-nvidia-default.conf`:

```conf
options nvidia NVreg_OpenRmEnableUnsupportedGpus=1
```

To use `nouveau`, do not install that package and add `nouveau.force_probe=1`
to the kernel command line.

### Leap 16 automatic NVIDIA setup (`leap-16.0-guide`)

Supported GPUs receive the open kernel driver, NVIDIA repository, and user-space
acceleration automatically. If installation graphics cannot start, use
`rd.driver.blacklist=nouveau` for nouveau-specific failures or `nomodeset` for
general graphics failures.

### x86-64 floor and firmware (`leap-16.0-guide`)

Leap 16 requires x86-64-v2. Legacy BIOS still works, but TPM-backed full-disk
encryption requires UEFI and legacy BIOS support is planned for removal.

## IBM Z

### Leap and SLES hardware floors

Leap 16 requires z14 (`leap-16.0-guide`). SLES 16 requires z15; it may run on
z14, but that SLES configuration is unsupported.

### Leap 16 enablement and boot format (`leap-16.0-guide`)

Leap enables z17 and LinuxONE 5 in the kernel, toolchain, KVM, and libraries,
and adds MSA 10 XTS, MSA 11 HMAC, and MSA 12 SHA-3 cryptography.
`openssl-ibmpkcs11` is replaced by `openssl-pkcs11`; `cpacinfo` reports CPACF
capabilities.

After the `linuxrc`→`dracut` transition, the `parmfile` must describe networking
and disks and point to a loop-mounted ISO. Leap's documented form is:

```conf
root=live:ftp://$SERVER_URL/install/agama-online.iso
agama.install_url=ftp://$SERVER_URL/install/agama
```

### Secure IPL minimums on SLES 15 SP6

- NVMe requires LinuxONE III or newer.
- FC-attached SCSI requires LinuxONE III, z15, or newer.
- ECKD DASD with CDL requires z16, LinuxONE 4, or newer.

Older systems can IPL only in non-secure mode.

### Protected-key disk encryption on SLES 15 SP7

With a Crypto Express adapter, YaST can select `paes-xts-plain64`. CCA and EP11
modes are supported, but EP11 requires CEX7S or newer. LUKS2 can use either an
AES data key or AES cipher key.

### Deprecated networking and management interfaces

`netiucv` and `lcs` are deprecated for SLES 16 removal. `snIPL` is deprecated
because HMC supplies most capabilities; command-line automation can use
`zhmccli` with the HMC Web Services API.

### SLES 16 Secure Boot

After installation, `/etc/sysconfig/bootloader` contains `SECURE_BOOT=yes`.
Secure Boot is unsupported with the combined ECKD DASD and LinuxONE III
configuration.

### Cryptographic interfaces

SLES 16 `openssl-pkcs11` works in programs that fork. openCryptoki's CCA token
is available on x86-64 and ppc64le as well as IBM Z. The kernel `pkey` module
can derive AES-XTS and HMAC keys from clear keys, create keys identified by
Secure Execution retrievable-key identifiers, and use EP11 API ordinal 6 in
secure guests.

### Secure Execution management

The SLES 16 KVM stack adds host-key-hash discovery, host-specific `genprotimg`
validation, encrypted and unencrypted inspection through `pvimg info`,
retrievable-secret passthrough, and unencrypted Secure Execution images for
generic-image workflows. It also exposes `virsh hypervisor-cpu-models` and full
boot ordering across multiple targets.

### SLES 16 Agama `parmfile`

For an online SLES installation, `root=` must name the ISO image and the former
`agama.install_url` entry must be removed. On z/VM, explicitly describe network
and disks, for example:

```text
root=live:http://$SERVER_URL/install/online.iso
ip=$IP_ADDRESS::$IP_GATEWAY:24:SLES16-system:enc800:none
rd.zdev=qeth,0.0.0800:0.0.0801:0.0.0802,layer2=1,portno=0
cio_ignore=all,!condev,!0.0.0160 nameserver=$NAMESERVER_IP
rd.zdev=dasd,0.0.0160
```

## POWER

### Leap floor and nested KVM (`leap-16.0-guide`)

Leap 16 supports POWER10; POWER9 may run but is unsupported. With PowerVM
firmware 1060.10, a dedicated-core, KVM-enabled LPAR can itself host KVM guests
managed with `virsh`. If GNOME login through an HMC virtual terminal times out,
add `plymouth.enable=0` to the kernel command line.

### SLES 15 SP6 adapter and installation constraints

On POWER9 and Power10, DLPAR removal of any Emulex FC adapter can leave it
attached; adding it later can trigger EEH, kernel oops, and a crash. There is no
fix or live workaround: shut down the LPAR before changing that adapter.

If GRUB runs out of memory loading the large installer ramdisk with Secure Boot
and vTPM enabled, disable vTPM for installation.

### SLES 16 capacity

The logical-CPU limit rises to 8192. User-space addressing defaults to 128 TiB,
and an application can explicitly request mappings up to 4 PiB.

## Arm64

### Leap boot requirements (`leap-16.0-guide`)

Enabled SoCs include Ampere, AWS Graviton, Broadcom, Fujitsu, Huawei, Marvell,
NVIDIA, NXP, Rockchip, Socionext, and Xilinx families, but board-level external
chips can still need extra drivers. Hardware must satisfy SBBR or EBBR using
UEFI with ACPI or a Flat Device Tree. When both are present, the kernel chooses
the device tree unless `acpi=force` is supplied. The architecture floor is
Armv8.0-A.

### SLES 15 SP6 64 KiB kernel

`kernel-64kb` is supported on selected systems such as NVIDIA Grace, but KVM
with it is a technology preview; use the default kernel for supported
virtualization. Four-KiB-block Btrfs works, but changing page size requires swap
reinitialization and destroys suspend data:

```sh
swapon --fixpgsz /dev/sdc1
```

RAID 5 stripe size is bounded by `PAGE_SIZE`; avoid RAID 5 when comparing 4 KiB
and 64 KiB kernel performance.

### SLES 15 SP6 graphics

Integrated GH200 graphics require
`nvidia-open-driver-G06-signed-kmp-default` and
`kernel-firmware-nvidia-gspx-G06` 545.29.02 or later; discrete H100 is
unaffected. SLES supplies no graphics drivers for Jetson, IGX, or DRIVE. NXP
LS1028A/LS1018A has no DisplayPort because the HDP-TX PHY driver is absent, and
its `etnaviv` driver is a technology preview.

### SLES 15 SP7 previews

Running SLES on a BlueField-2 DPU remains a preview, distinct from using it as a
SmartNIC; `rshim` comes from Package Hub. Mali Utgard `lima`/`Mesa-dri` is a
preview and needs a matching Device Tree. Raspberry Pi preview
`u-boot-rpiarm64` Btrfs support lets U-Boot `ls` and `load` access Btrfs and
adds `btrsubvol` to list subvolumes.

## Cross-platform reminders

The SLES 15 SP7 2 MB OVMF image is deprecated for removal in SLES 16.1. Update
VM definitions before that minor release. Architecture-neutral CPU limits and
kernel timing are in [kernel-hardware.md](kernel-hardware.md).
