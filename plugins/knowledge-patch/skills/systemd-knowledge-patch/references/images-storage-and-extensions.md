# Images, Storage, and Extensions

## Select versioned files and images

- A directory ending in `.v/` holds UAPI-versioned files. `systemd-vpick` selects the newest matching file, and nspawn, dissect, portabled, `RootImage=`, `RootDirectory=`, `ExtensionImages=`, and `ExtensionDirectories=` understand the same protocol (since 256).

```sh
systemd-vpick --suffix=.conf ss.v/
```

- Unprivileged image tools search `~/.local/state/machines/`. `systemd-dissect --all` includes directory images, and `systemd-loop@.service` attaches an encoded image path during boot (since 258).
- For duplicate partition definitions in `RootImageOptions=` and the mount-image parameters of `ExtensionImages=` and `MountImages=`, the last definition wins rather than the first (announced in 259 for 260).

## Transfer and pull images

- `importctl` transfers tar, raw, and filesystem images through `systemd-importd`. Pull, import, export, and transfer-management verbs cover system extensions, configuration extensions, portable services, and machine images (since 256).
- `systemd-import-generator` schedules extension, portable-service, nspawn, or vmspawn downloads during boot from the kernel command line or credentials (since 257).
- `systemd.pull=` and `rd.systemd.pull=` support `blockdev`, `bootorigin`, and `runtime=`. A pull can expose a raw image as a root block device or resolve relative to a network-loaded UKI. Initrd pulls default to `/run`; host pulls default to `/var` (since 258).
- `root=bind:` boots a downloaded tar tree through a bind-mounted root. `root=off` suppresses the initrd-to-host root transition (since 258).

```text
rd.systemd.pull=raw,machine,verify=no,blockdev:image:https://boot.example.invalid/image.raw root=/dev/disk/by-loop-ref/image.raw-part2
```

## Discover and mount DDIs

- `root=dissect` and `mount.usr=dissect` request full DDI discovery, including automatic Verity metadata. `systemd.image_filter=` selects partition-label variants (since 258).
- Automatically dissected XBOOTLDR partitions must be VFAT, like ESPs. Mount a deliberate non-VFAT XBOOTLDR explicitly through `/etc/fstab` (since 259).
- Mountfsd's `MountImage()` supports bare filesystem images with separate Verity data and signature files, and can decide whether images with the same root hash share a device-mapper Verity volume (since 259).
- `MountImage()` accepts per-partition `mountOptions` and `relaxExtensionReleaseChecks`; its result reports `singleFileSystem` for a bare filesystem without a GPT envelope. `MakeDirectory()` accepts `mode` (since 260).
- Mountfsd and nsresourced enable unprivileged, descriptor-based DDI mounting; see [Containers and Virtual Machines](containers-and-virtual-machines.md).

## Build partitioned images with repart

- `Compression=` and `CompressionLevel=` compress an offline-created filesystem internally. `MakeSymlinks=` creates links in the filesystem, and `CopyBlocks=` accepts character devices (since 257).
- `SupplementFor=` allocates a partition only when another partition cannot meet its constraints, such as an XBOOTLDR added only for an undersized ESP (since 257).
- ESP and XBOOTLDR minimum sizes are 100M on 512-byte-sector disks and 260M on 4K-sector disks. `Format=empty` creates an `_empty`, `NoAuto` partition suitable for sysupdate (since 258).
- `AddValidateFS=` defaults on and records protected filesystem-use constraints. `systemd-validatefs@.service` checks them; `x-systemd.validatefs` pulls the check into an fstab mount, and mismatch triggers immediate reboot (since 258).
- The default LUKS label is the partition/filesystem label prefixed by `luks-`, avoiding ambiguous `/dev/disk/by-label/` links. Set `VolumeLabel=` in the partition definition to override it (since 259).
- Pass `-` as the repart device to calculate the minimum required size without modifying a block device. `--defer-partitions-empty=yes` and `--defer-partitions-factory-reset=yes` let an installer postpone `Format=empty` or `FactoryReset=yes` partitions until first boot (since 259).
- A `Subvolumes=` entry ending in `:nodatacow` creates a btrfs subvolume with data copy-on-write disabled (since 259).
- Udevd and repart update live partition tables incrementally with `BLKPG` rather than `BLKRRPART`, adding, removing, or growing changed partitions while retaining unchanged kernel partition objects (since 259).
- Repart is available through Varlink (since 259). Populating XFS requires xfsprogs 6.17.0 or newer (since 260).

## Encrypt and verify images

- `systemd-integrity-setup` supports HMAC-SHA256, PHMAC-SHA256, and PHMAC-SHA512 (since 259).
- Repart's `Integrity=` and `IntegrityAlgorithm=` enable dm-integrity for LUKS volumes. An image-dissection policy can require it with `encryptedwithintegrity` (since 260).
- Partition definitions accept `TPM2PCRs=` and binary `KeyFile=` encryption inputs. Crypttab's `fixate-volume-key=` pins an entry to a hash derived from the volume key; repart can produce the needed metadata (since 259 and 260).
- Verity image loads can be measured into the dedicated `verity` NvPCR; see [Boot, UKIs, and TPM Policy](boot-uki-and-tpm.md).

## Manage system and configuration extensions

- `systemd-sysext --mutable=` adds a writable upper layer below `/var/lib/extensions.mutable/`. Ephemeral mode uses tmpfs and discards changes when extensions are reattached (since 256).
- Systemd-sysext and systemd-confext read persistent merge policy from `/etc/systemd/systemd-sysext.conf` and `/etc/systemd/systemd-confext.conf`. Add OverlayFS options with `SYSTEMD_SYSEXT_OVERLAYFS_MOUNT_OPTIONS` or `SYSTEMD_CONFEXT_OVERLAYFS_MOUNT_OPTIONS` (since 259).
- `systemd-sysext refresh` and `systemd-confext refresh` do nothing when the image set is unchanged. Use `--always-refresh=yes` to force unmount/remount behavior (since 260).
- OCI-backed MStacks can serve as service and container roots; see [Containers and Virtual Machines](containers-and-virtual-machines.md).

## Acquire system updates

- Experimental `systemd-sysupdated` exposes updates over D-Bus and is controlled with `updatectl`. Transfer files should use `.transfer` instead of the compatible legacy `.conf`; `.feature` files group independently selectable transfers. Definitions may link changelog and AppStream metadata (since 257).
- `systemd-sysupdate acquire` downloads without installing. SHA256SUMS manifests may use a dated `BEST-BEFORE-` filename whose expiration is enforced, and partitions can be marked partially downloaded (since 260).
