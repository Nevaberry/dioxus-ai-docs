# Networking, HTTP, and TLS

Use this reference for networking, http, and tls work.

## Arbitrary informational HTTP responses (`24.18.0`)

`ServerResponse.writeInformation()` sends arbitrary 1xx responses, extending the dedicated helpers for statuses such as 100, 102, and 103.

```js
res.writeInformation(102);
```

## Broader idle-connection shutdown (`26.4.0`)

`http.Server.closeIdleConnections()` now also closes sockets that were accepted but have not yet received a request, so pre-request connections no longer survive an idle-connection sweep.

## Caller-controlled HTTP default headers (`23.5.0`)

`http.request()` adds a `setDefaultHeaders` option, allowing callers to control whether Node automatically supplies the request's default headers.

## Certificate signature algorithms (`24.9.0`)

`X509Certificate.signatureAlgorithm` exposes the algorithm used to sign a certificate, avoiding separate certificate parsing for this metadata.

## Client keep-alive timeout buffer (`24.7.0`)

HTTP agents accept `agentKeepAliveTimeoutBuffer`, which shortens the server-provided keep-alive lifetime used when deciding whether a socket is still reusable. This is the client-side counterpart to the server timeout buffer and reduces reuse near the expiry boundary.

```js
import { Agent } from 'node:http';

const agent = new Agent({ agentKeepAliveTimeoutBuffer: 1_000 });
```

## Conditional QUIC built-in visibility (`23.8.0`)

`module.builtinModules` now omits `node:quic` when the QUIC flag is not in use, so feature detection no longer reports that disabled experimental module.

## Configurable HTTP header-value validation (`24.19.0`)

The HTTP implementation adds an `httpValidation` option for configuring header-value validation. Applications that intentionally need a non-default policy can select it without replacing Node's validation path.

## Configurable HTTP/2 stream-reset rate limiting (`23.0.0`)

HTTP/2 options now expose nghttp2's stream-reset rate limiter, allowing applications to configure how aggressively reset streams are limited.

## Connection-level network block lists (`23.4.0`)

`net.connect()` and `net.Server` now accept a `blockList` option, allowing a `net.BlockList` to reject outbound destinations and inbound peers during connection setup.

```js
import net from 'node:net';

const blockList = new net.BlockList();
blockList.addSubnet('10.0.0.0', 8);

net.connect({ host: '10.1.2.3', port: 443, blockList });
const server = net.createServer({ blockList });
```

## Custom HTTP/2 ALPN selection (`23.5.0`)

HTTP/2 server options now support `ALPNCallback`, enabling application-defined protocol selection during TLS ALPN negotiation.

## Early synchronous TCP binding (`26.4.0`)

`node:net` adds `net.BoundSocket` for synchronously binding a TCP endpoint before the later asynchronous networking work begins.

## Early-hints header validation (`24.18.0`)

`writeEarlyHints()` now validates non-`link` headers as well as link values, so malformed auxiliary early-hints headers are rejected rather than sent unchecked.

## Environment proxies for built-in fetch (`24.0.0`)

Setting `NODE_USE_ENV_PROXY=1` makes built-in `fetch()` use the standard proxy environment variables.

```sh
NODE_USE_ENV_PROXY=1 HTTPS_PROXY=http://proxy.example:8080 node app.js
```

## Expanded `BoundSocket` connections (`26.7.0`)

`net.BoundSocket` now supports synchronous connections and `AF_UNIX` paths, extending early synchronous setup to client connections and Unix-domain endpoints.

## Full TCP keepalive tuning (`26.4.0`)

`net.Socket.setKeepAlive()` now supports the `TCP_KEEPINTVL` and `TCP_KEEPCNT` controls, allowing callers to tune the probe interval and failure count as well as the initial delay.

## Graceful HTTP/2 shutdown and raw request headers (`24.0.0`)

HTTP/2 servers now track sessions for graceful server shutdown. `ClientHttp2Session.request()` also accepts a raw alternating name/value header array.

```js
const request = session.request([':method', 'GET', ':path', '/']);
```

## Hostname and TLS validation hardening (`24.17.0`)

DNS and network APIs now reject hostnames containing embedded NUL bytes. TLS normalizes hostnames for server identity checks, matches SNI contexts without case sensitivity, and binds reusable sessions to the authenticated host.

## HTTP constructors require normal construction (`24.2.0`)

Calling `node:http` classes without `new` is deprecated. Use their documented factory functions or construct the classes with `new`.

## HTTP header limits and HTTPS agent keys (`22.23.2`)

HTTP now rejects requests that exceed the maximum header count. HTTPS agents also distinguish object-array PFX keys, so different client-certificate configurations no longer share the same agent key.

## HTTP keep-alive timeout buffer (`24.6.0`)

HTTP servers add `server.keepAliveTimeoutBuffer`, a grace interval added to `server.keepAliveTimeout` when calculating the socket timeout. It lets the socket remain open slightly beyond the advertised keep-alive limit, reducing boundary-time connection resets.

