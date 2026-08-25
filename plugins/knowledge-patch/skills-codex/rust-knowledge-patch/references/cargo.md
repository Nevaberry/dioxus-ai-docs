# Cargo

## Configuration and command-line precedence

### Merge and flag behavior

- Since 1.85.0, compiler flags placed at the end of a Cargo command take precedence over earlier conflicting flags, so `cargo rustc -- -C opt-level=1` is an effective override.
- Since 1.86.0, a configuration key describing a program path plus arguments replaces the earlier value as one unit during merge rather than combining values.
- Since 1.94.0, a top-level `include` array in `.cargo/config.toml` loads required paths or `{ path = "...", optional = true }` entries.

### Build output and warning policy

- Since 1.91.0, stable `build.build-dir` relocates intermediate Cargo/rustc artifacts. Its internal structure is not a supported interface.
- Since 1.97.0, stable `build.warnings = "allow" | "warn" | "deny"` controls local-package warnings without cache invalidation from `RUSTFLAGS=-Dwarnings`. `CARGO_BUILD_WARNINGS=deny cargo check --keep-going` is suitable for a temporary CI policy.
- Successful linker output is exposed through the special warn-by-default `linker_messages` lint since 1.97.0. It is not part of `warnings`; configure it explicitly under `[lints.rust]`.

### Target and documentation flags

- Since 1.91.0, `--target host-tuple` and `build.target = "host-tuple"` substitute the machine's actual host triple.
- Since 1.96.0, cfg-based target configuration tables support `rustdocflags`.
- Custom JSON targets require nightly Cargo's `-Z json-target-spec` as of 1.95.0; stable Cargo/rustc no longer accepts them.

## Build-script environment and linking

- Since 1.85.0, build scripts receive enabled features in `CARGO_CFG_FEATURE`.
- Since 1.93.0, build scripts receive `CARGO_CFG_DEBUG_ASSERTIONS` according to the profile. `static-init` 1.0.1–1.0.3 breaks when this variable appears; upgrade or avoid those versions.
- Cargo's current changelog adds `CARGO_MANIFEST_PATH`, pointing to the manifest file itself alongside `CARGO_MANIFEST_DIR`; compile-time consumers may use `env!("CARGO_MANIFEST_PATH")`.
- `cargo::rustc-link-arg-cdylib=ARG` is no longer applied to test targets; emit `cargo::rustc-link-arg-tests=ARG` separately when tests need it (`cargo-changelog`).
- With nightly `-Zany-build-script-metadata`, any build script may emit `cargo::metadata=KEY=VALUE`; dependents receive `CARGO_DEP_<name>_<key>` (`cargo-changelog`).

## Manifests and target discovery

- Cargo accepts TOML 1.1 syntax since 1.94.0, including multiline inline tables, trailing commas, `\xHH`/`\e` escapes, and times without seconds. These raise the development MSRV and can require parser upgrades; published manifests are rewritten for older parsers.
- The `package.autolib` manifest key independently controls automatic library-target discovery (`cargo-changelog`).
- Raw identifiers such as `r#gen` are accepted in cfg expressions since 1.85.0; bare keywords produce a future-incompatibility warning.
- Rust 2024 manifest spellings and inherited dependency defaults have edition-specific constraints detailed in [edition-2024.md](edition-2024.md).

## Package selection and workspaces

- Since 1.86.0, combining `--package` and `--workspace` errors when the named package is absent instead of silently ignoring it.
- `cargo publish --workspace` publishes crates in dependency order and verifies the complete set as if published since 1.90.0. It is not atomic; failures can leave a partially published workspace.
- `cargo package --package name` now packages only explicitly named packages, not also the current-directory package (`cargo-changelog`).
- `cargo tree --depth workspace` restricts output to workspace members (`cargo-changelog`).
- `cargo clean --workspace` cleans artifacts belonging to workspace members (`cargo-changelog`).
- Since 1.97.0, `cargo clean --target-dir PATH` rejects directories that do not look like Cargo target directories.

## Packaging, publishing, and lockfiles

### Package archives

- Since 1.87.0, `cargo package --exclude-lockfile` explicitly excludes `Cargo.lock` from the package archive.
- With `build.build-dir` configured, `cargo publish` stopped retaining a `.crate` in 1.91.0. Since 1.93.0 it no longer leaves a user-accessible archive in the remaining case either. Run `cargo package` when the local archive is required.

### Dependency sources and registry metadata

- Since 1.96.0, a dependency may specify both `git` and an alternate `registry`; Cargo uses Git locally and the registry version when publishing.
- Since 1.94.0, registry indexes may include optional `pubtime`, recording publication time. Tooling must tolerate absence while old entries are gradually backfilled.
- Nightly `cargo generate-lockfile --publish-time <cutoff>` excludes packages published after the cutoff when the index provides `pubtime` (`cargo-changelog`).

### Alternate lockfiles

- Since 1.97.0, stable `resolver.lockfile-path` selects the dependency-resolution lockfile and supports read-only source trees.

## Cache, freshness, and build analysis

### Automatic cache cleanup

Since 1.88.0, Cargo removes network-downloaded cache entries unused for three months and local-system entries unused for one month. Cleanup does not run with `--offline` or `--frozen`. Cargo before 1.78 does not update the access records used by current Cargo, so shared mixed-version caches may need:

```toml
cache.auto-clean-frequency = "never"
```

### Experimental freshness and reports

- `cargo +nightly -Zchecksum-freshness build` compares file content rather than mtimes, useful for unreliable filesystems and CI (`cargo-changelog`).
- `-Zbuild-analysis` writes JSONL sessions under `~/.cargo/log/` with timings and rebuild reasons. Inspect them with `cargo report sessions`, `cargo report rebuilds`, and `cargo report timings` (`cargo-changelog`).
- The unstable `build-plan` interface and optional `--timings=<FMT>` forms were removed. Use `--unit-graph` or build-analysis reports instead (`cargo-changelog`).

## Credentials, networking, and platform requirements

- The positional token for `cargo login` is deprecated since 1.86.0 because it can leak through shell history; use Cargo's credential mechanisms.
- Since 1.90.0, `http.proxy-cainfo` specifies CA information for an HTTP proxy.
- Cargo shipped by the official Rust distribution now uses OpenSSL 3 and therefore depends on `libatomic` on 32-bit platforms (`cargo-changelog`).

## Tests and binaries

- Since 1.89.0, `cargo fix` and `cargo clippy --fix` use ordinary build-command target selection; `cargo fix --edition` still operates on all targets.
- Since 1.94.0, integration-test processes receive `CARGO_BIN_EXE_<crate>` at runtime, allowing `std::env::var` instead of compile-time environment access.
- Cross-compiled doctest execution and runners are detailed in [docs-tests-and-formatting.md](docs-tests-and-formatting.md).

## Installation, initialization, and terminal behavior

- `cargo init` rejects the user's home directory, preventing a parent manifest from affecting discovery throughout the home tree (`cargo-changelog`).
- A relative `install.root` without a trailing slash still resolves from the working directory but now warns ahead of changing to config-file-relative behavior; use an unambiguous absolute or explicitly rooted path (`cargo-changelog`).
- `[term.progress] term-integration = true` enables OSC 9;4 progress updates on supporting terminals (`cargo-changelog`).

## Nightly artifact metadata

- Nightly Cargo can emit SBOM precursor files next to every artifact with `[build] sbom = true` plus `cargo +nightly -Zsbom build` (`cargo-changelog`).
