# Package Management, RPM, and Base-System Packaging

## Contents

- DNF and PackageKit
- RPM build and transaction behavior
- RPM 6 formats, keys, signatures, and verification
- Base-system and package-layout changes

## DNF and PackageKit

### DNF5 state and DNF4 fallback (41)

`dnf` and `yum` invoke DNF5. The legacy implementation remains available as
`dnf4` and `dnf-3`, but the implementations do not share transaction history
or installed-package reasons. DNF5 attempts a one-time state import on its
first transaction; do not alternate implementations for system changes.

### DNF5 automation and transaction hooks (41)

Replace `dnf-automatic` with `dnf5-plugin-automatic`. Essential plugins come
from DNF5 itself or `dnf5-plugins`; invoke unported DNF4 plugins through
`dnf4`. Use DNF5's Actions plugin in place of the old Snapper plugin to run
external programs before or after transactions and inspect DNF configuration.

### DNF5 manages expired repository keys (42)

An enabled-by-default libdnf5 plugin detects expired or obsolete repository
PGP keys before transactions. Interactive runs ask before deleting each key.
Non-interactive runs need no extra workflow and no preliminary
`rpmkeys --delete` step.

### Anaconda uses DNF5 and drops modularity (43)

Anaconda installs packages through DNF5, not DNF4, and no longer supports DNF
modularity. Installer automation cannot select module streams.

### PackageKit moves to DNF5 (44)

PackageKit uses a libdnf5-based backend, so PackageKit-driven operations no
longer go through the old DNF backend.

## RPM build and transaction behavior

### RPM 4.20 packaging interfaces (41)

RPM 4.20 adds a declarative build system, extended dynamic spec generation,
file-trigger arguments, spec-local dependency generators, the sysusers `m`
directive, guaranteed per-build directories, and a public plugin API. Install
scriptlets run with stronger isolation, which can expose assumptions about
their execution environment.

### RPM consumes `sysusers.d` metadata (42)

Ship package-owned users and groups as `sysusers.d` snippets. RPM consumes the
metadata and creates them directly, replacing package-specific user-creation
scriptlets.

### Static libraries retain debuginfo (43)

RPM build defaults no longer strip debuginfo from static libraries, and
`debugedit` processes it. Applications linked from static archives can
therefore be debugged with the retained information.

### Packages can extend Fedora's build flags locally (43)

Add package-specific compiler and linker options through the
`_pkg_extra_*flags` macro family. This extends rather than replaces Fedora's
distribution-wide defaults.

### RPM transactions propagate more scriptlet failures (43)

Scriptlet errors affect the transaction result code. Failures in
`%triggerprein` or `%triggerun` fail their associated install or erase
operation, so automation must handle a failed transaction rather than assuming
success from the older behavior.

### RPM builds hardlink identical files automatically (44)

A post-build macro step hardlinks identical files under `/usr` in every
package. Packaging checks and tools must tolerate identical installed files
sharing an inode.

## RPM 6 formats, keys, signatures, and verification

### Fedora's RPM 6 keeps conservative defaults (43)

RPM 6.0 continues to generate v4 packages and retains Fedora's legacy
signature-enforcement behavior rather than adopting both upstream defaults.
Set `_rpmformat` to `6` to test v6 explicitly. RPM v3 packages can be queried
or unpacked but no longer installed.

### RPM v6 modernizes the package format (43)

The opt-in v6 format provides 64-bit size fields, removes MD5 and SHA-1, adds
stronger payload and header digests, and records per-file MIME data. It does
not support external dependency generators. Older RPM releases can query v6
from 4.6, unpack it from 4.12, and verify or install it from 4.14, with
limitations.

### RPM 6 changes verification of old v4 packages (43)

Default verification can reject v4 packages built before RPM 4.14 because of
weak MD5 or SHA-1 digests. For a strongly signed package, set
`_pkgverify_level signature` to ignore those weak digests. Set
`_pkgverify_flags 0` only when legacy digest verification is unavoidable.

### RPM keys use full fingerprints (43)

`rpmkeys --import` accepts piped input and can update an existing key.
`--export` and `--rebuild` are also available. Key listing, checking, and
deletion use full fingerprints; stop parsing short key IDs or manipulating
`gpg-pubkey` pseudo-packages directly.

### RPM signing preserves multiple signatures (43)

`rpmsign --addsign` preserves existing signatures; `--resign` replaces them.
V6 packages support arbitrary multiple signatures, and v4 packages can do so
when explicitly using v6 signing mode. Select GnuPG or Sequoia `sq` with
`_openpgp_sign`, put the identity in `_openpgp_sign_id`, and configure
automatic build signing with `_openpgp_autosign_id` or
`rpm-setup-autosign`.

### RPM 6 adds and removes packaging interfaces (43)

Use `%{span:...}` for multiline macros and `%{xdg:...}` for XDG base
directories. Queries can expose package format, OpenPGP signatures, hash
names, and file MIME data. Remove uses of `--pkgid`, `--hdrid`,
`rpmbuild --nodirtokens`, the `brp-elfperms` policy script, and custom
`%__gpg_sign_cmd` overrides.

## Base-system and package-layout changes

### `/usr/bin` and `/usr/sbin` are unified (42)

`/usr/sbin` points to `/usr/bin`, `/usr/local/sbin` points to
`/usr/local/bin`, and `/usr/sbin` is absent from the default `PATH`. Legacy
absolute paths continue through symlinks. RPM's `%_sbindir` expands to
`%_bindir`; an upgraded system can defer the directory merge while an
unconverted package still owns a real file below `/usr/sbin`.

### OpenDMARC tools move to subpackages (42)

The base `opendmarc` package contains only core service utilities. Request
optional commands from `opendmarc-check`, `opendmarc-expire`,
`opendmarc-import`, `opendmarc-importstats`, `opendmarc-params`, or
`opendmarc-reports`.

### GnuPG is split into core and optional packages (43)

The formerly monolithic `gnupg2` packaging no longer makes common core tools
pull in every utility and service. Minimal installations and RPM dependencies
must request the optional GnuPG components they actually invoke.

### `PLATFORM_ID` is removed from `os-release` (43)

Do not require the Modularity-era `PLATFORM_ID` key when detecting Fedora or
selecting repositories; Fedora no longer places it in `os-release`.
