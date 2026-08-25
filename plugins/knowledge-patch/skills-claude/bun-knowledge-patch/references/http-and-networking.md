# HTTP and networking

## `Bun.serve()` routing and lifecycle

### Route migration and handlers (`1.2-guide`, `1.2.3`)

The initial HTML/static map was named `static`; use `routes`. Routes accept
static `Response` or HTML values, parameters on `req.params`, wildcards, async
functions, and method-specific handler objects. A fallback `fetch` is optional.

```ts
Bun.serve({
  routes: {
    "/api/users": {
      GET: () => Response.json([]),
      POST: async req => Response.json(await req.json()),
    },
    "/api/users/:id": req => Response.json(req.params),
  },
});
```

### Cookies (`1.2.7`)

`request.cookies` is a lazily parsed `Bun.CookieMap`. Mutations cause Bun to add
the corresponding `Set-Cookie` headers; deleting creates an expiring cookie.
Standalone `Bun.Cookie` serializes one cookie, and `CookieMap` can parse,
mutate, and produce `toSetCookieHeaders()`. Standalone serialization defaults
to `Path=/` and `SameSite=Lax`.

### Method and file route values (`1.2.14`, `1.2.16`)

Static values may sit under a method (`{ GET: homepage }`), and `/*` no longer
outranks a method-specific route. A `Bun.file()` may be a direct route value.

### Validators and ranges (`1.2.20`, `1.3.13`, `1.4-2`)

- Static non-function values receive an automatic `ETag`; matching
  `If-None-Match` gets `304`.
- File-backed static and dynamic responses handle single byte ranges, including
  suffix and open-ended forms. Valid ranges return `206`, invalid ranges `416`,
  and multi-range falls back to the full body. SSL and Windows file responses
  stream incrementally.
- Static and file routes enforce `If-Match` and `If-Unmodified-Since` with
  `412`.

### Directory routes (`1.4`)

`{ dir: "./public" }` serves a directory with content type, `ETag`,
`Last-Modified`, `304`, ranges and `index.html`. Paths are normalized; Linux
uses `openat2` with beneath-only resolution to stop symlink escape.

```ts
Bun.serve({ routes: { "/static/*": { dir: "./public" } } });
```

### Shutdown and validation (`1.2-guide`, `1.4-2`)

`server.stop()` returns `Promise<void>`. It closes idle keep-alive connections,
finishes busy responses, and resolves when the last connection closes. A
half-sent request keeps it pending; `server.stop(true)` forces closure and can
be called after graceful shutdown started.

Ports must be integer and in range or `Bun.serve` throws `RangeError`.
Malformed `Content-Length`/`Transfer-Encoding` gets `400` without invoking
`fetch`. Returning a response with status outside 100–999 invokes `error()` and
produces `500`. Per-method `GET` also answers `HEAD`.

### Streaming backpressure (`1.4`)

`Bun.serve` applies socket backpressure to request/response `ReadableStream`s;
`pull()` pauses when the send buffer fills instead of accumulating unsent
chunks. The same behavior applies to Fetch, TransformStreams, HTMLRewriter,
subprocesses, and file/blob streams.

### Request framing (`1.3.12`)

The HTTP server rejects conflicting duplicate `Content-Length` headers before
the handler, following RFC 9112.

`node:http` permits bodies on GET requests, and the maximum request/response
header count increased from 100 to 200 (`1.3.7`).

### Server type migration (`1.3-guide`)

`Bun.Server` is generic over WebSocket data and becomes
`Bun.Server<undefined>` without WebSockets. The data declaration uses an
XState-style pattern. `Bun.ServeOptions` is deprecated in favor of
`Bun.Serve.Options`; existing type annotations may stop compiling.

## Fetch

### Streaming input and body consumers (`1.2-guide`, `1.2.18`)

`fetch()` accepts a request body supplied by an async generator function.
`ReadableStream` has `.text()`, `.json()`, `.bytes()`, and `.blob()` for direct
consumption.

### Compression (`1.2.14`, `1.4`)

