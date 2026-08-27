# HTTP and networking

Use this reference for servers, routes, fetch, WebSockets, sockets, proxies, TLS, DNS, cookies, and network protocols.

## `NO_PROXY` with explicit proxies

*Batch: `1.3.9`.*

`fetch()` and `WebSocket` now honor `NO_PROXY` even when their `proxy` option is supplied explicitly, so matching destinations bypass that proxy.

```ts
// With NO_PROXY=localhost, this connects directly.
await fetch("http://localhost:3000/api", {
  proxy: "http://proxy.example:8080",
});
```

## `TLSSocket.allowHalfOpen` compatibility

*Batch: `1.2.11`.*

When `TLSSocket` wraps a `net.Socket` or `stream.Duplex`, an `allowHalfOpen: true` option is ignored and the resulting property is `false`, matching Node.js.

```js
import { Socket } from "node:net";
import { TLSSocket } from "node:tls";

const socket = new TLSSocket(new Socket(), { allowHalfOpen: true });
console.log(socket.allowHalfOpen); // false
```

## `URLPattern` Web API

*Batch: `1.3.4`.*

Bun now provides the `URLPattern` Web API for declarative URL matching. It supports string or `URLPatternInit` inputs, `test()`, `exec()`, component properties, named and wildcard groups, and `hasRegExpGroups`.

```ts
const pattern = new URLPattern({ pathname: "/users/:id" });
const match = pattern.exec("https://example.com/users/123");
console.log(match?.pathname.groups.id); // "123"
```

## Abortable `node:net` servers

*Batch: `1.2.5`.*

`net.Server.listen()` accepts an `AbortSignal`; aborting it closes the server, while a signal that is already aborted closes it immediately.

```js
import { createServer } from "node:net";

const controller = new AbortController();
const server = createServer();
server.listen({ port: 3000, signal: controller.signal });
controller.abort();
```

## Automatic byte ranges for file responses

*Batch: `1.3.13`.*

`Bun.serve()` automatically handles a `Range: bytes=...` header when a static or dynamic handler returns a whole-file `200` response, producing `206` with `Content-Range` or `416` for an invalid range. Suffix and open-ended ranges are supported; multi-range requests fall back to the full response.

```ts
Bun.serve({
  routes: { "/video.mp4": new Response(Bun.file("./video.mp4")) },
});
```

## Automatic static-route ETags

*Batch: `1.2.20`.*

Static `Response` routes in `Bun.serve({ routes })` now receive an `ETag` automatically. A request with a matching `If-None-Match` is answered with `304 Not Modified` without application code handling the conditional request.

## Automatic WebSocket client compression

*Batch: `1.2.18`.*

The built-in WebSocket client now enables and negotiates `permessage-deflate` compression by default when the server supports it. After the connection opens, `webSocket.extensions` reports the negotiated extension.

## Built-in cookie APIs

*Batch: `1.2.7`.*

`Bun.serve()` requests expose a lazily parsed `CookieMap` as `request.cookies`; calling `set()` or `delete()` on it automatically adds the corresponding `Set-Cookie` headers to the returned response. Outside a server handler, `Bun.Cookie` represents a mutable, serializable cookie, while `Bun.CookieMap` manages multiple cookies and produces headers with `toSetCookieHeaders()`.

```ts
Bun.serve({
  routes: {
    "/sign-in": request => {
      request.cookies.set("sessionId", "123", {
        httpOnly: true,
        sameSite: "strict",
      });
      return new Response("Signed in");
    },
    "/sign-out": request => {
      request.cookies.delete("sessionId");
      return new Response("Signed out");
    },
  },
});

const cookie = new Bun.Cookie("theme", "dark");
console.log(cookie.serialize());

const cookies = new Bun.CookieMap();
cookies.set("theme", "dark");
console.log(cookies.toSetCookieHeaders());
```

## Built-in HTTP routing

*Batch: `1.2.3`.*

`Bun.serve()` renames its `static` option to `routes`, whose values may be imported HTML, handlers with typed `req.params`, or method-specific handler maps. Supplying routes makes `fetch` optional.

```ts
Bun.serve({
  routes: {
    "/api/users/:id": req => Response.json({ id: req.params.id }),
  },
});
```

## Bundled CA certificate inspection

*Batch: `1.2.17`.*

`tls.getCACertificates()` returns Bun's bundled trusted root certificates as PEM strings. It does not yet include system-wide CA certificates.

