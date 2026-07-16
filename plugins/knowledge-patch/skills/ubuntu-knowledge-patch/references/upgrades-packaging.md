# Upgrades, Packages, and Release Lifecycle

## Release upgrades and lifecycle

### Seeded snaps and post-upgrade review

An upgrade to Ubuntu 24.10 refreshes seeded snaps to the channels chosen for that
release, regardless of channels they previously tracked, and installs newly
seeded snaps. Reapply intentional channel overrides after the upgrade.

An s390x upgrade from 25.04 to 25.10 can report an error while processing
`kdump-tools` because of a race. The upgrade can complete, but reboot the machine
manually afterward.

### Direct LTS upgrade path

Direct upgrades to Ubuntu 26.04 are supported only from 25.10 and 24.04 LTS.
Older installations must first reach one of those releases. Automatic offers
start immediately for 25.10, while 24.04 LTS users wait for 26.04.1, scheduled
for 4 August 2026.

## APT, repositories, and historical packages

### APT 3.0 transition

In Ubuntu 25.04, APT 3.0 automatically tries its new dependency solver when the
classic solver fails. `apt show` and `apt list` use an automatic pager.

`apt-key` is removed. Repository tooling must manage key files directly and use
the `gpgv` verification model documented in `apt-secure(8)`.

### APT 3.1 defaults

In Ubuntu 25.10, the new solver is the default. `apt why` and `apt why-not`
explain successful and failed solver decisions. Repository definitions accept
`Include` and `Exclude` directives that restrict which packages a repository can
supply.

### Retrieve an unavailable historical version

The server-administration snapshot-service workflow retrieves package versions
that have left the live archive. Use the snapshot service when deployment must
reproduce an exact historical version instead of assuming only the current
repository version is installable.

## Package and command-provider transitions

### Minimal images and storage or HA packages

From Ubuntu 24.10, `unminimize` is a separate package and is not present in every
minimal image. Install it before invoking it:

```sh
apt-get install -y unminimize
```

`kpartx-boot` is discontinued because `kpartx` contains its functionality.
`dmraid` is removed; use an alternative such as `mdadm`. The transitional
`fence-agents` package is gone, so install `fence-agents-base`,
`fence-agents-extra`, or both according to the required agents and enabled
repository components.

### Low-latency and kernel tooling

Ubuntu 25.04 packages BPF and `linux-perf` tools independently of the kernel
version. The `linux-lowlatency` binary package is retired; use `linux-generic`
with `lowlatency-kernel`, which applies responsiveness tuning on the GRUB command
line.

Ubuntu 25.10 removes the deprecated `linux-modules-extra-*` split. All modules
ship in `linux-modules-<version>-<flavor>`.

### Timezone file compatibility

Starting with `tzdata` 2024b-5 in Ubuntu 25.04, new installations do not create
`/etc/timezone`; the `/etc/localtime` symlink is authoritative. An existing file
is still updated, but software must stop requiring it because maintainer-script
support is scheduled for removal in 25.10.

### sudo-rs and Rust coreutils

Ubuntu 25.10 uses `sudo-rs` as the default `sudo` provider. It supports
`sudoedit`, `NOEXEC`, and AppArmor profile switching. Classic sudo binaries have
`.ws` suffixes. `sudo-ldap` is removed; implement LDAP authentication through
PAM.

The same release uses `rust-coreutils` 0.2.2 for core operating-system
utilities. GNU coreutils remain available alongside them through managed
diversions, allowing a compatibility-driven switch back.

### Leaner server seed

The Ubuntu 25.10 server image and `ubuntu-server` metapackage no longer seed
`screen`, `wget`, `byobu`, `cloud-guest-utils`, or `dirmngr`. `screen` and
`wget` remain in `main`; `byobu` moves to `universe`; some packages can still
arrive as dependencies. Use seeded `wcurl URL` for simple download cases or
install `wget` explicitly for its specialized behavior.

## Development toolchains

Ubuntu 25.04 supplies a GCC 15 snapshot, binutils 2.44, glibc 2.41, Python
3.13.3, LLVM 20, Rust 1.84, and Go 1.24. OpenJDK 21 remains the default;
OpenJDK 24 and an OpenJDK 25 early-access snapshot are also available, and the
`dotnet` snap adds .NET 9.

Ubuntu 25.10 supplies GCC 15.2, binutils 2.45, glibc 2.42, Python 3.13.7, LLVM
20, Rust 1.85, and Go 1.24. It also offers Python 3.14, LLVM 21, Rust 1.88,
OpenJDK 25 LTS, an OpenJDK 26 early-access build, and Zig 0.14.1. OpenJDK 21
remains the default; .NET 10 initially ships as RC1, and GraalVM CE 25 gains
arm64 support through its snap.