```js
import { createServer } from 'node:http';

const server = createServer((request, response) => response.end('ok'));
server.keepAliveTimeout = 5_000;
server.keepAliveTimeoutBuffer = 1_000;
```

## HTTP limit validation (`25.5.0`)

HTTP `rawHeaders` now respects `maxHeadersCount`, and HTTP/2 validates `initialWindowSize` according to the protocol specification. Code that supplied an out-of-range HTTP/2 window size can now be rejected instead of proceeding with invalid configuration.

## HTTP/2 close-event ordering (`24.18.0`)

An HTTP/2 session now emits its `close` event before its streams emit theirs. Cleanup code that observes both levels should account for the session already being closed during stream-close handlers.

## HTTP/2 priority and padding removals (`24.2.0`)

Node.js 24 removes HTTP/2 priority signaling after nghttp2 dropped the deprecated RFC 9113 feature. The obsolete `options.selectPadding` option is also removed, so applications must stop relying on either behavior.

## Intermediate certificates from the system CA store (`23.10.0`)

`--use-system-ca` now supports intermediate certificates supplied by the operating system trust store, allowing chains that depend on those intermediates to validate.

## Longer network-family autoselection timeout (`25.2.0`)

The default network-family autoselection timeout is increased to 500 ms. Connection fallback between candidate address families therefore waits longer unless callers configure the timeout explicitly.

## Maximum DNS query timeouts (`24.5.0`)

The DNS resolver now supports a maximum query timeout, allowing applications to cap how long resolution attempts can extend.

## Negotiated TLS group reporting (`26.5.0`)

TLS connections now report their negotiated group, allowing diagnostics and policy checks to observe the selected key-exchange group.

## Network and crypto stability promotions (`26.4.0`)

`net.BlockList` advances to release-candidate stability, while the Argon2 and key encapsulation/decapsulation APIs are now stable.

## Network-facing legacy APIs (`25.0.0`)

`response.writeHeader()` is deprecated in favor of `writeHead()`. Falsy hostnames passed to DNS lookup, IP addresses used as a TLS `servername`, and invalid ports in the legacy URL API have reached end-of-life and must be replaced with explicit valid inputs.

## Opt-in system CA stores (`23.8.0`)

The `--use-system-ca` flag lets Node use certificates from the operating system trust store. In this release it is available on macOS and Windows, alongside the existing bundled-CA and OpenSSL-CA choices.

```sh
node --use-system-ca app.js
```

## Optimized empty HTTP requests (`25.1.0`)

HTTP server creation now accepts `optimizeEmptyRequests`, allowing servers to opt into optimized handling for requests with no body.

```js
import { createServer } from 'node:http';

const server = createServer({ optimizeEmptyRequests: true }, (request, response) => {
  response.end('ok');
});
server.listen(3000);
```

## Persistent network block lists (`24.5.0`)

`net.BlockList` can now save and manage its rules through files, allowing a rule set to persist across process runs instead of being rebuilt in code.

## Programmatic environment-proxy activation (`25.4.0`)

`http.setGlobalProxyFromEnv()` activates environment-proxy handling for the global core HTTP clients at runtime.

```js
import { setGlobalProxyFromEnv } from 'node:http';

setGlobalProxyFromEnv();
```

## Proxies for core HTTP clients (`24.5.0`)

`http.request()`, `https.request()`, and their default global agents now support environment-configured proxies. Enable this globally with `NODE_USE_ENV_PROXY=1` or `--use-env-proxy`; the agents read `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` as well as their lowercase forms.

Custom `http.Agent` and `https.Agent` instances also accept a `proxyEnv` option:

```js
import https from 'node:https';

const agent = new https.Agent({
  proxyEnv: {
    HTTPS_PROXY: 'http://proxy.example.com:8080',
    NO_PROXY: 'localhost,127.0.0.1',
  },
});
```

## Proxy, HTTP, and WebCrypto security hardening (`24.17.0`)

Tunnel errors now redact proxy credentials, HTTP/2 caps its origin set to prevent unbounded memory growth, and `http.Agent` prevents response-queue poisoning. WebCrypto cipher operations also guard their output length.

## QUIC endpoint and certificate surfaces (`26.4.0`)

`node:quic` adds `listEndpoints()`. QUIC certificates are now exposed as JavaScript `X509Certificate` objects rather than raw handles, so consumers must update type handling.

## Raw HTTP/2 headers populate `sentHeaders` (`24.6.0`)

When an HTTP/2 request is created from a raw alternating name/value header array, its `Http2Stream.sentHeaders` property is now populated rather than being left unset.

## Raw HTTP/2 response header arrays (`24.7.0`)

`Http2Stream.respond()` now accepts raw alternating header name/value arrays, extending raw-array support to server responses.

```js
stream.respond([':status', '200', 'content-type', 'text/plain']);
```

## Removed HTTP and private stream aliases (`26.0.0`)

