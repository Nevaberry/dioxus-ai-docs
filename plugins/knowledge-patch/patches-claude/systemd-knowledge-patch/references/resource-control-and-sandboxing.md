# Resource Control and Sandboxing

## Cgroup accounting and workload limits

### Zswap, OOM inputs, and HugeTLB (256, 257, 259)

`MemoryZSwapWriteback=` controls `memory.zswap.writeback`. Generators receive
`SYSTEMD_SOFT_REBOOTS_COUNT`, and
`ManagedOOMMemoryPressureDurationSec=` chooses the PSI interval used with
`ManagedOOMMemoryPressureDurationLimit=`. On supporting kernels, PID 1 mounts
cgroup2 with `memory_hugetlb_accounting`, so HugeTLB contributes to overall
cgroup memory usage.

### Slice concurrency and directory quotas (258)

`ConcurrencySoftMax=` queues excess slice members; `ConcurrencyHardMax=` fails
jobs beyond the active-and-queued limit. Nested slices create hierarchical
pools. `StateDirectoryAccounting=`/`StateDirectoryQuota=`,
`CacheDirectoryAccounting=`/`CacheDirectoryQuota=`, and
`LogsDirectoryAccounting=`/`LogsDirectoryQuota=` enforce ext4/XFS project
quotas and expose usage in `systemctl status`; btrfs is unsupported.

### Per-unit OOM counters and pre-kill hooks (259, 260)

Process-spawning units expose `OOMKills` for kernel kills and
`ManagedOOMKills` for systemd-oomd kills. Components may register a Varlink
hook in oomd's designated hook directory to run synchronously before a cgroup
is killed.

## User and process namespaces

### Namespace modes (257, 258, 260)

- `PrivateUsers=identity` identity-maps the first 65,536 IDs.
- `PrivateUsers=full` identity-maps the complete 32-bit ID range.
- `PrivateUsers=managed` asks nsresourced for a transient 65,536-ID range.
- `PrivatePIDs=yes` makes the service PID 1 in a private PID namespace with a
  matching `/proc`.
- `ProtectControlGroups=private` creates a private cgroup namespace and mount;
  `strict` also makes it read-only.
- `ProtectHostname=private[:hostname]` provides a writable private hostname.

### Namespace and BPF delegation (258)

`DelegateNamespaces=` selects namespaces owned by the unit's private user
namespace. `PrivateBPF=` supplies a private bpffs; use the `BPFDelegate*=`
settings to grant only the required BPF operations.

### Join an existing namespace (259)

`UserNamespacePath=` puts a service in an existing user namespace. Transient
services may receive their root through `RootDirectoryFileDescriptor` rather
than a path.

## Filesystem and execution isolation

### Manager protection and sandbox resources (256, 257)

`ProtectSystem=` is a manager setting and is enabled by default in the initrd,
so initrd code must not assume `/usr` is writable. `BindLogSockets=` controls
whether logging sockets enter a mount sandbox. `StateDirectory=`,
`RuntimeDirectory=`, `CacheDirectory=`, `LogsDirectory=`, and
`ConfigurationDirectory=` accept trailing `:ro`; `ImportCredential=` can
rename imported credentials.

### Private temporary directories (257, 260)

`PrivateTmp=disconnected` supplies separate tmpfs mounts for `/tmp` and
`/var/tmp`. For early-boot units combining `PrivateTmp=yes` with
`DefaultDependencies=no`, no explicit `/tmp` requirement now means a
disconnected `/tmp`; without explicit `/var` ordering there is no private
`/var/tmp`, which can alter visibility and ordering.

### Schedulers and huge pages (260)

`CPUSchedulingPolicy=ext` selects SCHED_EXT. `MemoryTHP=` independently
controls transparent-huge-page behavior for a service.
