# Storage and Filesystems

Use this reference for mount behavior, Btrfs support, encryption, installation storage, removed file systems, and storage-management integration.

## Mount behavior

### `mountfd` read-only semantics

Leap 16 `util-linux` uses the kernel `mountfd` API. An initially physical read-only mount prevents a later read-write mount of that filesystem. Keep only the virtual layer read-only when later read-write access is required:

```sh
mount -oro=vfs
```

### Volatile temporary storage

Leap 16 mounts `/tmp` as `tmpfs`, so it does not survive reboot. Move persistent application state elsewhere.

## Btrfs behavior and support

### Empty compression values

On SLES 15 SP6, an empty Btrfs compression value restores the default instead of disabling compression. Specify `none` or `no` to disable it.

### Supported feature boundary

SLES supports Btrfs subvolumes, snapshots, qgroups, swap files, compression, multi-device layouts, and RAID 0/1/10. User, group, and project quotas, automatic defragmentation, RAID 5/6, device replacement, seeding devices, and in-band deduplication are outside the stated support boundary.

### Unsupported feature gate

SLES 15 SP6 filesystem drivers refuse unsupported on-disk features, especially for read-write mounts. Setting `allow_unsupported=1` in `/etc/modprobe.d` or `/sys/module/MODULE/parameters/allow_unsupported` bypasses the gate but makes the kernel and entire system unsupported.

### Arm page-size changes

Four-KiB-block Btrfs works with the SLES 15 SP6 Arm 64 KiB kernel. Reinitialize swap after switching page size, which destroys suspend data:

```sh
swapon --fixpgsz /dev/sdc1
```

RAID 5 stripe size is bounded by `PAGE_SIZE`; avoid RAID 5 when comparing 4 KiB and 64 KiB kernel performance.

## Installation and encryption

The SLES 15 SP6 installer does not attempt to reuse an existing LVM layout. LUKS2 is fully supported in the YaST Partitioner, including AutoYaST profiles.

For IBM Z protected-key encryption and SLES 16 Secure Boot limits, see [platforms.md](platforms.md).

## Removed filesystems

SLES 16 removes quota v1, OCFS2, ReiserFS, HFS+, and UFS. Migrate OCFS2 workloads to read/write GFS2, which is available only with SLE High Availability.

Leap 16's unsupported `lklfuse` preview is built without Btrfs because it handles only one device per mount and cannot support Btrfs multi-device filesystems.

## Storage-management integrations

SLES 15 SP6 `libstoragemgmt` 1.9.8 folds its NetApp plug-in into the main package and removes the NetApp ONTAP and NexentaStor `nstor` plug-ins. Replace integrations using either removed backend before upgrade.

## NFS transport

Leap 16 can protect NFS storage traffic with TLS. See [networking-services.md](networking-services.md) for SLE protocol and IPv6 support boundaries.
