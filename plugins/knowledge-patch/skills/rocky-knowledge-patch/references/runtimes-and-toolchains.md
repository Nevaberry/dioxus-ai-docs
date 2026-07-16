# Runtimes and toolchains

## Select application and server runtimes

- Rocky Linux 9.4 adds Python 3.12 and module streams for Ruby 3.3, PHP 8.2,
  nginx 1.24, MariaDB 10.11, and PostgreSQL 16. It rebases Git to 2.43.0 and Git
  LFS to 3.4.1.
- Rocky Linux 9.5 provides later Application Streams for Apache HTTP Server
  2.4.62 and Node.js 22. Installing `java`, `java-devel`, or `jre` selects Java
  17 rather than Java 11 by default.
- Rocky Linux 9.6 adds module streams for PHP 8.3, MySQL 8.4, and nginx 1.26.
- Rocky Linux 9.8 adds later Application Streams for MariaDB 11.8, PostgreSQL
  18, and Ruby 4.0.
- Rocky Linux 10.0 includes Perl 5.40 in addition to its Varnish Cache 7.6,
  Squid 6.10, and Valkey 8.0 server baselines.
- Rocky Linux 10.1 adds Node.js 24 and Apache HTTP Server 2.4.63.
- Rocky Linux 10.2 adds PHP 8.4. Because 8.3 and 8.4 packages coexist, resolve
  unqualified dependencies as described in
  [system-administration.md](system-administration.md).

## Choose compilers and build tools

Rocky Linux 9.4 provides LLVM 17.0, Rust 1.75.0, Go 1.21.0, GCC Toolset 13,
elfutils 0.190, SystemTap 5.0, and CMake 3.26. Clang's resource directory moves
from `/usr/lib64/clang/17` to `/usr/lib/clang/17`. New packages include
`maven-openjdk21`, `libzip-tools`, and `grafana-selinux`.

Rocky Linux 9.5 provides GCC Toolset 14, LLVM Toolset 18.1.8, Rust Toolset
1.79.0, and Go Toolset 1.22. The system toolchain moves to GCC 11.5 and Annobin
12.70.

Rocky Linux 9.6 provides LLVM Toolset 19.17, Rust Toolset 1.84.1, and Go
Toolset 1.23.

Rocky Linux 9.8 provides system binutils 2.35.2, GCC Toolset 15 with GCC 15.2,
LLVM Toolset 21.1.8, Rust Toolset 1.92.0, and Go Toolset 1.26.2.

The Rocky Linux 10.1 system toolchain comprises GCC 14.3, glibc 2.39, Annobin
12.99, and binutils 2.41. Optional toolsets provide GCC Toolset 15 with GCC
15.1 and binutils 2.44, LLVM 20.1.8, Rust 1.88.0, Go 1.24, .NET 10.0, and
OpenJDK 25. Rocky Linux 10.2 updates the system Annobin component to 13.02.

## Choose debugging, analysis, and monitoring tools

- Rocky Linux 9.5 provides GDB 14.2, Valgrind 3.23.0, SystemTap 5.1, elfutils
  0.191, libabigail 2.5, PCP 6.2.2, and Grafana 10.2.6.
- Rocky Linux 9.6 provides Valgrind 3.24.0, SystemTap 5.2, elfutils 0.192,
  libabigail 2.6, and PCP 6.3.2.
- Rocky Linux 9.8 provides Valgrind 3.26.0, SystemTap 5.4, elfutils 0.194,
  libabigail 2.9, and PCP 6.37.
- Rocky Linux 10.1 includes GDB 16.3, Valgrind 3.25.1, SystemTap 5.3, Dyninst
  13.0.0, elfutils 0.193, and libabigail 2.8.

## Replace retired software streams

- Rocky Linux 9.4 no longer updates Node.js 16 after April 2024 or .NET 7 after
  May 2024, and Rocky Linux 9 support for OpenJDK 11 ends in October 2024. Use
  Node.js 18 or 20, .NET 6 or 8, and OpenJDK 8, 17, or 21 for continued fixes.
- Rocky Linux 9.5 no longer updates GCC Toolset 12 or .NET 6 after November
  2024, Ruby 3.1 after March 2025, or Node.js 18 after April 2025. Use GCC
  Toolset 13 or 14, .NET 8 or 9, Ruby 3.3, or Node.js 20 or 22.