```js
import { getCACertificates } from "node:tls";

const bundledRoots = getCACertificates();
```

## Callback-based global catch-all routes

*Batch: `1.2.6`.*

`Bun.serve()` routes can now use a callback handler for the global `/*` catch-all, rather than requiring a static `Response` value.

```ts
Bun.serve({
  routes: { "/*": () => new Response("Global catch-all") },
});
```

## Closing idle HTTP connections

*Batch: `1.2.22`.*

Node-compatible HTTP servers implement `closeIdleConnections()`, allowing graceful shutdown to immediately drop idle keep-alive sockets while active requests finish.

```ts
server.close();
server.closeIdleConnections();
```

## Compressed fetch request bodies

*Batch: `1.4`.*

The Bun-specific `fetch()` `compress` option compresses buffered request bodies and sets `Content-Encoding` and the compressed `Content-Length` automatically. It accepts `true`, `"gzip"`, `"deflate"`, `"br"`, `"zstd"`, or an `{ encoding, level }` object; streaming bodies pass through unchanged.

```ts
await fetch(url, {
  method: "POST",
  body: largeJsonString,
  compress: "gzip",
});
```

## Cookie expiration precedence

*Batch: `1.4-4`.*

`Bun.Cookie` now serializes `Expires` as an RFC 6265 date, retains both `Expires` and `Max-Age` when parsing, and makes `isExpired()` give `Max-Age` precedence regardless of attribute order.

## Cookies during WebSocket upgrades

*Batch: `1.3.1`.*

Cookies set with `req.cookies.set()` before `server.upgrade()` are now included as `Set-Cookie` headers on the `101 Switching Protocols` response, including when custom upgrade headers are supplied.

## Correct `Socket.reload()` shape

*Batch: `1.3.9`.*

The TypeScript signature for `Socket.reload()` now matches runtime behavior: the replacement handler must be wrapped in a `socket` property.

```js
function replaceSocketHandler(socket, handler) {
  socket.reload({ socket: handler });
}
```

## Corrected socket and mapping parameters

*Batch: `1.4-2`.*

`Bun.Socket#setKeepAlive(true, initialDelay)` now interprets the delay as milliseconds, so one minute is `60_000`; values below 1000 leave `TCP_KEEPIDLE` unchanged. `Bun.mmap(path, { offset })` now exposes the requested byte at index zero instead of exposing the page-aligned boundary, so old manual offset compensation must be removed.

## Credentials in WebSocket URLs

*Batch: `1.3.7`.*

Credentials embedded in a target URL such as `ws://user:pass@example.com/socket` are sent as a Basic `Authorization` header during the upgrade. An explicitly supplied `Authorization` header takes precedence.

## CSRF token helpers

*Batch: `1.2.5`.*

`Bun.CSRF.generate` and `Bun.CSRF.verify` are built-in helpers for generating and verifying XSRF/CSRF tokens.

## Custom proxy headers in `fetch()`

*Batch: `1.3.4`.*

The `proxy` option now accepts `{ url, headers }`; these headers are sent in HTTPS `CONNECT` requests and direct HTTP proxy requests. An explicit `Proxy-Authorization` header overrides credentials embedded in the proxy URL.

```ts
await fetch("https://example.com/data", {
  proxy: {
    url: "http://proxy.example.com:8080",
    headers: { "Proxy-Authorization": "Bearer token" },
  },
});
```

## Directory routes

*Batch: `1.4`.*

`Bun.serve()` routes can serve a directory, automatically handling `Content-Type`, validators, conditional and range requests, and directory `index.html` files. Paths are normalized before lookup, and Linux prevents symlinks inside the route from escaping its root.

```ts
Bun.serve({
  routes: { "/static/*": { dir: "./public" } },
});
```

## Expanded `Bun.connect()` socket addresses

*Batch: `1.2.9`.*

Sockets passed to `Bun.connect()` handlers now expose `localAddress`, `localFamily`, `remoteFamily`, and `remotePort`, matching the same-named `node:net.Socket` properties; `localPort` and `remoteAddress` remain available.

## Expanded HTTP/2 compatibility

*Batch: `1.4-3`.*

`node:http2` now supports server push, raw headers, graceful shutdown, and `respondWithFD`. It also adds diagnostics-channel events, Alt-Svc and Origin frames, extended CONNECT, and `allowHTTP1` fallback on compatibility servers.

## Experimental HTTP/2 and HTTP/3 `fetch()`

