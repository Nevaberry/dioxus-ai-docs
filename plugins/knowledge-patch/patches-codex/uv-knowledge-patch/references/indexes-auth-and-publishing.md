# Indexes, Authentication, and Publishing

Use this reference for package-index configuration, credential selection,
certificate and network policy, archive validation, and publishing.

## Index Configuration and Lookup

### Authenticate private indexes fail-closed

Set `authenticate = "always"` when credentials must be present. With the
default `first-index` strategy, a 401 or 403 stops lookup rather than falling
through. Configure `ignore-error-codes` only for an index whose nonstandard
behavior requires fallthrough. (Batch `0.6-0.8`.)

```toml
[[tool.uv.index]]
name = "private"
url = "https://example.invalid/simple"
authenticate = "always"
```

### Name flat indexes

`--find-links`-style flat indexes can be declared in `[[tool.uv.index]]` and
participate in named-index configuration. (Batch `0.6-0.8`.)

### Validate default and explicit indexes

Configuration errors if more than one index has `default = true` or if an
`explicit = true` index has no name. Resolve these errors in configuration
rather than relying on declaration order. (Batch `0.9-0.10`.)

### Select configured indexes by name

With the preview `index-by-name` feature, `--index` and `--default-index` can
select a configured index by `name`, for example `uv lock --index internal`,
instead of repeating its URL. Preview index configuration also accepts an
index-specific `hash-algorithm` for lockfile generation. (Since `0.12.5`.)

```toml
[[tool.uv.index]]
name = "internal"
url = "https://packages.example.invalid/simple"
```

### Resolve local index paths from their source file

Relative package-index paths in PEP 723 scripts resolve against the script's
directory. `--find-links` paths in requirements files resolve against the
containing file. Local HTML files are accepted as flat indexes. (Since
`0.12.5`.)

## Credentials and Certificates

### Manage credentials by URL

`uv auth` commands manage credentials by URL, and stored token credentials
can be used by `uv publish`. (Batch `0.6-0.8`.)

When multiple stored credentials match one URL, provide the username
explicitly—for example, `uv auth token --username foo example.com`—instead of
relying on first-match order. (Batch `0.9-0.10`.)

### Treat explicit certificate overrides as authoritative

If `SSL_CERT_FILE` or `SSL_CERT_DIR` explicitly names a missing, inaccessible,
empty, or certificate-free source, uv does not fall back to default trust
roots. Fix or remove the invalid override. (Since `0.12.5`.)

### Configure process-wide network behavior

Uploads honor `UV_UPLOAD_HTTP_TIMEOUT` and `UV_HTTP_TIMEOUT`; uv supports
`SSL_CERT_DIR`, and proxy variables may be set in global or user
configuration. Managed CPython and installer downloads use Astral-hosted
mirrors by default, so restricted networks may need allow-list changes.
(Batch `0.9-0.10`.)

## Archive Validation

### Reject ambiguous ZIP archives

Archive handling rejects duplicate entries and other ZIP forms that Python
tools could interpret differently. `UV_INSECURE_NO_ZIP_VALIDATION=1` restores
earlier behavior only as an escape hatch for falsely rejected inputs; do not
use it as a default. (Batch `0.6-0.8`.)

### Validate source distributions and wheel contents

Source distributions must use `.tar.gz`, though legacy `.zip` source
distributions remain accepted; `.tar.bz2` and `.tar.xz` are rejected. ZIP
entries may use stored, DEFLATE, or zstd compression. Wheels are rejected if
entry points or data files could overwrite a Python interpreter, including
case variants on case-insensitive filesystems. (Since `0.12.5`.)

## Publishing

### Publish with managed credentials

Stored token credentials from `uv auth` can authenticate `uv publish`. Verify
the URL and username when multiple credentials could match. (Batch
`0.6-0.8`.)

### Attach attestations and sign cloud uploads

`uv publish` can collect and upload PEP 740 attestations and use Trusted
Publishing with pyx. Preview publishing paths support S3 pre-signed URLs and
GCS request signing. A durable release workflow should distinguish stable and
preview paths and validate the destination before uploading. (Batch
`0.9-0.10`.)
