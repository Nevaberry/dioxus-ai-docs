# Packaging, publishing, and registries

Use this reference when deciding package contents, verifying archives,
publishing one or more workspace crates, or implementing registry consumers.

## Package input validation

### External readme and license files

Since 1.85.0, `cargo package` checks VCS status for `package.readme` and
`package.license-file` even when they point outside the package root. It also
avoids selecting potentially blocking non-files such as FIFOs for publication.

### External symlinks

Cargo 1.86.0 extended package VCS validation to symlinks that point outside
the package root.

### Dirty workspace manifests

Cargo 1.87.0 reports the VCS status of a dirty workspace manifest during
packaging.

### Nonfatal status-check failures

As of 1.88.0, failure of the Git dirtiness check is informational and no
longer fails the entire `cargo package` command. This differs from a successful
check that reports actual dirty inputs.

## Lockfiles and file listings

### Lockfile inclusion

`cargo package` always includes `Cargo.lock` in the archive as of 1.86.0.

Cargo 1.87.0 added `--exclude-lockfile`, which prevents packaging from
verifying a lockfile when one is present:

```console
cargo package --exclude-lockfile
```

### JSON package listings

The unstable `cargo package --message-format` option added in 1.87.0 can emit
an alternative JSON representation of the file listing requested by `--list`.

## Workspace packaging

### Dry runs before version bumps

Under `-Zpackage-workspace`, Cargo 1.85.0 allows a workspace packaging dry run
before workspace versions have been bumped.

### Dev-dependencies and publish exclusions

Cargo 1.89.0 expanded `-Zpackage-workspace`: it retains versioned
dev-dependencies, permits self-cycles, skips packages with `publish = false`,
and avoids unnecessary registry checks.

### Verification target directory

Since 1.91.0, `cargo package` verification reuses the workspace target
directory instead of creating a standalone target directory inside the
unpacked source.

## Publishing

### Multiple packages

Cargo 1.90.0 can publish a whole workspace or several selected packages,
including workspace crates that depend on one another:

```console
cargo publish --workspace
cargo publish -p foo -p bar
```

The operation is not atomic. A server failure can leave only part of the
requested package set published.

### Local archive retention

With `build.build-dir` configured, Cargo 1.91.0 stopped retaining the `.crate`
tarball as a final artifact after `cargo publish`. Cargo 1.93.0 applied that
behavior even without `build.build-dir`. Run `cargo package` when the local
archive is required.

### Publish credentials

`cargo publish --token` became soft-deprecated in 1.92.0. Prefer configured
credential providers for new workflows.

### Deterministic generated files

Cargo 1.93.0 assigns deterministic timestamps to files it generates while
assembling the package tarball.

## Registry data and local inspection

### Publication timestamps

Cargo 1.94.0 stabilized the registry-index `pubtime` field, recording when a
crate version was published for future time-based dependency resolution.
Consumers must tolerate the field being absent because existing packages may
not have been backfilled.

### Local `cargo info`

As of 1.94.0, `cargo info` defaults to the local package when no registry is
selected:

```console
cargo info
```

Choose a registry explicitly when local inspection is not intended.

### Registry API URLs

For Cargo 1.97.0, the `api` URL in a registry's `config.json` should not have a
trailing slash:

```json
{
  "api": "https://registry.example/api"
}
```

### Registry response throttling

Since 1.89.0, Cargo waits according to `Retry-After` before retrying an HTTP
429 response.

## Manifest format compatibility

Cargo 1.94.0 parses TOML 1.1 in manifests and configuration. Using TOML 1.1
features in `Cargo.toml` raises the project's development MSRV, even though
Cargo emits a publication manifest compatible with older TOML parsers.
