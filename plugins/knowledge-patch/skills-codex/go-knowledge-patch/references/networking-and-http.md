# Networking and HTTP

## DNS and transport selection

### Inspectable DNS failures (`1.23.0`)

`net.DNSError` wraps timeout and cancellation causes, so
`errors.Is(err, context.DeadlineExceeded)` and similar checks work through the
DNS error.

### Disabling EDNS0 headers (`1.23.0`)

Set `GODEBUG=netedns0=0` to stop the resolver adding EDNS0 headers when an
incompatible DNS server or modem breaks requests.

### MPTCP listening by default (`1.24.0`)

`net.ListenConfig` uses Multipath TCP by default on supporting systems,
currently Linux.

## HTTP protocol configuration and scheduling

### Explicit HTTP protocol selection (`1.24.0`)

`Server.Protocols` and `Transport.Protocols` select HTTP/1, HTTP/2, and
unencrypted HTTP/2. A server may accept HTTP/1 and prior-knowledge h2c on one
cleartext port. A transport uses h2c for `http://` only when unencrypted HTTP/2
is enabled and HTTP/1 is disabled; `Upgrade: h2c` is unsupported.

### Informational-response limits (`1.24.0`)

`http.Transport` limits 1xx responses by combined size using
`MaxResponseHeaderBytes` instead of aborting after five. With
`Got1xxResponse`, there is no response-count limit; the hook may return an error
to abort the request.

### Manual HTTP/2 connection control (`1.26.0`)

`HTTP2Config.StrictMaxConcurrentRequests` controls whether another connection
opens after an HTTP/2 connection reaches its stream limit.
`Transport.NewClientConn` exposes a connection for callers managing connections
themselves; ordinary clients should keep using `RoundTrip`.

### HTTP/2 priority signals (`1.27.0`)

HTTP/2 servers honor RFC 9218 client priority signals by default. An option
retains the earlier round-robin scheduling.

### HTTP/1 response-body draining (`1.27.0`)

Closing an HTTP/1 response body drains a conservative amount of unread data to
permit connection reuse. A client intentionally avoiding reuse should disable
keep-alives rather than depend on an unread body.

## Servers, browser requests, and redirects

### Headers on `ServeContent` errors (`1.23.0`)

`ServeContent`, `ServeFile`, and `ServeFileFS` remove `Cache-Control`,
`Content-Encoding`, `ETag`, and `Last-Modified` on error responses. This can
affect compression middleware. `GODEBUG=httpservecontentkeepheaders=1` restores
the prior behavior temporarily.

### Standard-library CSRF protection (`1.25.0`)

`net/http.CrossOriginProtection` rejects unsafe cross-origin browser requests
using Fetch Metadata without tokens or cookies. It supports explicit origin-
and pattern-based bypasses.

### HTTP host and redirect semantics (`1.26.0`)

`http.Client` scopes cookies to `Request.Host` when explicitly set instead of
always using the connection address. `ServeMux` trailing-slash redirects use
307 instead of 301. A client from `httptest.Server.Client` redirects
`example.com` and its subdomains to the test server.

## Proxies and URL validation

### Safe reverse-proxy rewriting (`1.26.0`)

`httputil.ReverseProxy.Director` is deprecated because a client can use
hop-by-hop declarations to remove headers it adds. Use `Rewrite`, whose hook
receives both the unmodified inbound request and outbound request.

### Strict URL host colons (`1.26.0`)

`url.Parse` rejects malformed host components such as `http://::1/` and
`http://localhost:80:80/`; bracketed IPv6 remains valid.
`GODEBUG=urlstrictcolons=0` temporarily restores permissive parsing.
