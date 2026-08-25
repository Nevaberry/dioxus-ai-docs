# Builds, targets, and artifacts

Use this reference when migrating editions, controlling target selection,
relocating intermediate files, configuring rustc or rustdoc, cross-compiling,
or collecting and cleaning artifacts.

## Editions and cfg expressions

### Rust 2024 workflows

Cargo 1.85.0 supports packages with `edition = "2024"`:

```toml
[package]
edition = "2024"
```

`cargo fix --edition` also migrates workspace dependencies declared in virtual
manifests. Edition migration modes continue to cover all targets even though
ordinary fix commands now default to the default target set.

### Boolean cfg predicates

Since 1.88.0, manifests and Cargo configuration accept boolean literals in cfg
predicates, including target dependency tables:

```toml
[target.'cfg(not(false))'.dependencies]
```

Do not confuse boolean literals with legacy cfg identifiers named after
keywords; use a raw identifier such as `r#true` for the latter.

## Build directories and path mapping

### Stable intermediate build directory

Cargo 1.87.0 introduced unstable `build.build-dir`; `cargo metadata` gained a
`build_directory` field for it in 1.88.0. The setting became stable in 1.91.0:

```toml
[build]
build-dir = "build"
```

It selects where Cargo and rustc place intermediate artifacts. Its internal
layout is not a public interface and may change.

### Workspace path hashes and trimmed paths

For the unstable build-directory template, `workspace-path-hash` resolves
symlinks before hashing as of 1.88.0. Since 1.89.0, trim-paths remaps all paths
to the configured `build.build-dir`.

### Experimental layout

Cargo 1.91.0 added `-Zbuild-dir-new-layout`, an opt-in filesystem layout aimed
at caching and locking improvements. Do not build tooling around either the
stable or experimental internal layout.

### iCloud Drive

On macOS, Cargo 1.96.0 excludes the target directory from iCloud Drive
synchronization.

## Target and standard-library builds

### Build-std target detection

Under `-Zbuild-std`, Cargo 1.85.0 probes `metadata.std` in a JSON target
specification to determine whether the target supports `std`. Procedural-macro
tests always link to `std`.

Cargo 1.86.0 parses `build-std` and `build-std-features` values as
comma-separated lists:

```console
cargo +nightly build -Zbuild-std=std,panic_abort
```

As of 1.96.0, implicit standard-library dependencies from `-Zbuild-std` are
ignored by rustc's `unused_crate_dependencies` lint.

### Custom JSON targets

Cargo 1.95.0 added unstable `-Zjson-target-spec` support for builds using
custom JSON target specifications:

```console
cargo +nightly -Zjson-target-spec build --target custom-target.json
```

### Portable host selection

Since 1.91.0, `--target host-tuple` and `build.target = "host-tuple"` resolve
to the current host triple.

### Target discovery environment

Cargo 1.96.0 sets `CARGO` while running the `rustc -vV` probe used for target
discovery.

## Compiler and linker behavior

### Trailing rustc flags

Flags after `--` in `cargo rustc` take precedence on conflict as of 1.85.0:

```console
cargo rustc -- -C opt-level=3
```

`cargo rustc --print` also initializes the normal Cargo environment before
invoking rustc as of 1.86.0.

### cdylib build-script link arguments

Since 1.87.0, arguments emitted with `cargo::rustc-link-arg-cdylib` are not
passed to test targets.

### OUT_DIR search precedence

Library search paths under `OUT_DIR` precede external library search paths as
of 1.88.0. Account for the new winner when libraries share a name.

### Configurable codegen backends

Cargo 1.89.0 allows arbitrary codegen backends to be configured.

### Metadata-free library artifacts

The unstable `-Zno-embed-metadata` option added in 1.89.0 passes
`-Zembed-metadata=no` to rustc. Metadata then lives only in `.rmeta` files
rather than also being embedded in `.rlib` and `.dylib` artifacts.

## Profiles and diagnostics

### Mostly-unused hints

Cargo 1.89.0 can pass rustc's `-Zhint-mostly-unused` setting through as a
profile option. In 1.90.0, unstable `-Zprofile-hint-mostly-unused` added a
manifest `[hints]` form:

```toml
[hints]
mostly-unused = true
```

### Immediate-abort panic

Cargo profiles accept `immediate-abort` as of 1.92.0:

```toml
[profile.release]
panic = "immediate-abort"
```

### Unicode diagnostics

Unstable `-Zrustc-unicode`, added in 1.93.0, enables rustc's Unicode error
format in diagnostics displayed by Cargo:

```console
cargo +nightly -Zrustc-unicode build
```

## Documentation and tests

### Cross-compiled doctests

Doctest cross-compilation is stable as of 1.89.0. When host and target differ,
Cargo runs doctests like other tests.

### Rustdoc dep-info

Unstable `-Zrustdoc-depinfo`, added in 1.88.0, uses rustdoc dep-info files to
decide whether documentation needs regeneration:

```console
cargo +nightly doc -Zrustdoc-depinfo
```

### Mergeable rustdoc information

Unstable `-Zrustdoc-mergeable-info`, added in 1.93.0, lets `cargo doc` merge
cross-crate indexes from separate output directories and run rustdoc in
parallel:

```console
cargo +nightly -Zrustdoc-mergeable-info doc
```

### Cfg-specific rustdoc flags

Cargo 1.96.0 allows target tables selected by cfg expressions to set
`rustdocflags`:

```toml
[target.'cfg(unix)']
rustdocflags = ["--cfg", "docsrs"]
```

## Artifact scope and cleaning

### Workspace cleaning

Cargo 1.93.0 added `cargo clean --workspace`, which removes artifacts
belonging to workspace members:

```console
cargo clean --workspace
```

### Explicit target-directory safety

Since 1.97.0, `cargo clean --target-dir` rejects a path that does not look like
a Cargo target directory, reducing the risk of deleting an unrelated path.

### Publish and package artifacts

`cargo publish` no longer keeps `.crate` tarballs as final artifacts as of
1.93.0. Use `cargo package` when the archive itself is required.

During package verification, Cargo 1.91.0 began reusing the workspace target
directory instead of creating one inside the unpacked package source.
