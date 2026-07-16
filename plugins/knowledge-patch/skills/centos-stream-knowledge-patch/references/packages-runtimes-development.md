# Packages, runtimes, and development

## Contents

- [Distribution and application baselines](#distribution-and-application-baselines)
- [Databases and web proxies](#databases-and-web-proxies)
- [Compilers, runtimes, and native libraries](#compilers-runtimes-and-native-libraries)
- [Package and infrastructure migrations](#package-and-infrastructure-migrations)
- [DNF and repositories](#dnf-and-repositories)
- [RPM signing, specs, and builds](#rpm-signing-specs-and-builds)

## Distribution and application baselines

### Default software versions

CentOS Stream 10 starts with Linux 6.12; Python 3.12, GCC 14, Go 1.23, Rust 1.82, LLVM 19, Ruby 3.3, Node.js 22, PHP 8.3, and OpenJDK 21; Apache HTTP Server 2.4.62 and nginx 1.26; PostgreSQL 16, MariaDB 10.11, MySQL 8.4, and Valkey 7.2. Desktop and package-management baselines are GNOME 47, Qt 6.7, DNF 4.20, and RPM 4.19. (10.0)

### Non-modular alternative packages

CentOS Stream 10 no longer uses modularity for alternative software versions. AppStream supplies optional alternatives as ordinary non-modular RPM packages. (10.0)

### Redis replacement

Valkey 7.2 replaces Redis. (10.0)

### Additional application runtimes and images

The 9.8 application choices add Node.js 24, `ruby:4.0`, the `python3.14` stack, OpenJDK 25, and `maven-openjdk25`. Registry images include `rhel9/ruby-40`, `rhel9/postgresql-18`, `rhel9/python-314-minimal`, `rhel9/python-314`, and `rhel9/mariadb-118`. (9.8)

## Databases and web proxies

### PostgreSQL 18 module defaults

The `postgresql:18` stream adds an AIO subsystem selected with `io_method`, native OAuth 2.0 authentication, FIPS validation, and statistics-preserving `pg_upgrade`; MD5 authentication is deprecated. Data-page checksums are enabled by default. When upgrading an installation with checksums disabled, enable them first or explicitly disable them during the upgrade. (9.8)

### MariaDB 11.8 migration

The `mariadb:11.8` stream defaults to `utf8mb4`; adds `VECTOR(N)`, vector-distance operations, UUID v4/v7 functions, parallel `mariadb-dump` and `mariadb-import` through `--dir` and `--parallel`, and per-session or per-instance temporary-space limits. The `mysql`, `mysqldump`, and `mysqladmin` names remain only as deprecated symlinks. Remove `innodb_defragment` from configuration. Install with `dnf module install mariadb:11.8`. (9.8)

### MariaDB Galera upgrade blocker

After upgrading a Galera cluster from MariaDB 10.11 to 11.8, SELinux enforcing mode blocks replication. The release notes provide no secure workaround. (10.2)

### HAProxy 2.8 baseline

The supported HAProxy package moves from the 2.4 LTS line to 2.8 because 2.4 reaches end of life in the second quarter of 2026. (9.8)

## Compilers, runtimes, and native libraries

### Compiler and diagnostic toolchain versions

The 9.8 system toolchain is GCC 11.5, glibc 2.39, Annobin 12.98, and Binutils 2.35.2. Rolling toolsets provide GCC 15.2 with Binutils 2.44, LLVM 21.1.8, Rust 1.92.0, and Go 1.26.2. GDB is 16.3 and Valgrind is 3.26.0. (9.8)

### Valgrind 3.26 diagnostics

Valgrind adds `--track-fds=bad` to report only invalid descriptor use, `--modify-fds=yes`, and XML protocol 6 summaries. `vgstack <PID>` attaches to a running Valgrind process and prints its backtraces. (9.8)

### LLVM 21 IR compatibility changes

LLVM IR replaces `nocapture` with `captures(none)`, removes constant-expression forms of arithmetic instructions such as `mul`, and rejects `label` operands on inline-assembly calls in favor of `callbr`. It adds floating-point `fmaximum` and `fminimum` operations to `atomicrmw`. (9.8)

### GCC 14 source and ABI migration

GCC 14 treats implicit `int`, implicit function declarations, and pointer-to-integer misuse as C compilation errors instead of warnings. On IBM Power, `long double` defaults to the hardware-backed IEEE128 ABI instead of IBM double-double, which is incompatible with the release 8-and-earlier ABI.

### Native library and compiler-target compatibility

TBB 2021.11 is incompatible with earlier enterprise TBB releases, so rebuild dependent applications. Traditional zlib is replaced by `zlib-ng` compatibility packages. Release 10.1 removes LLVM's 32-bit ARM and MIPS backends; choose another build target or toolchain.

### Sized glibc origin-path lookup

The `dlinfo` request `RTLD_DI_ORIGIN_PATH` accepts a destination-buffer size when retrieving a shared object's origin path, avoiding the overflow risk of the unchanged `RTLD_DI_ORIGIN` interface. (10.2)

### Bulgarian and Croatian locale currency change

Release 10.2 changes the Bulgarian and Croatian glibc locales to the euro symbol. Locale interfaces are unversioned, so this affects existing data. Re-test formatting, parsing, validation, and reports that assumed the previous symbol.

### Berkeley DB removal

`libdb` is absent from release 10. Applications using Berkeley DB 5 must move to another key-value store. This also requires backend changes in services such as Directory Server and Postfix.

### Environment Modules 5.6 administration

Environment Modules adds recursive `spider` searches, module aliases through `provide`, `module-help`, `module-warn`, and syslog event logging. Automatic unloading of conflicts and their dependents requires both `auto_handling` and `conflict_unload`. (10.2)

## Package and infrastructure migrations

### Newly deprecated transports and images

Corosync's unsupported SCTP transport for `knet` is deprecated; `pcs cluster setup` and link commands warn when it is selected. MySQL 8.0, Python 3.11, Node.js 20, and Node.js 20 Minimal container images are deprecated. Move to MySQL 8.4, Python 3.12, and Node.js 22 or 24 images. (9.8)

### Infrastructure deprecation replacements

Plan to replace `ftp`, `lftp`, and `vsftpd` with SFTP or WebDAV; `ipset` with nftables sets; SquashFS with EROFS; and BIND `auto-dnssec` with `dnssec-policy`. Other deprecated packages include `wget`, persistent-memory `libpmem*` and `nvml` tools, `libslirp`, and `gvisor-tap-vsock-gvforwarder`. (10.2)

### DHCP and infrastructure package migrations

Kea replaces ISC DHCP server packages; the old `dhcp` packages are absent, with Kea or `dhcpcd` as alternatives. `sendmail` is replaced by Postfix. `mod_security` and SpamAssassin move to EPEL, and `xsane` is unavailable.

### Postfix LMDB conversion

Postfix defaults to LMDB because Berkeley DB is unavailable. Convert existing BDB maps before upgrading or Postfix reports an unsupported `hash` dictionary type.

## DNF and repositories

### DNF `versionlock` bypass for local RPM paths

DNF can install an excluded version when it is passed as a local RPM path. To enforce `versionlock`, turn the containing directory into a repository with `createrepo_c`, enable it, and install by package name. (9.8)

### DNF metadata and diagnostic changes

DNF no longer downloads filelists metadata by default. For unresolved path dependencies, pass `--setopt=optional_metadata_types=filelists` or set `optional_metadata_types=filelists` in `/etc/dnf/dnf.conf`. The `debug-dump` and `debug-restore` plugin commands are removed. Capture state with `dnf repoquery --installed` and `dnf repolist -v`, then reproduce a set with `dnf install $(</tmp/list)`.

### `createrepo_c` defaults

`createrepo_c` compresses ordinary metadata with Zstandard instead of gzip. Override with `--general-compress-type` for incompatible consumers. SQLite metadata is generated only when `--database` is passed.

## RPM signing, specs, and builds

### Multiple RPM signatures

RPM supports multiple signatures, RFC 9580 OpenPGP, and post-quantum package signatures. `rpmsign --addsign` preserves existing signatures and appends another; it rejects an identical signature rather than replacing it.

### RPM spec patch and file syntax

`%patch` must name patch numbers explicitly, for example `%patch -P1 -P2` or `%patch 1 2`. An unnumbered `%patch` is an error and `%patchN` is deprecated. `%autopatch` accepts selected positional numbers such as `%autopatch 1 4 6`. `%files` patterns use more conventional shell-like globbing and escaping.

### RPM build and macro controls

Successful `rpmbuild` runs remove `%_builddir` unless `--noclean` is used. RPM estimates parallelism from memory with `%_smp_tasksize_proc` and `%_smp_tasksize_thread`, accepts a `T` thread count in `zstdio` payload modes, and adds `%conf`, `%preuntrans`, `%postuntrans`, `%{rpmversion}`, `%{exists:...}`, and `%{shescape:...}`.

### RPM ownership resolution

With `rpm --root`, user and group names resolve strictly from the target root's `passwd` and `group` files, not NSS. During builds, a `-` user or group in `%defattr` means `root`. Source-RPM contents are always owned by root regardless of source-tree ownership.
