# Storage and Filesystems

## Mount semantics and Btrfs

Leap 16 `util-linux` uses the kernel `mountfd` API. An initially physical
read-only mount prevents a later read-write mount of that filesystem. If later
write access is required, make only the virtual layer read-only:

```sh
mount -oro=vfs
```

On SLES 15 SP6, an empty Btrfs compression value restores the default instead
of disabling compression. Use `none` or `no` to disable it.

The supported SLES Btrfs feature set includes subvolumes, snapshots, qgroups,
swap files, compression, multi-device layouts, and RAID 0/1/10. User, group,
and project quotas, automatic defragmentation, RAID 5/6, device replacement,
seeding devices, and in-band deduplication are outside the support boundary.

Filesystem drivers refuse unsupported on-disk features, especially for
read-write mounts. Setting `allow_unsupported=1` in `/etc/modprobe.d` or
`/sys/module/MODULE/parameters/allow_unsupported` bypasses the gate but makes
the kernel and entire system unsupported.

## Encryption, page sizes, and removed filesystems

SLES 15 SP6 fully supports LUKS2 in YaST Partitioner and AutoYaST partitioning
profiles. On IBM Z, SLES 15 SP7 can select `paes-xts-plain64` with a configured
Crypto Express adapter. CCA and EP11 modes are supported, EP11 requires CEX7S
or newer, and LUKS2 may use an AES data key or AES cipher key.

When changing Arm kernel page size, reinitialize swap, which destroys any
suspend image:

```sh
swapon --fixpgsz /dev/sdc1
```

A 4 KiB-block Btrfs filesystem works with the 64 KiB kernel. RAID 5 stripe size
is bounded by `PAGE_SIZE`, so avoid RAID 5 in comparisons between 4 KiB and
64 KiB kernel performance.

SLES 16 removes quota v1, OCFS2, ReiserFS, HFS+, and UFS. Migrate OCFS2 to the
read/write-capable GFS2 available only with SLE HA.

## XFS and EROFS

The later SLES 16.0 revision changes XFS log stripe-unit alignment. Revalidate
storage provisioning that assumes the previous alignment behavior. It also
removes `erofs` from the kernel module blacklist, so EROFS is no longer disabled
by that default policy. (16.0-rev-2026-08-04)
