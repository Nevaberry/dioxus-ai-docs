# Workspaces, dependencies, and metadata

Use this reference when querying workspace graphs, controlling features,
editing dependency sources, interpreting metadata, or operating on multiple
packages.

## Workspace selection and commands

### Workspace-only trees

Cargo 1.85.0 added `workspace` as a tree depth:

```console
cargo tree --depth workspace
```

This limits output to members of the current workspace.

### Missing package selection

Since 1.86.0, passing `--package` with `--workspace` is an error when the named
package does not exist. Older behavior silently ignored the missing package:

```console
cargo build --workspace --package missing-package
```

### Workspace cleaning

`cargo clean --workspace`, added in 1.93.0, removes artifacts for workspace
members.

### Duplicate binary names

Cargo 1.87.0 made `cargo run` disambiguate binaries in different packages
that share the same name.

## Feature unification and public dependencies

### Workspace feature-unification control

Cargo 1.86.0 introduced unstable `-Zfeature-unification`, enabling the
`resolver.feature-unification` configuration. Cargo 1.90.0 expanded the
implementation to support per-package feature unification.

### Public dependency trees

Under `-Zpublic-dependency`, Cargo 1.87.0 initially exposed public dependency
trees as:

```console
cargo -Zpublic-dependency tree --depth public
```

Cargo 1.92.0 replaced that form with:

```console
cargo -Zpublic-dependency tree --edges public
```

The same 1.92.0 feature also makes `cargo add` consider whether a dependency is
public when selecting a version.

### Long tree-format variables

Since 1.93.0, `cargo tree --format` accepts long variable names such as
`{package}` and `{features}` in addition to short forms:

```console
cargo tree --format '{package} {features}'
```

## Dependency source behavior

### Git plus alternate registry

Cargo 1.96.0 permits a multiple-location dependency to combine a Git source
with a named alternate registry:

```toml
[dependencies]
helper = { git = "https://example.com/helper.git", registry = "my-registry" }
```

### Exact registry-source vendoring

Since 1.89.0, `cargo vendor` includes `.rej` and `.orig` files and directly
extracts registry sources, making vendored contents match their originals.

### Registry throttling

Cargo 1.89.0 honors `Retry-After` after a registry returns HTTP 429.

## Cargo metadata

### Target-independent base output

As of 1.87.0, `cargo metadata` no longer reads `CARGO_BUILD_TARGET`. Consumers
that need a platform-specific view should pass an explicit filter.

### Host filtering

Cargo 1.93.0 allows `host-tuple` in `cargo metadata --filter-platform`, where
it resolves to the host target triple:

```console
cargo metadata --filter-platform host-tuple
```

### Intermediate build directory

For unstable `build-dir`, Cargo 1.88.0 added `build_directory` to metadata
output so consumers can locate intermediate artifacts. The
`build.build-dir` setting itself became stable in 1.91.0.

### Unit graph identities

The unstable unit-graph representation uses Package ID Specifications as of
1.88.0. Parse identities according to that grammar.

### Artifact dependency boundaries

Under `-Zbindeps`, Cargo 1.93.0 stopped propagating artifact dependencies to
procedural-macro or build dependencies.

## Workspace manifests and path bases

### Path bases in patches

Cargo 1.85.0 extended the `path-bases` feature to bases used inside `[patch]`
tables in virtual manifests.

### Edition migration in virtual manifests

`cargo fix --edition` in 1.85.0 gained support for migrating workspace
dependencies declared by a virtual manifest.

### Workspace manifest packaging status

Since 1.87.0, `cargo package` reports the VCS status of a dirty workspace
manifest, not only package-local inputs.
