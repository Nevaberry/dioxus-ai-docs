# Cargo

Use this reference for Cargo configuration, builds, workspaces, packaging and publishing, lockfiles, registries, metadata, cache policy, and environment variables. Edition 2024 resolver and manifest migration rules are in [edition-2024.md](edition-2024.md).

## Configuration loading and merge behavior

### Include other configuration files

The top-level `include` key in `.cargo/config.toml` loads additional configuration files (1.94.0). Inline tables can make a path optional for per-developer or environment-specific settings.

```toml
include = [
    { path = "required.toml" },
    { path = "local.toml", optional = true },
]
```

### Program-valued configuration

When Cargo merges a configuration key representing a program path together with its arguments, the later value replaces the earlier value as a unit instead of combining them (1.86.0). Keep the executable and arguments together at the intended precedence level.

### Boolean `cfg` literals

Manifests and configuration accept `true` and `false` as cfg literals, including inside predicate operators:

```toml
[target.'cfg(not(false))'.dependencies]
libc = "0.2"
```

### Relative `install.root`

A relative `install.root` without a trailing slash still resolves from the current working directory but emits a deprecation warning. Do not depend on that interpretation; it is planned to resolve relative to the configuration file like other config paths.

## Build locations, targets, and compiler flags

### Separate intermediate artifacts

`build.build-dir` selects where Cargo and rustc write intermediate artifacts (1.91.0). Its internal layout is not a supported interface.

```toml
[build]
build-dir = "build"
```

This is distinct from the target directory and from `resolver.lockfile-path`. When a separate build directory is enabled, publishing does not retain a `.crate` as a final artifact; later Cargo versions apply that publishing behavior even without the setting.

### Portable host target

`--target host-tuple` and `build.target = "host-tuple"` substitute the current host triple (1.91.0), allowing portable target-specific configuration.

```console
cargo build --target host-tuple
```

### Target-specific rustdoc flags

Target-selected Cargo configuration supports `rustdocflags` from 1.96.0:

```toml
[target.'cfg(unix)']
rustdocflags = ["--cfg", "unix_docs"]
```

### Trailing flags

For Cargo commands that accept trailing flags, those flags can take precedence over flags from other supported sources (1.85.0). Treat the command line as the final override when diagnosing an unexpected setting.

## Warning policy and linker messages

### Cache-preserving warning policy

`build.warnings` accepts `allow`, `warn` (the default), or `deny` for warnings emitted by local packages (1.97.0). Changing it does not invalidate underlying build artifacts, unlike `RUSTFLAGS=-Dwarnings`. CI can use `CARGO_BUILD_WARNINGS=deny`, including with `--keep-going`.

```toml
[build]
warnings = "deny"
```

### Successful linker output

Rustc reports successful linker output through the warn-by-default `linker_messages` lint from 1.97.0. This special lint is not controlled by the `warnings` group; configure it explicitly when silence is required.

```toml
[lints.rust]
linker_messages = "allow"
```

## Build-script inputs and outputs

### Feature and debug-assertion cfgs

- Build scripts receive `CARGO_CFG_FEATURE` from 1.85.0. Cargo also accepts raw identifiers in cfgs and warns about cfg names written as bare keywords for future compatibility.
- Build scripts receive `CARGO_CFG_DEBUG_ASSERTIONS` according to the chosen profile from 1.93.0. This exposed an incompatibility in `static-init` 1.0.1 through 1.0.3; select a different release of that dependency.

### Manifest path

Cargo sets `CARGO_MANIFEST_PATH` in addition to `CARGO_MANIFEST_DIR`. The former points directly to the package manifest:

```rust
const MANIFEST: &str = env!("CARGO_MANIFEST_PATH");
```

### Native-library search precedence

Native-library paths inside a build script's `OUT_DIR` are searched before external library paths. If both contain the same library name, the generated or bundled copy in `OUT_DIR` wins.

### Binary path at runtime

`CARGO_BIN_EXE_<crate>` is available at runtime from 1.94.0, in addition to its compile-time use in integration tests.

## Cache, artifacts, and cleaning

### Automatic cache cleaning

Cargo automatically removes network-downloaded cache files unused for three months and locally obtained files unused for one month from 1.88.0. Cleanup does not run with `--offline` or `--frozen`. If Cargo older than 1.78 shares otherwise unobserved cache entries, disable automatic cleanup:

```toml
cache.auto-clean-frequency = "never"
```

The manual `cargo gc` command remains unstable.

### Safer targeted cleaning

`cargo clean --target-dir` rejects a supplied path that does not resemble a Cargo target directory from 1.97.0, reducing the risk of deleting unrelated files.

### Publishing artifacts

`cargo publish` no longer leaves the `.crate` tarball as a user-accessible final artifact (1.93.0, after the behavior first applied with `build.build-dir` in 1.91.0). Run `cargo package` when a local tarball is required.

