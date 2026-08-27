# Images, Storage, and Extensions

## Image discovery and transfer

### Version-picked paths (256)

`systemd-vpick` chooses the newest UAPI-versioned file from a directory ending
in `.v/`. Nspawn, dissect, portabled, `RootImage=`, `RootDirectory=`,
`ExtensionImages=`, and `ExtensionDirectories=` understand the same protocol.

```sh
systemd-vpick --suffix=.conf ss.v/
```

### General image transfer (256)

`importctl` moves tar, raw, and filesystem images through `systemd-importd`. Pull,
import, export, and transfer-management verbs cover sysext, confext,
portable-service, nspawn, and vmspawn images, including machine-image work
formerly done with `machinectl`.

### Unprivileged DDIs and per-user images (256, 258)

`systemd-nsresourced` allocates transient 64K ID ranges and delegates mounts,
cgroups, and interfaces; `systemd-mountfsd` mounts Verity DDIs and returns
mount fds. This enables unprivileged dissect, user-manager `RootImage=`, and
`systemd-nspawn --image=`, with Polkit for untrusted images.

Image tools search `~/.local/state/machines/`; `systemd-dissect --all` includes
directory images, and `systemd-loop@.service` attaches an encoded path at boot.
Use `root=dissect` or `mount.usr=dissect` for complete DDI discovery and
automatic Verity metadata, `systemd.image_filter=` for label variants, and
`/dev/disk/by-designator/` for dissected partitions.

### Mountfsd controls (260)

`MakeDirectory()` accepts `mode`. `MountImage()` accepts per-partition
`mountOptions` and `relaxExtensionReleaseChecks`, and reports
`singleFileSystem` for a bare filesystem without GPT.

## Extensions and portable services

### Mutable and configured extensions (256, 259)

`systemd-sysext --mutable=` uses a writable upper layer below
`/var/lib/extensions.mutable/`; ephemeral mode uses tmpfs discarded on
reattach. Sysext and confext read `/etc/systemd/systemd-sysext.conf` and
`/etc/systemd/systemd-confext.conf` for mutability and DDI policy. Add overlay
options with `SYSTEMD_SYSEXT_OVERLAYFS_MOUNT_OPTIONS` and
`SYSTEMD_CONFEXT_OVERLAYFS_MOUNT_OPTIONS`.

### Refresh semantics (258, 260)

Service reload also reloads associated confext images, subject to
`RefreshOnReload=`. `systemd-sysext refresh` and `systemd-confext refresh` do
nothing when the image set is unchanged; use `--always-refresh=yes` to force
an unmount/remount.

### Portable image limits (258.10-261.2)

Portabled enforces configured pool limits for portable-service images; they no
longer bypass the pool budget.

## Repart and filesystem construction

### Filesystem construction controls (257)

Repart can compress offline-created filesystems using `Compression=` and
`CompressionLevel=`, create internal links through `MakeSymlinks=`, and read
`CopyBlocks=` from character devices. `SupplementFor=` adds a partition only
when another cannot meet its constraints.

### Validation and special partitions (258)

Minimum ESP/XBOOTLDR sizes are 100M on 512-byte-sector media and 260M on 4K
media. `Format=empty` creates an `_empty`, `NoAuto` sysupdate partition.
`AddValidateFS=` defaults on and records protected filesystem-use constraints;
`x-systemd.validatefs` in `/etc/fstab` pulls in
`systemd-validatefs@.service`, and a mismatch reboots immediately.

### Duplicate definitions, labels, and XBOOTLDR (259)

The last duplicate partition definition wins in `RootImageOptions=` and
mount-image parameters for `ExtensionImages=` and `MountImages=`. Automatic
dissection rejects non-VFAT XBOOTLDR; mount one explicitly through fstab if
another filesystem is deliberate.

The default LUKS label is the partition/filesystem label prefixed by `luks-`,
avoiding ambiguous `/dev/disk/by-label/` links. Set `VolumeLabel=` to override.

### Installer sizing and staged layout (259)

`systemd-repart -` calculates minimum required device size without changing a
device. `--defer-partitions-empty=yes` and
`--defer-partitions-factory-reset=yes` postpone `Format=empty` or
`FactoryReset=yes` partitions to first boot.

### Btrfs and live partition tables (259)

A `Subvolumes=` value ending in `:nodatacow` disables data CoW for that
subvolume. Repart and udevd use incremental `BLKPG` instead of `BLKRRPART`,
preserving unchanged in-kernel partitions while adding, removing, or growing
others.

### XFS population dependency (260)

Repart always uses `mkfs.xfs` directory population and no longer has the
protofile fallback. Populating XFS requires xfsprogs 6.17.0 or newer.

### Dry-run and JSON changes (258.10-261.2)

In v259.8, v260.4, and v261.2, repart skips generated files during dry runs,
while dissect JSON includes image size. Do not clean up files that a dry run
did not create, and accept the extra JSON field.

## Integrity, Verity, and encryption

### Integrity and external Verity data (259)

`systemd-integrity-setup` supports HMAC-SHA256, PHMAC-SHA256, and
PHMAC-SHA512. Mountfsd can mount a bare filesystem with separate Verity data
and signature files and control whether images with one root hash share the
device-mapper Verity volume.

### Encrypted image integrity (260)

Repart's `Integrity=`/`IntegrityAlgorithm=` configure dm-integrity for LUKS,
and dissection policy can require `encryptedwithintegrity`. Crypttab
`fixate-volume-key=` pins to a hash of the volume key; repart can generate the
metadata.

## Updates and imports

### Boot-time image imports (257)

`systemd-import-generator` schedules sysext, confext, portable-service,
nspawn, or vmspawn pulls from kernel-command-line or credential settings.

### Sysupdate feature groups (257)

The experimental `systemd-sysupdated` service exposes updates over D-Bus
through `updatectl`. Prefer `.transfer` over legacy `.conf`; `.feature` groups select
independent transfers, which may reference changelog and AppStream metadata.

### Acquisition without installation (260)

`systemd-sysupdate acquire` downloads without installing. A dated
`BEST-BEFORE-` SHA256SUMS filename rejects expired manifests, and partitions
may be marked partially downloaded.