*Batch: `1.3.14`.*

The Bun-specific `RequestInit.protocol` can force `"http1.1"`/`"h1"`, `"http2"`/`"h2"`, or `"http3"`/`"h3"`; forced HTTP/2 rejects with `HTTP2Unsupported` when unavailable, while HTTP/3 remains an early preview. `--experimental-http2-fetch` enables multiplexed HTTP/2 negotiation globally, while `--experimental-http3-fetch` enables per-origin upgrades after an `Alt-Svc: h3` response; HTTP/2 proxies, Unix sockets, and h2c are not supported.

```ts
await fetch("https://example.com", { protocol: "http2" });
await fetch("https://example.com", { protocol: "http3" });
```

## Experimental HTTP/3 servers

*Batch: `1.3.14`.*

`Bun.serve({ tls, http3: true })` binds TCP for HTTP/1.1 and HTTP/2 plus UDP for HTTP/3 on the same port, reuses the same handlers, and advertises the QUIC endpoint with `Alt-Svc`. This is explicitly not production-ready yet and does not support WebSockets over HTTP/3, 0-RTT, trailers, or `Expect: 100-continue`.

```ts
Bun.serve({
  port: 443,
  tls: { cert, key },
  http3: true,
  fetch: () => new Response("hello"),
});
```

## Fetch and server conformance changes

*Batch: `1.4-2`.*

Duplicate fetch-response and server-request headers are comma-joined except that `Set-Cookie` remains separately available through `getSetCookie()`; cloning a consumed or locked body throws immediately, and network failures reject with `TypeError` while marking a failed body as used. Method routes use `GET` for `HEAD` when no `HEAD` handler exists; `Bun.serve()` throws for invalid ports and routes an invalid response status through `error()` to a default `500`.

## Fetch and WebSocket compatibility

*Batch: `1.2.19`.*

A `Request` now retains its `redirect` option, so `fetch(new Request(url, { redirect: "manual" }))` does not follow redirects. Accessing the body of affected `FormData` or stream-backed requests preserves `Content-Type`, `fetch()` permits an explicit `Connection` header, and WebSocket `error` events now carry an `Error` object rather than only a string.

## Fetch cancellation and failure semantics

*Batch: `1.4-3`.*

Cancelling a fetch response reader now aborts the underlying request and closes the connection instead of draining the body. DNS failures report `ENOTFOUND` with `syscall: "getaddrinfo"`, and `redirect: "error"` rejects only actual redirect statuses rather than every 3xx response.

## File-backed server routes

*Batch: `1.2.16`.*

`Bun.serve({ routes })` now accepts a `Bun.file()` value directly, serving the file without manually reading or buffering it.

```ts
Bun.serve({
  routes: { "/report.pdf": Bun.file("./report.pdf") },
});
```

## Graceful server shutdown

*Batch: `1.2-guide`.*

`server.stop()` now returns a `Promise<void>` that resolves after in-flight HTTP connections close, so shutdown can be awaited.

## HSTS headers behind TLS proxies

*Batch: `1.2.5`.*

`Bun.serve()` and `node:http` no longer remove `Strict-Transport-Security` from responses sent over backend HTTP, allowing the header to survive when a reverse proxy terminates HTTPS.

## HTTP and HTTPS client caveats

*Batch: `nodejs-compatibility`.*

Although `node:http` is listed as fully implemented, outgoing client request bodies are buffered rather than streamed. `node:https` APIs are implemented, but `Agent` is not always used, so code whose behavior depends on an agent is not fully compatible.

## HTTP client compatibility

*Batch: `1.2.18`.*

An HTTP/2 client now emits `remoteSettings` even when the server sends an empty `SETTINGS` frame to select defaults, preventing consumers such as `grpc-js` from waiting indefinitely. Calling `flushHeaders()` on a `node:http` client request also no longer prevents its request body from being sent.

## HTTP/2 handoff from `net.Server`

*Batch: `1.3.9`.*

Raw sockets accepted by `node:net` can now be handed to an `Http2SecureServer` by emitting its `connection` event, enabling custom HTTP/2 proxy and connection-upgrade servers.

```ts
import { readFileSync } from "node:fs";
import { createSecureServer } from "node:http2";
import { createServer } from "node:net";

const h2 = createSecureServer({
  key: readFileSync("key.pem"),
  cert: readFileSync("cert.pem"),
});
createServer(socket => h2.emit("connection", socket)).listen(8443);
```

## HTTP/2 server and client controls

