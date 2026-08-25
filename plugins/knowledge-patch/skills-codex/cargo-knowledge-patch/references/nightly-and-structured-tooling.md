# Nightly and Structured Tooling

All features in this reference require the stated unstable opt-in unless a
later entry explicitly says the feature became stable. Pin the nightly
toolchain in automation and validate structured output before parsing it.

## Feature unification and public dependencies

Cargo 1.86.0 adds `-Zfeature-unification` and the
`resolver.feature-unification` configuration for controlling workspace feature
unification. Cargo 1.90.0 extends the implementation to per-package
unification.

With `-Zpublic-dependency`, Cargo 1.87.0 initially displays public dependency
trees using `--depth public`. Cargo 1.92.0 replaces this with:

```console
cargo -Zpublic-dependency tree --edges public
```

The same 1.92.0 implementation makes `cargo add` consider public dependencies
while selecting a version.

## Build-standard-library and target specifications

Cargo 1.85.0 uses `metadata.std` in a JSON target specification to detect
whether `-Zbuild-std` can build `std`; procedural-macro tests always link it.
Cargo 1.86.0 accepts comma-separated `build-std` and
`build-std-features` lists.

Cargo 1.95.0 introduces `-Zjson-target-spec` for building against custom JSON
target files:

```console
cargo +nightly -Zjson-target-spec build --target custom-target.json
```

Cargo 1.96.0 prevents implicit standard-library crates from triggering
`unused_crate_dependencies` under `-Zbuild-std`.

## Build directories and dependency artifacts

The `build.build-dir` experiment begins in Cargo 1.87.0, exposes
`build_directory` through metadata and makes `workspace-path-hash`
symlink-aware in 1.88.0, and becomes stable in 1.91.0. The separate
`-Zbuild-dir-new-layout` flag added in 1.91.0 opts into an experimental
filesystem layout.

Cargo 1.89.0 adds `-Zno-embed-metadata`, passing `-Zembed-metadata=no` to
rustc. Metadata then lives only in `.rmeta`, rather than also in `.rlib` and
`.dylib` artifacts.

Cargo 1.93.0 changes `-Zbindeps` so artifact dependencies do not propagate to
procedural-macro or build dependencies.

## Profiles, hints, and warnings

Cargo 1.89.0 can pass rustc's `-Zhint-mostly-unused` as a profile option.
Cargo 1.90.0 adds `-Zprofile-hint-mostly-unused` and a manifest hints table:

```toml
[hints]
mostly-unused = true
```

Under `-Zwarnings`, Cargo 1.96.0 restricts `build.warnings` to local
dependencies. `allow` cannot mask denied diagnostics or hard warnings, denied
warnings fail the build unless `--keep-going` is used, and warning summaries
are errors. The policy becomes stable in Cargo 1.97.0.

## SBOM and unit-graph data

Cargo 1.87.0 adds `-Zsbom` and `build.sbom`, generating SBOM precursor files
beside each compiled artifact.

In Cargo 1.88.0, `--unit-graph` uses Package ID Specifications for package
identity. Structured consumers must parse that syntax.

## Rustdoc and diagnostics

Cargo 1.88.0 adds `-Zrustdoc-depinfo`, using rustdoc dep-info to decide whether
documentation needs regeneration:

```console
cargo +nightly doc -Zrustdoc-depinfo
```

Cargo 1.93.0 adds `-Zrustc-unicode` for Unicode rustc diagnostics displayed by
Cargo, and `-Zrustdoc-mergeable-info` for merging cross-crate indexes from
separate output directories while running rustdoc in parallel:

```console
cargo +nightly -Zrustc-unicode build
cargo +nightly -Zrustdoc-mergeable-info doc
```

## Timings and persistent build analysis

Cargo 1.91.0 adds `-Zsection-timings`, extending the HTML and JSON produced by
`cargo build --timings` with individual rustc section timings:

```console
cargo +nightly -Zsection-timings build --timings
```

The same release introduces `-Zbuild-analysis`, which persists timings and
rebuild reasons. Cargo 1.93.0 stores one JSONL file per Cargo invocation under
`~/.cargo/log/`.

Cargo 1.94.0 removes formatted `--timings=<FMT>` values. Use structured
build-analysis logs for machine-readable data. It also adds:

- `cargo report sessions` to list build-session IDs,
- `cargo report rebuilds` to inspect earlier rebuild reasons, and
- `cargo report timings` to regenerate an HTML timing report.

Cargo 1.95.0 adds a `command` field to the build-analysis `BuildStarted`
message so consumers can identify the Cargo command for each session.

## Removed build output interfaces

Cargo 1.93.0 removes the unstable `build-plan` feature entirely. Use plumbing
commands, `--unit-graph`, or structured build-analysis logging.

Cargo 1.95.0 removes the deprecated unstable `--out-dir`; use
`--artifact-dir`.

## Configured lockfile paths

Cargo 1.94.0 introduces `resolver.lockfile-path` under `-Zlockfile-path`,
replacing the planned-for-removal CLI `--lockfile-path`:

```toml
[resolver]
lockfile-path = "/workspace/locks/Cargo.lock"
```

Cargo 1.95.0 removes the CLI option and makes `cargo fix` and `cargo install`
honor the configured path. Cargo 1.96.0 then deliberately changes install
behavior: `cargo install` ignores `resolver.lockfile-path`. Do not redirect an
install lockfile through this setting.

## Cargo lint groups

Cargo 1.94.0 expands `-Zcargo-lints` with Clippy-like lint groups and
`implicit_minimum_version_req`.

Cargo 1.95.0 adds:

- `non_kebab_case_bins`
- `missing_lints_inheritance`
- `unused_workspace_package_fields`
- `unused_workspace_dependencies`
- `redundant_homepage`
- `redundant_readme`
- `non_*_case_features`
- mutually exclusive `non_kebab_case_packages` and
  `non_snake_case_packages`

On-by-default lints do not run when a package's MSRV is too old for them.

Cargo 1.96.0 adds `unused_dependencies`:

```toml
[lints.cargo]
unused_dependencies = "warn"
```

Cargo 1.97.0 gives explicitly configured lint levels precedence over defaults.
It also evaluates `unused_dependencies` independently of rustc's
`unused_crate_dependencies` level.

## Additional evolving experiments

- Cargo 1.87.0 supports JSON package file listings through unstable
  `cargo package --message-format`.
- Cargo 1.89.0 makes `-Zscript` ignore enclosing workspaces.
- Cargo 1.90.0 adds `multiple-build-scripts`.
- Cargo 1.92.0 tightens Cargo script frontmatter and adds per-script output
  directories.
- Cargo 1.93.0 allows optional configuration includes under
  `-Zconfig-include` and supports shallow Git CLI fetching under `-Zgit`.
- Cargo 1.94.0 allows any build script to publish metadata under
  `-Zany-build-script-metadata`.
- Cargo 1.95.0 adds host runners under `-Zhost-config`.
