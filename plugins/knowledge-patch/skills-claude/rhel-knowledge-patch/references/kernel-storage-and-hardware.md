# Kernel, Storage, and Hardware

Consult this reference for kernel boot controls, patching and tracing, Secure Boot, hardware enablement, filesystems, LVM, multipath, snapshots, VDO, and NVMe.

## Contents

- [Kernel execution and boot controls](#kernel-execution-and-boot-controls)
- [Kernel patching, observability, and real-time tooling](#kernel-patching-observability-and-real-time-tooling)
- [Secure Boot and hardware enablement](#secure-boot-and-hardware-enablement)
- [Filesystems, LVM, multipath, snapshots, and NVMe](#filesystems-lvm-multipath-snapshots-and-nvme)

## Kernel execution and boot controls

### Restricted `io_uring` access (10.0)

`io_uring` is a Technology Preview and is disabled for every process by default with `kernel.io_uring_disabled=2`. Set it to `0` for all users or `1` to limit creation to `CAP_SYS_ADMIN` or members of `io_uring_group`; the new `kernel.io_uring_group` defaults to `-1`, meaning capability-only access.

### External kernel controls (10.0)

New boot controls include `accept_memory=lazy|eager`, `ia32_emulation=true|false`, `spec_rstack_overflow=` mitigations (default `safe-ret`), and `workqueue.unbound_cpus=`. AMD IOMMU adds `pgtbl_v1` (default), `pgtbl_v2`, and `irtcachedis`; `cpu0_hotplug` and `sysfs.deprecated` are removed.

### New kernel operating features (10.0)

The EFIVARS pstore backend can be enabled at runtime with `echo N > /sys/module/efi_pstore/parameters/pstore_disable` and switched without rebooting. Landlock is available for process self-confinement, while disabled waived kernel features require the new `rh_waived` boot parameter.

### New speculative-execution controls (10.1)

`indirect_target_selection=on|off|force|vmexit|stuff` controls Intel ITS mitigation and defaults to `on`; `tsa=on|off|user|vm` controls AMD Transient Scheduler Attack mitigation and also defaults to `on`. `mitigations=off` now includes `indirect_target_selection=off` on x86.

### ARM, PCI, and scheduler boot controls (10.1)

ARM KVM adds `kvm-arm.mode=nvhe|protected|nested`; protected mode disables host kexec and hibernation, while nested mode requires FEAT_NV2 hardware and is experimental. Other additions include `preempt=lazy`, `pcie=notph`, and the `external` per-port value for `libata.force=`.

### Shared-memory huge-page controls (10.1)

`thp_shmem=` can set an `always`, `inherit`, `never`, `within_size`, or `advise` policy for individual THP sizes or size ranges and can be repeated. `transparent_hugepage_shmem=` separately accepts `always`, `within_size`, `advise`, `never`, `deny`, or `force` for the internal shmem mount.

### Entropy-source default (10.1)

`rng-tools` disables jitter entropy by default to avoid unnecessary CPU use on systems with hardware entropy or `/dev/hwrng`. Older systems without either source must explicitly re-enable jitter in `/etc/sysconfig/rngd`.

### Microcode, NVMe, and VMscape boot controls (10.2)

The new `microcode=` control accepts `base_rev=X`, `dis_ucode_ldr`, and `force_minrev`, replacing the removed `microcode.force_minrev=` parameter; `nvme.quirks=VID:PID:quirk,...` can augment or disable built-in device quirks. `vmscape=off|ibpb|force` controls the new VMscape mitigation and defaults to `ibpb`, while `mitigations=off` now disables it too.

### Core-dump and VSOCK namespace controls (10.2)

`core_pattern` gains `%F` for the crashing task's pidfd, while `core_sort_vma=1` writes VMAs smallest-first for truncated dumps but is known to break elfutils. `net.vsock.child_ns_mode=global|local` chooses the AF_VSOCK isolation inherited by new network namespaces; its first write is permanent, and a local namespace cannot create global children.


## Kernel patching, observability, and real-time tooling

### Kernel patching and BPF tooling (10.1)

`kpatch-dnf` now steers kernel updates toward versions supported by kpatch, and `rteval` uses `rtla timerlat` as its default measurement module while allowing `cyclictest` through `rteval.config`. The 6.14-level BPF subsystem adds uprobe sessions, `bpf_fastcall`, a `kmem_cache` iterator, eligible-program private stacks, and verifier improvements; `perf annotate --code-with-type` and drgn's debuginfod/module APIs expand analysis.

### Kdump encryption and live-patch reporting (10.2)

On x86_64, `kdumpctl setup-crypttab` passes a LUKS volume key into the crash kernel so `vmcore` can be written to encrypted storage. Kpatch now reports which CVEs the running base kernel has remediated through live patches.

### BPF and real-time tooling (10.2)

The 6.17-level BPF API adds dynamic-pointer copying, dentry and cgroup xattr helpers, rbtree traversal, DMA-buffer iteration, BTF delegation and `mmap`, atomic map-of-maps updates, and `load_acquire`, `store_release`, and timed `may_goto` instructions. The `function_graph` tracer can display return values, `rtla` can trigger userspace actions, `rteval` gains a `measurement-module` override, `kernel-tools-libs-devel` ships cpupower Python bindings, and `tuna cpu_power` manages CPU idle states.


## Secure Boot and hardware enablement

### Signed Secure Boot shim (10.1)

RHEL 10.1 ships signed shim binaries for x86_64 and aarch64, enabling enforced Secure Boot on both architectures. The x86_64 shim carries Red Hat Secure Boot CAs 5 and 8, while aarch64 carries CA 8, with updated SBAT entries.

### RHEL-distributed accelerator drivers (10.1)

Signed partner GPU and accelerator stacks such as NVIDIA/CUDA and AMD/ROCm can be managed through RHEL channels and Secure Boot. Install `rhel-drivers`, then run `rhel-drivers install --auto-detect` for the matching stack.

### UKI boot entries and Secure Boot (10.2)

BLS snippets under `/boot/efi/loader/entries` can use `efi /EFI/Linux/IMAGE.efi` instead of `linux` to boot a UKI. PowerVM LPARs gain dynamic enrollment of Secure Boot verification keys, and x86_64/aarch64 shim binaries carry both Microsoft 2011 and 2023 UEFI signatures alongside the existing RHEL signature.


## Filesystems, LVM, multipath, snapshots, and NVMe

### Snapshot Manager and multipath behavior (10.0)

The new `snapm` tool coordinates multi-volume system snapshots, Boom boot entries, rollback, and snapshot boot. `multipathd.socket` is no longer enabled by default, reconfiguration reloads only changed devices unless `multipathd reconfigure all` is used, and automatic ALUA policy detection is enabled through `detect_pgpolicy` with optional `group_by_tpg` grouping.

### VDO and NVMe Opal management (10.0)

In-kernel `dm-vdo` replaces `kmod-kvdo`; VDO-specific sysfs configuration and statistics disappear in favor of `dmsetup message stats`, `dmsetup status`, and `dmsetup table`. `nvme sed discover|initialize|lock|unlock|password|revert` now automates Opal management, with `revert -e` performing a destructive reset.

### Network filesystems, atomic writes, and RAID checks (10.0)

NFS over TLS is supported even though general-purpose kTLS remains a Technology Preview. CIFS creates native SMB symlinks by default and supports `reparse=default|nfs|wsl` for special files; `RWF_ATOMIC` adds torn-write protection, and `raid-check.service` is enabled by default.

### Removed networking and storage interfaces (10.0)

Network teams must become bonds, `dhclient` must become NetworkManager's internal client, and the ConnectX-3 `mlx4` driver is absent. Native NVMe multipath is permanently enabled, DM multipath for NVMe is unsupported, XFS V4 cannot mount, GFS2/Resilient Storage and `md-faulty`/`md-multipath` are gone, and `kexec_file_load` replaces `kexec_load`.

### Kernel and storage caveats (10.0)

Do not reduce SR-IOV VF counts at runtime on IOMMU/page-pool systems because the kernel can panic. Asynchronous NVMe scanning makes `/dev/nvmeXnY` unstable across boots, XFS enables `rmapbt` despite possible small-write regressions (`mkfs.xfs -m rmapbt=0` disables it), and uninstalling `kernel-uki-virt` with package tools can also remove the conventional kernel.

### Multipath container access and LVM RAID repair (10.1)

`multipathd` listens on the bind-mountable `/run/multipathd.socket` in addition to its abstract socket, enabling management from containers. After temporarily missing RAID4/5/6 members reappear, unmount and deactivate the volume before running `lvconvert --repair /dev/VG/LV`, even when the outage exceeded the RAID level's fault tolerance.

### iSCSI-backed LVM caveat (10.1)

A non-root logical volume spanning local and iSCSI storage can fail to activate after reboot because Anaconda omits automatic startup for the iSCSI node. Create the LV after installation or set `node.startup=automatic` in its `/var/lib/iscsi/nodes/` configuration.

### Corrected 10.0 operating caveats (10.1)

Reducing SR-IOV VF counts no longer panics IOMMU/page-pool hosts, and misaligned guest discards no longer pause a VM under `werror=stop`, although configuring `discard_granularity` remains preferable. `virtiofsd` stays alive after an open-file-limit error, and the deprecated ReaR `IPL` output again uses `vmlinuz-$kernel_version` plus `initrd.cgz`; portable `RAMDISK` output retains the RHEL 10 names.

### Fanotify, io_uring, and shared LVM (10.2)

An optional `fs.fanotify.watchdog_timeout` logs the task responsible for stalled permission events. `io_uring` moves into the regular 10.2 feature set for asynchronous I/O, and LVM gains volume-group persistent-reservation management through `lvmpersist` for shared storage.

### Stratis, Snapm, and disconnected LUNs (10.2)

Stratis keeps encrypted-pool volume keys in the `stratisd` process keyring so automatic pool extension can proceed after unlock. Snapm adds `snapset mount|umount|exec|shell` and multiple diff formats, while `purge_disconnected yes` in `multipath.conf` makes multipathd remove disconnected SCSI devices rather than leave queued or misdirected I/O.

### VDO capacity planning (10.2)

The new `vdocalculatesize` utility calculates VDO volume and memory requirements from logical size, physical size, slab size, index memory, and block-map cache inputs.

### NVMe/TLS compatibility break (10.2)

The preview NVMe/TLS implementation now follows standard PSK derivation, breaking keys imported by `nvme-cli` before 2.16 or `libnvme` before 1.16. Retry imports with `--compat` for old targets; after a target upgrade, re-provision the PSK if compatibility mode still fails.

