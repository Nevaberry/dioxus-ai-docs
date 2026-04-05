# Caddyfile Directives

New and changed directives since Caddy 2.8.0.

## `{file.*}` Placeholder (2.8.0)

Reads file contents into config (strips trailing newline). Ideal for secrets:

```
reverse_proxy {header_up Authorization "Bearer {file./run/secrets/token}"}
```

## `uri query` Structured Rewrites (2.8.0)

Manipulate query parameters directly instead of regex rewrites:

```
uri query +key value    # add parameter
uri query -key          # delete parameter
uri query key value     # set/replace parameter
```

## `handle_errors` Status Code Filtering (2.8.0)

Filter error handlers by status code or class:

```
handle_errors 404 {
    respond "Not found" 404
}
handle_errors 5xx {
    respond "Server error" 500
}
```

## `log_append` Handler (2.8.0)

Adds custom fields to structured access logs:

```
log_append X-Request-ID {header.X-Request-ID}
```

### Logging Request/Response Bodies (2.11.1)

Debug by logging bodies:

```
log_append request_body {http.request.body_base64}
log_append response_body {http.response.body}
```

## `{?query}` Placeholder (2.9.0)

Returns the full query string including the `?` prefix. Returns empty string if no query parameters. Useful in rewrites where `{http.request.uri.query}` doesn't include the `?`.

## `try_files` Fallback Strategy (2.9.0)

New `first_exist_fallback` policy falls back to the last file if none of the earlier ones exist (instead of returning 404):

```
try_files {
    policy first_exist_fallback
}
```

## `header` Directive Response Matching (2.9.1)

Match on response properties before applying header mutations:

```
header @response match {
    status 200
}
header @response Cache-Control "public, max-age=3600"
```

## `request_body set` (2.10.0)

Replace the request body entirely:

```
request_body {
    set "replacement body content"
}
```

## `{http.request.local}` Placeholders (2.8.0)

New placeholders for the local (server-side) address:

- `{http.request.local}` — full local address
- `{http.request.local.host}` — local host
- `{http.request.local.port}` — local port

## Directive Renames (2.8.0)

| Old Name | New Name | Notes |
|----------|----------|-------|
| `basicauth` | `basic_auth` | Old name works with deprecation warning |
| `skip_log` | `log_skip` | Old name works with deprecation warning |

The `scrypt` hash algorithm was removed from `basic_auth`. The `forwarded` option was removed from the `remote_ip` matcher — use the `client_ip` matcher instead.

## Buffering Changes (2.8.0)

`buffer_requests`, `buffer_responses`, and `max_buffer_size` were removed. Use the new directives:

- `request_buffers` — buffer request bodies
- `response_buffers` — buffer response bodies

## `SIGUSR1` Config Reload (2.11.1)

Reload config by sending SIGUSR1 signal (works if config was loaded from a file and not changed via API):

```bash
kill -USR1 $(pidof caddy)
```

## Argon2id Hash for `basic_auth` (2.11.1)

New hash algorithm option alongside bcrypt:

```
basic_auth {
    user $argon2id$...
}
```
