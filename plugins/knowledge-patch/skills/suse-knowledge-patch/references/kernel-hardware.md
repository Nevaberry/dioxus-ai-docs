# Kernel and Hardware Behavior

Use this reference for kernel configuration, observability, CPU behavior, hardware limits, graphics drivers, and reported kernel limitations.

## Contents

- [Kernel builds and observability](#kernel-builds-and-observability)
- [Scheduling, timing, and CPU behavior](#scheduling-timing-and-cpu-behavior)
- [Capacity limits](#capacity-limits)
- [Graphics and accelerators](#graphics-and-accelerators)
- [Known kernel and device issues](#known-kernel-and-device-issues)

## Kernel builds and observability

### External module compiler

Leap 16 builds its kernel with GCC 13 rather than the default compiler. Install `gcc13` and invoke `gcc-13` for external modules or kernel rebuilds. This compiler is supported only for kernel and kernel-module builds.

### External module taint state

SLES 15 SP6 no longer sets a kernel taint flag merely because an externally supported module is loaded. Do not use the former taint bit to detect such modules in monitoring or support automation.

### I/O delay accounting

On kernels 5.14 and later, `iotop` cannot show SWAPIN and IO percentages unless task delay accounting is active. Add the `delayacct` boot parameter or enable it at runtime:

```sh
sysctl -w kernel.task_delayacct=1
```

### BPF pairing

Use SLES 15 SP6 `libbpf`, `bpftool`, BCC, and `bpftrace` only with a kernel from the same product. Pair BCC and `bpftrace` with matching `kernel-*-devel` headers; `bpftrace` may instead use matching built-in kernel BTF when accessing kernel data types.

### Lightweight guard regions

Leap 16 supports `MADV_GUARD_INSTALL` through `madvise()` for a lightweight guard region over an address range without a conventional mapped backing region.

### Userspace live patching

Leap 16 `libpulp` can live-patch `glibc` and OpenSSL binaries on x86-64 and ppc64le. Do not assume support for other libraries or architectures.

## Scheduling, timing, and CPU behavior

### Timer frequency

SLES 15 SP6 fixes non-overridable `CONFIG_HZ` at 250 Hz on x86-64 and Arm and at 100 Hz on POWER and IBM Z. Retest timing-sensitive Arm applications that assumed 100 Hz.

### Real-time group scheduling

The SLES 15 SP7 kernel can enable `CONFIG_RT_GROUP_SCHED` with the `rt_group_sched` kernel command-line parameter and backports cgroup v2 CPU load balancing. Use these features without leaving the SP7 kernel line.

### AMD P-State

SLES 16 enables AMD P-State by default on AMD EPYC Turin and later processors, including Energy Performance Preference control and autonomous workload-driven frequency scaling.

### CPU mitigation policy

SLES 15 SP7 defaults side-channel mitigations to `Auto`, but the boot parameters represented by `Auto` can change between service packs. Revalidate the effective mitigation set after every upgrade when performance or threat policy depends on it.

### Intel hybrid PMU limitation

Do not rely on Performance Monitoring Unit profiling on Intel hybrid CPUs under SLES 15 SP7. Its kernel 6.4 lacks the required kernel 6.9 changes, so PMU features do not work correctly.

### `hwloc` interfaces

SLES 15 SP7 `hwloc` 2.11 adds:

- `hwloc-calc --cpuset-output-format systemd-dbus-api` for systemd-slice `AllowedCPUs` data.
- `hwloc-calc --cpuset-input-format list` for bit lists; the option is `--cpuset-input-format list`.
- `hwloc-info --get-attr` for returning one attribute.
- `HWLOC_MEMBIND_WEIGHTED_INTERLEAVE` and the `weighted` binding policy.

Use `--cpuset-output-format` instead of superseded `--taskset`. The weighted interleave API needs Linux 6.9 or later and is therefore unavailable with the stock SP7 6.4 kernel.

## Capacity limits

SLES 15 SP6 documents these logical CPU limits: 8192 on x86-64, 512 on IBM Z, 2048 on POWER, and 768 on Arm. The theoretical/certified RAM limits are over 1 PiB/64 TiB on x86-64, 10 TiB/256 GiB on IBM Z, 1 PiB/64 TiB on POWER, and 256 TiB/no stated certified limit on Arm. Block devices can be as large as 8 EiB.

For the higher SLES 16 POWER limits, see [platforms.md](platforms.md).

## Graphics and accelerators

### Leap NVIDIA selection

Leap 15.6 disables `nouveau` by default for NVIDIA Turing and Ampere GPUs. For the recommended openGPU path, install the signed G06 module and GSP firmware:

```sh
zypper install nvidia-open-driver-G06-signed-kmp-default kernel-firmware-nvidia-gsp-G06
```

Enable unsupported-GPU support in `/etc/modprobe.d/50-nvidia-default.conf`:

```conf
options nvidia NVreg_OpenRmEnableUnsupportedGpus=1
```

To use `nouveau` instead, do not install that openGPU package and add `nouveau.force_probe=1` to the kernel boot parameters.

Leap 16 automatically installs the open kernel driver, NVIDIA repository, and user-space acceleration drivers for supported GPUs. If the installer cannot start graphics, boot with `rd.driver.blacklist=nouveau` for nouveau-specific failures or `nomodeset` for general graphics failures.

### Preview drivers

On SLES 15 SP6, the AMD Navi32 “Wheat Nas” GPU driver remains a preview because matching firmware is unavailable. The Intel IAA crypto-compression driver is also a preview. Do not treat package presence as support.

## Known kernel and device issues

### SMC freeze risk

The updated Shared Memory Communications (`smc`) driver can freeze an SLES 15 SP7 host. Avoid it for workloads that cannot tolerate a host hang until the announced maintenance fix is available.

### IDXD probe message

The SLES 15 SP7 message `IDXD: user: probe of wq1.0 failed with error -95` can be harmless in certain configurations and may be ignored pending the announced future fix. Do not treat that message alone as proof of failed setup.

### Kernel and filesystem removals

SLES 16 uses kernel 6.12 and removes quota v1. For the removed file systems and migration target, see [storage-filesystems.md](storage-filesystems.md).

### Kdump on POWER

Custom SLES 15 SP6 POWER Kdump configurations must replace `maxcpus` with `nr_cpus`. Packaged configurations migrate automatically; custom scripts do not.
