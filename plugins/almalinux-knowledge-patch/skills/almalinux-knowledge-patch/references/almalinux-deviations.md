# AlmaLinux Deviations from RHEL 10

AlmaLinux 10 "Heliotrope Lion" is based on RHEL 10 but includes several features that RHEL removes or disables. These deviations are the primary reason to choose AlmaLinux over other RHEL rebuilds.

## Btrfs Filesystem Support

RHEL 10 does not support Btrfs. AlmaLinux provides full kernel and userspace enablement:

- Can install and boot from Btrfs root filesystem
- Full subvolume, snapshot, and RAID support
- Available in the default kernel — no additional packages required

```bash
# Create Btrfs filesystem
mkfs.btrfs /dev/sda1

# Mount with common options
mount -o compress=zstd,noatime /dev/sda1 /mnt

# Subvolume management
btrfs subvolume create /mnt/@root
btrfs subvolume create /mnt/@home
btrfs subvolume snapshot -r /mnt/@root /mnt/@root-snapshot

# Check filesystem
btrfs filesystem show
btrfs filesystem usage /mnt
```

## x86-64-v2 Architecture Builds

RHEL 10 raised the minimum CPU baseline to x86-64-v3 (requires AVX2, BMI1/2, FMA — Intel Haswell+ or AMD Excavator+). AlmaLinux additionally ships x86-64-v2 builds for older hardware.

### Caveat

Third-party packages compiled for RHEL 10 target x86-64-v3 only. Running on v2 hardware means:

- AlmaLinux's own repositories work fully
- Third-party RHEL 10 packages may fail with `SIGILL` (illegal instruction)
- Software compiled from source on v2 hardware will work

### Detecting Architecture Level

```bash
# Check CPU support
/lib64/ld-linux-x86-64.so.2 --help 2>&1 | grep supported
# Output shows: x86-64-v2, x86-64-v3, x86-64-v4
```

## CRB Repository Enabled by Default

On new AlmaLinux 10 installations, the CodeReady Builder (CRB) repository is enabled by default. This means development headers, libraries, and build dependencies are available without manual repo activation.

```bash
# Previously required on RHEL/AlmaLinux 9:
#   dnf config-manager --set-enabled crb

# On AlmaLinux 10+ new installs, CRB is already enabled
dnf repolist | grep crb
# crb    AlmaLinux 10 - CRB
```

Note: Upgrades from AlmaLinux 9 preserve existing repo configuration.

## SPICE Re-enabled

RHEL 10 removed SPICE support. AlmaLinux re-enables both server and client components for virtual desktop/display protocol use cases.

## Frame Pointers Enabled by Default

All AlmaLinux 10 packages are compiled with frame pointers enabled, allowing system-wide real-time tracing and profiling without recompilation.

```bash
# System-wide profiling works out of the box
perf record -g -a -- sleep 10
perf report
```

## KVM on IBM POWER

RHEL 10 removed KVM support on IBM POWER architecture. AlmaLinux re-enables it in the virtualization stack for ppc64le users.

## Firefox and Thunderbird as RPMs

RHEL 10 ships Firefox and Thunderbird as Flatpak-only. AlmaLinux provides them as regular RPMs, which integrates better with system package management and enterprise deployment tools.

```bash
# Regular RPM install (not Flatpak)
dnf install firefox thunderbird
```
