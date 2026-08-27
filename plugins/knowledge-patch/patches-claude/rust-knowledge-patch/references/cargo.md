# Cargo

## Dependency resolution and MSRV

### Resolver v3

Resolver v3 can prefer dependency versions compatible with a package's
declared `rust-version` instead of always selecting the newest compatible
release (`1.84.0`). Opt into the policy without raising the workspace's MSRV:

```toml
# .cargo/config.toml
[resolver]
incompatible-rust-versions = "fallback"
```

Alternatively, set `package.resolver = "3"`; that manifest setting requires
MSRV 1.84 or newer. Resolver v3 is the edition-2024 default. `cargo add` and
`cargo update` warn when choosing an older compatible version. Latest-
dependency CI can override fallback with
`CARGO_RESOLVER_INCOMPATIBLE_RUST_VERSIONS=allow`.

TOML 1.1 syntax changes the development MSRV separately, as described below.

## Build directories, targets, and artifacts

### Separate intermediates from final artifacts

`build.build-dir` (`1.91.0`) puts incremental data, objects, and dep-info in a
scratch directory while `target-dir` retains outputs users consume:

```toml
# .cargo/config.toml
[build]
build-dir = "/tmp/cargo-build/{workspace-root-hash}"
target-dir = "target"
```

The internal layout of `build-dir` is unstable; tooling must not inspect it.
With this setting, `cargo publish` no longer leaves a `.crate` tarball as a
final artifact. Run `cargo package` when that file is required. From `1.93.0`,
`cargo publish` otherwise no longer leaves a `.crate` in a user-accessible
location unless `build.build-dir` is configured.

### Portable explicit host target

`--target host-tuple` and `build.target = "host-tuple"` (`1.91.0`) substitute
the host target without hard-coding it. This still activates explicit-target
mode: host and target features are not unified, and outputs go beneath
`target/<target>/`.

### Lockfile outside a read-only source tree

`resolver.lockfile-path` moves the lockfile away from the workspace root
(`1.97.0`):

```toml
[resolver]
lockfile-path = "/writable/dir/Cargo.lock"
```

This replaces the removed unstable `--lockfile-path` flag. `cargo install`
deliberately ignores the configuration key.

### Build-script environment

- Build scripts receive `CARGO_CFG_FEATURE`, a comma-separated list of enabled
  features, from `1.85.0`, in addition to `CARGO_FEATURE_<NAME>` variables.
- `CARGO_CFG_DEBUG_ASSERTIONS` follows the active profile in more situations
  from `1.93.0`. This exposes an unresolved-`parking_lot` failure in
  `static-init` 1.0.1 through 1.0.3.
- `CARGO_BIN_EXE_<name>` is available at test/bench runtime as well as through
  compile-time `env!` from `1.94.0`.

## Configuration composition and policy

### Include configuration files

Top-level `include` in `.cargo/config.toml` loads more configuration files
(`1.94.0`). Entries may be paths or inline tables with `optional = true`:

```toml
include = [
    { path = "shared.toml" },
    { path = "local-dev.toml", optional = true },
]
```

When Cargo merges configuration, a value consisting of a program path plus
arguments is replaced as a unit rather than concatenated across files
(`1.86.0`).

### TOML 1.1

Manifests and configuration accept TOML 1.1 from `1.94.0`, including multiline
inline tables with trailing commas, `\xHH` and `\e` escapes, and times without
seconds.

```toml
serde = {
    version = "1.0",
    features = ["derive"],
}
```

Using this syntax raises the development MSRV and may break third-party
manifest parsers. `cargo publish` rewrites a manifest into the older form, so
consumers retain the crate's declared MSRV.

### Warnings policy

`build.warnings` lets Cargo apply `allow`, `warn` (the default), or `deny` to
warnings from local packages (`1.97.0`). Because this is Cargo configuration,
changing it does not invalidate the rustc build cache.

```toml
# .cargo/config.toml
[build]
warnings = "deny"
```

Use `CARGO_BUILD_WARNINGS=deny cargo check --keep-going` to collect failures in
CI or `CARGO_BUILD_WARNINGS=allow` to mute local noise. The rustc
`linker_messages` lint sits outside the `warnings` group and is not escalated by
this setting or `-Dwarnings`.

### Target-specific rustdoc flags and proxy CAs

Cargo configuration accepts `target.'cfg(...)'.rustdocflags` from `1.96.0`.
`http.proxy-cainfo` selects a proxy-specific CA bundle from `1.90.0`.

## Cache behavior

Cargo automatically removes cached downloads not accessed for three months
for network sources or one month for local sources (`1.88.0`). Collection is
skipped under `--offline` and `--frozen`. If the cache is shared with Cargo
before 1.78, which does not record access times, disable cleanup:

```toml
# .cargo/config.toml
[cache]
auto-clean-frequency = "never"
```

## Workspaces and command selection

- `cargo build -p missing --workspace` errors rather than ignoring the missing
  package (`1.86.0`).
- `cargo fix` and `cargo clippy --fix` use the same default target selection as
  other build commands from `1.89.0`; `cargo fix --edition` still selects all
  targets.
- `cargo clean --workspace` is available from `1.93.0`.
- `cargo clean` rejects a `--target-dir` that does not resemble a Cargo target
  directory, and `-m` abbreviates `--manifest-path` (`1.97.0`).