Fetch transparently decodes zstd and sends `Accept-Encoding: gzip, deflate, br,
zstd`. Request option `compress` accepts `true`, `gzip`, `deflate`, `br`, `zstd`
or `{ encoding, level }`, setting `Content-Encoding` and compressed
`Content-Length`. Streaming bodies are not compressed.

### User agent and header casing (`1.2.21`, `1.3.7`)

`bun --user-agent "value"` overrides Fetch's process-wide User-Agent. Outgoing
header names retain caller casing rather than being lowercased, including
through `node:https`.

### Proxy object and environment (`1.3.4`, `1.3.9`, `1.3.12`)

`proxy` accepts a URL or `{ url, headers }`; for HTTPS targets the headers go on
CONNECT, while HTTP receives them directly. Explicit `Proxy-Authorization`
wins over URL credentials. `NO_PROXY` applies even to an explicitly supplied
proxy.

Upper/lowercase `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` are reread for each
request, so runtime environment changes work. HTTPS CONNECT tunnels are pooled
by proxy, credentials, target and TLS configuration.

### TLS pooling (`1.3.10`, `1.3.14`)

Fetch and package-manager requests with custom CA or mTLS settings participate
in keepalive pooling. TLS-using APIs share an SSL context cache per VM keyed by
TLS settings except servername and ALPN.

### Protocol selection (`1.3.14`)

`RequestInit.protocol` accepts `http1.1`/`h1`, `http2`/`h2`, and
`http3`/`h3`. Per-request opt-in needs no flag; forcing unsupported HTTP/2 fails
with `HTTP2Unsupported`. Global experimental flags/env vars enable HTTP/2
multiplexing or HTTP/3 Alt-Svc upgrades. Proxy/CONNECT, Unix sockets, server
push and h2c are unsupported on these client paths.

The global controls are `--experimental-http2-fetch` or
`BUN_FEATURE_FLAG_EXPERIMENTAL_HTTP2_CLIENT=1`, and
`--experimental-http3-fetch` or
`BUN_FEATURE_FLAG_EXPERIMENTAL_HTTP3_CLIENT=1`. The HTTP/3 switch enables
automatic per-origin Alt-Svc upgrades on later requests.

### Request compression and client certificates (`1.4`, `1.4-4`)

Use `compress` for buffered outgoing bodies. For mTLS, put `cert` and `key` in
the per-request `tls` object.

```ts
await fetch("https://mtls.example", { tls: { cert, key } });
```

### Spec-alignment changes (`1.3.2`, `1.4-2`)

- Reading an already consumed request/response body rejects with `TypeError`.
- Duplicate response or server-request headers join with `, `; empty values
  read as `""`. `getSetCookie()` is unchanged.
- Cloning a disturbed or locked body throws
  `TypeError: Body is disturbed or locked`; clone before reading.
- Network errors reject as `TypeError` while retaining `.code`. A failed body
  read marks `bodyUsed`, so issue a fresh Fetch rather than reading again.
- Getters/options that throw cause a rejected promise rather than a synchronous
  throw.
- Aborting the signal errors the body even if all bytes already arrived.
- Request header values are emitted byte-for-byte as Latin-1, not UTF-8.
- `redirect: "error"` rejects only for 301, 302, 303, 307, and 308.
- The 300-second idle timeout is one deadline for the entire header block.

### Cancellation and network errors (`1.4-3`)

Cancelling a response body reader aborts the underlying request and closes its
connection rather than draining it. DNS failures from Fetch or `Bun.connect`
report `ENOTFOUND`, `syscall: "getaddrinfo"`, and hostname instead of
`ECONNREFUSED`. Content-Encoding matching is case-insensitive, including
`x-gzip`, and OPTIONS requests may carry bodies.

## WebSocket

### Compression and error values (`1.2.18`, `1.2.19`)

The global client negotiates `permessage-deflate` by default and reports it in
`extensions`. Its `error` event carries an `Error` object rather than a string.

### Subprotocols and header overrides (`1.2.22`)

