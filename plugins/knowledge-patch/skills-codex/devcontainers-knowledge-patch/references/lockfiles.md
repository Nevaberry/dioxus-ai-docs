# Feature Lockfiles

The lockfile schema guidance comes from `lockfile-stable`.

## Current path and purpose

Use `.devcontainer-lock.json`, including the leading dot, beside
`devcontainer.json`. Earlier guidance and older tooling may refer to
`devcontainer-lock.json` without the leading dot; treat that as the superseded
name rather than the current CLI filename.

The file pins OCI and tarball Features for reproducible, cache-stable builds.
Checksums also detect a release artifact whose contents changed.

Do not record:

- Local Features
- Deprecated GitHub Releases Features
- Features supplied through `--additional-features` on CLI 0.86.1 and later

## Record schema

The top-level `features` object uses lowercased Feature references as keys.
Each record contains:

- `version`: the complete resolved Feature version
- `resolved`: a digest-qualified OCI Feature ID or a tarball HTTPS URL
- `integrity`: an artifact checksum in `sha256:<hex>` form
- `dependsOn`: optional lowercased dependency identifiers

```json
{
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "1.0.4",
      "resolved": "ghcr.io/devcontainers/features/node@sha256:567d704b3f4d3eca3acee51ded7c460a8395436d135d53d1175fb565daff42b8",
      "integrity": "sha256:567d704b3f4d3eca3acee51ded7c460a8395436d135d53d1175fb565daff42b8"
    }
  }
}
```

When present, `dependsOn` is an array. Preserve any version or checksum suffix
on each lowercased Feature identifier. Every named dependency must have its own
record in the lockfile. Omit `dependsOn` when the array would be empty.

## Generation policy

On CLI 0.87.0 and later, `devcontainer build` and `devcontainer up` generate
the lockfile by default.

```sh
devcontainer build --frozen-lockfile
devcontainer up --no-lockfile
```

- Use `--no-lockfile` to suppress lockfile generation.
- Use `--frozen-lockfile` to require the file to exist and to reject any
  proposed change.
- Replace deprecated `--experimental-lockfile` and
  `--experimental-frozen-lockfile` uses. They still parse but emit warnings.

## Maintenance

```sh
devcontainer outdated
devcontainer upgrade
```

Run `outdated` to report locked Features with newer releases. Run `upgrade` to
update them. Review the resulting version, resolved artifact, integrity value,
and dependency records together.
