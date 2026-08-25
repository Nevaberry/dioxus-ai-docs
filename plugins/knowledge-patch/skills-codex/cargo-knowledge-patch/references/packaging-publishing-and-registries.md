# Packaging, Publishing, and Registries

## Package input validation

Cargo 1.85.0 makes `cargo package` inspect VCS status for `package.readme` and
`package.license-file` even when the paths point outside the package root. It
also avoids selecting potentially blocking non-files, such as FIFOs, for
publication.

Cargo 1.86.0 extends external-path checks to symlinks that point outside the
package root. Cargo 1.87.0 also reports a dirty workspace manifest during
packaging.

Since Cargo 1.88.0, failure of the Git dirtiness check is informational and no
longer aborts the entire package command. This does not remove the status
information; distinguish an unavailable status check from a known-clean tree.

## Lockfiles and package listings

Cargo 1.86.0 always includes `Cargo.lock` in a generated package. Cargo 1.87.0
adds:

```console
cargo package --exclude-lockfile
```

This flag stops package verification of an existing lockfile. The unstable
`cargo package --message-format` from 1.87.0 can emit a JSON representation of
the file listing requested with `--list`.

## Workspace packaging

Under `-Zpackage-workspace`, Cargo 1.85.0 permits dry runs before workspace
versions have been bumped. Cargo 1.89.0 further:

- retains versioned dev-dependencies,
- permits self-cycles,
- skips packages with `publish = false`, and
- avoids registry checks when they are unnecessary.

Cargo 1.91.0 reuses the workspace target directory while verifying a package
instead of creating a separate target directory inside the unpacked source.

## Reproducibility and local archives

Cargo 1.93.0 assigns deterministic timestamps to files generated while
building a `cargo package` tarball, improving package reproducibility.

Archive-retention behavior changed in two steps. Cargo 1.91.0 stopped retaining
the `.crate` archive after `cargo publish` when `build.build-dir` was
configured. Cargo 1.93.0 applies that behavior even without `build.build-dir`.
Run `cargo package` whenever the local archive is a required artifact.

## Multi-package publishing

Cargo 1.90.0 can publish an entire workspace or several selected packages,
including workspace crates that depend on each other:

```console
cargo publish --workspace
cargo publish -p foo -p bar
```

Publishing is not atomic. A registry failure can leave only some requested
packages published, so retry and release tooling must inspect registry state.

Cargo 1.92.0 soft-deprecates `cargo publish --token`; new workflows should use
the supported credential configuration instead.

## Registry protocol behavior

Since Cargo 1.89.0, a registry HTTP 429 response causes Cargo to honor the
server's `Retry-After` header before retrying.

Cargo 1.94.0 stabilizes the registry-index `pubtime` field, which records when
a crate version was published for future time-based resolution. Consumers
must tolerate an absent field because crates.io backfills historical versions
gradually when new versions are published.

In registry `config.json`, Cargo 1.97.0 expects the `api` URL without a
trailing slash:

```json
{
  "api": "https://registry.example/api"
}
```

## SSH, Git, and TLS transport

With `net.git-fetch-with-cli = true`, Cargo 1.85.0 sets `GIT_DIR`, allowing
CLI Git fetches to work in bare repositories.

Cargo 1.89.0 supports `*` and `?` patterns in SSH known-host matching. Cargo
1.95.0 correctly parses negated `net.known_hosts` patterns, so exclusion
entries participate in SSH host verification.

Under unstable `-Zgit`, Cargo 1.93.0 supports shallow fetches even when
`net.git-fetch-with-cli` selects the Git CLI backend.

Cargo 1.90.0 adds a separate CA path for proxy TLS:

```toml
[http]
proxy-cainfo = "proxy-ca.pem"
```

## Distribution and extraction compatibility

Cargo in the official Rust distribution uses OpenSSL 3 as of Cargo 1.87.0.
This creates a hard `libatomic` dependency on 32-bit platforms.

Cargo 1.94.0 fixes CVE-2026-33055 and CVE-2026-33056. On Unix-like systems, a
malicious crate extracted by an affected older Cargo could alter permissions
on arbitrary filesystem paths. Use Cargo 1.94.0 or newer before handling
untrusted crates.
