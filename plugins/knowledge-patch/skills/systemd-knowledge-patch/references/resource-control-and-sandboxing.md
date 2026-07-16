# Resource Control and Sandboxing

## Enforce a unified cgroup hierarchy

- Cgroup v1 was force-enableable in 256 but removed in 258; current boot and nspawn operation require unified cgroup v2.
- PID 1 mounts cgroup2 with `memory_hugetlb_accounting` when the kernel supports it, so HugeTLB usage contributes to a cgroup's memory-controller accounting (since 259).
- `MemoryZSwapWriteback=` controls the kernel's `memory.zswap.writeback` cgroup knob (since 256).

## Create private namespaces

- `PrivateUsers=identity` creates a user namespace with identity mappings for the first 65,536 IDs. `PrivateUsers=full` identity-maps the full 32-bit UID range (since 257 and 258).
- `PrivateUsers=managed` asks `systemd-nsresourced` for a dynamic, transient range of 65,536 UIDs and GIDs (since 260).
- `PrivatePIDs=yes` runs a service as PID 1 in a private PID namespace with matching `/proc` (since 257).
- `ProtectHostname=private[:hostname]` provides a writable private hostname (since 258).
- `UserNamespacePath=` joins a service to an existing user namespace (since 259).

```ini
[Service]
PrivateUsers=managed
ProtectHostname=private:worker
PrivatePIDs=yes
```

## Isolate temporary files and cgroups

- `PrivateTmp=disconnected` supplies separate tmpfs mounts for both `/tmp` and `/var/tmp` (since 257).
- For an early-boot unit combining `PrivateTmp=yes` and `DefaultDependencies=no`, an absent explicit `/tmp` requirement now yields a disconnected `/tmp`. Without explicit `/var` ordering, no private `/var/tmp` mount is created (since 260).
- `ProtectControlGroups=private` creates a private cgroup namespace and mount; `strict` also makes it read-only (since 257).
- `ProtectSystem=` is also a manager setting and defaults on in the initrd, so initrd code must not assume `/usr` is writable (since 256).

## Delegate namespace and BPF capabilities

- `DelegateNamespaces=` selects namespaces owned by a unit's private user namespace (since 258).
- `PrivateBPF=` creates a private bpffs. The `BPFDelegate*=` settings selectively delegate BPF operations (since 258).
- Nsresourced can delegate multiple UID/GID ranges and its resources to nested containers; see [Containers and Virtual Machines](containers-and-virtual-machines.md).

## Limit slices and service storage

- `ConcurrencySoftMax=` queues excess units in a slice until capacity becomes available. `ConcurrencyHardMax=` fails jobs beyond the hard active-plus-queued limit. Nested slices form hierarchical workload pools (since 258).
- `StateDirectoryQuota=`/`StateDirectoryAccounting=`, `CacheDirectoryQuota=`/`CacheDirectoryAccounting=`, and `LogsDirectoryQuota=`/`LogsDirectoryAccounting=` enforce per-unit project quotas and expose usage in `systemctl status` (since 258).
- Managed-directory quotas support ext4 and XFS, not btrfs (since 258).

## Control service resources and scheduling

- `StateDirectory=`, `RuntimeDirectory=`, `CacheDirectory=`, `LogsDirectory=`, and `ConfigurationDirectory=` accept a trailing `:ro`. `BindLogSockets=` controls whether logging AF_UNIX sockets enter a mount sandbox (since 257).
- `CPUSchedulingPolicy=ext` selects the kernel SCHED_EXT scheduler. `MemoryTHP=` independently controls transparent huge pages for a service (since 260).
- `ManagedOOMMemoryPressureDurationSec=` chooses the PSI measurement interval used with `ManagedOOMMemoryPressureDurationLimit=` (since 257).
- Other components can register a Varlink socket in the designated hook directory to run synchronously before systemd-oomd kills a cgroup (since 260).
