# Images, Storage, and Extensions

## Image discovery and transfer

### Versioned `.v/` selection (256)

`systemd-vpick` selects the newest UAPI-versioned file from a directory ending
`.v/`. Nspawn, dissect, portabled, `RootImage=`, `RootDirectory=`,
`ExtensionImages=`, and `ExtensionDirectories=` understand the same protocol.

### General image transfer (256)

`importctl` moves tar, raw, and filesystem images through importd. Pull,
import, export, and transfer management cover sysext, confext,
portable-service, nspawn, and vmspawn images.

### Boot-time image imports (257, 258)

`systemd-import-generator` schedules sysext, confext, portable, nspawn, or
vmspawn downloads from kernel-command-line or credential configuration.
`systemd.pull=`/`rd.systemd.pull=` supports `blockdev`, `bootorigin`, and
`runtime=`. Initrd pulls default to `/run`, host pulls to `/var`; a downloaded
raw image may become the root block device. `root=bind:` boots a downloaded tar
tree and `root=off` prevents initrd-to-host transition.

### Per-user images and DDI root discovery (258)

Unprivileged tools search `~/.local/state/machines/`; `systemd-dissect --all`
includes directories, and `systemd-loop@.service` attaches an encoded path at
boot. `root=dissect` and `mount.usr=dissect` request full DDI/Verity discovery;
`systemd.image_filter=` chooses partition-label variants, and udev exposes
partitions below `/dev/disk/by-designator/`.

### XBOOTLDR must be VFAT (259)

Automatic image dissection rejects non-VFAT XBOOTLDR, like ESP. Mount an
intentional non-VFAT XBOOTLDR explicitly through fstab.

## Repart and filesystem construction

### Filesystem controls (257)

Repart can use `Compression=`/`CompressionLevel=`, create filesystem links via
`MakeSymlinks=`, and read `CopyBlocks=` from character devices.
`SupplementFor=` creates a partition only when another cannot satisfy its
constraints.

### Metadata and validation (258)

Minimum ESP/XBOOTLDR sizes are 100M on 512-byte-sector disks and 260M on 4K.
`Format=empty` creates an `_empty`, `NoAuto` partition for sysupdate.
`AddValidateFS=` records filesystem-use constraints; a mismatch pulled in by
`x-systemd.validatefs` triggers an immediate reboot.

### LUKS and filesystem labels (259)

The default LUKS superblock label is `luks-` plus the partition/filesystem
label. Set `VolumeLabel=` in a partition definition when old naming is needed.

### Sizing, deferred layouts, and subvolumes (259)

`systemd-repart -` calculates minimum device size without modifying a device.
Installers can defer `Format=empty` and `FactoryReset=yes` partitions using
`--defer-partitions-empty=yes` and
`--defer-partitions-factory-reset=yes`. A `Subvolumes=` entry ending
`:nodatacow` creates a btrfs no-data-CoW subvolume.

### Live partition table changes (259)

Udevd and repart use incremental `BLKPG` add/remove/grow operations rather
than `BLKRRPART`, preserving unchanged in-kernel partition objects.

### XFS population requirement (260)

Populating XFS requires xfsprogs 6.17.0+ because repart unconditionally uses
`mkfs.xfs` directory population and removed its protofile fallback.

### Dry runs and JSON (258.10-261.2)

In v259.8, v260.4, and v261.2, repart dry runs skip generated files, and
dissect JSON includes image size. Do not clean up files a dry run did not
generate; tolerate the extra JSON field.

## Extensions and image policy

### Mutable system extensions (256)

`systemd-sysext --mutable=` attaches a writable upper layer under
`/var/lib/extensions.mutable/`; ephemeral mode uses tmpfs discarded on
reattach.

### Confext reload and persistent merge policy (258, 259)

Reloading a service reloads associated confext images. Sysext/confext read
`/etc/systemd/systemd-sysext.conf` and
`/etc/systemd/systemd-confext.conf` for mutability and DDI policy. Supply
overlay options with `SYSTEMD_SYSEXT_OVERLAYFS_MOUNT_OPTIONS` and
`SYSTEMD_CONFEXT_OVERLAYFS_MOUNT_OPTIONS`.

### No-op refresh (260)

Sysext/confext refresh does not unmount/remount when the image set is
unchanged. Use `--always-refresh=yes` to force it.

## Integrity, Verity, and mountfsd

### Bare image Verity and integrity algorithms (259)

`systemd-integrity-setup` supports HMAC-SHA256, PHMAC-SHA256, and
PHMAC-SHA512. Mountfsd `MountImage()` can attach bare filesystem images with
separate Verity data/signatures and choose whether equal root hashes share a
device-mapper Verity volume.

### Richer mountfsd controls (260)

`MakeDirectory()` accepts `mode`; `MountImage()` accepts per-partition
`mountOptions` and `relaxExtensionReleaseChecks`, and reports
`singleFileSystem` for a bare filesystem without GPT.

### Encrypted image integrity (260)

Repart `Integrity=`/`IntegrityAlgorithm=` enables dm-integrity for LUKS;
dissection policy can require `encryptedwithintegrity`. Crypttab
`fixate-volume-key=` pins to a volume-key-derived hash.

## System updates and portable images

### Transfer definitions and feature groups (257)

Experimental sysupdated is controlled by `updatectl`. Prefer `.transfer` over
legacy `.conf`; `.feature` groups independently selectable transfers, and
definitions can point to changelog and AppStream metadata.

### Acquisition separate from installation (260)

`systemd-sysupdate acquire` downloads without installing. SHA256SUMS can use
dated `BEST-BEFORE-` filenames whose expired manifests are rejected;
partitions may be marked partially downloaded.

### Portable pool enforcement (258.10-261.2)

V260.4 and v261.2 count portable-service images against configured portabled
pool limits.
