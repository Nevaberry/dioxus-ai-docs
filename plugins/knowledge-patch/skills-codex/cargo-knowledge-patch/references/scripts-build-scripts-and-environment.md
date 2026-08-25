# Scripts, Build Scripts, and Environment

## Build-script inputs and reruns

Cargo 1.85.0 exposes every activated package feature to build scripts in
`CARGO_CFG_FEATURE`.

Since Cargo 1.86.0, `cargo::rerun-if-env-changed` correctly notices changes
whose values originate from Cargo's `[env]` configuration table.

Cargo 1.93.0 exposes `CARGO_CFG_DEBUG_ASSERTIONS` according to the active
profile's debug-assertion setting.

## Link arguments and output directories

Cargo 1.87.0 stops forwarding link arguments emitted with
`cargo::rustc-link-arg-cdylib` to test targets. Those arguments apply to the
intended `cdylib`, not the test harness.

Since Cargo 1.88.0, library search paths inside `OUT_DIR` take precedence over
external search paths.

With unstable `multiple-build-scripts`, Cargo 1.92.0 gives each script a
`<script-name>_OUT_DIR` environment variable.

## Multiple build scripts

Cargo 1.90.0 introduces the unstable `multiple-build-scripts` feature:

```toml
cargo-features = ["multiple-build-scripts"]

[package]
build = ["build.rs", "generate.rs"]
```

Do not assume one shared output directory; use the named environment variable
for each script.

## The `CARGO` executable path

Cargo 1.87.0 gives external subcommands the path to the correct Cargo binary
in `CARGO`. It is not a promise that the variable can be used as a generic
Cargo wrapper.

Cargo 1.88.0 stops canonicalizing that executable path, so a path invoked
through symlinks remains symlinked. Cargo 1.96.0 also sets `CARGO` while
running the `rustc -vV` target-discovery probe.

## Runtime binary discovery

Cargo 1.94.0 provides `CARGO_BIN_EXE_<name>` in the runtime environment as
well as at compile time. Runtime code launched by Cargo can use it to locate a
Cargo-built binary.

## Cargo script maintenance and isolation

Under `-Zscript`, Cargo 1.85.0 can add or remove script dependencies and
migrate a script manifest across editions. Script builds preserve the
configured release profile.

Cargo 1.86.0 makes `cargo pkgid` support Cargo scripts. Cargo 1.89.0 makes a
Cargo script independent of any enclosing workspace.

Cargo 1.92.0 tightens script frontmatter:

- only horizontal whitespace may follow a frontmatter fence,
- fields invalid for Cargo scripts are rejected, and
- `bin.name` defaults to `package.name`.

That release stores script lockfiles in the build directory and derives the
script target directory using build-directory templating.

Cargo 1.95.0 supersedes the lockfile-location detail: scripts load
configuration relative to the script file, and their lockfiles are
script-specific independently of `build.build-dir`.

## Metadata from build scripts

With Cargo 1.94.0 and `-Zany-build-script-metadata`, any build script may emit:

```text
cargo::metadata=KEY=VALUE
```

Dependents receive it as `CARGO_DEP_<name>_<key>`. This lifts the earlier
restriction on which build scripts could publish dependency metadata.

## Build-standard-library interactions

Under `-Zbuild-std`, Cargo 1.85.0 probes `metadata.std` in a JSON target
specification to decide whether the target supports `std`. Tests of procedural
macros always link to `std`.

Cargo 1.86.0 parses both `build-std` and `build-std-features` values as
comma-separated lists:

```console
cargo +nightly build -Zbuild-std=std,panic_abort
```

Cargo 1.96.0 excludes implicit standard-library dependencies from
`unused_crate_dependencies` when `-Zbuild-std` is active.

## Artifact dependencies

With `-Zbindeps`, Cargo 1.93.0 no longer propagates artifact dependencies to
procedural-macro or build dependencies. Model dependency graphs and build
inputs using the consuming target's actual edge rather than assuming that
propagation.