`cargo rustc -- <flags>` appends trailing rustc flags after every other source,
so they outrank `RUSTFLAGS`, `build.rustflags`, `target.<...>.rustflags`, and
profile-derived flags. This is stable behavior from 1.85:

```sh
RUSTFLAGS="-Copt-level=3" cargo rustc -- -Copt-level=0
```

## Packaging and publishing

### Workspace publishing

`cargo publish --workspace` topologically orders and publishes workspace
packages (`1.90.0`). Verification builds the full set as though already on the
registry, including under `--dry-run`. Publishing is not atomic: a failure can
leave only part of the workspace published. Cargo performs the dependency
sequencing itself instead of requiring manual sequencing or `cargo-release`.

### Lockfiles and package archives

Published `.crate` files always contain `Cargo.lock`, including library-only
packages. This supports reproducible `cargo install --locked`, and the committed
lockfile is the one shipped.

`cargo package --exclude-lockfile` skips lockfile verification while packaging
(`1.87.0`).

Do not depend on `cargo publish` leaving a local `.crate`; use
`cargo package` when the archive itself is needed.

### Registry index publication time

The registry-index `pubtime` field records a version's publication timestamp
(`1.94.0`). crates.io backfills it lazily, so many older versions do not have
the field.

## Credentials and registries

Passing a token as an argument to `cargo login` is deprecated because it leaks
into shell history (`1.86.0`). Pipe it on stdin or let the prompt read it.
`cargo publish --token` is soft-deprecated; prefer `cargo login`, a registry
credential provider, or `CARGO_REGISTRY_TOKEN`.

From `1.96.0`, a dependency may specify a git source for local use and an
alternate registry plus version for publication:

```toml
[dependencies]
my-lib = { git = "https://example.com/my-lib.git", version = "1.2", registry = "my-registry" }
```

Cargo `1.96.0` fixes CVE-2026-5223 involving symlinks in extracted crate
archives and CVE-2026-5222 involving authentication with normalized URLs; both
affect third-party registries. `1.96.1` restores missing HTTP retries and
timeouts and updates Cargo's bundled libssh2 for CVE-2025-15661,
CVE-2026-55199, and CVE-2026-55200.

Cargo `1.94.1` updates `tar` to 0.4.45 for CVE-2026-33055 and
CVE-2026-33056; crates.io users are unaffected. It also downgrades `curl-sys`
to 0.4.83 to restore certificate validation on some FreeBSD versions.

## CLI changes and removals

- Unstable `--out-dir` was removed. `--artifact-dir`, still gated by
  `-Z unstable-options`, copies final artifacts out.
- `--timings` no longer accepts formats and emits only the SVG-backed HTML
  report. Machine-readable data moved to unstable `-Zbuild-analysis` logs.
- Unstable `--lockfile-path` became `resolver.lockfile-path` configuration.
- Unstable `--build-plan` and its feature were removed. Alternatives are
  `--unit-graph`, `-Zbuild-analysis`, or out-of-tree plumbing commands.
- `cargo init` refuses to initialize the home directory because a manifest
  there would absorb descendant projects into accidental manifest/workspace
  discovery.

Cargo emits ANSI OSC 9;4 sequences to terminals that render native build
progress (`1.87.0`).

## Nightly-only capabilities

The following are explicitly unstable:

- `multiple-build-scripts` lets `package.build` list scripts and exposes each
  output as `<script-name>_OUT_DIR`.
- `-Zany-build-script-metadata` lets any build script emit
  `cargo::metadata=KEY=VALUE`, exposed as `CARGO_DEP_<name>_<key>`. The older
  links-based variable is `DEP_<LINKS>_<KEY>`, keyed by the `links` value.
- `-Zcargo-lints` enables `[lints.cargo]`, including lints for unused workspace
  dependencies, naming, implicit minimum versions, and Cargo lint groups.
- `-Zbuild-analysis` writes persistent JSONL beneath `~/.cargo/log/` and adds
  `cargo report timings`, `cargo report rebuilds`, and
  `cargo report sessions`.
- `-Zhost-config` enables `[host]` linker and runner settings for build scripts
  and proc macros, distinct from `[target]`.
- `[hints]` includes `hints.mostly-unused`; related unstable controls include
  `-Zno-embed-metadata` and `panic = "immediate-abort"`.
- `-Zpublic-dependency` enables `cargo add --public` and
  `cargo tree --edges public`; the tree option is not `--depth public`.
- `-Zjson-target-spec` enables custom JSON target specs.
- `-Zscript` enables single-file packages with a frontmatter manifest.

## Rustdoc and cross-target tests

`doctest-xcompile` is stable from `1.89.0`: `cargo test --doc --target <other>`
runs doctests using the target runner rather than skipping them. Use the
`ignore-<target>` code-fence attribute where a doctest intentionally does not
run on that target.

## Edition-related manifest rules

Edition migration also removes `[project]` in favor of `[package]` and
underscore dependency keys such as `default_features` in favor of
`default-features`. A member cannot set `default-features = false` on an
inherited dependency when the workspace declaration enables them; place the
choice in `[workspace.dependencies]`. See
[edition-2024.md](edition-2024.md) for per-target editions and migration.