## Lockfiles and dependency resolution

### Alternate lockfile path

`resolver.lockfile-path` selects the lockfile used for dependency resolution from 1.97.0, including when source directories are read-only.

```toml
[resolver]
lockfile-path = "../locks/Cargo.lock"
```

### Lockfile format v4

New or updated lockfiles default to format v4, readable by Cargo 1.78 and newer. Projects supporting an earlier Cargo should declare the true `package.rust-version` so newer Cargo can preserve a compatible lockfile format.

```toml
[package]
rust-version = "1.77"
```

### Lockfiles in packages and publications

- `cargo package --exclude-lockfile` omits the lockfile from the generated package archive (1.87.0).
- Published crates always include `Cargo.lock`, regardless of whether they have executable or example targets.

These behaviors serve different workflows: the package command can create a local archive without a lockfile, while publication includes one.

### Precise exceptional updates

`cargo update --precise` may deliberately select a yanked registry release or an arbitrary Git revision:

```console
cargo update -p registry-dep --precise 1.2.3
cargo update -p git-dep --precise <git-revision>
```

### Git locally, registry when published

A dependency may declare both a Git repository and an alternate registry from 1.96.0. Cargo uses Git locally and the registry release when publishing.

## Workspaces and target selection

### Publish a workspace

`cargo publish --workspace` publishes workspace crates in dependency order and verifies the complete set as though published, including during dry runs (1.90.0). Publication is not atomic; a network or server failure can leave a partial workspace release.

### Fix target selection

`cargo fix` and `cargo clippy --fix` use the normal default target selection from 1.89.0 instead of processing every binary, example, and test. `cargo fix --edition` continues to operate on all targets.

### Package selection

- Combining `--package` with `--workspace` errors when a requested package is missing instead of silently ignoring it (1.86.0).
- `cargo package --package` packages only explicitly named packages and no longer implicitly adds the package in the current directory.

```console
cargo package --package api --package data
```

### Workspace-only tree depth

`cargo tree --depth workspace` shows only dependencies that are workspace members.

```console
cargo tree --depth workspace
```

## Metadata and package discovery

### Target filtering

`cargo metadata` does not apply `CARGO_BUILD_TARGET`. Tools needing a target-specific resolved graph must pass `--filter-platform` explicitly.

```console
cargo metadata --format-version 1 --filter-platform x86_64-unknown-linux-gnu
```

### Local package information

Without an explicit registry, `cargo info` with no package argument inspects the current local package.

```console
cargo info
```

### Home-directory initialization guard

`cargo init` refuses to initialize the user's home directory, preventing manifest discovery from treating every descendant directory as part of one package.

### Library auto-discovery

`package.autolib` independently controls automatic discovery of a library target.

```toml
[package]
autolib = false
```

### Versionless local packages

`package.version` may be omitted and then defaults to `0.0.0`, which is useful for non-published workspace packages. A package without an explicit version cannot be published.

```toml
[package]
name = "internal-tool"
edition = "2024"
```

## Manifests and TOML syntax

Cargo accepts TOML 1.1 from 1.94.0, including multiline inline tables with trailing commas, `\xHH` and `\e` string escapes, and times without seconds.

```toml
serde = {
    version = "1.0",
    features = ["derive"],
}
```

These forms raise the development-tool Cargo requirement and can require updates to third-party parsers. Cargo rewrites published manifests for older parsers, so using the syntax need not raise the crate's user-facing Rust requirement.

## Registry, publishing, and authentication

### Publish tokens

- The positional token argument to `cargo login` is deprecated from 1.86.0 because it can enter shell history.
- `cargo publish --token` is soft-deprecated. Configure a registry credential provider for new publishing workflows.

### Registry publication time

The registry-index `pubtime` field is stable from 1.94.0. Existing index entries are only gradually backfilled, so consumers must handle it being absent.

### Proxy certificate authority

`http.proxy-cainfo` selects the CA certificate used with an HTTP proxy from 1.90.0.

```toml
[http]
proxy-cainfo = "/path/to/proxy-ca.pem"
```

### Third-party registry security

Cargo 1.96.0 fixes CVE-2026-5223 in extracting crates containing symlinks and CVE-2026-5222 in authentication with normalized URLs. Both affect third-party registries; crates.io users are unaffected by these two issues.

### Runtime dependencies of distributed Cargo

Cargo in the official Rust distribution uses OpenSSL 3. On 32-bit platforms, this adds a hard dependency on `libatomic`, which must be present to install or run the toolchain.

## Terminal behavior

`term.progress.term-integration` makes Cargo emit ANSI OSC 9;4 progress updates for compatible terminals, allowing progress to appear in desktop surfaces such as a task bar.

```toml
[term.progress]
term-integration = true
```