RFC 6455 subprotocol negotiation populates `ws.protocol`; a missing or invalid
server selection rejects the connection. Constructor headers may override
reserved handshake fields such as Host, Sec-WebSocket-Key and
Sec-WebSocket-Protocol.

### Proxy and TLS (`1.3.6`)

`proxy` accepts a URL or `{ url, headers }` for both `ws:` and `wss:`. `tls`
accepts `ca`, `cert`, `key`, `passphrase`, and `rejectUnauthorized`.
A proxy scheme other than HTTP or HTTPS throws during construction (`1.4-2`).

### Credentials and proxy bypass (`1.3.7`, `1.3.9`)

URL credentials become Basic authorization unless an explicit Authorization
header wins. `NO_PROXY` applies to explicit constructor proxies as well as proxy
environment variables.

### Unix sockets (`1.3.13`)

`ws+unix://` and `wss+unix://` use the npm `ws` convention: split the socket
path and request path on the first colon after the path. Host defaults to
localhost, proxying is skipped, and the secure form performs TLS over the Unix
socket.

```ts
new WebSocket("ws+unix:///tmp/app.sock:/api/stream?x=1");
```

### Compression opt-out (`1.3-guide`, `1.3.14`)

The constructor accepts `perMessageDeflate: true`; `false` is now honored and
omits the extension offer. If the server returns the extension without an
offer, the handshake fails.

### Server publish and client validation (`1.4-2`)

- `server.publish()` and `ws.publish()` return `0` for no delivery, `-1` when
  any subscriber has backpressure, otherwise byte count.
- `server.upgrade()` returns false without a WebSocket Upgrade header and a
  valid key, and answers 426 for versions other than 13.
- In-memory Blob sends binary bytes; a `Bun.file()` blob throws.
- Global WebSocket does not accept `agent`; use the `ws` package when needed.
- `close()` validates codes and its 123-byte UTF-8 reason; ping/pong max is 125
  bytes. Close/terminate queue the close event, leaving `CLOSING` immediately.
- An unacknowledged requested subprotocol fails with close code 1002.
- The undocumented server `inspector: true` is ignored; use `bun --inspect`.

### Compatibility events (`1.4-3`)

Bun's client emits `upgrade` and `unexpected-response`, matching the `ws`
package.

### Server subscriptions (`1.3.2`)

`ServerWebSocket.subscriptions` returns de-duplicated topics. It returns an empty
array after close, so a close callback cannot use it to recover prior topics.

## TLS and certificate trust

### CA sources (`1.2.17`, `1.2.23`, `1.3-guide`, `1.3.14`)

- `tls.getCACertificates()` initially returned bundled roots while system stores
  were not read.
- `--use-system-ca` or `NODE_USE_SYSTEM_CA=1` adds OS trust to the bundled list.
- `NODE_EXTRA_CA_CERTS` accepts a whole bundle.
- `tls.getCACertificates("system")` returns OS roots without enabling the flag;
  the flag affects the `default` set. Windows also reads CA, TrustedPeople and
  policy/enterprise stores.

### Tightened verification (`1.4-2`)

- `tls.connect({ host })` uses host for SNI and identity when servername is
  absent; IP/localhost connections can fail `ERR_TLS_CERT_ALTNAME_INVALID`.
  Supply the certificate name or a `checkServerIdentity` override when CA-only
  trust is intended.
- `Bun.connect({ tls })`, `upgradeTLS()`, and listener client-certificate checks
  default to `rejectUnauthorized: true`. Failed Bun socket handshakes deliver
  an unauthorized socket, reject writes with `-1`, and close without data.
- `NODE_TLS_REJECT_UNAUTHORIZED=0` is honored by clients, but not used as a
  `tls.Server` default.
- A TLS server requesting a certificate destroys unauthorized clients unless
  `rejectUnauthorized` is explicitly false, emitting `tlsClientError`.
- Only literal `false` disables rejection and only literal `true` enables
  `requestCert`.
- Accepted net/TLS sockets no longer auto-resume before a data listener.
- Per-serverName client-certificate policy is enforced by `Bun.serve`, including
  HTTP/3.

