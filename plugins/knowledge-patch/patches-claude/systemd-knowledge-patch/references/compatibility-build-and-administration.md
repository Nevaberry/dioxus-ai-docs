# Compatibility, Builds, and Administration

## Platform and boot compatibility

### Cgroup hierarchy migration (256, 258)

Version 256 refuses legacy or hybrid cgroup v1 unless the kernel command line
contains `SYSTEMD_CGROUP_ENABLE_LEGACY_FORCE=1`; its `default-hierarchy` build
option can select only v2. Version 258 removes cgroup v1 support entirely for
both boot and nspawn, so remove the transitional override.

Version 258 requires Linux 5.4 (5.7 recommended), makes OpenSSL mandatory for
resolved and importd, and requires ukify 257.9 or newer with its stub.

### Removed legacy state interfaces (258, 260)

Version 258 removes `initctl`, `runlevel`, `telinit`, `/dev/initctl`,
`runlevel[0-6].target`, `init 3`-style changes, runlevel utmp/wtmp records,
plus `/forcefsck`, `/fastboot`, and
`/forcequotacheck`. Use `fsck.mode=`, `fsck.repair=`, and `quotacheck.mode=` as
kernel arguments or credentials.

Version 260 also removes `systemd-sysv-generator`, `systemd-sysv-install`,
`systemd-rc-local-generator`, and `rc-local.service`. Convert scripts to native
units. `-Dcompat-sysv-interfaces=yes` restores runlevel targets and
`legacy.conf`, not script loading.

### Announced v260 dependency floor (259)

Version 259 announced Linux 5.10, glibc 2.34, libxcrypt 4.4, util-linux 2.37,
elfutils 0.177, OpenSSL 3.0, cryptsetup 2.4, libseccomp 2.4, and Python 3.9 as
the planned next-release baselines. Confirm downstream build requirements
instead of assuming an older platform remains supported.

## Configuration and metadata

### Main-file and drop-in search (256, 259)

Main configuration is selected from `/etc`, `/run`, `/usr/local/lib`, then
`/usr/lib`; this applies to programs such as logind. `kernel-install` follows
the expanded search and supports drop-ins, and `systemd-udevd` supports
`udev.conf` drop-ins.
Most configuration loaders ignore installed drop-ins ending in `.ignore`.

### OS lifecycle and display fields (257, 260)

`os-release` supports `RELEASE_TYPE=` (`development`, `stable`, `lts`, or
`experimental`) plus `EXPERIMENT=` and `EXPERIMENT_URL=`. Version 260 adds
version-free `FANCY_NAME=`; the manager, hostnamed, and `hostnamectl` prefer it
over `PRETTY_NAME=`. `FANCY_NAME=` may contain ANSI and non-ASCII text.

### Automatic nscd flushing is gone (257)

Systemd no longer flushes nscd user and group caches. Arrange invalidation in
the identity-management workflow if it depended on that side effect.

## Build and packaging

### Runtime-loaded libraries (256, 259)

Compression and crypto libraries (`liblz4`, `libzstd`, `liblzma`, `libgcrypt`)
and libkmod became `dlopen()` dependencies; missing libkmod can prevent boot.
Audit, PAM, ACL, blkid, seccomp, SELinux, and most libmount integration are
also weakly loaded by 259, although the service manager still requires
libmount. Systemd no longer links libcap. Declare package feature dependencies
and inspect ELF notes with:

```sh
systemd-analyze dlopen-metadata /usr/lib/systemd/systemd
```

### Executor upgrade safety (257)

Use `-Dlink-executor-shared=false` when the pinned `systemd-executor` must keep
working while an upgrade replaces the versioned shared systemd library before
PID 1 reexecutes.

### Removed build options and IDN provider (260)

`-Dintegration-tests=` and `-Dcryptolib=` no longer exist. Libidn is
unsupported; use libidn2. The obsolete `-Dlibidn=` option is deprecated for
later removal.

### Experimental musl build (259)

Meson's `libc=musl` mode is experimental. Without NSS equivalents it disables
nss-systemd, nss-resolve, `DynamicUser=`, homed, userdbd, foreign-UID
allocation, unprivileged nspawn, and nsresourced; normal memory-pressure
behavior for long-running services is also unavailable.

### Standalone administrative builds (260)

Standalone `systemd-tmpfiles` and `systemd-sysusers` now provide full
functionality. Features requiring libmount are selected at installation time
according to whether the runtime-loaded library is present.
