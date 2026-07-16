# Storage, kernel, and hardware

## Kernel baseline, interfaces, and mitigations

### Kernel baseline and newly enabled interfaces

The 9.8 kernel baseline is `5.14.0-687.5.3`, with `io_uring` asynchronous I/O available. PowerPC gains BPF trampolines and `STRUCT_OPS`, Intel QAT GEN6 uses the new `qat_6xxx` driver, and Wildcat Lake IAA support moves from Technology Preview to full support. (9.8)

### New and changed kernel boot parameters

New controls include `arm64.nompam`, `cgroup_v1_proc={true|false}`, `initramfs_options=`, `nvme.quirks=<vendor>:<product>:<quirks>`, `rh_waived=<items>`, and `vmscape={off|ibpb|force}`. VMscape mitigation defaults to `ibpb`. Waived features can weaken security or support status. `mitigations=off` also implies `vmscape=off`; `mitigations=auto` remains the default. (9.8)

### Transient Scheduler Attack mitigation

The `tsa=` kernel parameter controls AMD Transient Scheduler Attack mitigation. `on` is the default. `off`, `user`, and `vm` disable it entirely or restrict it to user-to-kernel or guest-to-host transitions. (10.2)

### Kernel parameter and core-dump changes

`microcode.force_minrev=` is removed; use the `force_minrev` option of `microcode=`. The `core_sort_vma=1` sysctl writes small VMAs first in core files but can break elfutils. `%F` in `core_pattern` expands to the crashing task's pidfd number. (10.2)

### Fanotify permission-event watchdog

Write a timeout to `/proc/sys/fs/fanotify/watchdog_timeout` to enable the otherwise-disabled watchdog. It logs the PID and name of a task responsible for a fanotify permission-event hang. (10.2)

### EEVDF scheduler tuning

EEVDF replaces CFS as the default scheduler. Rename `sched_min_granularity` tuning to `sched_base_slice`; `sched_wakeup_granularity` is unused and removed.

### Kernel-module ELF addresses in live-patch tooling

The `klp-build` and `objtool` path can give kernel-module sections such as `.text` nonzero `sh_addr` values. Update in-house ELF parsers. Use release 10-compatible elfutils or SystemTap instead of assuming module sections begin at address zero.

## LUKS, snapshots, and crash recovery

### Cryptsetup 2.8 token-aware re-encryption

`cryptsetup reencrypt` can re-encrypt LUKS2 devices with bound tokens. Version 2.8 supports NVMe inline mode for authenticated encryption and integrity devices, avoiding the double writes from `dm-integrity` journaling. (9.8)

### Snapshot sets as working and boot environments

Snapm 0.7 adds `snapset mount`, `umount`, `exec`, and `shell`, plus a Difference Engine with path, JSON, diff, summary, and tree output. System Role integration can request a `bootable` snapshot set so a host can boot directly into it. (9.8)

## Multipath, clustered storage, and volume management

### Automatic removal of disconnected LUNs

Set `purge_disconnected yes` in the `defaults`, `devices`, or `multipaths` section of `multipath.conf` so `multipathd` removes disconnected SCSI devices. This avoids indefinitely queued I/O and writes to a removed and repurposed LUN. (9.8)

### LVM persistent reservations

LVM can manage persistent reservations at volume-group scope for shared clustered storage. See `lvmpersist(8)` for the administration interface. (10.2)

### Encrypted Stratis pool keys

Stratis 3.8 keeps an unlocked encrypted pool's volume key in the `stratisd` process keyring so automatic pool extension can proceed. It removes the key when the daemon exits or the pool stops or is destroyed. (10.2)

### NVMe/TLS PSK compatibility break

Technology Preview NVMe/TLS now follows standard TLS key derivation. This can break PSKs imported by `nvme-cli` before 2.16 or `libnvme` before 1.16. Retry import with `--compat` for an old target; if an upgraded target still fails, reprovision its PSKs. (10.2)

### Resilient Storage and GFS2 removal

The Resilient Storage Add-On and GFS2 are unsupported in release 10. Keep workloads that require GFS2 on an earlier supported major release or migrate them to another storage design before upgrading.

### In-kernel VDO migration

In-kernel `dm-vdo` replaces `kmod-kvdo`. VDO-specific `sysfs` configuration and statistics are removed except module-level `log_level`. Query targets with `dmsetup message stats`, `dmsetup status`, and `dmsetup table`. Settings formerly changed through removed `sysfs` parameters cannot be changed there.

### RAID and NVMe multipath removals

The `md-faulty` and `md-multipath` kernel modules are removed. DM Multipath for NVMe over RDMA or Fibre Channel is unsupported, `nvme_core.multipath` is removed, and native NVMe multipath is always enabled.

### XFS format and size requirements

Release 10 cannot mount XFS V4. Back up its data, create an XFS V5 file system, and restore before migration. `mkfs.xfs` refuses file systems smaller than 300 MB; use `ext4` for smaller file systems.

## Hardware and driver audit

### Hardware support audit

The `firewire_core`, `mlx4`, `nfp`, `qla3xxx`, `qla4xxx`, `rdma_rxe`, and `usnic_verbs` drivers are removed. Numerous older storage, network, and netfilter drivers are unmaintained, including `aacraid`, `bnx2*`, `e1000`, `hpsa`, legacy MPT, `myri10ge`, `netxen_nic`, `nvmet_fc`, `nvmet_tcp`, `team`, and selected `be2net`, `lpfc`, `megaraid_sas`, `mpt3sas`, `qla2xxx`, and `sfc` device IDs. Audit hardware with `lspci -nn` before upgrading.

### QLogic firmware-update prerequisite

Firmware updates for QLE2772C and QLE2872C adapters can fail with error 541. Verify that `/sys/class/scsi_host/hostXX/mpi_fw_state` exists. If the inbox driver lacks it, install out-of-box `qla2xxx` 10.02.13.00 or newer before retrying. (9.8)
