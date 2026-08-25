# Upgrades and compatibility

Use this reference before upgrading Cargo, modernizing older command lines, or
diagnosing behavior that changed without a manifest edit.

## Security and platform requirements

### Crate extraction permissions

Cargo 1.94.0 fixes CVE-2026-33055 and CVE-2026-33056. On Unix-like systems, a
malicious crate extracted by an affected Cargo could alter permissions on
arbitrary filesystem paths. Upgrade before processing untrusted archives.

### OpenSSL and 32-bit systems

The Cargo binary in the official Rust distribution uses OpenSSL 3 as of
1.87.0. On 32-bit platforms this introduces a hard dependency on `libatomic`;
update images and system-package prerequisites accordingly.

### Dependency-cache hash migration

Cargo 1.85.0 changed dependency-cache path hashes to the cross-platform
`rustc-stable-hash` algorithm. The first use after upgrading may redownload
registry indices and crate tarballs and reclone Git dependencies because hash
suffixes under `$CARGO_HOME` change.

## Removed and replaced interfaces

### Build plans

The unstable `build-plan` feature was removed in 1.93.0. Use Cargo plumbing
commands, `--unit-graph`, or structured `-Zbuild-analysis` logging instead.

### Artifact output directories

The deprecated unstable `--out-dir` option was removed in 1.95.0. Use
`--artifact-dir` for artifact collection.

### Lockfile-path command-line option

Cargo 1.94.0 introduced `resolver.lockfile-path` under `-Zlockfile-path` as the
replacement for the planned-to-be-removed `--lockfile-path` CLI option:

```toml
[resolver]
lockfile-path = "/workspace/locks/Cargo.lock"
```

The CLI option was removed in 1.95.0. That release made `cargo fix` and
`cargo install` honor the configured path, but 1.96.0 changed `cargo install`
to ignore `resolver.lockfile-path`. Do not assume all commands share one
lockfile-path policy.

### Timings formats

Formatted `--timings=<FMT>` values were removed in 1.94.0. Use
`-Zbuild-analysis` logs for machine-readable timings. Use the unstable
`cargo report timings` command to replay an HTML timing report.

### Public dependency tree syntax

The initial `-Zpublic-dependency` tree interface used `--depth public` in
1.87.0:

```console
cargo -Zpublic-dependency tree --depth public
```

It changed to `--edges public` in 1.92.0:

```console
cargo -Zpublic-dependency tree --edges public
```

Use the latter spelling with current Cargo.

## Deprecations and stricter validation

### Target-specific edition

Cargo 1.87.0 reports `<target>.edition` as deprecated. Define the edition at
the package level and migrate target-specific uses.

### Relative install roots

Since 1.93.0, a relative `install.root` without a trailing slash emits a
deprecation warning. It is currently resolved against the working directory
but is intended to become relative to the configuration file, like other path
settings. Make the path unambiguous.

### Publish tokens

`cargo publish --token` is soft-deprecated as of 1.92.0. New publishing
workflows should use a credential-provider setup instead of depending on the
flag.

### Raw identifiers for keyword cfg names

Cargo 1.85.0 warns that keyword-named cfgs such as `cfg(true)` and
`cfg(false)` are future-incompatible when they are meant as identifiers. Use
raw identifiers such as `cfg(r#true)` to preserve the old identifier meaning.
Boolean cfg literals are separately supported by modern Cargo.

### Cargo script frontmatter

Under `-Zscript`, Cargo 1.92.0 accepts only horizontal whitespace after
frontmatter fences and rejects fields that are invalid for Cargo scripts.

### Home-directory initialization

As of 1.95.0, `cargo init` refuses to initialize the user's home directory.
This prevents a home-level manifest from interfering with manifest discovery
for descendant directories.

## Changed command scope and precedence

### Fix target selection

Starting in 1.89.0, `cargo fix` and `cargo clippy --fix` operate only on
default Cargo targets. Pass `--all-targets` to restore the broader scope:

```console
cargo fix --all-targets
cargo clippy --fix --all-targets
```

`--edition` and `--edition-idioms` continue to imply all targets.

Since 1.86.0, `cargo fix --allow-dirty` also implies `--allow-staged`, so
staged changes do not require both flags.

### Rustc command-line precedence

Since 1.85.0, flags after `--` in `cargo rustc` have higher precedence when
options conflict:

```console
cargo rustc -- -C opt-level=3
```

### Layered list precedence

Cargo 1.93.0 made non-mergeable list values passed with `--config` take
precedence over environment variables. Nested non-mergeable lists now replace,
rather than merge with, values from other configuration layers.

### Invoked Cargo paths

Cargo stopped canonicalizing the executable path stored in `CARGO` in 1.88.0.
If Cargo is invoked through a symlink, consumers now see that invoked path
rather than the resolved executable.

### Library search order

Since 1.88.0, library search paths inside `OUT_DIR` precede external library
search paths. When library names collide, an `OUT_DIR` library may now be
selected first.

## Packaging and generated artifacts

### Publish archive retention

Cargo 1.91.0 stopped retaining the `.crate` tarball after `cargo publish` when
`build.build-dir` was configured. Cargo 1.93.0 extended that behavior to all
publishes. Run `cargo package` when a local archive is needed.

### Deterministic package timestamps

Since 1.93.0, files Cargo generates while assembling a package tarball receive
deterministic timestamps, improving archive reproducibility.

### Documentation cleanup scope

Since 1.93.0, when a rustc version mismatch triggers cleanup, `cargo doc`
removes generated documentation only for requested targets rather than
deleting documentation for other target platforms.

### Unit-graph package identities

The unstable unit-graph output uses Package ID Specifications as of 1.88.0.
Consumers must parse package identities in that format rather than expecting
the older representation.
