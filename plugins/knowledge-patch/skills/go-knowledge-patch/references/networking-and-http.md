# Networking and HTTP

Batch coverage: `1.23.0`, `1.24.0`, `1.25.0`, `1.26.0`.

## Contents

- [DNS](#dns)
- [HTTP protocol selection](#http-protocol-selection)
- [Responses, hosts, and redirects](#responses-hosts-and-redirects)
- [Reverse proxies and cross-origin protection](#reverse-proxies-and-cross-origin-protection)
- [URL host parsing](#url-host-parsing)
- [Multipath TCP](#multipath-tcp)

## DNS

### Inspectable failures

`net.DNSError` wraps timeout and cancellation causes. Use checks such as `errors.Is(err, context.DeadlineExceeded)` through the DNS error.

### EDNS0 compatibility

The resolver normally adds EDNS0 headers to DNS requests. Set `GODEBUG=netedns0=0` when an incompatible DNS server or modem fails on them.

## HTTP protocol selection

### Explicit protocol sets

`http.Server.Protocols` and `http.Transport.Protocols` select HTTP/1, HTTP/2, and unencrypted HTTP/2.

A server can accept HTTP/1 and prior-knowledge h2c on the same cleartext port. A transport uses h2c for an `http://` URL only when unencrypted HTTP/2 is enabled and HTTP/1 is disabled. The `Upgrade: h2c` mechanism is not supported.

### Manual HTTP/2 connections

`HTTP2Config.StrictMaxConcurrentRequests` controls whether a transport opens another connection after an existing HTTP/2 connection reaches its stream limit.

`Transport.NewClientConn` exposes a client connection to callers that manage connections themselves. Ordinary clients should continue using `RoundTrip`.

## Responses, hosts, and redirects

### `ServeContent` error headers

`ServeContent`, `ServeFile`, and `ServeFileFS` remove `Cache-Control`, `Content-Encoding`, `ETag`, and `Last-Modified` from error responses. This can break response-wrapping compression middleware. Set `GODEBUG=httpservecontentkeepheaders=1` to restore the earlier behavior temporarily.

### Informational responses

`http.Transport` limits 1xx responses by their combined size through `MaxResponseHeaderBytes`, rather than stopping after five responses. When `Got1xxResponse` is installed there is no response-count limit, and the hook may return an error to abort the request.

### Host and redirect semantics

`http.Client` scopes cookies to `Request.Host` when that field is set, instead of always using the connection address.

`ServeMux` trailing-slash redirects use status 307 instead of 301. A client returned by `httptest.Server.Client` also redirects `example.com` and its subdomains to the test server.

## Reverse proxies and cross-origin protection

### Safe reverse-proxy rewriting

`httputil.ReverseProxy.Director` is deprecated. A client can use hop-by-hop header declarations to remove headers added by `Director`. Use `Rewrite`, which receives both the unmodified inbound request and the outbound request.

### Fetch Metadata CSRF defense

`net/http.CrossOriginProtection` rejects unsafe cross-origin browser requests using Fetch Metadata, without requiring tokens or cookies. Configure explicit origin- and pattern-based bypasses where needed.

## URL host parsing

`url.Parse` rejects malformed host components such as `http://::1/` and `http://localhost:80:80/`. Bracketed IPv6 literals remain valid. Set `GODEBUG=urlstrictcolons=0` to restore permissive parsing temporarily.

## Multipath TCP

`net.ListenConfig` uses Multipath TCP by default on supported systems, currently Linux.
