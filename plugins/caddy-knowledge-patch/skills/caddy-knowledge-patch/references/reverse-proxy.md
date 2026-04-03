# Reverse Proxy

Reverse proxy changes since Caddy 2.8.0.

## Buffering Changes (2.8.0, Breaking)

`buffer_requests`, `buffer_responses`, and `max_buffer_size` were removed. Use the replacements:

- `request_buffers` — buffer request bodies
- `response_buffers` — buffer response bodies

## HTTP/3 to Backends (2.8.0, Experimental)

Proxy to HTTP/3 backends:

```
reverse_proxy https://backend:443 {
    transport http {
        versions h3
    }
}
```

## Via Header (2.10.0)

Reverse proxy now sets a `Via` header instead of a duplicate `Server` header on proxied responses.

## Auto-Rewrite Host for HTTPS Upstreams (2.11.1)

When proxying to an HTTPS upstream, the `Host` header is automatically rewritten to match the upstream address. Previously this required manual configuration.
