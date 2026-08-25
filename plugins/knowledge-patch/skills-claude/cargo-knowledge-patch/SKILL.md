---
name: cargo-knowledge-patch
description: Cargo
version: 1.97.0
license: MIT
metadata:
  author: Nevaberry
---


# Cargo Knowledge Patch

Use this skill when changing Cargo manifests, configuration, dependency
workflows, builds, workspaces, packaging, publishing, Cargo scripts, or
unstable Cargo features. Inspect the repository and installed toolchain before
applying the guidance: project manifests, lockfiles, configuration, tests, and
observed behavior take precedence.

## Working method

1. Run `cargo --version` and identify whether the repository pins a toolchain.
2. Inspect `Cargo.toml`, `Cargo.lock`, `.cargo/config.toml`, workspace
   manifests, and CI commands relevant to the task.
3. Separate stable behavior from features that still require nightly Cargo
   and `-Z` flags.
4. Check the compatibility and removal notes before copying an older command
   line or configuration key.
5. Open the task-specific reference from the index and preserve the
   repository's minimum supported Rust version.
6. Validate manifest and configuration changes with the narrowest applicable
   Cargo command before running the full project test suite.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrades-and-compatibility.md](references/upgrades-and-compatibility.md) | Security fixes, removals, deprecations, changed defaults, platform requirements, migration hazards |
| [configuration-networking-and-cache.md](references/configuration-networking-and-cache.md) | Configuration merging and includes, cache cleanup, Git and SSH, proxies, runners, warning policy |
| [builds-targets-and-artifacts.md](references/builds-targets-and-artifacts.md) | Editions, targets, build directories, rustc and rustdoc, profiles, doctests, artifacts, cleaning |
| [workspaces-dependencies-and-metadata.md](references/workspaces-dependencies-and-metadata.md) | Workspaces, feature unification, dependency trees, metadata, vendoring, target filtering |
| [packaging-publishing-and-registries.md](references/packaging-publishing-and-registries.md) | Package validation, archives, workspace publishing, registry data and APIs |
| [scripts-build-scripts-and-subcommands.md](references/scripts-build-scripts-and-subcommands.md) | Cargo scripts, build-script environment and metadata, external subcommands, completions and help |
| [unstable-analysis-and-lints.md](references/unstable-analysis-and-lints.md) | Build analysis, timings, SBOM data, Cargo lints, unit graphs, experimental build controls |

## Breaking changes and migration checks

### Upgrade vulnerable Cargo installations

Treat crate extraction as a security boundary. Affected older Cargo versions on
Unix-like systems can allow malicious archives to alter permissions outside
the extraction tree. Use a toolchain containing the extraction fix before
handling untrusted crates.

### Replace removed interfaces

- Replace the removed unstable `build-plan` feature with plumbing commands,
  `--unit-graph`, or structured build-analysis logs.
- Replace removed unstable `--out-dir` with `--artifact-dir`.
- Replace removed `--lockfile-path` command-line usage with
  `resolver.lockfile-path` under `-Zlockfile-path`, while accounting for
  command-specific behavior.
- Do not pass a format value to `--timings`; use build-analysis logs for
  machine-readable data and `cargo report timings` for an HTML report.
- For public dependencies, use `cargo tree --edges public`, not the earlier
  `--depth public` spelling.

### Recheck changed defaults

- `cargo fix` and `cargo clippy --fix` operate on default targets unless
  `--all-targets` is requested. Edition migration modes still imply all
  targets.
- `cargo publish` does not retain the generated `.crate` archive. Run
  `cargo package` when a local archive is required.
- `cargo metadata` is independent of `CARGO_BUILD_TARGET`; use
  `--filter-platform` when platform filtering is required.
- `cargo install` ignores a configured `resolver.lockfile-path`.
- `cargo package` includes `Cargo.lock`, but `--exclude-lockfile` can skip
  verification of a present lockfile.

### Audit configuration layering

