# Packages, Application Streams, and Toolchains

Use this reference when choosing runtime versions, enabling module streams,
building software, debugging performance, or checking package availability.

## Application and module baselines

| Coverage batch | Applications and streams |
| --- | --- |
| `9.4` | Python 3.12, Ruby 3.3, PHP 8.2, nginx 1.24, MariaDB 10.11, and PostgreSQL 16 module streams. |
| `9.5` | New .NET 9.0 and BIND 9.18 packages; updated Apache HTTP Server 2.4.62 and Node.js 22 streams. |
| `9.6` | Maven 3.9, MySQL 8.4, nginx 1.26, and PHP 8.3 streams. |
| `9.7` | .NET 10.0; Node.js 24 and SWIG 4.3 streams; GIMP 3.0.4, Mesa 25.0.7, and Samba 4.22.4. |
| `9.8-10.2-ga` | AlmaLinux 9.8 adds Python 3.14 as a package and adds MariaDB, PostgreSQL, and Ruby streams. AlmaLinux 10.2 provides Python 3.14, PostgreSQL 18, MariaDB 11.8, Ruby 4.0, PHP 8.4, GNOME 49, SDL3, `libkrun`, `trustee`, and FIDO Device Onboard tooling. |
| `10.0` | Perl 5.40, Subversion 1.14, Varnish Cache 7.6, Squid 6.10, and Valkey 8.0. |
| `10.1` | Apache HTTP Server 2.4.63 and Python 3.12.11. Firefox and Thunderbird are ordinary RPM packages in the system repositories. |

## Compilers and build tools

### AlmaLinux 9 build stacks

- `9.4`: GCC Toolset 13, LLVM Toolset 17.0.6, Rust Toolset 1.75.1,
  Go Toolset 1.21.7, Git 2.43.0, and Git LFS 3.4.1.
- `9.5`: GCC Toolset 14, LLVM Toolset 18.1.8, Rust Toolset 1.79.0,
  Go Toolset 1.22, base GCC 11.5, and Annobin 12.70.
- `9.6`: LLVM Toolset 19.1.7, Go Toolset 1.23.6, Rust Toolset 1.84.1,
  Git 2.47.1, and Git LFS 3.6.1.
- `9.7`: GCC Toolset 15 with GCC 15.1 and binutils 2.44, LLVM Toolset
  20.1.8, Rust Toolset 1.88.0, Go Toolset 1.24, and system Annobin 12.98.
  Starting with GCC Toolset 15, the toolset no longer includes Annobin or
  `dwz`.
- `9.8`: LLVM Toolset 21.1.8, Rust Toolset 1.92.0, Git 2.52.0, Git LFS
  3.7.1, and CMake 3.31.8.

### AlmaLinux 10 build stacks

- `10.0`: base GCC 14.2, glibc 2.39, Annobin 12.92, and binutils 2.41.
- `10.1`: GCC 14.3.1 and Annobin 12.99.
- `10.2`: GCC Toolset 15 with GCC 15.2.1, BCC 0.35.0, and libbpf 1.7.0.

## Debugging, tracing, and performance tools

| Coverage batch | Tool versions and behavior |
| --- | --- |
| `9.4` | Valgrind 3.22, SystemTap 5.0, elfutils 0.190, and PCP 6.2.0. |
| `9.5` | GDB 14.2, Valgrind 3.23.0, SystemTap 5.1, elfutils 0.191, libabigail 2.5, PCP 6.2.2, and Grafana 10.2.6. |
| `9.6` | elfutils 0.192, Valgrind 3.24.0, SystemTap 5.2, and PCP 6.3.2. |
| `9.7` | GDB 16.3, Valgrind 3.25.1, SystemTap 5.3, Dyninst 13.0.0, elfutils 0.193, libabigail 2.8, and bpftrace 0.23.5. |
| `9.8` | elfutils 0.194, Valgrind 3.26.0, SystemTap 5.4, and bpftrace 0.24. |
| `10.0` | Dyninst 12.3.0 and libabigail 2.6. |

AlmaLinux 10 enables frame pointers throughout the distribution by default,
allowing real-time system-wide tracing and profiling without rebuilding
workloads for that purpose (`10.0`).

## Other updated user-space components

AlmaLinux 9.8 also provides Samba 4.23.5, Mesa 25.2.7, PipeWire 1.4.9,
Cockpit 356, and sudo 1.9.17p2 (`9.8`).

`libkcapi` 1.4.0 adds tools and options including `-T`, which selects target
file names for hash-sum calculations (`9.4`).

## Distribution package differences

Do not assume every package in the compatible upstream distribution exists in
AlmaLinux:

- AlmaLinux 9.5 omits `insights-client`, `kmod-redhat-*`, `kpatch*`,
  `openssl-fips-provider`, `rhc` and its worker, Subscription Manager
  add-ons, `virt-who`, `virtio-win`, and Windows SPICE packages (`9.5`).
- AlmaLinux 9.6 does not include the upstream-specific
  `command-line-assistant` package (`9.6`).
- AlmaLinux 10 does not provide `redhat-cloud-client-configuration`,
  `redhat-flatpak-data`, `redhat-support-lib-python`, or
  `redhat-support-tool` (`10.0`).

AlmaLinux's branding and release replacements are
`almalinux-backgrounds`, `almalinux-indexhtml`, `almalinux-logos`,
`almalinux-logos-httpd`, `almalinux-logos-ipa`, and `almalinux-release`.
They replace the corresponding upstream branding, index, release, and EULA
packages (`9.7`).
