---
name: cargo-knowledge-patch
description: Cargo
version: "1.97.0"
license: MIT
metadata:
  author: Nevaberry
---


# Cargo Knowledge Patch

Use this skill when working on Cargo manifests, configuration, workspaces,
dependency resolution, packaging, publishing, build scripts, or unstable Cargo
tooling. First determine the project's Cargo version, Rust edition, MSRV,
workspace shape, target platforms, and enabled `-Z` flags. Apply guidance only
when the installed Cargo is new enough for it.

## Reference index

| Reference | Topics |
| --- | --- |
| [build-configuration-and-artifacts.md](references/build-configuration-and-artifacts.md) | Layered configuration, cache cleanup, target selection, build directories, warnings, artifacts, platform behavior |
| [commands-workspaces-and-dependencies.md](references/commands-workspaces-and-dependencies.md) | Edition migration, workspaces, `fix`, `tree`, `metadata`, `clean`, dependency and target commands |
| [packaging-publishing-and-registries.md](references/packaging-publishing-and-registries.md) | Package validation, lockfiles, reproducibility, workspace publishing, registries, Git and SSH transport |
| [scripts-build-scripts-and-environment.md](references/scripts-build-scripts-and-environment.md) | Cargo scripts, multiple build scripts, Cargo-provided environment variables, link arguments and script state |
| [nightly-and-structured-tooling.md](references/nightly-and-structured-tooling.md) | Unstable feature flags, build analysis, Cargo lints, SBOM precursors, unit graphs, rustdoc and lockfile experiments |

## Apply this patch

1. Read `rust-version`, `edition`, workspace resolver settings, and any
   `cargo-features` declaration from the manifests.
2. Check `cargo --version`; unstable behavior also depends on the selected
   nightly toolchain and the exact `-Z` flags.
3. Inspect `.cargo/config.toml`, environment variables, and CLI `--config`
   values as separate configuration layers.
4. Identify whether commands run against a virtual workspace, a selected
   package, the host, or a cross-compiled target.
5. Treat the target directory, intermediate build directory, package archive,
   and persistent analysis logs as distinct artifact locations.
6. For publishing, check registry credentials, package dirtiness, lockfile
   policy, workspace dependency order, and whether a local `.crate` archive is
   required.
7. For build scripts and Cargo scripts, distinguish compile-time environment,
   runtime environment, per-script output directories, and script-local state.

## Breaking changes and deprecations

### Patch vulnerable Cargo installations

Cargo 1.94 fixes CVE-2026-33055 and CVE-2026-33056. On Unix-like systems,
earlier affected versions can let a malicious crate archive alter permissions
on arbitrary filesystem paths during extraction. Upgrade Cargo before
fetching or unpacking untrusted crates.

### Update removed unstable interfaces

- The unstable `build-plan` feature is gone. Use plumbing commands,
  `--unit-graph`, or structured `-Zbuild-analysis` logs.
- `--timings=<FMT>` is gone. Use build-analysis data for machine-readable
  timings or `cargo report timings` for HTML.
- The deprecated unstable `--out-dir` is gone; use `--artifact-dir`.
- The unstable `--lockfile-path` CLI option is gone. Under
  `-Zlockfile-path`, configure `resolver.lockfile-path`.

### Do not rely on `cargo publish` retaining archives

`cargo publish` no longer leaves the `.crate` tarball as a final local
artifact. Run `cargo package` when a workflow needs the archive. Publishing
several workspace packages is not atomic: a server failure may leave only a
prefix of the requested packages published.

### Recheck fix-command target scope

`cargo fix` and `cargo clippy --fix` operate on default targets unless
`--all-targets` is passed. Edition and edition-idiom migrations still imply
all targets. Also, `cargo fix --allow-dirty` now implies `--allow-staged`.

```console
cargo fix --all-targets
cargo clippy --fix --all-targets
```

### Replace deprecated manifest and configuration forms

- Move a deprecated `<target>.edition` setting to the package-level edition.
- Avoid `cargo publish --token` in new workflows.
- Make `install.root` absolute or use a trailing slash while migrating away
  from working-directory-relative interpretation.
- Do not put a trailing slash on a registry `config.json` `api` URL.
- Spell keyword-named cfg identifiers as raw identifiers, such as
  `cfg(r#true)`, when identifier semantics are intended.

## High-value stable behavior

### Rust 2024 and manifest parsing

