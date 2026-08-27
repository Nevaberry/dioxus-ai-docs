# Resource Control and Sandboxing

## Cgroups and workload limits

### Unified cgroups and zswap (256, 258)

Version 256 required an explicit transitional kernel override for legacy or
hybrid hierarchy; 258 removed cgroup v1 entirely. Use cgroup v2. Manager and
unit `MemoryZSwapWriteback=` controls `memory.zswap.writeback`.

### Managed OOM pressure timing (257)

`ManagedOOMMemoryPressureDurationSec=` selects the PSI measurement interval
used with `ManagedOOMMemoryPressureDurationLimit=`.

### Slice concurrency (258)

`ConcurrencySoftMax=` queues excess units; `ConcurrencyHardMax=` fails jobs
beyond the active-plus-queued limit. Nested slices create hierarchical pools.

### Managed directory quotas (258)

`StateDirectoryQuota=`/`Accounting=`, `CacheDirectoryQuota=`/`Accounting=`,
and `LogsDirectoryQuota=`/`Accounting=` use project quotas on ext4/XFS and
report usage in `systemctl status`; btrfs is unsupported.

### HugeTLB accounting and OOM counters (259)

On supporting kernels PID 1 mounts cgroup2 with
`memory_hugetlb_accounting`, charging HugeTLB to memory-controller use.
Process units expose kernel `OOMKills` separately from oomd
`ManagedOOMKills`.

### Oomd synchronous hooks (260)

Components can register a Varlink socket in the designated hook directory to
run synchronously before systemd-oomd kills a cgroup.

## Filesystem and namespace sandboxing

### System protection and soft mounts (256)

`ProtectSystem=` is also a manager setting and defaults on in the initrd; do
not assume initrd `/usr` is writable. Units use `WantsMountsFor=` for nonfatal
mount dependencies.

### Identity, temporary, cgroup, and PID namespaces (257)

`PrivateUsers=identity` identity-maps the first 65,536 IDs.
`PrivateTmp=disconnected` creates separate tmpfs `/tmp` and `/var/tmp`.
`ProtectControlGroups=private` provides private cgroup namespace/mount;
`strict` makes it read-only. `PrivatePIDs=yes` runs the service as PID 1 with a
matching private `/proc`.

### Sandbox resource plumbing (257)

`BindLogSockets=` controls logging socket bind mounts. Managed directory
settings accept trailing `:ro`; `ImportCredential=` can rename imported
credentials.

### Full user, hostname, and BPF namespaces (258)

`PrivateUsers=full` maps the full 32-bit ID range.
`ProtectHostname=private[:hostname]` gives a writable private hostname.
`DelegateNamespaces=` selects namespaces owned by the private user namespace.
`PrivateBPF=` and `BPFDelegate*=` create private bpffs and selectively
delegate operations.

### Existing and managed user namespaces (259, 260)

`UserNamespacePath=` joins an existing namespace. `PrivateUsers=managed`
asks nsresourced for a transient 65,536 UID/GID range.

### Early-boot PrivateTmp behavior (260)

For `PrivateTmp=yes` with `DefaultDependencies=no`, no explicit `/tmp`
requirement yields disconnected `/tmp`. With no explicit `/var` ordering,
no private `/var/tmp` is created; account for changed ordering and visibility.

### Nested namespace resource delegation (260)

Nsresourced can allocate multiple extra 64K ranges and vary client/foreign ID
mapping. Nspawn `--private-users-delegate=` exposes nsresourced and mountfsd
Varlink services to nested containers.

## Scheduling and execution resources

### Debug-only restart context (257)

`RestartMode=debug` sets `DEBUG_INVOCATION=1` and temporarily raises
`LogLevelMax=` to debug for automatic retries only.

### SCHED_EXT and transparent huge pages (260)

`CPUSchedulingPolicy=ext` chooses SCHED_EXT. `MemoryTHP=` independently
controls transparent huge pages for a service.
