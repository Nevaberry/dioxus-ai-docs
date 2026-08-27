# Architecture-Specific Platforms

## NVIDIA and x86-64

Leap 15.6 disables `nouveau` by default for Turing and Ampere GPUs. The openGPU
path installs the signed G06 module and GSP firmware, then enables unsupported
GPU support:

```sh
zypper install nvidia-open-driver-G06-signed-kmp-default kernel-firmware-nvidia-gsp-G06
```

```conf
options nvidia NVreg_OpenRmEnableUnsupportedGpus=1
```

To use `nouveau`, do not install that package and boot with
`nouveau.force_probe=1`. (leap-15.6)

Leap 16 automatically installs the open kernel driver, NVIDIA repository, and
user-space acceleration for supported GPUs. If installation graphics fail,
boot with `rd.driver.blacklist=nouveau` for nouveau-specific failures or
`nomodeset` for general failures.

Leap 16 requires x86-64-v2. Legacy BIOS still works, but TPM-backed disk
encryption requires UEFI and legacy BIOS support is planned for removal.

## IBM Z

Leap 16 requires z14, while SLES 16 supports z15 or newer; SLES may run on z14
but that is unsupported. Leap enables z17 and LinuxONE 5, MSA 10 XTS, MSA 11
HMAC, and MSA 12 SHA-3. `openssl-ibmpkcs11` becomes `openssl-pkcs11`, and
`cpacinfo` reports CPACF capabilities. (leap-16.0-guide)

For Leap IBM Z installation, `parmfile` must point to a loop-mounted ISO and,
after the `linuxrc`-to-`dracut` transition, describe networking and disks:

```conf
root=live:ftp://$SERVER_URL/install/agama-online.iso
agama.install_url=ftp://$SERVER_URL/install/agama
```

SLES 15 SP6 secure IPL requires LinuxONE III or newer for NVMe; LinuxONE III,
z15, or newer for FC-attached SCSI; and z16, LinuxONE 4, or newer for ECKD DASD
with CDL. Older systems can IPL only in non-secure mode.

The `netiucv` and `lcs` drivers are deprecated for SLES 16 removal. SLES 16
sets `SECURE_BOOT=yes` in `/etc/sysconfig/bootloader` after installation, but
Secure Boot is unsupported with ECKD DASD on LinuxONE III.

SLES 16's `openssl-pkcs11` provider is fork-safe, and openCryptoki's CCA token
is available on x86-64 and ppc64le as well as IBM Z. Kernel `pkey` can derive
AES-XTS and HMAC keys from clear keys, create Secure Execution retrievable-key
identifier keys, and use EP11 API ordinal 6 in secure guests.

Secure Execution management adds host-key-hash discovery, host-specific
`genprotimg` validation, encrypted and unencrypted inspection with `pvimg info`,
retrievable-secret passthrough, and unencrypted images for generic-image
workflows. It also adds `virsh hypervisor-cpu-models` and full multi-target boot
ordering.

For SLES 16 online IBM Z installation, `root=` must name an ISO and
`agama.install_url` must be absent. On z/VM, explicitly describe network and
disks, for example:

```text
root=live:http://$SERVER_URL/install/online.iso
ip=$IP_ADDRESS::$IP_GATEWAY:24:SLES16-system:enc800:none
rd.zdev=qeth,0.0.0800:0.0.0801:0.0.0802,layer2=1,portno=0
cio_ignore=all,!condev,!0.0.0160 nameserver=$NAMESERVER_IP
rd.zdev=dasd,0.0.0160
```

`snIPL` is deprecated because HMC supplies most of its features; use `zhmccli`
against the HMC Web Services API for command-line automation.

## POWER

Leap 16 requires POWER10; POWER9 may work but is unsupported. With PowerVM
firmware 1060.10, a dedicated-core, KVM-enabled LPAR can host KVM guests managed
with tools such as `virsh`. If GNOME login through an HMC virtual terminal times
out, boot with `plymouth.enable=0`.

On SLES 15 SP6 POWER9/Power10, DLPAR removal of an Emulex FC adapter can leave it
attached; adding it later can cause EEH errors, oops, and crash. Shut down the
LPAR before changing it. If GRUB runs out of memory loading the large installer
ramdisk with Secure Boot and vTPM, disable vTPM for installation.

SLES 16 documents 8192 logical CPUs on POWER. User-space addressing defaults to
128 TiB, while applications may explicitly map up to 4 PiB.

## Arm64

Leap 16 requires Armv8.0-A. Supported SoC families include Ampere, AWS Graviton,
Broadcom, Fujitsu, Huawei, Marvell, NVIDIA, NXP, Rockchip, Socionext, and Xilinx,
but board-level external chips can need extra drivers. Systems must meet SBBR or
EBBR with UEFI plus ACPI or a Flat Device Tree; when both exist the kernel picks
the tree unless booted with `acpi=force`.

SLES 15 SP6 glibc enables Armv8.5 Memory Tagging. Its kernel changes IOMMU from
passthrough to translated mode; restore passthrough with `iommu.passthrough=1`.

`kernel-64kb` is supported on selected systems such as NVIDIA Grace, but KVM
with it is a technology preview. Use the default kernel for supported
virtualization.

GH200 integrated graphics require `nvidia-open-driver-G06-signed-kmp-default`
and `kernel-firmware-nvidia-gspx-G06` 545.29.02 or later; discrete H100 is
unaffected. SLES has no graphics drivers for Jetson, IGX, or DRIVE. NXP
LS1028A/LS1018A has no DisplayPort because its HDP-TX PHY lacks a driver, and
its `etnaviv` GPU is a technology preview.

SLES 15 SP7 technology previews include SLES on BlueField-2 DPU (distinct from
SmartNIC use; `rshim` is in Package Hub), `lima`/`Mesa-dri` on Mali Utgard with
a matching Device Tree, and Raspberry Pi `u-boot-rpiarm64` Btrfs commands `ls`,
`load`, and `btrsubvol`.

## Preview and support boundaries

SLES 15 SP6 previews the AMD Navi32 “Wheat Nas” GPU driver without matching
firmware, Intel IAA crypto compression, and a disabled-by-default Confidential
Computing Module containing unsupported host, secure-VM, and attestation tools.

Leap 16 previews the no-permission-by-default `mcphost` agent and `lklfuse`.
`lklfuse` lacks Btrfs because it handles only one device per mount and cannot
support Btrfs multi-device filesystems.