The deprecated `response.writeHeader()` alias is removed; use `response.writeHead()`. The `_stream_wrap`, `_stream_readable`, `_stream_writable`, `_stream_duplex`, `_stream_transform`, and `_stream_passthrough` modules are also removed in favor of public `node:stream` APIs.

## Replacing the default TLS CA set (`24.5.0`)

`tls.setDefaultCACertificates()` changes both the list returned by `tls.getCACertificates('default')` and the certificates used by TLS clients that do not supply their own `ca`. To extend rather than replace the bundled Mozilla roots, include the current default list in the new value.

```js
import tls from 'node:tls';

tls.setDefaultCACertificates(
  tls.getCACertificates('default').concat(
    tls.getCACertificates('system'),
  ),
);
```

## Root certificate changes (`24.7.0`)

The bundled trust store moves to NSS 3.114, adding the TrustAsia TLS ECC and RSA roots and SwissSign RSA TLS Root CA 2022 - 1. It removes the GlobalSign Root CA, Entrust.net Premium 2048 Secure Server CA, Baltimore CyberTrust Root, Comodo AAA Services root, XRamp Global CA Root, Go Daddy Class 2 CA, and Starfield Class 2 CA, which can change certificate-chain validation.

## Selective HTTP upgrades (`24.9.0`)

HTTP server creation options now accept `shouldUpgradeCallback(request)`, which decides which incoming requests enter upgrade handling. This lets a server reject unsupported upgrade protocols before its `'upgrade'` handler runs.

```js
import { createServer } from 'node:http';

const server = createServer({
  shouldUpgradeCallback: request => request.headers.upgrade === 'websocket',
});
```

## Synchronous UDP setup (`24.19.0`)

`node:dgram` sockets add `bindSync()` and `connectSync()`, allowing address binding and peer selection to complete before subsequent code runs.

```js
import { createSocket } from 'node:dgram';

const socket = createSocket('udp4');
socket.bindSync(0, '127.0.0.1');
socket.connectSync(53, '127.0.0.1');
socket.close();
```

## System CA support on additional platforms (`23.9.0`)

`--use-system-ca` now works on platforms beyond macOS and Windows.

## TCP and UDP port-reuse modes (`23.1.0`)

Networking now supports the `UV_TCP_REUSEPORT` and `UV_UDP_REUSEPORT` modes for TCP and UDP port reuse.

## TLS CA certificate inspection (`23.10.0`)

`tls.getCACertificates()` exposes the CA certificates available to TLS code.

```js
import { getCACertificates } from 'node:tls';

const certificates = getCACertificates();
```

## TLS certificate compression (`26.4.0`)

TLS accepts a `certificateCompression` option, and the OpenSSL build configuration includes compression support for negotiating compressed certificate chains.

## TLS error delivery (`24.13.0`)

`TLSSocket` now has a default error handler, and exceptions thrown by TLS callbacks are routed through error handlers. This fixes CVE-2025-59465 and CVE-2026-21637; applications should still attach explicit error listeners when they need logging or recovery.

## TLS listener exception routing (`26.4.0`)

Exceptions thrown by TLS event listeners now pass through TLS error handlers, changing which error path observes listener failures.

## TLSA DNS records (`23.9.0`)

`node:dns` can now query and parse TLSA records, so applications can consume this record type through the built-in DNS implementation.

## Transferable TCP handles (`26.7.0`)

TCP `Server` and `Socket` objects can be transferred across worker threads, with TCP handle transfer now supported on Windows as well.

## UDP block lists (`23.5.0`)

`node:dgram` now supports block lists for UDP traffic, extending address filtering beyond the TCP-side `net` APIs.

## Unicode 17 URLs and updated root certificates (`24.13.0`)

Node.js 24.13.1 adds Unicode 17 support to its URL implementation and updates its bundled root store to NSS 3.119. Internationalized URL handling and certificate-chain acceptance can therefore differ after upgrading.

## Updated built-in root certificates (`23.2.0`)

The bundled root store is updated to NSS 3.104, adding FIRMAPROFESIONAL CA ROOT-A WEB, TWCA CYBER Root CA, and SecureSign Root CA12, CA14, and CA15.

## Updated bundled root certificates (`23.10.0`)

The bundled CA set is updated to NSS 3.108, which can change which certificate chains validate when Node uses its bundled trust store.

## Updated bundled root certificates (`24.18.0`)

The bundled root certificate store is updated to NSS 3.123.1. Certificate chains accepted when using Node's bundled CA set can therefore change after upgrading.

## Updated trust and time-zone data (`25.9.0`)

The bundled root certificates are updated to NSS 3.121 and the bundled time-zone data to 2026a. Certificate-chain validation and civil-time calculations can therefore change after upgrading.

## WebSocket inspection (`24.7.0`)

The inspector gains initial support for inspecting WebSocket traffic, extending its network diagnostics beyond HTTP and Undici requests.
