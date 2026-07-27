# Indexes, Authentication, and Publishing

Use this reference for package-index configuration, credential selection,
publishing transports, attestations, and archive validation.

## Index Definition and Lookup

### Fail closed when authentication is required

The 0.6-0.8 batch added `authenticate = "always"` for indexes whose credentials
must be present:

```toml
[[tool.uv.index]]
name = "private"
url = "https://example.invalid/simple"
authenticate = "always"
```

With the default `first-index` strategy, HTTP 401 or 403 stops package lookup
instead of falling through to a later index. For a nonstandard index that uses
those responses for ordinary misses, configure `ignore-error-codes`
deliberately.

### Name flat indexes

`--find-links`-style flat indexes can be represented in `[[tool.uv.index]]`.
They can therefore participate in named-index configuration rather than
remaining anonymous CLI-only inputs.

### Keep index configuration unambiguous

In the 0.9-0.10 batch, configuration became stricter:

- More than one index with `default = true` is an error.
- An index with `explicit = true` must have a name.

## Credential Management

Use `uv auth` commands to manage credentials by URL. Stored token credentials
can be consumed by `uv publish`.

When several stored credentials match the same URL, specify the username
instead of relying on the first match:

```console
uv auth token --username foo example.com
```

## Publishing

`uv publish` can collect and upload PEP 740 attestations and can use Trusted
Publishing with pyx.

Preview publishing transports include:

- S3 pre-signed URLs.
- Google Cloud Storage request signing.

Treat preview transport configuration as subject to change, and validate the
exact upload target and authentication path before publishing.

## Archive Validation

uv rejects malformed ZIP archives with duplicate entries or other structures
that Python tooling could interpret inconsistently. This closes ambiguity in
archive extraction and package installation.

`UV_INSECURE_NO_ZIP_VALIDATION=1` restores the earlier behavior only as an
escape hatch for falsely rejected archives. Scope it narrowly and remove it
after resolving the offending artifact.
