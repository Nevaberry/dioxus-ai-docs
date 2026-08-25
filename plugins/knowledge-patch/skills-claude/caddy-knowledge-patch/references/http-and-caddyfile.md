# HTTP and Caddyfile

## Reusable and optional imports

### Passing a block

Since 2.9.0, `import` can pass a directive block to a snippet. `{block}` expands at the point where the snippet chooses to insert the caller's directives, enabling higher-order wrappers.

```caddyfile
(wrapped) {
	{block}
}

:80 {
	import wrapped {
		respond "ok"
	}
}
```

Caddy 2.10.2 fixes the 2.10.1 regression that mishandled nested tokens imported through `{block}`. Since 2.11.1, `{block}` is a no-op when the caller supplies no block, and later fixes keep an explicitly empty block from panicking the parser. A snippet can therefore accept an optional body.

## Matching requests and responses

### Response matching in `header`

Since 2.9.0, `header` has a `match` subdirective. Changes in the block are applied only to matching responses.

```caddyfile
header {
	match {
		status 2xx
	}
	Cache-Control "public, max-age=60"
}
```

### Request and CEL matchers

- Request header matching recognizes `Transfer-Encoding`, and access logs record that header (since 2.9.0).
- Caddyfile CEL expressions can use `vars` and `vars_regexp` matchers and can escape placeholders (since 2.9.0).
- Selected HTTP and TLS matchers can resolve runtime placeholders (since 2.9.0); verify that a specific matcher documents placeholder support rather than assuming all do.

```caddyfile
@chunked header Transfer-Encoding chunked
respond @chunked "chunked request"
```

### Safe matching and literal expansion

- Host matching remains case-insensitive even when the configured list contains more than 100 entries (2.11.1).
- Path matching normalizes escape sequences, and file-match globs sanitize metacharacters (2.11.1).
- `vars_regexp` no longer performs a second placeholder expansion (2.11.2).
- `vars` values no longer expand placeholders, closing a data-to-template boundary (2.11.3).
- Windows backslashes are normalized during path matching, injected queries cannot trigger placeholder re-expansion, `stripHTML` is hardened, and HTTP header fields containing underscores are ignored (2.11.4).

These changes may reject or reinterpret configurations that depended on unsafe matching behavior. Keep request-derived values literal and use explicit matchers for transformations.

## Placeholders and replacement

### Query preservation

`{?query}` expands to the complete request query with its leading `?`, but only when a query exists (since 2.9.0). It avoids a dangling separator in redirects and rewrites.

```caddyfile
redir /new-location{?query}
```

### New and changed values

- Access logs have a `spanID` field, with `{http.vars.span_id}` exposing the same span identifier (since 2.9.0).
- `{http.reverse_proxy.retries}` exposes the proxy retry count (since 2.9.0).
- Active-health-check headers can interpolate the target host and target network address (since 2.9.0).
- Messages emitted by `error` run through the replacer (since 2.9.0).
- Global `{file.*}` placeholders strip trailing newlines from loaded file content (since 2.9.0).
- Search patterns used by header replacement can contain runtime placeholders (since 2.10.0).
- A reverse-proxy HTTP transport correctly establishes TLS when its configured server name contains a placeholder (since 2.10.0).
- `{http.request.body_base64}` exposes a base64-encoded request body, and `{http.response.body}` exposes a captured response body to `log_append` (2.11 line).

## Request and response bodies

### Replacing the request body

Since 2.10.0, `request_body` supports `set`. Caddy replaces the body and recalculates `Content-Length`.

```caddyfile
request_body {
	set "replacement body"
}
```

Fully buffered reverse-proxy bodies also receive a `Content-Length` header (since 2.9.0). Proxy retry and FastCGI buffering behavior is covered in [Reverse proxy](reverse-proxy.md).

### Logging bodies

The 2.11 line makes the captured response body available to `log_append` and adds an early-execution option for fields that must exist before the handler chain completes.

```caddyfile
log_append request_body {http.request.body_base64}
log_append response_body {http.response.body}
```

Body logging can disclose credentials or personal data; use it only with deliberate capture, retention, and access controls.

## Headers, authentication, and identity

- The generated `Server` response header is customizable in the 2.11 line.
- `basic_auth` can verify Argon2id password hashes in the 2.11 line.
- Since 2.11.2, `forward_auth copy_headers` removes client-supplied copies of identity headers before writing authenticated values. This prevents a client from injecting an identity value that survives authentication.

Do not prepopulate identity headers on the client side and expect them to remain available after `forward_auth`.

## Content encoding

### Defaults and negotiation

Bare `encode` selects useful default encoders without an explicit format list (since 2.9.0).

```caddyfile
encode
```

The 2.11 line adds recognition of the GraphQL response content type, supports configurable zstd checksums, and prefers zstd and Brotli over gzip during content negotiation.

### Precompressed files

Bare `precompressed` also selects useful formats (since 2.9.0). In the 2.11 line, precompressed responses include `Content-Length`.

```caddyfile
file_server {
	precompressed
}
```

## Choosing and serving files

### `try_files` fallback policy

The `first_exist_fallback` policy checks candidates in order for an existing file but treats the final candidate as a fallback even when it does not exist (since 2.9.0).

```caddyfile
try_files {path} /index.html {
	policy first_exist_fallback
}
```

This is useful when the last value is a rewritten application route rather than a file that must already exist.

### Browse controls

- Browse sorting is configured under the `browse` block (since 2.9.0).
- The experimental `file_limit` bounds a browse listing (since 2.9.0).
- Grid-mode browse output gains sorting controls (since 2.10.0).
- File modification times are represented in UTC (since 2.10.0).
- Browse output shows symlink targets verbatim in the 2.11 line.

```caddyfile
file_server {
	browse {
		file_limit 1000
	}
}
```

### File types and filesystem behavior

The file server recognizes `.avif` images since 2.10.0. In the 2.11 line, `hide` follows the underlying filesystem's case sensitivity. If `hide` is part of an access boundary, test on the target filesystem: a rule developed on a case-insensitive filesystem may behave differently on a case-sensitive one.

Named plugin-backed filesystem modules are covered in [Server operations](server-operations.md).

## HTTP early-data safeguards

Since 2.9.0, IP matchers reject QUIC 0-RTT early data because address-based decisions are unsafe for replayable requests. Proxied early-data requests receive an `Early-Data` header so the upstream can enforce its own policy. The 2.11 server configuration can disable QUIC 0-RTT altogether.

## Administration-request hardening

Since 2.11.1, admin requests attempted with browser `no-cors` mode are blocked. Version 2.11.3 also canonicalizes remote-admin array indices and path boundaries. Use the supported admin API shape and configure origin checks rather than relying on browser opaque requests or ambiguous paths.