*Batch: `1.2.14`.*

`node:http2` servers now accept `maxSendHeaderBlockLength` to cap a single outgoing header block, and client sessions support `setNextStreamID()`.

```js
import http2 from "node:http2";
const server = http2.createServer({
  maxSendHeaderBlockLength: 1024 * 1024,
});
```

## Increased HTTP header count

*Batch: `1.3.7`.*

The maximum number of request or response headers increased from 100 to 200.

## Inspector server control

*Batch: `1.4-3`.*

`node:inspector` now implements `open()`, `url()`, `close()`, and `waitForDebugger()`, including Node-compatible discovery endpoints for Chrome DevTools and VS Code attachment.

## Native UDP sockets

*Batch: `1.2-guide`.*

`Bun.udpSocket()` is the Bun-native alternative to `node:dgram`; its `socket.data` callback receives datagrams, `send()` transmits one, and `sendMany()` batches multiple datagrams into one syscall. A `socket.drain` callback signals that operating-system backpressure has cleared.

## Network and TLS compatibility

*Batch: `1.4-3`.*

`net.Socket.end()` now half-closes, while `net.Socket.connect()` and `Bun.connect()` accept `localAddress` and `localPort` for binding outbound connections. TLS adds session and keylog events, structured OpenSSL errors, SNI and ALPN callbacks, PFX credentials, plus per-context `secureContext.addCACert()` and process-wide `tls.setDefaultCACertificates()`.

## Network stream backpressure

*Batch: `1.4`.*

`Bun.serve()` now pauses streaming request and response bodies when the connection cannot accept more data, instead of buffering unsent chunks without bound. Receiving through `fetch()` follows the same rule, including pipelines using transform streams, subprocesses, `Bun.file().stream()`, and `Blob.stream()`.

## Node DNS promise APIs

*Batch: `1.3.12`.*

`node:dns/promises` now exports `getDefaultResultOrder()` and `getServers()`; the former returns the configured `"ipv4first"`, `"ipv6first"`, or `"verbatim"` string. The callback-based `node:dns.getDefaultResultOrder()` now returns that string as well.

## Node HTTP body-write rejection

*Batch: `1.2.10`.*

`node:http` now implements `rejectNonStandardBodyWrites` consistently with Node.js. When it is `true`, writing a response body for a `HEAD` request throws; when it is `false`, `undefined`, or omitted, the write is ignored.

```js
import http from "node:http";

http.createServer({ rejectNonStandardBodyWrites: true }, (req, res) => {
  if (req.method === "HEAD") res.write("body"); // throws
});
```

## Node HTTP client and server parity

*Batch: `1.4-3`.*

`node:http` clients now use `net`/`tls` sockets, Node's HTTP parser, and an `Agent` pool instead of a `fetch()`-based shim, enabling Node-compatible keep-alive reuse, `Upgrade`/`CONNECT`, informational responses, and custom connections. Servers honor Node's timeout sweep, HTTP/1.1 pipelining through `maxRequestsPerSocket`, `insecureHTTPParser`, `maxHeaderSize`, and the normal `net.Socket` lifecycle.

## Node HTTP keep-alive pooling

*Batch: `1.3.4`.*

`node:http` agents configured with `{ keepAlive: true }` now reuse pooled connections across requests. Bun also handles `Connection: keep-alive` headers case-insensitively, matching HTTP header semantics.

## Node HTTP parser binding

*Batch: `1.2.16`.*

For packages that depend on Node's internal HTTP parser surface, Bun now exposes `process.binding("http_parser").HTTPParser` and also exports `HTTPParser` from `node:_http_common`.

```js
const { HTTPParser } = process.binding("http_parser");
const parser = new HTTPParser();
parser.initialize(HTTPParser.REQUEST, {});
parser.execute(Buffer.from("GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"));
```

## Node network and callback semantics

*Batch: `1.4-2`.*

On Linux, `dns.lookup()`, its promise form, and `net.connect()` now use the system `getaddrinfo()` resolver, so `dns.setServers()` affects only `resolve*()` calls while `Bun.dns.lookup(host, { backend: "c-ares" })` remains available. Accepted `net.Server` and `tls.Server` sockets start paused and buffer early bytes, while exceptions thrown from `node:fs`, `node:dns`, or `crypto.pbkdf2()` callbacks reach `uncaughtException` rather than `unhandledRejection`.

## Node-compatible socket addresses

*Batch: `1.2.4`.*

