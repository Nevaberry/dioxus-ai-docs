# HTTP & Transport

## 103 Early Hints (1.29.0)

New `early_hints` directive controls passing 103 responses from backends to clients:

```nginx
map $http_sec_fetch_mode $early_hints {
    navigate $http2$http3;
}

server {
    location / {
        early_hints $early_hints;
        proxy_pass http://backend;
    }
}
```

The 103 response is passed only when all string parameters are non-empty and non-zero. This allows conditional Early Hints — e.g., only for navigation requests over HTTP/2 or HTTP/3.

---

## Header/Trailer Inheritance (1.29.3)

`add_header_inherit` and `add_trailer_inherit` control inheritance of `add_header`/`add_trailer` directives from parent contexts.

Previously, defining any `add_header` in a child block silently dropped all parent headers. This was a long-standing footgun. These new directives let you explicitly control inheritance behavior.

---

## keepalive_min_timeout (1.27.4)

Sets a minimum time a keep-alive connection stays open, preventing premature closure during graceful shutdown or connection reuse:

```nginx
keepalive_min_timeout 10s;  # default: 0
```

---

## MPTCP Support (1.29.7)

The `multipath` parameter on the `listen` directive enables Multipath TCP (RFC 8684):

```nginx
server {
    listen 80 multipath;
    listen 443 ssl multipath;
}
```

Note: implicitly enables `SO_REUSEPORT`.

---

## proxy_pass_trailers (1.27.2)

Enables passing HTTP trailer fields from backends to clients.

```nginx
location / {
    proxy_pass http://backend;
    proxy_pass_trailers on;
}
```

---

## New Variables (1.29.3)

| Variable | Description |
|---|---|
| `$request_port` | Port from the request line |
| `$is_request_port` | Whether the port is explicitly specified in the request |
