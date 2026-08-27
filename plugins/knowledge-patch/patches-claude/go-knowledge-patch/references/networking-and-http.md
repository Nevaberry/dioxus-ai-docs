# Networking and HTTP

## DNS and listeners

### Inspectable DNS errors and EDNS0 (1.23.0)

`net.DNSError` wraps timeout and cancellation causes. For example,
`errors.Is(err, context.DeadlineExceeded)` works through the DNS error.

The resolver adds EDNS0 headers by default. Set `GODEBUG=netedns0=0` when an
incompatible DNS server or modem breaks requests containing them.

### Multipath TCP by default (1.24.0)

`net.ListenConfig` enables Multipath TCP by default where the OS supports it,
currently on Linux. Set policy explicitly if applications or infrastructure
must avoid MPTCP.

## Protocol selection and transport behavior

### Explicit HTTP versions (1.24.0)

`Server.Protocols` and `Transport.Protocols` select HTTP/1, HTTP/2, and
unencrypted HTTP/2. A server can accept HTTP/1 and prior-knowledge h2c on one
cleartext port. For `http://`, a transport uses h2c only when unencrypted
HTTP/2 is enabled and HTTP/1 is disabled; `Upgrade: h2c` is unsupported.

### Informational responses (1.24.0)

`http.Transport` limits 1xx responses by combined bytes using
`MaxResponseHeaderBytes`, not a fixed response count. When `Got1xxResponse` is
installed there is no response-count limit, and the hook may return an error
to abort the request.

### Manual HTTP/2 connections (1.26.0)

`HTTP2Config.StrictMaxConcurrentRequests` controls whether another connection
opens after the current HTTP/2 connection reaches its stream limit.
`Transport.NewClientConn` exposes a connection for manual management; ordinary
clients should continue using `RoundTrip`.

### Priority and response-body draining (1.27.0)

HTTP/2 servers honor RFC 9218 client priority signals by default; configure the
previous round-robin scheduling only when compatibility requires it.

Closing an HTTP/1 response body drains a conservative amount of unread data so
the connection can be reused. A client that intentionally avoids reuse should
disable keep-alives instead of depending on an unread body.

## Servers, middleware, and browser protections

### Headers on file-serving errors (1.23.0)

`ServeContent`, `ServeFile`, and `ServeFileFS` remove `Cache-Control`,
`Content-Encoding`, `ETag`, and `Last-Modified` from error responses. This can
affect compression middleware that wraps responses.
`GODEBUG=httpservecontentkeepheaders=1` temporarily retains the old behavior.

### Cross-origin request protection (1.25.0)

`net/http.CrossOriginProtection` uses Fetch Metadata to reject unsafe
cross-origin browser requests without tokens or cookies. Configure explicit
origin and pattern bypasses only for intended exceptions.

### Safe reverse-proxy rewriting (1.26.0)

`httputil.ReverseProxy.Director` is deprecated: a client can name a header in a
hop-by-hop declaration and cause a header added by `Director` to be removed.
Use `Rewrite`, whose input exposes both the unmodified inbound request and the
outbound request.

## Hosts, cookies, redirects, and URLs

### Request host semantics (1.26.0)

`http.Client` scopes cookies to `Request.Host` when explicitly set, rather than
always using the connection address. `httptest.Server.Client` redirects
`example.com` and its subdomains to the test server.

`ServeMux` trailing-slash redirects use status 307 rather than 301. Account for
method and body preservation in clients and tests.

### Strict host colons (1.26.0)

`url.Parse` rejects malformed hosts such as `http://::1/` and
`http://localhost:80:80/`; bracketed IPv6 remains valid.
`GODEBUG=urlstrictcolons=0` temporarily restores permissive parsing.