`node:net` now exports `SocketAddress`; `SocketAddress.parse()` parses an IP endpoint and exposes its `family`, `address`, and `port`.

```ts
import { SocketAddress } from "node:net";

const address = SocketAddress.parse("[::1]:1234");
console.log(address.family, address.address, address.port);
```

## Node-compatible socket descriptors

*Batch: `1.3.3`.*

Sockets from `node:net` and `node:tls` now expose their file descriptor as `_handle.fd`, enabling packages that depend on this Node.js compatibility surface.

## Node-compatible Unix socket lifecycle

*Batch: `1.3.12`.*

`Bun.listen()`, `Bun.serve()`, and `net.Server` now throw `EADDRINUSE` instead of unlinking an existing Unix socket, and remove their own socket file when closed. Unix socket paths beyond macOS's normal 104-byte limit are also supported.

## Operating-system CA roots

*Batch: `1.2.23`.*

`--use-system-ca` or `NODE_USE_SYSTEM_CA=1` adds the operating system's trusted roots to Bun's built-in Mozilla CA store, allowing TLS connections to corporate or locally installed authorities.

```sh
bun run --use-system-ca index.js
```

## Outbound HTTP header casing

*Batch: `1.3.7`.*

`fetch()` and `node:https` now preserve the spelling of request header names instead of lowercasing them, matching Node.js and supporting services that incorrectly require exact casing.

## Runtime CA certificate bundles

*Batch: `1.2.3`.*

Bun now loads complete CA bundles from `NODE_EXTRA_CA_CERTS=/path/to/full/bundle.crt` for TLS connections, matching Node.js rather than requiring certificate-by-certificate configuration.

## Runtime proxy environment changes

*Batch: `1.3.12`.*

Changes to `process.env.HTTP_PROXY`, `HTTPS_PROXY`, or `NO_PROXY`, including their lowercase forms, now affect the next `fetch()` instead of proxy configuration being fixed at process startup.

## Runtime-wide fetch user agent

*Batch: `1.2.21`.*

The `--user-agent` runtime flag overrides the `User-Agent` header for every `fetch()` request made by the application.

```sh
bun --user-agent "MyApp/1.0" app.js
```

## Session-bound CSRF tokens

*Batch: `1.4-2`.*

`Bun.CSRF.generate()` and `verify()` accept `sessionId`, binding a token to a principal through HMAC associated data. Verification fails for another session or when only one side supplies `sessionId`, while tokens made without it retain their old behavior.

## Socket error objects

*Batch: `1.2.4`.*

`node:net` socket `"error"` handlers now always receive JavaScript `Error` instances rather than leaked engine-internal exception objects, so `error instanceof Error` is reliable.

## Static server routes

*Batch: `1.2-guide`.*

`Bun.serve({ static })` maps paths directly to cached `Response` objects before the dynamic `fetch` handler. `server.reload({ static: ... })` replaces the route table when generated responses need refreshing.

```ts
const server = Bun.serve({
  static: { "/health": new Response("ok") },
  fetch: () => new Response("dynamic"),
});
```

## String ports in `net.Server.listen()`

*Batch: `1.2.13`.*

Node-compatible networking now coerces a numeric string passed as the port to a number, so `server.listen("3000")` listens on TCP port 3000.

## System CA inspection and Windows trust stores

*Batch: `1.3.14`.*

`tls.getCACertificates("system")` now returns operating-system certificates without requiring `--use-system-ca`; that flag still controls whether system roots join the default trust set. On Windows, opting into system CAs now reads `ROOT`, `CA`, and `TrustedPeople` stores across user, machine, Group Policy, and enterprise locations, allowing locally cached intermediates to complete certificate chains.

```ts
import tls from "node:tls";
const systemCertificates = tls.getCACertificates("system");
```

## TLS validation and identity defaults

*Batch: `1.4-2`.*

`fetch()` now runs `tls.checkServerIdentity` after the handshake but before sending any request bytes, and repeats it for every redirect hop. `tls.connect({ host })` uses `host` as the default SNI and certificate name, while `Bun.connect()`, `socket.upgradeTLS()`, `RedisClient`, and listener APIs with `requestCert: true` now enforce verification by default; pass the correct `ca`/`servername`, or a literal `rejectUnauthorized: false` only when verification is intentionally disabled.

## UDP errors and truncation metadata

*Batch: `1.3.12`.*