Cargo supports `edition = "2024"`, and `cargo fix --edition` migrates workspace
dependencies declared in virtual manifests. Cargo 1.94 parses TOML 1.1 in
manifests and configuration; using TOML 1.1 syntax in `Cargo.toml` raises the
development MSRV even though the manifest emitted for publication remains
compatible with older parsers.

```toml
[package]
edition = "2024"
```

### Intermediate build directories

`build.build-dir` is stable. It separates intermediate Cargo and rustc files
from the target directory, but its internal layout is not public and may
change. Trimmed paths remap to this directory. When tools need its resolved
location, read `build_directory` from `cargo metadata`.

```toml
[build]
build-dir = "build"
```

### Warning policy

Cargo 1.97 honors `build.warnings = "warn" | "allow" | "deny"` and
`CARGO_BUILD_WARNINGS`; the default is `warn`. The policy does not alter
compiler flags used to identify cached artifacts. `deny` makes warnings and
warning summaries fail the build unless `--keep-going` allows other work to
continue. `allow` cannot conceal denied diagnostics or hard warnings.

```toml
[build]
warnings = "deny"
```

### Configuration includes

The top-level `include` key is stable and can split shared Cargo configuration
across files. The earlier unstable optional form requires list syntax:

```toml
include = [{ path = "local.toml", optional = true }]
```

An optional missing file is skipped. `include.path` does not accept glob or
template syntax.

### Host target shorthand

Use `host-tuple` in `--target`, `build.target`, and
`cargo metadata --filter-platform` when the current machine's host triple is
needed without hard-coding it.

```console
cargo build --target host-tuple
cargo metadata --filter-platform host-tuple
```

### Workspace operations

- `cargo tree --depth workspace` limits output to workspace members.
- `cargo clean --workspace` removes artifacts belonging to workspace members.
- `cargo tree --format` accepts long variables such as `{package}` and
  `{features}`.
- `--package` combined with `--workspace` errors if a requested package is
  missing.

```console
cargo tree --depth workspace
cargo clean --workspace
cargo tree --format '{package} {features}'
```

### Safer command conveniences

`-m` is an alias for `--manifest-path`. `cargo clean --target-dir` refuses a
path that does not look like a Cargo target directory. `cargo init` refuses to
initialize the user's home directory. With no explicit registry, `cargo info`
defaults to the local package.

```console
cargo build -m path/to/Cargo.toml
```

## Packaging and registry checklist

- `cargo package` includes `Cargo.lock`; `--exclude-lockfile` stops verification
  of an existing lockfile.
- Package validation examines external readme, license-file, and symlink
  targets, and reports a dirty workspace manifest.
- Generated package files have deterministic timestamps.
- Multi-package publishing supports `--workspace` and repeated `-p`, but is
  non-atomic.
- Registry HTTP 429 responses honor `Retry-After`.
- Registry index consumers must tolerate a missing `pubtime` while historical
  entries are being backfilled.
- `cargo vendor` preserves `.rej` and `.orig` and directly extracts registry
  sources so vendored files match their originals.

## Build scripts and Cargo scripts

- Build scripts receive activated features in `CARGO_CFG_FEATURE` and profile
  debug-assertion state in `CARGO_CFG_DEBUG_ASSERTIONS`.
- With multiple build scripts, each script gets
  `<script-name>_OUT_DIR`.
- `CARGO_BIN_EXE_<name>` is available at runtime as well as compile time.
- The `CARGO` value is the invoked Cargo path and may retain symlinks; external
  subcommands must not treat it as a general-purpose wrapper.
- Cargo script manifests have strict frontmatter fences, default `bin.name` to
  `package.name`, load configuration relative to the script, and use
  script-specific lockfiles.

## Unstable-feature discipline

Unstable Cargo flags evolve quickly. Keep each `-Z` opt-in explicit in CI,
check the exact toolchain before consuming structured output, and avoid
depending on experimental filesystem layouts. In particular:

- Public dependency trees use `--edges public`; the older `--depth public`
  spelling was replaced.
- `-Zbuild-analysis` writes one JSONL log per invocation under
  `~/.cargo/log/` and supports `cargo report sessions`, `rebuilds`, and
  `timings`.
- `-Zcargo-lints` has lint groups and independent explicit-level precedence.
- `-Zlockfile-path` does not redirect `cargo install`; install intentionally
  ignores the configured path.
- `-Zbuild-std` accepts comma-separated components and excludes implicit
  standard-library crates from `unused_crate_dependencies`.

Consult the topic references before changing an unstable workflow; they record
the transitions and the structured fields consumers must parse.
