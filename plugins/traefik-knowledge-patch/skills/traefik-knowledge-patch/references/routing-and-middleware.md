# Routing & Middleware

New and changed routing and middleware features since Traefik v3.1.

## Multi-Layer Routing (v3.6)

Routers can now have parent-child relationships via `parentRefs`. Parent routers apply shared middleware (e.g., auth) and child routers make routing decisions based on enriched request context.

Three router types: **Root** (attached to entryPoints, no service), **Intermediate** (has children, inherits from root), **Leaf** (must define a service).

```yaml
http:
  routers:
    api-parent:
      rule: "Host(`api.example.com`)"
      middlewares:
        - auth-with-tier
      entryPoints:
        - websecure
      tls: {}
      # No service — this is a parent router

    api-enterprise:
      rule: "Header(`X-Customer-Tier`, `enterprise`)"
      service: stable-backend
      parentRefs:
        - api-parent

    api-free:
      rule: "Header(`X-Customer-Tier`, `free`)"
      service: canary-backend
      parentRefs:
        - api-parent
```

Child routers cannot be called directly — requests must flow through their parent.

---

## ForwardAuth Enhancements (v3.3–v3.6)

```yaml
http:
  middlewares:
    my-auth:
      forwardAuth:
        address: "http://auth:8080"
        forwardBody: true # Send request body (v3.3)
        maxBodySize: 1048576 # Limit forwarded body size
        preserveLocationHeader: true # Keep Location header from auth server (v3.3)
        preserveRequestMethod: true # Keep original method (GET/POST/etc.) (v3.4)
        maxResponseBodySize: 4096 # Limit auth response body (v3.6.9, default -1 = unlimited)
```

---

## Zstandard Compression & Encodings Option (v3.1/v3.2)

Compress middleware now supports Zstandard and allows specifying preferred encodings:

```yaml
http:
  middlewares:
    compress:
      compress:
        encodings:
          - gzip
          - br
          - zstd
```

Default order since v3.3.5: `gzip, br, zstd`.

---

## Error Page Status Rewrites (v3.4)

```yaml
http:
  middlewares:
    custom-errors:
      errors:
        status:
          - "500-599"
        service: error-service
        query: "/{status}.html"
        statusRewrites:
          "500": 200
          "503": 200
```

---

## Path Sanitization (v3.3.6+)

Incoming paths are auto-cleaned (`/../`, `/./`, `//`). Disable per-entrypoint if needed (not recommended):

```yaml
entryPoints:
  web:
    address: ":80"
    http:
      sanitizePath: false
```

---

## Encoded Characters Security (v3.6.4+)

Configure which encoded characters to allow/reject in request paths:

```yaml
entryPoints:
  web:
    address: ":80"
    http:
      encodedCharacters:
        allowEncodedSlash: true # %2F - default true since v3.6.7
        allowEncodedBackSlash: true # %5C
        allowEncodedNullCharacter: true # %00
```
