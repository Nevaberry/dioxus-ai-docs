# Commands, Workspaces, and Dependencies

## Edition and fix workflows

Cargo 1.85.0 supports packages with `edition = "2024"`. `cargo fix --edition`
also migrates workspace dependencies declared in virtual manifests.

Since Cargo 1.89.0, `cargo fix` and `cargo clippy --fix` operate only on
default Cargo targets unless `--all-targets` is passed. `--edition` and
`--edition-idioms` continue to imply all targets:

```console
cargo fix --all-targets
cargo clippy --fix --all-targets
```

Since Cargo 1.86.0, `cargo fix --allow-dirty` implies `--allow-staged`.

## Workspace selection and cleanup

Cargo 1.85.0 adds `cargo tree --depth workspace`, restricting the displayed
tree to current workspace members:

```console
cargo tree --depth workspace
```

Cargo 1.86.0 makes `--workspace --package missing-package` an error instead of
silently ignoring the nonexistent package. Cargo 1.93.0 adds
`cargo clean --workspace`, which removes artifacts belonging to workspace
members:

```console
cargo clean --workspace
```

Cargo 1.97.0 makes `cargo clean --target-dir` reject paths that do not look
like Cargo target directories, reducing accidental deletion risk.

## Tree and public-dependency output

Cargo 1.93.0 lets `cargo tree --format` use long variables such as `{package}`
and `{features}` in addition to short forms:

```console
cargo tree --format '{package} {features}'
```

The unstable public-dependency tree interface changed. Cargo 1.87.0 initially
used `-Zpublic-dependency tree --depth public`; Cargo 1.92.0 replaces that
spelling with:

```console
cargo -Zpublic-dependency tree --edges public
```

Under the same feature, Cargo 1.92.0 makes `cargo add` consider public
dependencies when selecting a version.

## `cargo rustc`, run, and documentation commands

Since Cargo 1.85.0, flags after `cargo rustc --` take higher precedence when
options conflict:

```console
cargo rustc -- -C opt-level=3
```

Cargo 1.86.0 sets up the Cargo environment before `cargo rustc --print`
invokes rustc.

Cargo 1.87.0 disambiguates `cargo run` binaries from different packages that
share a name. Cargo 1.89.0 stabilizes cross-compiled doctests: when target and
host differ, Cargo runs doctests like other cross-compiled tests.

When a rustc version mismatch requires cleanup, Cargo 1.93.0 makes
`cargo doc` delete generated documentation only for requested targets, leaving
other target platforms intact.

Cargo 1.96.0 lets `cargo help` find manpages for nested subcommands:

```console
cargo help report future-incompat
```

## Metadata and package identities

As of Cargo 1.87.0, `cargo metadata` ignores `CARGO_BUILD_TARGET`; metadata
queries are target-independent unless a target is requested through supported
arguments.

Cargo 1.93.0 accepts `host-tuple` for metadata platform filtering:

```console
cargo metadata --filter-platform host-tuple
```

The unstable unit-graph representation in Cargo 1.88.0 uses Package ID
Specifications. Consumers must parse identities in that format instead of
assuming the older representation.

## Dependency sources and vendoring

Cargo 1.89.0 changes `cargo vendor` to include `.rej` and `.orig` files and
directly extract registry sources. The resulting vendored files match the
source archive exactly.

Cargo 1.96.0 permits a multiple-location dependency to combine a Git source
with a named alternate registry:

```toml
[dependencies]
helper = { git = "https://example.com/helper.git", registry = "my-registry" }
```

## Command environment and convenience

Cargo 1.87.0 forwards Bash completion requests to third-party Cargo
subcommands.

Cargo 1.94.0 changes unqualified `cargo info` to inspect the local package when
no registry is selected:

```console
cargo info
```

Cargo 1.95.0 refuses `cargo init` when the requested directory is the user's
home directory, preventing a home-level manifest from interfering with
manifest discovery below it.

Cargo 1.97.0 adds `-m` as an alias for `--manifest-path`:

```console
cargo build -m path/to/Cargo.toml
```

Cargo 1.87.0 applies `--frozen` consistently anywhere `--offline` or
`--locked` is accepted.
