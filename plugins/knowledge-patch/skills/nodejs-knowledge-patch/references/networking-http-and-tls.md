# Networking, HTTP, and TLS

TCP, UDP, DNS, HTTP/1, HTTP/2, QUIC, proxies, TLS, and certificate trust.

## Contents

- [HTTP/1 and proxies](#http1-and-proxies)
- [HTTP/2](#http2)
- [TLS and certificate trust](#tls-and-certificate-trust)
- [DNS, TCP, UDP, and sockets](#dns-tcp-udp-and-sockets)
- [QUIC and WebSockets](#quic-and-websockets)

## HTTP/1 and proxies

### Arbitrary HTTP informational responses (since 24.18.0)

`http.ServerResponse.writeInformation()` can send an arbitrary `1xx` response before the final response, covering informational status codes beyond the dedicated 100, 102, and 103 helpers.

### Client keep-alive timeout buffers (since 24.7.0)

`http.Agent` accepts an `agentKeepAliveTimeoutBuffer` option, allowing a client pool to leave a safety margin when applying server-provided keep-alive timeout hints and avoid reusing a socket near expiry.

### Deprecated HTTP response alias (since 25.0.0)

`response.writeHeader()` is now deprecated; use `response.writeHead()`.

### Environment-proxy support for `fetch()` (since 24.0.0)

Setting `NODE_USE_ENV_PROXY=1` makes Node's built-in `fetch()` honor the conventional HTTP proxy environment variables, including bypasses in `NO_PROXY`.

```console
NODE_USE_ENV_PROXY=1 HTTPS_PROXY=http://proxy.example:8080 \
  NO_PROXY=localhost,127.0.0.1 node app.js
```

### HTTP keep-alive timeout buffers (since 24.6.0)

HTTP servers now expose `server.keepAliveTimeoutBuffer`, allowing keep-alive timeout handling to include a separately configurable buffer.

### HTTP object-creation diagnostics channels (since 23.2.0)

`node:diagnostics_channel` now publishes `http.client.request.created` with `{ request }` and `http.server.response.created` with `{ request, response }`. Subscribe with `subscribe('http.client.request.created', ({ request }) => console.log(request.method))` to observe a client request as soon as its object is created.

### HTTP response bodies in the inspector (since 25.2.0)

Inspector network tooling can now inspect HTTP response bodies. For HTTP/2 traffic, both request and response bodies are supported.

### Null-prototype distinct-header collections (since 25.8.2)

HTTP `headersDistinct` and `trailersDistinct` collections now use null-prototype objects (CVE-2026-21710). Consumers must not assume inherited `Object.prototype` methods are present; use helpers such as `Object.hasOwn()` when inspecting them.

### Optimized empty HTTP requests (since 25.1.0)

HTTP servers accept the `optimizeEmptyRequests` option for more efficient handling of requests with no body: `createServer({ optimizeEmptyRequests: true }, requestListener)`.

### Pre-request sockets in HTTP shutdown (since 26.4.0)

`server.closeIdleConnections()` now also closes accepted sockets that have not yet received a request, so they no longer remain open during idle-connection cleanup.

### Programmatic global HTTP proxy activation (since 25.4.0)

`setGlobalProxyFromEnv()` from `node:http` applies the current proxy environment settings to the global core HTTP and HTTPS agents: `import { setGlobalProxyFromEnv } from 'node:http'; setGlobalProxyFromEnv();`.

### Proxies for core HTTP clients (since 24.5.0)

The default agents used by `http.request()` and `https.request()` now honor `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` (including their lowercase forms) when enabled with `NODE_USE_ENV_PROXY=1` or `--use-env-proxy`. Individual `http.Agent` and `https.Agent` instances accept a `proxyEnv` option, such as `new https.Agent({ proxyEnv: { HTTPS_PROXY: 'http://proxy.example.com:8080' } })`.

### Proxy, HTTP, and WebCrypto hardening (since 24.17.0)

Tunnel errors now redact proxy credentials, HTTP/2 caps its origin set to prevent unbounded memory growth, and `http.Agent` prevents response-queue poisoning. WebCrypto also guards cipher output lengths; applications on older Node.js 24 releases should upgrade to receive these corrections.

### Removed HTTP and stream aliases (since 26.0.0)

The deprecated `response.writeHeader()` alias has been removed; use `response.writeHead()`. The private `_stream_wrap`, `_stream_readable`, `_stream_writable`, `_stream_duplex`, `_stream_transform`, and `_stream_passthrough` entry points are also removed, so stream APIs must be imported from `node:stream`.

### Selective HTTP upgrades (since 24.9.0)

HTTP servers accept `shouldUpgradeCallback` in their creation options, letting a server decide which incoming requests enter the upgrade path. For example, `createServer({ shouldUpgradeCallback: request => request.headers.upgrade === 'websocket' })` limits upgrades to WebSocket requests.

### Undici traffic in the inspector (since 24.4.0)

Inspector network tooling can now inspect Undici traffic, including requests made by the built-in `fetch()` implementation.


## HTTP/2

### Graceful HTTP/2 server shutdown (since 24.0.0)

HTTP/2 servers now track their sessions during shutdown. `Http2Server.close()` coordinates graceful closure of active sessions instead of closing only the listening side while leaving sessions untracked.

### HTTP/2 ALPN callbacks (since 23.5.0)

Secure HTTP/2 servers now support the TLS `ALPNCallback` option for callback-based application-protocol selection.

### HTTP/2 client-stream diagnostics (since 24.1.0)

`node:diagnostics_channel` adds `http2.client.stream.created` and `http2.client.stream.start` channels for observing HTTP/2 client stream creation and startup.

### HTTP/2 priority signaling removed (since 24.2.0)

HTTP/2 priority signaling is no longer supported in Node.js 24 after its removal from nghttp2; it is deprecated on other release lines. The `selectPadding` HTTP/2 option was also removed, so code must not depend on either control.

### HTTP/2 request-body diagnostics (since 25.2.0)

`node:diagnostics_channel` now exposes channels for HTTP/2 client-stream request bodies, extending the earlier lifecycle stream diagnostics with body activity.

### HTTP/2 server-stream close diagnostics (since 24.3.0)

`node:diagnostics_channel` adds `http2.server.stream.close`, filling in the server-side close event that was absent from the other HTTP/2 stream lifecycle channels.

### HTTP/2 stream lifecycle diagnostics (since 24.2.0)

`node:diagnostics_channel` adds `http2.server.stream.created`, `http2.server.stream.start`, `http2.server.stream.finish`, and `http2.server.stream.error`, plus `http2.client.stream.finish`, `http2.client.stream.error`, and `http2.client.stream.close`.

### HTTP/2 traffic in inspector network tools (since 24.8.0)

Inspector network tracking now includes HTTP/2 client calls. Start the process with `node --inspect-wait --experimental-network-inspection app.js`, then open the dedicated Node DevTools from Chrome's `about:inspect` page to view the calls in the Network tab.

### Raw HTTP/2 push and trailer headers (since 24.18.0)

HTTP/2 `push` and `trailers` event listeners now receive a `rawHeaders` argument in addition to normalized headers.

### Raw HTTP/2 request headers (since 24.0.0)

`ClientHttp2Session.request()` accepts a raw alternating name/value header array in addition to a header object.

```js
const request = session.request([
  ':method', 'GET',
  ':path', '/',
  'accept', 'application/json',
]);
request.end();
```

### Raw HTTP/2 response headers (since 24.7.0)

HTTP/2 response streams now accept raw alternating name/value arrays in `respond()`, matching the raw-array form already supported for client requests.

```js
stream.respond([':status', '200', 'content-type', 'text/plain']);
```

### Raw HTTP/2 sent headers (since 24.6.0)

When an HTTP/2 stream is created with raw headers, its `Http2Stream.sentHeaders` property is now populated.


## TLS and certificate trust

### Environment toggle for system CAs (since 24.6.0)

Setting `NODE_USE_SYSTEM_CA=1` enables the existing system certificate-store behavior without requiring the `--use-system-ca` command-line flag.

```console
NODE_USE_SYSTEM_CA=1 node app.js
```

### Hostname and TLS security handling (since 24.17.0)

DNS and network APIs now reject hostnames containing embedded NUL bytes. TLS normalizes hostnames for server identity checks, matches SNI contexts without case sensitivity, and binds reusable sessions to the authenticated host, so malformed names and cross-host session reuse no longer follow the earlier behavior.

### Mutable default TLS CA certificates (since 24.5.0)

`tls.setDefaultCACertificates(certificates)` changes the list returned by `tls.getCACertificates('default')` and used by TLS clients that do not specify their own CAs. For example, add the system store to the existing default bundle with `tls.setDefaultCACertificates(tls.getCACertificates('default').concat(tls.getCACertificates('system')))`.

### Negotiated TLS groups (since 26.5.0)

TLS connections now report the negotiated group, allowing telemetry and policy checks to observe which key-exchange group a connection selected.

### QUIC certificate objects (since 26.4.0)

Experimental QUIC APIs now expose certificates as JavaScript `X509Certificate` objects rather than raw native handles.

### Removed TLS APIs (since 24.0.0)

The deprecated `tls.createSecurePair()` API has been removed, and `tls.Server.prototype.setOptions()` has reached end-of-life.

### Stricter DNS and TLS inputs (since 25.0.0)

`dns.lookup()` no longer accepts a falsy value in place of a hostname. TLS clients also can no longer put an IP address in the `servername` SNI option; omit SNI for an IP endpoint or supply its DNS hostname.

### System CA certificates on macOS and Windows (since 23.8.0)

The new `--use-system-ca` flag selects trusted CA certificates from the operating-system store. In this release it is available only on macOS and Windows, alongside the existing `--use-bundled-ca` and `--use-openssl-ca` choices.

```console
node --use-system-ca app.js
```

### System CA certificates on other platforms (since 23.9.0)

`--use-system-ca`, introduced on macOS and Windows in 23.8.0, now also works on other supported platforms.

### TLS CA inspection and system intermediates (since 23.10.0)

`node:tls` now exports `getCACertificates()` for retrieving CA certificates. In addition, `--use-system-ca` now supports intermediate certificates from the system certificate store, and the bundled roots have been updated to NSS 3.108.

### TLS certificate compression (since 26.4.0)

TLS configuration now accepts a `certificateCompression` option for configuring certificate compression.

### TLS, async-hook, and buffer security handling (since 24.13.0)

This security release gives `TLSSocket` a default error handler (CVE-2025-59465), routes TLS callback exceptions through error handlers (CVE-2026-21637), rethrows stack-overflow exceptions in `async_hooks` (CVE-2025-59466), and removes the zero-fill toggle from unsafe buffer creation (CVE-2025-55131). Deployments on earlier Node.js 24 releases should upgrade to receive these corrections.

### TLSA DNS records (since 23.9.0)

`node:dns` can now query and parse TLSA records through `resolveTlsa()`, including promise-based lookups.

```js
import { resolveTlsa } from 'node:dns/promises';

const records = await resolveTlsa('_443._tcp.example.com');
```

### Updated built-in root certificates (since 23.2.0)

Node's bundled CA set now follows NSS 3.104 and adds FIRMAPROFESIONAL CA ROOT-A WEB, TWCA CYBER Root CA, and SecureSign Root CA12, CA14, and CA15. TLS connections that use the bundled roots can now validate chains anchored at these authorities.

### Updated built-in root certificates (since 23.7.0)

Node's bundled CA set now follows NSS 3.107, changing the roots used by TLS clients that rely on the default trust store.

### Updated built-in root certificates (since 24.11.0)

Node.js 24.11.1 refreshes its bundled CA set to NSS 3.116, changing the roots available to TLS connections that rely on Node's built-in trust store.

### Updated built-in root certificates (since 24.7.0)

Node's bundled CA set now follows NSS 3.114. It adds the TrustAsia TLS ECC and RSA roots and SwissSign RSA TLS Root CA 2022 - 1, while removing GlobalSign Root CA, Entrust.net Premium 2048 Secure Server CA, Baltimore CyberTrust Root, Comodo AAA Services root, XRamp Global CA Root, Go Daddy Class 2 CA, and Starfield Class 2 CA.

### Updated built-in root certificates (since 25.5.0)

Node's bundled CA set now follows NSS 3.119, changing the roots used by TLS connections that rely on the built-in trust store.


## DNS, TCP, UDP, and sockets

### Additional TCP keepalive controls (since 26.4.0)

`net.Socket.prototype.setKeepAlive()` can now configure the `TCP_KEEPINTVL` interval and `TCP_KEEPCNT` probe count in addition to the existing keepalive behavior.

### Connection block lists (since 23.4.0)

`net.connect()` now accepts a `blockList` option for outbound connections, while `net.Server` accepts one for inbound connections. The same `net.BlockList` API used to describe blocked addresses can therefore enforce policy at connection setup.

```js
import { BlockList, connect, createServer } from 'node:net';

const blockList = new BlockList();
blockList.addAddress('192.0.2.1');
connect({ host: '192.0.2.1', port: 443, blockList });
createServer({ blockList }).listen(8000);
```

### Dropping excess cluster connections (since 23.1.0)

In cluster mode, setting `server.dropMaxConnection = true` makes a server close connections above `server.maxConnections` instead of passing them to another worker.

### Maximum DNS timeouts (since 24.5.0)

`dns.Resolver` accepts a `maxTimeout` constructor option, allowing applications to cap query timeouts instead of relying only on the initial `timeout` setting; for example, `new Resolver({ timeout: 1_000, maxTimeout: 5_000 })`.

### Network-family autoselection timing (since 25.2.0)

The default network-family autoselection timeout is now 500 ms. Connections that need different fallback timing should set `autoSelectFamilyAttemptTimeout` explicitly.

### Persistent connection block lists (since 24.5.0)

`net.BlockList` now supports saving and file-based management, allowing rule sets to persist instead of being reconstructed in memory on every start.

### QUIC port reuse (since 24.18.0)

The experimental `QuicEndpoint` accepts a `reusePort` option, allowing multiple endpoints to bind the same port where the platform supports it.

### Synchronous early TCP binding (since 26.4.0)

The new `net.BoundSocket` surface supports binding a TCP socket synchronously before later connection handling begins.

### TCP and UDP port reuse (since 23.1.0)

TCP and UDP listeners can opt into port reuse with `reusePort: true` in `net.Server.listen()` or `dgram.createSocket()` options, backed by new `UV_TCP_REUSEPORT` and `UV_UDP_REUSEPORT` support.

### UDP block lists (since 23.5.0)

UDP sockets now support address filtering with block lists, extending `net.BlockList`-based connection policy to `node:dgram`.

### WebSocket inspection (since 24.7.0)

The inspector has initial support for inspecting WebSocket traffic, extending its network-debugging coverage beyond ordinary HTTP traffic.


## QUIC and WebSockets

### Conditional QUIC built-in discovery (since 23.8.0)

`module.builtinModules` now omits `node:quic` unless the QUIC feature flag is enabled, so module enumeration reflects whether that experimental built-in is available.
