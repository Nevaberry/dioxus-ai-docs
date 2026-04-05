---
name: almalinux-knowledge-patch
description: AlmaLinux changes since training cutoff (latest: 10.1) — Btrfs root support, x86-64-v2 builds, post-quantum crypto via OpenSSL 3.5, SPICE re-enabled, CRB repo on by default. Load before working with AlmaLinux.
version: "10.1"
license: MIT
metadata:
  author: Nevaberry
---

# AlmaLinux 10+ Knowledge Patch

Claude's baseline knowledge covers AlmaLinux through 9.3. This skill provides changes from 10.1 (2025-11-24) onwards.

AlmaLinux 10 is based on RHEL 10 (kernel 6.12) but includes several significant deviations that differentiate it from upstream RHEL and other RHEL rebuilds.

## Quick Reference

### Breaking Changes / Key Differences from RHEL 10

| Feature | RHEL 10 | AlmaLinux 10 |
|---------|---------|--------------|
| Btrfs | Not supported | Full kernel + userspace; can install/boot from Btrfs |
| CPU baseline | x86-64-v3 only | x86-64-v2 AND x86-64-v3 builds |
| CRB repo | Disabled by default | Enabled by default on new installs |
| SPICE | Removed | Re-enabled (server + client) |
| Frame pointers | Not default | Enabled by default (system-wide profiling) |
| KVM on POWER | Removed | Re-enabled |
| Firefox/Thunderbird | Flatpak-only | Regular RPMs |

### Btrfs Support

AlmaLinux 10 is the only RHEL-based distro with full Btrfs support. You can use Btrfs as root filesystem during installation.

```bash
# Btrfs is available in the default kernel — no extra packages needed
mkfs.btrfs /dev/sda1
mount -o compress=zstd,noatime /dev/sda1 /mnt

# Subvolume management works out of the box
btrfs subvolume create /mnt/@home
btrfs subvolume snapshot -r /mnt/@home /mnt/@home-snapshot

# Check filesystem usage
btrfs filesystem usage /mnt
```

### x86-64-v2 Architecture Support

RHEL 10 raised the CPU baseline to x86-64-v3 (requires AVX2 — Intel Haswell+ / AMD Excavator+). AlmaLinux ships additional x86-64-v2 builds for older CPUs.

**Important caveat**: Third-party packages built for RHEL 10 target x86-64-v3 only. The v2 support is limited to AlmaLinux's own repository packages — third-party RHEL 10 packages may fail with `SIGILL` on v2 hardware.

```bash
# Check CPU architecture level support
/lib64/ld-linux-x86-64.so.2 --help 2>&1 | grep supported
```

### CRB Repository

On new AlmaLinux 10 installations, CRB (CodeReady Builder) is enabled by default — development headers and build dependencies are available without manual repo activation.

```bash
# Previously required on RHEL/AlmaLinux 9:
#   dnf config-manager --set-enabled crb

# On AlmaLinux 10+ new installs, already enabled
dnf repolist | grep crb

# Note: upgrades from AlmaLinux 9 preserve existing repo configuration
```

### Frame Pointers Enabled by Default

All packages are compiled with frame pointers, enabling system-wide profiling without recompilation:

```bash
# System-wide profiling works out of the box
perf record -g -a -- sleep 10
perf report
```

### SPICE, KVM on POWER, Firefox/Thunderbird

- **SPICE**: Re-enabled for server and client (removed in RHEL 10)
- **KVM on IBM POWER**: Re-enabled in virtualization stack (removed in RHEL 10)
- **Firefox/Thunderbird**: Shipped as regular RPMs, not Flatpak-only as in RHEL 10

```bash
# Regular RPM install (not Flatpak)
dnf install firefox thunderbird
```

### Post-Quantum Cryptography

System-wide crypto policies enable PQC algorithms by default in AlmaLinux 10:

- **OpenSSL 3.5**: Adds ML-KEM (Kyber), ML-DSA (Dilithium), SLH-DSA (SPHINCS+)
- **TLS**: Hybrid ML-KEM is in the default TLS group list — connections auto-negotiate PQC when both sides support it
- **RPM signatures**: RPMv6 supports PQC via Sequoia PGP tools

No configuration needed — PQC is active out of the box with default crypto policies.

See [references/pqc-and-crypto.md](references/pqc-and-crypto.md) for algorithm details.

### Key Toolchain Versions (AlmaLinux 10.1)

| Tool | Version | Notes |
|------|---------|-------|
| GCC | 14.3.1 | Default compiler |
| GCC Toolset 15 | GCC 15.1 | `dnf install gcc-toolset-15` |
| Go | 1.24 | |
| LLVM/Clang | 20.1 | |
| Rust | 1.88 | |
| Python | 3.12.11 | Default system Python |
| Node.js | 24 | |
| Podman | 5.6 | |
| QEMU-KVM | 10.0 | |
| Kernel | 6.12 | Frame pointers enabled |

See [references/toolchain-versions.md](references/toolchain-versions.md) for details.

### Dockerfile Base Image

```dockerfile
FROM almalinux:10
# or for minimal: FROM almalinux:10-minimal (uses microdnf)
```

## Reference Files

| File | Contents |
|------|----------|
| [almalinux-deviations.md](references/almalinux-deviations.md) | Full details on AlmaLinux vs RHEL 10 differences |
| [pqc-and-crypto.md](references/pqc-and-crypto.md) | Post-quantum cryptography algorithms and configuration |
| [toolchain-versions.md](references/toolchain-versions.md) | Compiler, runtime, and tool versions in 10.1 |
