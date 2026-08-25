# Kernel and Hardware Behavior

## Accounting, limits, and development

On kernels 5.14 and later, `iotop` needs task delay accounting for SWAPIN and IO
percentages. Boot with `delayacct` or enable it at runtime:

```sh
sysctl -w kernel.task_delayacct=1
```

Leap 16's kernel is built with GCC 13, not the default compiler. Install `gcc13`
and invoke `gcc-13` for external modules and kernel rebuilds; this compiler is
supported only for those uses.

Leap 16 `libpulp` live-patches glibc and OpenSSL binaries on x86-64 and ppc64le;
other libraries and architectures are outside its userspace-live-patching scope.
Its kernel also exposes `MADV_GUARD_INSTALL` through `madvise()` for lightweight
guard regions without conventional mapped backing. (leap-16.0-guide)

For SLES 15 SP6, non-overridable `CONFIG_HZ` is 250 on x86-64 and Arm and 100 on
POWER and IBM Z; retest timing-sensitive Arm software. Documented logical-CPU
limits are 8192 on x86-64, 512 on IBM Z, 2048 on POWER, and 768 on Arm. The
theoretical/certified RAM limits are over 1 PiB/64 TiB, 10 TiB/256 GiB,
1 PiB/64 TiB, and 256 TiB/no stated certified limit respectively; block devices
may reach 8 EiB.

Loading an externally supported kernel module no longer sets a taint flag. Do
not use that bit to detect the module.

Pair `libbpf`, `bpftool`, BCC, and `bpftrace` with a kernel from the same product.
BCC and `bpftrace` also need matching `kernel-*-devel` headers, or built-in BTF
for `bpftrace`, when accessing kernel types.

## Scheduling, topology, and known limitations

SLES 15 SP7 can enable `CONFIG_RT_GROUP_SCHED` with the `rt_group_sched` boot
parameter and backports cgroup v2 CPU load balancing.

PMU features are unreliable on Intel hybrid CPUs because the SP7 6.4 kernel
lacks required 6.9 changes. Do not depend on PMU profiling there. The updated
SMC driver can freeze SP7 systems; avoid it for workloads unable to tolerate a
host hang until maintenance provides the stated fix.

`IDXD: user: probe of wq1.0 failed with error -95` can be harmless in some
configurations and is not, by itself, proof of failed setup.

`hwloc` 2.11 adds:

- `hwloc-calc --cpuset-output-format systemd-dbus-api` for `AllowedCPUs` data.
- `--cpuset-input-format list` for bit lists.
- `hwloc-info --get-attr` for a single attribute.
- `--cpuset-output-format` in place of `--taskset`.

`HWLOC_MEMBIND_WEIGHTED_INTERLEAVE` and the `weighted` binding policy require
Linux 6.9 or later and therefore do not work on the stock SP7 6.4 kernel.

The default side-channel mitigation policy is `Auto`, whose represented boot
parameters can change between service packs. Revalidate effective mitigations
after every upgrade.

## Kdump, drivers, and hardening

On POWER, replace custom Kdump `maxcpus` arguments with `nr_cpus`; packaged
configuration migrates automatically but custom scripts do not.

SLES 16.0 uses kernel 6.12. Its filesystem removals and migration requirements
are detailed in [storage-filesystems.md](storage-filesystems.md).

AMD EPYC Turin and later use AMD P-State by default, with Energy Performance
Preference and autonomous workload-driven frequency scaling.

The SLES 16.0 revision removes `erofs` from the kernel module blacklist. It also
enables regular-file security protection by default and centralizes kernel
hardening in a `tuned` profile; check workloads against the hardened file
behavior and make compliance automation profile-aware.
