# Compatibility, Builds, and Administration

## Remove legacy cgroup and init interfaces

- In 256, legacy or hybrid cgroup v1 boot required `SYSTEMD_CGROUP_ENABLE_LEGACY_FORCE=1` on the kernel command line, and the build-time `default-hierarchy` option could select only cgroup v2.
- In 258, cgroup v1 support was removed entirely. Boot and nspawn always use the unified cgroup v2 hierarchy; the force override is no longer a migration path.
- `initctl`, `runlevel`, `telinit`, `/dev/initctl`, runlevel utmp/wtmp records, and `init 3`-style state changes were removed in 258. `/forcefsck`, `/fastboot`, and `/forcequotacheck` were replaced by `fsck.mode=`, `fsck.repair=`, and `quotacheck.mode=` kernel options or credentials.
- Native units are mandatory in 260: `systemd-sysv-generator`, `systemd-sysv-install`, `systemd-rc-local-generator`, and `rc-local.service` were removed. `-Dcompat-sysv-interfaces=yes` restores `runlevel[0-6].target` and `legacy.conf`, but does not load SysV scripts.
- `getty@.service` now has an `[Install]` section and must be explicitly enabled (since 260):

```sh
systemctl enable --now getty@tty1.service
```

## Meet platform and tool requirements

- Systemd 258 requires Linux 5.4 or newer; 5.7 is recommended. Resolved and importd require OpenSSL.
- Requirements announced for 260 are Linux 5.10, glibc 2.34, libxcrypt 4.4, util-linux 2.37, elfutils 0.177, OpenSSL 3.0, cryptsetup 2.4, libseccomp 2.4, and Python 3.9 (announced in 259).
- Repart uses `mkfs.xfs` directory population and no longer has a protofile fallback. Populating XFS images therefore requires xfsprogs 6.17.0 or newer (since 260).
- The old F20–F23 key remapping moved out of the hardware database. Before 258, upgrade to `xf86-input-evdev` 2.11.0 or newer and `xf86-input-libinput` 1.5.0 or newer (announced in 257).
- TTY and PTY nodes default to `0600`, equivalent to `mesg n` instead of `mesg y`. A distribution that needs the former behavior can build with `-Dtty-mode=0620` (since 258).

## Package runtime-loaded dependencies

- `liblz4`, `libzstd`, `liblzma`, `libkmod`, and `libgcrypt` became runtime `dlopen()` dependencies in 256. ELF dependency scans may miss them; omitting `libkmod` can prevent boot. ELF notes advertise optional sonames to packaging tools.
- Audit, PAM, ACL, blkid, seccomp, SELinux, and most libmount integration also became weak runtime dependencies in 259. The service manager itself still requires libmount. Use `systemd-analyze dlopen-metadata` to inspect declared weak dependencies. Systemd no longer links to libcap.
- Build with `-Dlink-executor-shared=false` when an upgrade might remove an old shared systemd library before PID 1 reexecutes; this leaves the pinned `systemd-executor` usable (since 257).
- Standalone `systemd-tmpfiles` and `systemd-sysusers` builds expose full functionality. Features that need libmount are selected at installation time according to whether the runtime-loaded library exists (since 260).

## Handle build-library transitions

- The Meson options `-Dintegration-tests=` and `-Dcryptolib=` were removed in 260.
- Libidn support was removed; IDN requires libidn2. The obsolete `-Dlibidn=` switch is deprecated for later removal (since 260).
- `-Dlibiptc=` is deprecated because networkd and nspawn now require nftables for NAT (since 259).
- Meson's `libc=musl` enables an experimental, incomplete build. Without NSS-equivalent facilities, it disables nss-systemd, nss-resolve, `DynamicUser=`, homed, userdbd, foreign-ID allocation, unprivileged nspawn, and nsresourced; normal memory-pressure behavior for long-running services is also unavailable (since 259).
- `sd_varlink_field_type_t` briefly used incompatible numeric values in 260-rc1. Recompile software built with rc1 headers against rc2 or final 260 headers.

## Use configuration search paths and disable drop-ins

- Main configuration files are selected from `/etc`, `/run`, `/usr/local/lib`, then `/usr/lib`, using the first match. `kernel-install` uses this search and supports drop-ins; `systemd-udevd` supports `udev.conf` drop-ins (since 256).
- Most configuration loaders ignore drop-in files ending in `.ignore`, allowing an installed drop-in to be disabled without deleting it (since 259).

## Generate stable fleet hostnames

- Question marks in `/etc/hostname` are deterministically replaced by hexadecimal nibbles hashed from the machine ID. A shared `web-????????` image therefore receives a stable, distinct hostname on each machine (since 258).

## Describe the operating system

- `os-release` accepts `RELEASE_TYPE=development|stable|lts|experimental`, plus `EXPERIMENT=` and `EXPERIMENT_URL=` for experimental builds (since 257).
- `FANCY_NAME=` is a version-free display name and may contain ANSI sequences and non-ASCII glyphs. The manager, hostnamed, and `hostnamectl` prefer it over `PRETTY_NAME=` (since 260).

```ini
FANCY_NAME="Example Linux ◆"
PRETTY_NAME="Example Linux 260"
```

## Administrative behavior changes

- Systemd no longer flushes nscd user and group caches automatically; arrange invalidation explicitly if a deployment relied on it (since 257).
- `systemctl enqueue-marked` replaces deprecated `systemctl --marked`. `Markers=` accepts `needs-start` and `needs-stop` (since 260).
- More command-line tools can use interactive Polkit authorization: systemd-sysext and `varlinkctl` gained it, and authorized unprivileged callers can use `systemd-ask-password` (since 260).
