# Compatibility, Builds, and Administration

## Platform and boot compatibility

### Cgroup migration (256, 258)

Version 256 refused legacy or hybrid cgroup v1 unless the kernel command line
contained `SYSTEMD_CGROUP_ENABLE_LEGACY_FORCE=1`; its build-time hierarchy
choice was already cgroup v2-only. Version 258 removed cgroup v1 entirely for
both boot and nspawn. Remove transitional overrides and require the unified
hierarchy.

### Hard platform and tool baselines (258, 259)

Version 258 requires Linux 5.4 (5.7 recommended), and resolved/importd require
OpenSSL. Pair a v258 systemd-stub with ukify 257.9 or newer.

Version 259 announced the next baseline: Linux 5.10, glibc 2.34, libxcrypt
4.4, util-linux 2.37, elfutils 0.177, OpenSSL 3.0, cryptsetup 2.4, libseccomp
2.4, and Python 3.9. It also announced last-definition-wins behavior for
duplicate partitions in `RootImageOptions=` and the mount-image parameters of
`ExtensionImages=` and `MountImages=`.

### TPM and filesystem tool requirements (259, 260)

Systemd-boot and systemd-stub support only TPM 2.0 as of 259. Repart in 260
uses the XFS directory-population support introduced in xfsprogs 6.17.0 and
has no protofile fallback, so populated XFS images require that version or
newer.

## Removed and changed interfaces

### Native units replace runlevels, SysV, and rc.local (258, 260)

Version 258 removed `initctl`, `runlevel`, `telinit`, `/dev/initctl`, runlevel
targets, `init 3`-style state changes, and runlevel utmp/wtmp records. Replace
`/forcefsck`, `/fastboot`, and `/forcequotacheck` with the `fsck.mode=`,
`fsck.repair=`, and `quotacheck.mode=` kernel options or credentials.

Version 260 then removed `systemd-sysv-generator`, `systemd-sysv-install`,
`systemd-rc-local-generator`, and `rc-local.service`. Native units are
required. `-Dcompat-sysv-interfaces=yes` restores runlevel targets and
`legacy.conf`, not service-script loading.

### Removed build and IDN options (260)

The `-Dintegration-tests=` and `-Dcryptolib=` Meson options are gone. Libidn
is unsupported and IDN requires libidn2; `-Dlibidn=` is obsolete and
deprecated for later removal.

### Input-key and EFI-option migration (257)

Before v258, install `xf86-input-evdev` 2.11.0+ and
`xf86-input-libinput` 1.5.0+ because F20-F23 microphone/touchpad remapping
moved out of systemd's hardware database. Replace the deprecated
`SystemdOptions` EFI variable and `bootctl systemd-efi-options` with
credentials or configuration extensions.

### Rebuild the v260-rc1 sd-varlink ABI (260)

Programs compiled with v260-rc1 headers must be rebuilt: rc1 briefly changed
`sd_varlink_field_type_t` numeric values and rc2 restored them.

### Getty instances need explicit enablement (260)

`getty@.service` has an `[Install]` section and is inactive until explicitly
enabled, for example `systemctl enable --now getty@tty1.service`.

## Configuration, identity, and defaults

### Main configuration search and inactive drop-ins (256, 259)

Programs select the first main configuration file in `/etc`, `/run`,
`/usr/local/lib`, then `/usr/lib`. Kernel-install follows this search and has
drop-ins; udevd supports `udev.conf` drop-ins. Most configuration loaders in
259 skip files ending `.ignore`, leaving them installed but inactive.

### TTY privacy (258)

TTY and PTY nodes default to `0600`, effectively `mesg n`. A distribution
that deliberately needs the old `0620` default must build with
`-Dtty-mode=0620`.

### Clock, machine ID, and fleet hostname (257, 258)

PID 1 and timesyncd choose the newest minimum time from the compiled epoch,
`/usr/lib/clock-epoch`, and `/var/lib/systemd/timesync/clock`.
`systemd.machine_id=firmware` derives the machine ID from SMBIOS or DeviceTree
UUID on physical or virtual systems.

Question marks in `/etc/hostname` are replaced deterministically with machine
ID-derived hexadecimal nibbles. `ConditionVersion=` tests kernel, systemd, or
glibc versions; `ConditionKernelModuleLoaded=` tests a loaded or built-in
module.

### OS release metadata (257, 260)

`os-release` can declare `RELEASE_TYPE=` (`development`, `stable`, `lts`, or
`experimental`) and `EXPERIMENT=`/`EXPERIMENT_URL=`. Version 260 adds
`FANCY_NAME=` as a version-free display name, possibly with ANSI and non-ASCII
text; manager, hostnamed, and hostnamectl prefer it over `PRETTY_NAME=`.

### NSCD cache flushing was removed (257)

Systemd no longer flushes nscd user/group caches as a side effect. Arrange
cache invalidation explicitly if the deployment relies on it.

### Journal and coredump storage defaults (256, 259)

Coredumps default to two weeks of retention rather than three days. Journald
defaults `Storage=` to `persistent`, independent of pre-existing
`/var/log/journal`; `-Djournal-storage-default=` can change the build default.

## Packaging and builds

### Runtime-loaded dependencies (256, 259)

Compression libraries (`liblz4`, `libzstd`, `liblzma`), libkmod, and libgcrypt
moved to `dlopen()` in 256. Version 259 also weak-loads audit, PAM, ACL, blkid,
seccomp, SELinux, and most libmount integration; the manager itself still
requires libmount, and systemd no longer links libcap. Declare package feature
dependencies explicitly—missing libkmod can prevent boot—and inspect notes
with `systemd-analyze dlopen-metadata`.

### Upgrade-safe executor linking (257)

Build with `-Dlink-executor-shared=false` to keep PID 1's pinned
`systemd-executor` usable when an upgrade removes an old shared systemd
library before manager reexecution.

### Musl is experimental (259)

Meson's `libc=musl` build is not guaranteed. Without NSS-equivalent behavior,
nss-systemd, nss-resolve, `DynamicUser=`, homed, userdbd, foreign-ID
allocation, unprivileged nspawn, and nsresourced are disabled; normal
long-running-service memory-pressure behavior is also unavailable.

### Standalone tmpfiles and sysusers are full builds (260)

Standalone systemd-tmpfiles and systemd-sysusers expose full functionality.
Installation-time availability of the dlopen-loaded libmount controls the
features that need it.