On Linux, ICMP failures from `Bun.udpSocket()` now reach the socket's `error` handler without closing the socket. A fifth `flags` argument to `data` reports `flags.truncated` when a datagram exceeded the receive buffer.

```ts
const socket = await Bun.udpSocket({
  socket: {
    error(error) {
      console.error(error.code);
    },
    data(_socket, data, _port, _address, flags) {
      if (flags.truncated) discard(data);
    },
  },
});
```

## UDP socket compatibility changes

*Batch: `1.3.11`.*

`node:dgram` now supports `reusePort: true` on macOS and implicitly binds an unbound UDP socket when `send()` is first called there. UDP sockets also no longer enable `SO_REUSEADDR` by default, so pass `reuseAddr: true` explicitly when port reuse is intended.

## URL objects as fetch proxies

*Batch: `1.3.5`.*

The `fetch()` `proxy` option accepts a `URL` instance directly instead of mistaking it for the `{ url, headers }` object form.

```ts
await fetch("https://example.com/data", {
  proxy: new URL("http://proxy.example.com:8080"),
});
```

## WebSocket classes from `node:http`

*Batch: `1.2.2`.*

`node:http` now re-exports the global `WebSocket`, `CloseEvent`, and `MessageEvent` classes.

```js
const { WebSocket, CloseEvent, MessageEvent } = require("node:http");
```

## WebSocket connections through proxies

*Batch: `1.3.6`.*

The native `WebSocket` constructor accepts `proxy` as an HTTP/HTTPS URL or as `{ url, headers }`, including URL credentials and custom proxy authorization. Every `ws://`/`wss://` and HTTP/HTTPS proxy combination is supported, and `tls` accepts the same CA, certificate, key, and passphrase controls as `fetch()`.

```ts
const socket = new WebSocket("wss://example.com", {
  proxy: {
    url: "https://proxy.example:8443",
    headers: { "Proxy-Authorization": "Bearer token" },
  },
  tls: { rejectUnauthorized: true },
});
```

## WebSocket delivery results

*Batch: `1.4-2`.*

`server.publish()` and WebSocket publish variants return `0` when a message is dropped or has no subscribers, `-1` when any subscriber has backpressure, and otherwise the byte count. Sending an in-memory `Blob` now produces a binary frame, while a file-backed blob must be read first.

## WebSocket handshake header overrides

*Batch: `1.2.22`.*

The client-side `WebSocket` constructor accepts a `headers` option that can override normally managed handshake headers such as `Host`, `Sec-WebSocket-Key`, and `Sec-WebSocket-Protocol`. Required headers are still generated when they are not supplied.

```ts
const ws = new WebSocket("ws://localhost:8080", {
  headers: {
    Host: "custom-host.example.com",
    "Sec-WebSocket-Protocol": "chat, superchat",
  },
});
```

## WebSocket subprotocol negotiation

*Batch: `1.2.22`.*

The WebSocket client sends requested subprotocols, exposes the server's valid selection through `protocol`, and rejects invalid negotiation responses or a missing selection when one is required.

```ts
const ws = new WebSocket("ws://localhost:3000", ["chat", "superchat"]);
ws.addEventListener("open", () => console.log(ws.protocol));
```

## WebSocket subscription inspection

*Batch: `1.3.2`.*

`ServerWebSocket.subscriptions` returns a de-duplicated array of the connection's current pub/sub topics. It reflects `subscribe()` and `unsubscribe()` calls and becomes an empty array after the socket closes.

```ts
ws.subscribe("chat");
console.log(ws.subscriptions); // ["chat"]
```

## WebSocket upgrades in explicit routes

*Batch: `1.2.5`.*

Specific `Bun.serve()` route handlers can now upgrade WebSocket connections; upgrades are no longer restricted to the catch-all route.

```ts
Bun.serve({
  routes: {
    "/chat": (req, server) =>
      server.upgrade(req)
        ? undefined
        : new Response("WebSocket required", { status: 400 }),
  },
  websocket: { message: (ws, message) => ws.send(message) },
});
```

## WebSockets over Unix domain sockets

*Batch: `1.3.13`.*

The `WebSocket` client accepts `ws+unix://` and TLS-enabled `wss+unix://` URLs; append `:<request-path>` after the socket path when the handshake needs a non-root path. Unix-socket connections default `Host` to `localhost`, bypass configured proxies, and can perform a full TLS handshake.

```ts
const ws = new WebSocket("ws+unix:///tmp/app.sock:/api/stream?x=1");
```
