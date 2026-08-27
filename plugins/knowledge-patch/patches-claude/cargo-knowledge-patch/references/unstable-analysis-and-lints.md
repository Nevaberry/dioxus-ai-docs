# Unstable analysis, lints, and build controls

Use this reference when a workflow intentionally depends on nightly Cargo.
Keep the required `-Z` flag explicit, and verify it against the pinned
toolchain.

## Build analysis and timings

### Persistent analysis

Cargo 1.91.0 added `-Zbuild-analysis`, which persists timings and rebuild
reasons for later queries.

Cargo 1.93.0 writes timing and rebuild-reason records as JSONL under
`~/.cargo/log/`, using a unique file for each invocation.

Cargo 1.94.0 added:

- `cargo report sessions` to list build-session IDs;
- `cargo report rebuilds` to inspect past rebuild reasons;
- `cargo report timings` to replay an HTML timing report.

Cargo 1.95.0 added a `command` field to each `BuildStarted` record so consumers
can identify the command associated with a session.

### Section timings

Cargo 1.91.0 added `-Zsection-timings`, which includes individual rustc
compilation-section timings in HTML and JSON `cargo build --timings` output:

```console
cargo +nightly -Zsection-timings build --timings
```

Formatted `--timings=<FMT>` was removed in 1.94.0. Use build-analysis JSONL for
machine-readable data and `cargo report timings` for HTML.

## Supply-chain and graph output

### SBOM precursors

Cargo 1.87.0 added `-Zsbom` and `build.sbom`, generating SBOM precursor files
beside each compiled artifact.

### Unit graphs

As of 1.88.0, unstable unit-graph output expresses package identities as
Package ID Specifications.

### Artifact dependencies

With `-Zbindeps`, Cargo 1.93.0 no longer propagates artifact dependencies to
procedural-macro or build dependencies.

## Cargo lints

### Lint groups and minimum versions

Cargo 1.94.0 expanded `-Zcargo-lints` with Clippy-like lint groups and the
`implicit_minimum_version_req` lint.

### Expanded manifest lints

Cargo 1.95.0 added:

- `non_kebab_case_bins`;
- `missing_lints_inheritance`;
- `unused_workspace_package_fields`;
- `unused_workspace_dependencies`;
- `redundant_homepage` and `redundant_readme`;
- the `non_*_case_features` family;
- mutually exclusive `non_kebab_case_packages` and
  `non_snake_case_packages`.

On-by-default Cargo lints do not run when the package MSRV is too old to
support them.

### Unused dependencies

Cargo 1.96.0 added the `unused_dependencies` Cargo lint:

```toml
[lints.cargo]
unused_dependencies = "warn"
```

Since 1.97.0, explicit lint levels take precedence over defaults, and
`unused_dependencies` is evaluated independently of rustc's
`unused_crate_dependencies` setting.

## Experimental dependency controls

### Feature unification

Cargo 1.86.0 introduced `-Zfeature-unification` and
`resolver.feature-unification` for workspace control. Cargo 1.90.0 added
per-package unification.

### Public dependencies

Cargo 1.87.0 initially exposed public dependencies through
`cargo tree --depth public` under `-Zpublic-dependency`. Cargo 1.92.0 replaced
that syntax with `cargo tree --edges public` and made `cargo add` consider
public-dependency status during version selection.

## Experimental compiler and documentation controls

### Rustdoc regeneration and merging

Cargo 1.88.0 added `-Zrustdoc-depinfo` for dep-info-driven documentation
rebuild decisions. Cargo 1.93.0 added `-Zrustdoc-mergeable-info` for parallel
rustdoc execution and cross-crate index merging.

### Embedded metadata

Cargo 1.89.0 added `-Zno-embed-metadata`, leaving metadata only in `.rmeta`
instead of embedding it in `.rlib` and `.dylib` outputs.

### Profile hints

Cargo 1.89.0 began passing the `-Zhint-mostly-unused` rustc setting through
profiles. Cargo 1.90.0 added the `[hints] mostly-unused = true` manifest form
under `-Zprofile-hint-mostly-unused`.

### Unicode diagnostics

Cargo 1.93.0 added `-Zrustc-unicode` for rustc's Unicode diagnostic format.

### JSON target specifications

Cargo 1.95.0 added `-Zjson-target-spec` support for custom JSON target files.

## Experimental build structure

### Multiple build scripts

Cargo 1.90.0 added `multiple-build-scripts`; Cargo 1.92.0 added a distinct
`<script-name>_OUT_DIR` for each script.

### New build-directory layout

Cargo 1.91.0 added `-Zbuild-dir-new-layout` as an experimental layout for
caching and locking improvements.

### Standard-library builds

Cargo 1.85.0 uses `metadata.std` in JSON target specifications for
`-Zbuild-std` target detection. Cargo 1.86.0 made `build-std` and
`build-std-features` accept comma-separated lists. Cargo 1.96.0 excludes
implicit standard-library dependencies from `unused_crate_dependencies`.

### Configured lockfiles

Cargo 1.94.0 added `resolver.lockfile-path` under `-Zlockfile-path`. Cargo
1.95.0 made `cargo fix` and, temporarily, `cargo install` honor it. Cargo
1.96.0 changed `cargo install` to ignore the configured path.
