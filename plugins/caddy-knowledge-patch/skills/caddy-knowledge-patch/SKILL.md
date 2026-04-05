---
name: caddy-knowledge-patch
description: Caddy changes since training cutoff (latest: 2.11.2) — ECH, wildcard certs by default, file placeholders, log sampling, request_body set, SIGUSR1 reload, post-quantum TLS. Load before working with Caddy.
license: MIT
metadata:
  author: Nevaberry
  version: "2.11.2"
---

# Caddy 2.8+ Knowledge Patch

Claude's baseline knowledge covers Caddy through 2.7.x. This skill provides features from 2.8.0 (May 2024) onwards.

**Source**: Caddy release notes at https://github.com/caddyserver/caddy/releases

## Quick Reference: Breaking Changes

| Old | New | Since |
|-----|-----|-------|
| `basicauth` | `basic_auth` | 2.8.0 |
| `skip_log` | `log_skip` | 2.8.0 |
| `buffer_requests`/`buffer_responses`/`max_buffer_size` | `request_buffers`/`response_buffers` | 2.8.0 |
| `forwarded` option in `remote_ip` matcher | Use `client_ip` matcher instead | 2.8.0 |
| `scrypt` hash in `basic_auth` | Removed (use bcrypt or argon2id) | 2.8.0 |
| ZeroSSL as default issuer (no email) | ZeroSSL only if `email` is set | 2.8.0 |
| `auto_https prefer_wildcard` | Removed — wildcards are default | 2.10.0 |
| `roll_gzip` | `roll_compression zstd` | 2.11.2 |

## Quick Reference: New Placeholders

| Placeholder | Description | Since |
|-------------|-------------|-------|
| `{file./path/to/file}` | File contents (strips trailing newline) | 2.8.0 |
| `{?query}` | Full query string with `?` prefix (empty if none) | 2.9.0 |
| `{http.request.local}` | Local address (also `.host`, `.port`) | 2.8.0 |
| `{http.request.body_base64}` | Request body (base64) for logging | 2.11.1 |
| `{http.response.body}` | Response body for logging | 2.11.1 |

## Caddy 2.8.0 (May 2024)

### `{file.*}` Placeholder

Read secrets from files — avoids embedding credentials in config:

```
reverse_proxy {header_up Authorization "Bearer {file./run/secrets/token}"}
```

### `uri query` Structured Rewrites

```
uri query +key value    # add
uri query -key          # delete
uri query key value     # set/replace
```

### `handle_errors` Status Code Filtering

```
handle_errors 404 {
    respond "Not found" 404
}
handle_errors 5xx {
    respond "Server error" 500
}
```

### `log_append` Handler

Adds custom fields to access logs:

```
log_append X-Request-ID {header.X-Request-ID}
```

### On-demand TLS `permission` Module

JSON `ask` deprecated in favor of pluggable `permission` module. Caddyfile `ask` still works:

```
{
    on_demand_tls {
        ask https://auth.example.com/check
        # OR
        permission <module>
    }
}
```

### HTTP/3 to Backends (Experimental)

```
reverse_proxy https://backend:443 {
    transport http {
        versions h3
    }
}
```

For full details, consult **`references/caddyfile-directives.md`** and **`references/tls-and-certificates.md`**.

## Caddy 2.9.0 (Dec 2024)

### `{?query}` Placeholder

Returns full query string including `?` prefix (empty string if no query).

### `try_files` Fallback Strategy

```
try_files {
    policy first_exist_fallback
}
```

Falls back to the last file if none of the earlier ones exist.

### Log Sampling

```
{
    log {
        sampling {
            interval 1000
            first 100
            thereafter 100
        }
    }
}
```

### `header` Directive Response Matching (v2.9.1)

```
header @response match {
    status 200
}
header @response Cache-Control "public, max-age=3600"
```

### `force_automate` (Experimental)

Override wildcard cert preference: `tls force_automate`

For full details, consult **`references/caddyfile-directives.md`** and **`references/logging.md`**.

## Caddy 2.10.0 (Apr 2025)

### Encrypted ClientHello (ECH) (Major)

Encrypts domain names in TLS ClientHello. Requires DNS provider module:

```
{
    dns cloudflare {env.CLOUDFLARE_API_KEY}
    ech ech.example.net
}
```

### Wildcards by Default (Major)

Caddy now uses wildcard certificates for subdomains. Override with `tls force_automate`. The `auto_https prefer_wildcard` option is removed.

### Global `dns` Option

Configure DNS provider once for all features:

```
{
    dns cloudflare {env.CLOUDFLARE_API_KEY}
}
```

### Post-Quantum Key Exchange

`X25519MLKEM768` is now a default cryptographic group. No configuration needed.

### `request_body set`

```
request_body {
    set "replacement body content"
}
```

### Other Changes

- ACME profiles support (experimental, e.g., 6-day Let's Encrypt certs)
- Reverse proxy sets `Via` header instead of duplicate `Server` header

For full details, consult **`references/tls-and-certificates.md`** and **`references/reverse-proxy.md`**.

## Caddy 2.11.x (Feb-Mar 2026)

### `SIGUSR1` Config Reload (2.11.1)

```bash
kill -USR1 $(pidof caddy)
```

Works if config was loaded from a file and not changed via API.

### Argon2id for `basic_auth` (2.11.1)

```
basic_auth {
    user $argon2id$...
}
```

### Time-Rolling Logs (2.11.1)

Switched from lumberjack to timberjack. New time-based rolling:

```
log {
    output file /var/log/caddy/access.log {
        roll_time 24h
    }
}
```

### `tls_resolvers` Global Option (2.11.2)

```
{
    tls_resolvers 1.1.1.1 8.8.8.8
}
```

### Security Fixes (2.11.2)

- `forward_auth` `copy_headers` now strips client-supplied identity headers (prevents privilege escalation)
- `vars_regexp` double-expansion fixed (could leak secrets)

For full details, consult **`references/logging.md`**, **`references/server-options.md`**, and **`references/tls-and-certificates.md`**.