Fetch's `tls.checkServerIdentity` runs after handshake but before sending
request bytes and reruns for every redirect hop. Use manual redirect handling or
validate each hop when pinning a certificate.

## HTTP/2, HTTP/3, and QUIC

### HTTP/2 server evolution (`1.2-guide`, `1.2.14`, `1.3.9`)

`node:http2` secure servers can run gRPC. Server creation accepts
`maxSendHeaderBlockLength`; clients support `setNextStreamID`. Passing a raw
`net.Server` socket into `Http2SecureServer` works for wrapper/proxy upgrade
patterns.

### HTTP/3 server (`1.3.14`)

`Bun.serve({ tls, http3: true })` binds UDP and TCP on the same port and uses
the same handlers. HTTP/1.1 and HTTP/2 advertise Alt-Svc. `http1: false` permits
HTTP/3-only service. The feature is highly experimental: WebSocket upgrade
returns false, 0-RTT is disabled, Unix addresses skip H3, and trailers plus
Expect/100-continue are unsupported.

### Node QUIC and expanded HTTP/2 (`1.4-3`)

`node:quic` implements Node 26's experimental API over lsquic: listen/connect,
uni/bidirectional streams, datagrams, 0-RTT, migration, resets, per-SNI
certificates, qlog and keylog. Node's distributed binaries compile QUIC out;
Node requires a source build with its experimental flag.

`node:http2` now supports push streams/responses/FDs, HTTP/1 fallback, AltSvc
and Origin frames, extended CONNECT, and diagnostics channels.

## UDP, sockets, DNS, and proxies

### UDP (`1.2-guide`, `1.3.11`, `1.3.12`)

`Bun.udpSocket()` provides `data` and `drain` callbacks; `sendMany()` submits
several datagrams in one syscall. `drain` signals OS backpressure relief.

ICMP failures are delivered to `error` without closing unrelated Linux sends.
The data callback's fifth `flags` argument identifies truncated datagrams.

`dgram.createSocket()` sets reuse-address only with `reuseAddr: true`; a second
bind otherwise gets `EADDRINUSE`. `reusePort` works on any platform providing
`SO_REUSEPORT`, including macOS.

### Unix listener lifecycle (`1.3.12`)

`Bun.listen`, `Bun.serve`, and `net.Server` throw `EADDRINUSE` rather than
unlinking and stealing an active Unix socket. Closing removes the socket file.
`Bun.serve({ unix })` and `fetch({ unix })` accept paths beyond macOS's native
104-byte limit.

### Socket metadata and controls (`1.2.9`, `1.2.16`, `1.4-2`)

`Bun.connect()` sockets expose localAddress/localFamily/localPort and
remoteAddress/remoteFamily/remotePort. Node net server/socket support includes
maxConnections, BlockList, AbortSignal on listen, and resetAndDestroy.

`Bun.Socket#setKeepAlive(true, delay)` interprets delay in milliseconds; values
below 1000 round to zero and leave TCP_KEEPIDLE unchanged.

`node:net` BlockList supports `addAddress`, `addRange`, `addSubnet`, and
`check` (`1.2.12`).

### DNS resolver split (`1.2.23`, `1.4-2`)

`dns.resolve` callbacks no longer receive an extra hostname; promise A/AAAA
resolution returns string arrays. On Linux, `dns.lookup`, its promise form and
`net.connect` use `getaddrinfo`, so systemd-resolved and split-DNS names work;
`dns.setServers()` does not affect them. `dns.resolve*` and `Bun.dns.lookup`
remain on c-ares; request `{ backend: "c-ares" }` explicitly when needed.

### Node socket errors (`1.4-2`)

Calling `dgram.bind()` twice throws `ERR_SOCKET_ALREADY_BOUND` synchronously;
operations on a closed socket throw `ERR_SOCKET_DGRAM_NOT_RUNNING`.

### Server header behavior (`1.2.5`)

`Strict-Transport-Security` is preserved on plain HTTP responses, which matters
behind a TLS-terminating proxy.
