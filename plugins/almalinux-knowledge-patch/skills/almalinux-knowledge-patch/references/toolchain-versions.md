# Toolchain Versions (AlmaLinux 10.1)

AlmaLinux 10.1 "Heliotrope Lion" (2025-11-24), based on RHEL 10, kernel 6.12.

## Compilers and Languages

| Tool | Version | Notes |
|------|---------|-------|
| GCC | 14.3.1 | Default system compiler |
| GCC Toolset 15 | GCC 15.1 | Optional; install via `dnf install gcc-toolset-15` |
| LLVM/Clang | 20.1 | |
| Rust | 1.88 | |
| Go | 1.24 | |
| Python | 3.12.11 | Default system Python |
| Node.js | 24 | |

## Container and Virtualization

| Tool | Version |
|------|---------|
| Podman | 5.6 |
| QEMU-KVM | 10.0 |

## Kernel

- Linux 6.12
- Frame pointers enabled by default (enables `perf` profiling without debug symbols)
