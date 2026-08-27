# Storage and Filesystems

## Mount and compression semantics

### Read-only mounts with `mountfd` (`leap-16.0-guide`)

`util-linux` uses the kernel `mountfd` API. If the initial physical mount is
read-only, that filesystem cannot later become read-write. When later write
access is required, keep only the virtual layer read-only:

```sh
mount -oro=vfs
```

### Btrfs empty compression value

On SLES 15 SP6, an empty compression value restores the default rather than
disabling compression. Use explicit `none` or `no` when compression must be off.

## Support boundaries

### Unsupported on-disk features

SLES 15 SP6 file-system drivers refuse unsupported features, especially for
read-write mounts. Setting `allow_unsupported=1` in `/etc/modprobe.d` or
`/sys/module/MODULE/parameters/allow_unsupported` bypasses the gate but makes
the kernel and entire system unsupported. Do not use the bypass on a supported
production system.

### Supported SLES Btrfs features

The supported set includes subvolumes, snapshots, qgroups, swap files,
compression, multi-device layouts, and RAID 0/1/10. User/group/project quotas,
automatic defragmentation, RAID 5/6, device replacement, seeding devices, and
in-band deduplication are outside the stated support boundary.

### `lklfuse` preview limitation (`leap-16.0-guide`)

`lklfuse` is an unsupported technology preview built without Btrfs support. It
handles one device per mount and cannot support Btrfs multi-device filesystems.

## Installer and encryption behavior

### SLES 15 SP6 storage installation

The installer no longer attempts to reuse an existing LVM layout. LUKS2 is
fully supported in the YaST Partitioner, including AutoYaST partitioning
profiles, rather than remaining a technology preview.

IBM Z protected-key LUKS2 details are architecture-specific; see
[platforms.md](platforms.md).

## Storage integrations

### `libstoragemgmt` plug-ins

SLES 15 SP6 `libstoragemgmt` 1.9.8 folds the NetApp plug-in into the main
package and removes the NetApp ONTAP and NexentaStor `nstor` plug-ins. Replace
either removed backend integration before upgrading.

### Arm page-size changes

Four-KiB-block Btrfs works with the supported Arm 64 KiB kernel, but swap must
be reinitialized after changing page size, destroying suspend data:

```sh
swapon --fixpgsz /dev/sdc1
```

RAID 5 stripe size is bounded by `PAGE_SIZE`; avoid RAID 5 for comparisons
between 4 KiB and 64 KiB kernels.

## SLES 16 removals and revisions

### Removed file systems and quota format

SLES 16.0 uses kernel 6.12 and removes quota v1, OCFS2, ReiserFS, HFS+, and UFS.
Migrate OCFS2 workloads to the read/write GFS2 implementation supplied only by
SLE HA.

### EROFS module (`16.0-rev-2026-08-04`)

`erofs` has been removed from the kernel module blacklist and is no longer
disabled by that default policy.

### XFS log stripe alignment (`16.0-rev-2026-08-04`)

XFS log stripe-unit alignment behavior changed. Revalidate SLES 16.0 storage
provisioning that assumes the previous alignment behavior.
