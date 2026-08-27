# Userspace Tools and Relabeling

## Contents

- [Policy validation and conversion](#policy-validation-and-conversion)
- [Removed compatibility interfaces](#removed-compatibility-interfaces)
- [restorecond foreground operation](#restorecond-foreground-operation)
- [Hard-link relabel protection](#hard-link-relabel-protection)
- [Paths, symlinks, and filesystems](#paths-symlinks-and-filesystems)
- [mcstrans resource ceilings](#mcstrans-resource-ceilings)
- [Contributor and build workflow](#contributor-and-build-workflow)

## Policy validation and conversion

SELinux userspace 3.11 adds `secilcheck`, which checks CIL `neverallow` rules
against binary policies. Use it when the required assertion is about the
compiled policy rather than CIL parsing alone.

Policy conversions include several correctness changes:

- Module-to-CIL conversion now emits `constrain` and `validatetrans` unless the
  constraint contains a level-based expression.
- Conversion selects `tunableif` versus `booleanif` correctly and omits empty
  conditional blocks.
- CIL-to-`policy.conf` conversion handles constraint name lists correctly.
- CIL `classperm` declarations must contain at least one permission.
- Xperm permission linking is corrected, as are out-of-range values and
  complement handling at range boundaries.

Regenerate converted policy before maintaining local workarounds for any of
these cases.

## Removed compatibility interfaces

The following compatibility paths are gone:

- `sandbox` and `seunshare` no longer accept `-k` or `--kill`. Use `killall -Z`
  for context-aware process termination.
- `checkpolicy` no longer accepts the legacy `fscon` statement.
- `audit2why` no longer supports Python 2; invoke and package it with Python 3.

## restorecond foreground operation

`restorecond` accepts `-F` to remain in the foreground:

```console
restorecond -F
```

`restorecond.service` now uses foreground mode. A custom supervisor should
therefore track the foreground process and should not expect daemonization.

## Hard-link relabel protection

`SELINUX_RESTORECON_SKIP_MULTILINK` makes `selinux_restorecon(3)` refuse to
relabel a file that has multiple hard links. `restorecond` always passes this
flag. This prevents a watched path in a home directory, `/tmp`, or another
writable location from causing an inode reachable by another hard link to be
relabeled incorrectly.

`setfiles -A` disables `SELINUX_RESTORECON_ADD_ASSOC`. It is separate from the
multiple-hard-link safety flag; preserve that distinction in scripts and
documentation.

## Paths, symlinks, and filesystems

When `/proc` is available, `selinux_restorecon(3)` uses `/proc/self/fd` paths.
It falls back to full paths when `/proc` is unavailable.

Without `SELINUX_RESTORECON_REALPATH`, the library follows no symlinks. A caller
that sets the flag still canonicalizes intermediate symlinks in the initial
path. Consequently, a command-line or configured path containing intermediate
symlinks can behave differently among `setfiles`, `restorecond`, `sandbox`, and
`seunshare`. Test the actual caller and path instead of generalizing from one
tool.

`restorecon` now logs an error and continues on a read-only filesystem rather
than failing the entire traversal. This allows relabel walks to proceed when
they encounter read-only Btrfs subvolumes; the logged path remains unrelabelled
and should still be reviewed.

## mcstrans resource ceilings

`mcstrans` bounds resource consumption from faulty or abusive clients with:

- a cache-size cap;
- a connected-client cap;
- a receive timeout; and
- a `maxbit` cap.

Account for these ceilings when sizing the daemon or investigating stalled
clients and missing translations.

## Contributor and build workflow

The source tree follows `.clang-format`. Formatting is required for patches,
and the build provides both a check and a formatter:

```console
make check-format
make format
```

Libselinux and Python components use the system Python 3 `build` module. Build
isolation is disabled for the `sepolicy` module.

For libselinux builds using musl, LLVM, and `lld`, pass linker flags through
`EXTRA_LD_FLAGS`. For example, allow undefined symbol versions with:

```console
make -C libselinux EXTRA_LD_FLAGS=--undefined-version
```
