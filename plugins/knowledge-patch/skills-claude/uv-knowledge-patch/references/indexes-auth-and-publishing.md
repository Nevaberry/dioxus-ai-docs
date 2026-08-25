# Indexes, Authentication, and Publishing

## Fail-closed index authentication (0.6-0.8)

Use `authenticate = "always"` when credentials are mandatory. Missing
credentials then fail closed.

With the default `first-index` strategy, 401 or 403 stops package lookup rather
than falling through to another index. Configure `ignore-error-codes` only for
an index whose nonstandard response needs fallthrough.

```toml
[[tool.uv.index]]
name = "private"
url = "https://example.invalid/simple"
authenticate = "always"
```

## Named and configured indexes

Flat `--find-links`-style indexes can be declared in `[[tool.uv.index]]` and
participate in named-index configuration (0.6-0.8).

Configuration errors when multiple indexes have `default = true`, or when an
`explicit = true` index has no name (0.9-0.10).

With preview `index-by-name`, `--index` and `--default-index` can select a
configured index by name instead of repeating its URL (0.12.5). Preview index
configuration also supports per-index `hash-algorithm` for lockfile generation.

```toml
[[tool.uv.index]]
name = "internal"
url = "https://packages.example.invalid/simple"
```

## Credential management and matching

`uv auth` manages credentials by URL, and stored token credentials can be used
by `uv publish` (0.6-0.8).

If multiple stored credentials match a URL, specify the username rather than
depending on match order (0.9-0.10):

```console
uv auth token --username foo example.com
```

## Publishing attestations and cloud signing (0.9-0.10)

`uv publish` can collect and upload PEP 740 attestations and use Trusted
Publishing with pyx. Preview publishing paths support S3 pre-signed URLs and
GCS request signing.

## Archive validation

Archive handling rejects duplicate ZIP entries and other ambiguous forms that
Python tooling could interpret differently (0.6-0.8). Use
`UV_INSECURE_NO_ZIP_VALIDATION=1` only as an escape hatch for a falsely rejected
archive.

At 0.12.5, source distributions must use `.tar.gz`, although legacy `.zip`
source distributions remain accepted; `.tar.bz2` and `.tar.xz` are rejected.
ZIP entries may be stored, DEFLATE-compressed, or zstd-compressed. Wheels are
rejected when entry points or data files could overwrite a Python interpreter,
including case variants on case-insensitive filesystems.

## Explicit certificate overrides (0.12.5)

`SSL_CERT_FILE` and `SSL_CERT_DIR` are authoritative when explicitly set. A
missing, inaccessible, empty, or certificate-free source does not fall back to
default trust roots. Fix the source or remove the override.

## Local index path resolution (0.12.5)

Relative index paths in PEP 723 scripts resolve against the script directory.
`--find-links` paths in requirements files resolve against the containing
file. Local HTML files are accepted as flat indexes.
