# Kernel and Hardware Behavior

## Accounting, limits, and build compatibility

### I/O accounting for `iotop` (`leap-15.6`)

On kernels 5.14 and later, `iotop` cannot show SWAPIN and IO percentages unless
task delay accounting is active. Add the `delayacct` boot parameter or enable it
at runtime:

```sh
sysctl -w kernel.task_delayacct=1
```

### Kernel and module compiler (`leap-16.0-guide`)

The Leap 16 kernel is built with GCC 13 rather than the distribution's default
compiler. Install `gcc13` and invoke `gcc-13` for external module and kernel
builds. This compiler is supported only for those uses.

### Userspace live patching (`leap-16.0-guide`)

`libpulp` can live-patch `glibc` and OpenSSL binaries on x86-64 and ppc64le.
Other libraries and architectures are outside the stated scope.

### Lightweight guard regions (`leap-16.0-guide`)

Use `madvise()` with `MADV_GUARD_INSTALL` to install lightweight guard regions
over address ranges without conventional mapped backing regions.

### External modules and taint on SLES 15 SP6

Loading an externally supported kernel module no longer sets the former taint
flag. Do not use that bit to detect whether an external module is loaded.

### Timer frequency and sizing limits

On SLES 15 SP6, non-overridable `CONFIG_HZ` is 250 Hz on x86-64 and Arm and 100
Hz on POWER and IBM Z. Retest timing-sensitive applications that assumed Arm's
former 100 Hz value.

Documented logical-CPU limits are 8192 on x86-64, 512 on IBM Z, 2048 on POWER,
and 768 on Arm. Theoretical/certified memory limits are over 1 PiB/64 TiB on
x86-64, 10 TiB/256 GiB on IBM Z, 1 PiB/64 TiB on POWER, and 256 TiB/no stated
certified limit on Arm. Block devices can reach 8 EiB.

### BPF tool and kernel pairing

On SLES 15 SP6, `libbpf`, `bpftool`, BCC, and `bpftrace` are supported only with
a kernel from the same product. BCC and `bpftrace` also need matching
`kernel-*-devel` headers, or built-in kernel BTF for `bpftrace`, when accessing
kernel data types.

## SLES 15 SP7 scheduling and diagnostics

### CPU scheduling additions

Enable `CONFIG_RT_GROUP_SCHED` at boot with `rt_group_sched`. The SP7 kernel
also backports cgroup v2 CPU load balancing, so real-time and container
schedulers can use it without changing kernel lines.

### Intel hybrid CPU PMU limitation

PMU features do not work correctly on Intel hybrid CPUs because SP7 uses kernel
6.4 and lacks changes from kernel 6.9. Do not rely on PMU profiling or monitoring
on those processors.

### SMC freeze risk

The updated Shared Memory Communications (`smc`) driver can freeze the host.
Avoid it for workloads that cannot tolerate a hang until a maintenance update
provides the stated fix.

### Harmless IDXD probe message

`IDXD: user: probe of wq1.0 failed with error -95` can appear in certain
configurations and may be ignored pending a future fix. The message alone does
not indicate a failed system setup.

### `hwloc` 2.11 interfaces

- `hwloc-calc --cpuset-output-format systemd-dbus-api` emits `AllowedCPUs`
  data for systemd slices.
- `--cpuset-input-format list` accepts bit lists.
- `hwloc-info --get-attr` returns a single attribute.
- `--cpuset-output-format` supersedes `--taskset`.
- `HWLOC_MEMBIND_WEIGHTED_INTERLEAVE` and the `weighted` policy require Linux
  6.9 or later and therefore do not work with stock SP7 kernel 6.4.

### CPU mitigation policy drift

The default side-channel mitigation setting is `Auto`, but its represented boot
parameters can change between service packs. Revalidate the effective mitigation
set after upgrade, especially on performance-sensitive hosts.

## Architecture-related kernel behavior

### POWER Kdump CPU parameter

Custom SLES 15 SP6 POWER Kdump configurations must replace `maxcpus` with
`nr_cpus`. Packaged configuration is migrated automatically; custom scripts are
not.

### Arm Memory Tagging and IOMMU

SLES 15 SP6 glibc 2.38 enables Armv8.5 Memory Tagging Extension. The Arm kernel
changes its IOMMU default from passthrough to translated mode; restore the former
behavior with `iommu.passthrough=1` only when required.

### AMD EPYC Turin frequency scaling

SLES 16 uses AMD P-State by default on EPYC Turin and later processors, enabling
Energy Performance Preference and autonomous workload-driven frequency scaling.

## Revised SLES 16 defaults (`16.0-rev-2026-08-04`)

### EROFS availability

`erofs` is removed from the kernel module blacklist and is no longer disabled by
that default policy.

### Regular-file protection

Security protection for regular files is enabled by default. Recheck workloads
that relied on the former unprotected behavior; related identity and policy
defaults are described in [security-identity.md](security-identity.md).
