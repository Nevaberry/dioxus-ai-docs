# Scripts, build scripts, and subcommands

Use this reference for `build.rs`, experimental Cargo scripts, external Cargo
subcommands, shell completion, help integration, and runtime Cargo-provided
environment variables.

## Build-script inputs

### Activated features

Since 1.85.0, build scripts receive `CARGO_CFG_FEATURE`, containing every
activated feature for the package being built.

### Debug assertions

Cargo 1.93.0 added `CARGO_CFG_DEBUG_ASSERTIONS`, reflecting the active
profile's debug-assertion setting.

### Cargo-configured environment changes

As of 1.86.0, a `rerun-if-env-changed` instruction detects changes to values
originating in Cargo's `[env]` configuration table.

## Build-script outputs

### cdylib link arguments

Since 1.87.0, `cargo::rustc-link-arg-cdylib` output is not forwarded to test
targets.

### Multiple build scripts

Cargo 1.90.0 added unstable `multiple-build-scripts`, allowing an array in
`package.build`:

```toml
cargo-features = ["multiple-build-scripts"]

[package]
build = ["build.rs", "generate.rs"]
```

Cargo 1.92.0 exposes each script's output directory through a
`<script-name>_OUT_DIR` environment variable.

### Metadata from any build script

With `-Zany-build-script-metadata`, added in 1.94.0, any build script may emit
`cargo::metadata=KEY=VALUE`. Dependents receive it as
`CARGO_DEP_<name>_<key>`:

```console
cargo +nightly -Zany-build-script-metadata build
```

## Cargo scripts

All behavior in this section requires unstable `-Zscript`.

### Dependency and edition maintenance

Cargo 1.85.0 lets Cargo scripts add and remove dependencies and migrate their
embedded manifests across editions. Script builds also preserve the configured
release profile.

### Package identity

`cargo pkgid` supports Cargo scripts as of 1.86.0.

### Workspace independence

Since 1.89.0, Cargo scripts ignore an enclosing workspace.

### Frontmatter and binary names

Cargo 1.92.0 requires only horizontal whitespace after a script frontmatter
fence and rejects manifest fields that are invalid for scripts. The same
release defaults `bin.name` to `package.name`.

### Build-directory state

Cargo 1.92.0 placed script lockfiles in the build directory and defined the
script target directory through build-directory templating.

Cargo 1.95.0 then made configuration load relative to the script file and made
script lockfiles script-specific independently of `build.build-dir`. Follow
the newer rule rather than assuming all script state follows the build
directory.

## Cargo executable environment

### External subcommands

Since 1.87.0, external Cargo subcommands receive the path to the correct Cargo
binary in `CARGO`. Do not treat this variable as a general-purpose Cargo
wrapper.

Cargo stopped canonicalizing that path in 1.88.0, so a symlinked invocation is
preserved.

### `cargo rustc --print`

Cargo 1.86.0 prepares the Cargo environment before the rustc invocation used
by `cargo rustc --print`.

### Target discovery

Cargo 1.96.0 supplies `CARGO` when running `rustc -vV` for target discovery.

### Runtime binary paths

Since 1.94.0, `CARGO_BIN_EXE_<name>` is present at runtime as well as compile
time, allowing executed code to find the Cargo-built binary.

## Command integration

### Bash completion

Cargo 1.87.0 forwards Bash completion requests to third-party subcommands.

### Nested manpages

Since 1.96.0, `cargo help` can display manpages for nested subcommands:

```console
cargo help report future-incompat
```

### Manifest-path shorthand

Cargo 1.97.0 added `-m` as an alias for `--manifest-path`:

```console
cargo build -m path/to/Cargo.toml
```

### Frozen mode consistency

Since 1.87.0, Cargo honors `--frozen` everywhere that accepts `--offline` or
`--locked`.