Program-and-argument settings such as runners, credential providers,
credential aliases, and documentation browsers are atomic values when
configuration layers merge. Nested non-mergeable lists replace rather than
merge, and a `--config` value takes precedence over the corresponding
environment value.

## High-value stable features

### Control build output and warnings

```toml
[build]
build-dir = "build"
warnings = "deny"
```

`build.build-dir` relocates intermediate artifacts, but its internal layout is
not a supported interface. `build.warnings` accepts `warn`, `allow`, or `deny`;
the environment equivalent is `CARGO_BUILD_WARNINGS`. Warning policy does not
change compiler flags used to identify cached artifacts.

### Reuse shared configuration

Top-level `include` can compose Cargo configuration files:

```toml
include = ["../shared/cargo.toml"]
```

Nightly optional includes use list form with `{ path, optional = true }`.
Do not use glob or template syntax for include paths.

### Select the current host portably

Use `host-tuple` where Cargo accepts a target:

```console
cargo build --target host-tuple
cargo metadata --filter-platform host-tuple
```

This avoids hard-coding the host target triple.

### Use current command conveniences

`-m` is the short form of `--manifest-path`:

```console
cargo build -m crates/app/Cargo.toml
```

`cargo clean --workspace` limits cleaning to workspace members. An explicit
`cargo clean --target-dir` now rejects paths that do not resemble Cargo target
directories.

### Publish related workspace crates

```console
cargo publish --workspace
cargo publish -p core -p app
```

Cargo can order and publish workspace crates that depend on one another.
Publishing is not transactional: a registry failure can leave only part of
the requested set published.

### Configure proxy trust

```toml
[http]
proxy-cainfo = "proxy-ca.pem"
```

Use `http.proxy-cainfo` for the CA bundle used by TLS connections through a
proxy. Keep registry API URLs free of a trailing slash.

### Set profile and target behavior

Profiles accept an immediate-abort panic strategy:

```toml
[profile.release]
panic = "immediate-abort"
```

Target tables selected by cfg expressions can set `rustdocflags`:

```toml
[target.'cfg(unix)']
rustdocflags = ["--cfg", "docsrs"]
```

Boolean literals are valid cfg predicates in manifests and configuration.

## Build scripts and Cargo scripts

Build scripts receive activated features through `CARGO_CFG_FEATURE` and the
profile's debug-assertion state through `CARGO_CFG_DEBUG_ASSERTIONS`.
`rerun-if-env-changed` observes values supplied through Cargo's `[env]`
configuration.

Cargo-script behavior remains gated by `-Zscript`. Script configuration and
lockfiles are relative to the script, scripts ignore enclosing workspaces, and
their manifests accept only script-valid fields with strict frontmatter
fences. Read the scripts reference before relying on build-directory or
lockfile placement.

## Nightly feature discipline

Do not remove a required `-Z` flag merely because a related component became
stable. The following areas still include unstable controls:

- feature unification and public-dependency handling;
- standard-library builds and custom JSON target specifications;
- multiple build scripts and arbitrary build-script metadata;
- Cargo lints, Unicode diagnostics, and mergeable rustdoc information;
- build analysis, section timings, SBOM precursors, and experimental build
  directory layout;
- Cargo scripts, configurable lockfile paths, and artifact dependencies.

Confirm the exact flag and current behavior in the relevant reference. Keep
nightly-only configuration isolated when stable Cargo must still parse the
project.

## Validation checklist

- Confirm the installed Cargo version and pinned toolchain.
- Parse all touched manifests and configuration with the project's supported
  toolchains.
- Run `cargo metadata` after workspace, dependency, feature, or target changes.
- Run `cargo package --list` when package contents change.
- Run `cargo package` when archive generation or publication readiness matters.
- Test both host and cross-target paths when runners, doctests, build scripts,
  or target-specific flags change.
- Treat registry publishing as externally visible and non-atomic.
- Avoid depending on internal target or build-directory layouts.
- Record why an unstable flag is needed and which commands require it.
