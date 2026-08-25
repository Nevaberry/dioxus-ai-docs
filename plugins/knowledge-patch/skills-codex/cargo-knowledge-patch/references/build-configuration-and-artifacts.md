# Build Configuration and Artifacts

## Configuration-layer semantics

Since Cargo 1.86.0, program-and-argument values are atomic during layered
configuration merging: a higher-precedence layer replaces the entire value
instead of combining it. This applies to:

- `registry.credential-provider`
- `registries.*.credential-provider`
- `target.*.runner`
- `host.runner`
- `credential-alias.*`
- `doc.browser`

Since Cargo 1.93.0, non-mergeable list values supplied by CLI `--config` are
not overridden by environment variables. Nested non-mergeable lists replace,
rather than merge with, values from other layers.

Cargo 1.94.0 stabilizes the top-level configuration `include` key. Under the
earlier `-Zconfig-include` behavior added in 1.93.0, an include can use
`optional = true`; includes must use list form, and `include.path` accepts
neither glob nor template syntax:

```toml
include = [{ path = "local.toml", optional = true }]
```

A missing optional file is silently skipped.

## Manifests, cfg expressions, and paths

Cargo 1.88.0 accepts boolean literals in manifest and configuration cfg
predicates, including target dependency tables:

```toml
[target.'cfg(not(false))'.dependencies]
```

Cargo 1.85.0 warns that keyword-named cfgs such as `cfg(true)` and
`cfg(false)` are future-incompatible when used as identifiers. Preserve the
old identifier interpretation with raw identifiers such as `cfg(r#true)`.

The `path-bases` feature supports bases inside virtual-manifest `[patch]`
tables as of 1.85.0. Cargo 1.87.0 reports the deprecated `<target>.edition`
manifest setting; use the package-level edition.

Cargo 1.94.0 parses TOML 1.1 in manifests and configuration. TOML 1.1 syntax
in `Cargo.toml` raises the development MSRV, although publication rewrites the
manifest into syntax compatible with older parsers.

Cargo 1.93.0 deprecates a relative `install.root` without a trailing slash. It
currently resolves against the working directory, but is intended to become
relative to the configuration file like other path-valued settings.

## Build directory and artifact layout

The unstable `build.build-dir` option appeared in Cargo 1.87.0 and became
stable in Cargo 1.91.0:

```toml
[build]
build-dir = "build"
```

It selects the directory where Cargo and rustc place intermediate artifacts.
Its internal layout is not a public interface. With the feature enabled,
Cargo 1.88.0 adds `build_directory` to `cargo metadata`; build-directory
templates resolve symlinks before calculating `workspace-path-hash`.

Since Cargo 1.89.0, trim-paths remaps all paths to the configured
`build.build-dir`. Cargo also permits arbitrary configurable codegen backends.
Cargo 1.91.0 adds the experimental `-Zbuild-dir-new-layout` for future caching
and locking improvements; do not couple tools to that experimental layout.

On macOS, Cargo 1.96.0 excludes the target directory from iCloud Drive
synchronization.

## Cache and cleanup

Cargo 1.85.0 changed dependency-cache path hashes to the cross-platform
`rustc-stable-hash` algorithm. An upgrade therefore changes hash suffixes
under `$CARGO_HOME`; registry indexes and crate tarballs may be downloaded
again, and Git dependencies cloned again.

Starting with Cargo 1.88.0, automatic global-cache cleanup removes
network-downloaded entries unused for three months and locally obtained
entries unused for one month. Cleanup does not run under `--offline` or
`--frozen`. Only Cargo 1.78 and later record the access data, so caches shared
with older Cargo versions may repeatedly lose entries used only by those
versions. Disable automatic cleanup when necessary:

```toml
[cache]
auto-clean-frequency = "never"
```

Under `-Zgc`, the former `[gc]` table moved to `[cache]` in 1.88.0, with
low-level controls under `[cache.global-clean]`.

## Target, profile, and compiler configuration

Cargo 1.91.0 accepts the literal `host-tuple` in `--target` and
`build.target`, substituting the current host triple:

```console
cargo build --target host-tuple
```

Cargo 1.92.0 profiles accept `immediate-abort`:

```toml
[profile.release]
panic = "immediate-abort"
```

Cargo 1.95.0 adds `host.runner` under unstable `-Zhost-config`:

```toml
[host]
runner = "my-wrapper"
```

Cargo 1.96.0 permits `rustdocflags` in cfg-selected target configuration:

```toml
[target.'cfg(unix)']
rustdocflags = ["--cfg", "docsrs"]
```

## Link and artifact precedence

Since Cargo 1.88.0, library search paths inside `OUT_DIR` precede external
library search paths. A same-named library can therefore resolve differently
after upgrading.

Cargo 1.89.0 allows arbitrary codegen backends to be configured. When
metadata-free artifacts are enabled with `-Zno-embed-metadata`, metadata stays
in `.rmeta` files rather than also being embedded in `.rlib` and `.dylib`
files; see the nightly reference for the flag's 1.89.0 behavior.

## Terminal progress and proxy TLS

Cargo 1.87.0 adds `term.progress.term-integration`, which emits ANSI OSC 9;4
progress reports for compatible terminals.

Cargo 1.90.0 adds `http.proxy-cainfo` to select the CA bundle for TLS
connections through a proxy:

```toml
[http]
proxy-cainfo = "proxy-ca.pem"
```

## Warning policy

The unstable warning-control behavior in Cargo 1.96.0 limits
`build.warnings` to local dependencies. `allow` cannot hide denied diagnostics
or hard warnings. Denied warnings fail the build unless `--keep-going` is
used, and warning summaries count as errors.

Cargo 1.97.0 stabilizes `build.warnings` with values `warn` (default), `allow`,
and `deny`, and adds the `CARGO_BUILD_WARNINGS` environment equivalent:

```toml
[build]
warnings = "deny"
```

Changing this policy does not change the compiler flags used to identify
cached artifacts.
