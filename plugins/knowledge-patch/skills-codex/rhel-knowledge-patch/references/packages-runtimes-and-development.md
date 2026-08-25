# Packages, Runtimes, and Development

Consult this reference for DNF and RPM behavior, repositories, Application Streams, databases, language runtimes, compilers, libraries, and debugging tools.

## Contents

- [Package management, repositories, and RPM behavior](#package-management-repositories-and-rpm-behavior)
- [Application Streams, language runtimes, and databases](#application-streams-language-runtimes-and-databases)
- [Toolchains, libraries, and debugging](#toolchains-libraries-and-debugging)

## Package management, repositories, and RPM behavior

### Subscription CLI behavior (10.0)

`rhc connect` adds `--enable-feature` and `--disable-feature` controls for content, analytics, and remote management, all enabled by default. `subscription-manager status` now reports registration only, and the legacy attach, auto-attach, import, remove, role, service-level, usage, and related entitlement subcommands are removed.

### DNF metadata and weak-dependency defaults (10.0)

DNF no longer downloads or loads filelists metadata until a file argument requires it; filepath dependencies can require `--setopt=optional_metadata_types=filelists` or a persistent `optional_metadata_types=filelists`. `exclude_from_weak_autodetect=true` is now the default, so upgrades install newly introduced recommendations without backfilling all previously unmet weak dependencies.

### Package transactions and repository metadata (10.0)

Image-mode systems can run ephemeral transactions with `dnf install --transient make` or `persistence=transient`, keeping `/usr` read-only to other processes and discarding its changes at reboot. DNF gains a `pre-transaction-actions` plugin and uses rpm-sequoia through `librpmio`; RPM's database moves to `/usr/lib/sysimage/rpm`, while `createrepo_c` defaults to zstd and omits SQLite metadata unless `--database` is used.

### Removed platform packages and build syntax (10.0)

Sendmail, Redis, ISC DHCP, mod_security, SpamAssassin, and the DNF debug plugin are absent; migrate to Postfix, Valkey, Kea, or the documented DNF queries as applicable. RPM specs must spell `%patch 0` or `%patch -P 0`, because numberless `%patch` no longer means patch zero.

### Spec-local RPM dependency generators (10.1)

An RPM spec can register build-only file attributes in a colon-separated `%_local_file_attrs` list and define `%__NAME_path`, `%__NAME_provides`, or related generator macros without installing a separate attributes package.

```spec
%define _local_file_attrs foobar
%define __foobar_provides %{SOURCE1}
%define __foobar_path .*
```

### Installed-package provenance and DNF clock diagnosis (10.1)

RPM records whole-package SHA-256 and SHA-512 digests and exposes them with `rpm -q --qf "[%{packagedigestalgos:hashalgo} %{packagedigests}\n]" PACKAGE`; `%_pkgverify_digests` selects which algorithms are stored. DNF transactions report entitlement-server clock skew above two seconds, with debug logging in `/var/log/rhsm/rhsm.log` and warning severity above 15 minutes.

### Modularity deprecation (10.1)

The DNF `module` command and Anaconda's Kickstart `module` command are deprecated and should not be used in new package or installation workflows.

### Package-policy caveats (10.2)

DNF's versionlock does not block an excluded version installed from a local RPM path; turn the directory into a repository with `createrepo_c` and install by package name. Rust-rpm-sequoia aborts a multi-certificate import when any included key is forbidden by crypto policy, so remove the disallowed key first.

### Corrected package verification and ownership (10.2)

RPM and DNF accept a multiply signed package when at least one signature is valid and the others are merely `NOTTRUSTED`, but still reject invalid signatures. RPM now resolves installed-file owners through NSS outside `--root`; `%_passwd_path` and `%_group_path` force local lookup, and alternate roots never consult host NSS.

### Protected-package removal behavior (10.2)

DNF now treats protected packages as explicitly installed, so `clean_requirements_on_remove` does not try to autoremove one and block removal of the package that depended on it.


## Application Streams, language runtimes, and databases

### Non-modular Application Streams (10.0)

RHEL 10 distributes no modular Application Streams: initial streams are ordinary RPMs, while fast-moving compilers and container tools use Rolling Streams without parallel versions. Software Collections and Flatpaks remain Application Stream formats.

### RHEL 10 runtime streams (10.0)

The default/full-lifecycle Python is non-modular Python 3.12 in BaseOS, with additional parallel Python RPM streams having shorter lifecycles. Initial streams include Perl 5.40, Ruby 3.3, Node.js 22, PHP 8.3, PostgreSQL 16, MySQL 8.4, MariaDB 10.11, Valkey 7.2, and OpenJDK 21 as the default Java.

### Database compatibility changes (10.0)

PostgreSQL 16 removes the `postmaster` binary in favor of `postgres` and adds `pgvector`. MySQL 8.4 disables `mysql_native_password` by default and removes `mysql_upgrade`, `default_authentication_plugin`, and older SSL controls; MariaDB and MySQL Perl applications must use their matching `DBD::MariaDB` and `DBD::mysql` drivers.

### Runtime and database additions (10.1)

PostGIS is packaged for PostgreSQL, Apache HTTP Server 2.4.63 and .NET 10 LTS are available, and OpenJDK 25 is an additional LTS JDK. Rust Toolset 1.88 adds Rust 2024, async closures, let chains, and trait upcasting; Node.js 24 is a preview package with versioned binaries, while `rhel10/nodejs-24` and `rhel10/valkey-8` container images are available separately.

### MariaDB 11.8 compatibility (10.2)

MariaDB 11.8 defaults to `utf8mb4`, adds `VECTOR(N)` and distance functions, parallel `mariadb-dump`/`mariadb-import` through `--dir` and `--parallel`, UUID v4/v7, and temporary-space limits. Remove the unsupported `innodb_defragment` setting; `mysql`, `mysqldump`, and `mysqladmin` remain only as deprecated symlinks.

### PostgreSQL 18 defaults (10.2)

PostgreSQL 18 enables data-page checksums by default, adds OAuth 2.0 SSO and optional AIO through `io_method`, preserves statistics with `pg_upgrade`, and deprecates MD5 authentication. Upgrades from an instance without checksums must enable them first or explicitly disable them during the upgrade.

### Additional language stacks (10.2)

RHEL 10.2 adds parallel Ruby 4.0 and Python 3.14 stacks plus PHP 8.4, with matching `rhel10/ruby-40`, `rhel10/postgresql-18`, `rhel10/python-314-minimal`, `rhel10/mariadb-118`, and `rhel10/php-84` container images. PHP 8.4 includes property hooks, asymmetric property visibility, `#[\Deprecated]`, the `Dom` API, `BcMath\Number`, and the `array_find*` family.

### Crash-dump and database caveats (10.2)

Kdump cannot run on ARM64 with Secure Boot enabled; disabling Secure Boot is the only workaround. After upgrading a Galera cluster from MariaDB 10.11 to 11.8, SELinux blocks replication and there is no secure workaround that retains enforcing mode.


## Toolchains, libraries, and debugging

### Compiler and library ABI baseline (10.0)

GCC 14.2 targets x86-64-v3 by default; on IBM Power, `long double` changes to the hardware IEEE128 ABI and is incompatible with the RHEL 8-and-earlier double-double ABI. `zlib-ng-compat` replaces zlib in API/ABI-compatible mode, and 32-bit multilib packages are removed.

### Elfutils and Valgrind tooling (10.1)

`debuginfod` adds `--cors` and `--listen-address`, while the client caches `x-debuginfod-*` headers; `libdw` adds DWARF-language helpers and the preview `libdwfl_stacktrace` sampler interface. Valgrind 3.25.1 understands zstd debug sections and newer filesystem/Landlock syscalls, adds `--modify-fds=high`, and controls unlocked-condition warnings with `--check-cond-signal-mutex=yes|no` (default `no`).

### Compiler and debugger transitions (10.1)

The system toolchain moves to GCC 14.3, while GCC Toolset 15 contains GCC 15.1 and binutils 2.44 but no Annobin or `dwz`; invoke it as `gcc-toolset-15-env COMMAND`, not `scl enable`. LLVM Toolset moves to 20.1.8 and drops 32-bit ARM and MIPS back ends, Go Toolset moves to 1.24, and GDB 16.3 forbids direct `gdb.Progspace()` construction and renames `set unwindonsignal` to `set unwind-on-signal`; applications using the ABI-incompatible TBB 2021.11 must be rebuilt.

### New glibc scheduler APIs and IBM Z targeting (10.1)

`<sched.h>` now exposes `sched_setattr()` and `sched_getattr()`, including `SCHED_DEADLINE`, without direct syscalls or kernel headers. On s390x GCC tunes for z16 by default (`-mtune` overrides it), and glibc automatically loads z17-optimized libraries from `/usr/lib64/glibc-hwcap/z17/`.

### Debugging tool interfaces (10.2)

Valgrind 3.26 adds `--modify-fds=yes`, `--track-fds=bad`, always uses XML protocol 6 under `--xml=yes`, and provides `vgstack PID` for attaching to a running Valgrind process. SystemTap `@cast()` can discover types from UAPI `<vmlinux.h>` automatically, `crash` can unwind multi-stacks and inspect Rust, and Apache `ErrorLogFormat` supports millisecond timestamps through `%{m}t`.

### Compiler and libc interfaces (10.2)

LLVM 21 removes several constant-expression forms, replaces IR `nocapture` with `captures(none)`, and requires `callbr` rather than inline-assembly `label` operands; the rolling toolsets move to Rust 1.92, GCC Toolset 15.2, and Go 1.26.2. Glibc adds size-aware `RTLD_DI_ORIGIN_PATH`, `gcov -f` adds per-function branch and call coverage, and AArch64 vector math can reference symbols versioned for glibc 2.40 even though the base libc is 2.39.

