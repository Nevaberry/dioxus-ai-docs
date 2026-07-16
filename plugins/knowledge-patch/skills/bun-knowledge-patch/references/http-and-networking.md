# HTTP and networking

Use this reference for servers, routing, cookies, WebSockets, fetch, proxies, protocols, TLS, and socket APIs.

Entries are grouped by developer task. When entries describe evolving behavior, the later attribution supersedes earlier defaults or limitations.

## Serving, routing, and response behavior

### Static server routes *(1.2-guide)*

`Bun.serve({ static })` maps paths directly to cached `Response` objects before the dynamic `fetch` handler. `server.reload({ static: ... })` replaces the route table when generated responses need refreshing.

```ts
const server = Bun.serve({
  static: { "/health": new Response("ok") },
  fetch: () => new Response("dynamic"),
});
```

### Graceful server shutdown *(1.2-guide)*

`server.stop()` now returns a `Promise<void>` that resolves after in-flight HTTP connections close, so shutdown can be awaited.

### Built-in HTTP routing *(since 1.2.3)*

`Bun.serve()` renames its `static` option to `routes`, whose values may be imported HTML, handlers with typed `req.params`, or method-specific handler maps. Supplying routes makes `fetch` optional.

```ts
Bun.serve({
  routes: {
    "/api/users/:id": req => Response.json({ id: req.params.id }),
  },
});
```

### Callback-based global catch-all routes *(since 1.2.6)*

`Bun.serve()` routes can now use a callback handler for the global `/*` catch-all, rather than requiring a static `Response` value.

```ts
Bun.serve({
  routes: { "/*": () => new Response("Global catch-all") },
});
```

### Method-specific static and HTML routes *(since 1.2.14)*

`Bun.serve({ routes })` can now restrict static `Response` values and imported HTML routes to particular HTTP methods. Method-specific routes also take precedence over the global `/*` route.

### File-backed server routes *(since 1.2.16)*

`Bun.serve({ routes })` now accepts a `Bun.file()` value directly, serving the file without manually reading or buffering it.

```ts
Bun.serve({
  routes: { "/report.pdf": Bun.file("./report.pdf") },
});
```

### Automatic static-route ETags *(since 1.2.20)*

Static `Response` routes in `Bun.serve({ routes })` now receive an `ETag` automatically. A request with a matching `If-None-Match` is answered with `304 Not Modified` without application code handling the conditional request.

### Automatic byte ranges for file responses *(since 1.3.13)*

`Bun.serve()` automatically handles a `Range: bytes=...` header when a static or dynamic handler returns a whole-file `200` response, producing `206` with `Content-Range` or `416` for an invalid range. Suffix and open-ended ranges are supported; multi-range requests fall back to the full response.

```ts
Bun.serve({
  routes: { "/video.mp4": new Response(Bun.file("./video.mp4")) },
});
```

## Cookies and request security

### CSRF token helpers *(since 1.2.5)*

`Bun.CSRF.generate` and `Bun.CSRF.verify` are built-in helpers for generating and verifying XSRF/CSRF tokens.

### Built-in cookie APIs *(since 1.2.7)*

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

### Cookies during WebSocket upgrades *(since 1.3.1)*

Cookies set with `req.cookies.set()` before `server.upgrade()` are now included as `Set-Cookie` headers on the `101 Switching Protocols` response, including when custom upgrade headers are supplied.

## WebSockets

### WebSocket classes from `node:http` *(since 1.2.2)*

`node:http` now re-exports the global `WebSocket`, `CloseEvent`, and `MessageEvent` classes.

```js
const { WebSocket, CloseEvent, MessageEvent } = require("node:http");
```

### WebSocket upgrades in explicit routes *(since 1.2.5)*

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

### Automatic WebSocket client compression *(since 1.2.18)*

The built-in WebSocket client now enables and negotiates `permessage-deflate` compression by default when the server supports it. After the connection opens, `webSocket.extensions` reports the negotiated extension.

### Fetch and WebSocket compatibility *(since 1.2.19)*

A `Request` now retains its `redirect` option, so `fetch(new Request(url, { redirect: "manual" }))` does not follow redirects. Accessing the body of affected `FormData` or stream-backed requests preserves `Content-Type`, `fetch()` permits an explicit `Connection` header, and WebSocket `error` events now carry an `Error` object rather than only a string.

### WebSocket subprotocol negotiation *(since 1.2.22)*

The WebSocket client sends requested subprotocols, exposes the server's valid selection through `protocol`, and rejects invalid negotiation responses or a missing selection when one is required.

```ts
const ws = new WebSocket("ws://localhost:3000", ["chat", "superchat"]);
ws.addEventListener("open", () => console.log(ws.protocol));
```

### WebSocket handshake header overrides *(since 1.2.22)*

The client-side `WebSocket` constructor accepts a `headers` option that can override normally managed handshake headers such as `Host`, `Sec-WebSocket-Key`, and `Sec-WebSocket-Protocol`. Required headers are still generated when they are not supplied.

```ts
const ws = new WebSocket("ws://localhost:8080", {
  headers: {
    Host: "custom-host.example.com",
    "Sec-WebSocket-Protocol": "chat, superchat",
  },
});
```

### WebSocket subscription inspection *(since 1.3.2)*

`ServerWebSocket.subscriptions` returns a de-duplicated array of the connection's current pub/sub topics. It reflects `subscribe()` and `unsubscribe()` calls and becomes an empty array after the socket closes.

```ts
ws.subscribe("chat");
console.log(ws.subscriptions); // ["chat"]
```

### WebSocket connections through proxies *(since 1.3.6)*

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

### Credentials in WebSocket URLs *(since 1.3.7)*

Credentials embedded in a target URL such as `ws://user:pass@example.com/socket` are sent as a Basic `Authorization` header during the upgrade. An explicitly supplied `Authorization` header takes precedence.

### WebSockets over Unix domain sockets *(since 1.3.13)*

The `WebSocket` client accepts `ws+unix://` and TLS-enabled `wss+unix://` URLs; append `:<request-path>` after the socket path when the handshake needs a non-root path. Unix-socket connections default `Host` to `localhost`, bypass configured proxies, and can perform a full TLS handshake.

```ts
const ws = new WebSocket("ws+unix:///tmp/app.sock:/api/stream?x=1");
```

## Fetch, proxies, and outbound requests

### Runtime-wide fetch user agent *(since 1.2.21)*

The `--user-agent` runtime flag overrides the `User-Agent` header for every `fetch()` request made by the application.

```sh
bun --user-agent "MyApp/1.0" app.js
```

### Custom proxy headers in `fetch()` *(since 1.3.4)*

The `proxy` option now accepts `{ url, headers }`; these headers are sent in HTTPS `CONNECT` requests and direct HTTP proxy requests. An explicit `Proxy-Authorization` header overrides credentials embedded in the proxy URL.

```ts
await fetch("https://example.com/data", {
  proxy: {
    url: "http://proxy.example.com:8080",
    headers: { "Proxy-Authorization": "Bearer token" },
  },
});
```

### URL objects as fetch proxies *(since 1.3.5)*

The `fetch()` `proxy` option accepts a `URL` instance directly instead of mistaking it for the `{ url, headers }` object form.

```ts
await fetch("https://example.com/data", {
  proxy: new URL("http://proxy.example.com:8080"),
});
```

### Outbound HTTP header casing *(since 1.3.7)*

`fetch()` and `node:https` now preserve the spelling of request header names instead of lowercasing them, matching Node.js and supporting services that incorrectly require exact casing.

### `NO_PROXY` with explicit proxies *(since 1.3.9)*

`fetch()` and `WebSocket` now honor `NO_PROXY` even when their `proxy` option is supplied explicitly, so matching destinations bypass that proxy.

```ts
// With NO_PROXY=localhost, this connects directly.
await fetch("http://localhost:3000/api", {
  proxy: "http://proxy.example:8080",
});
```

### Runtime proxy environment changes *(since 1.3.12)*

Changes to `process.env.HTTP_PROXY`, `HTTPS_PROXY`, or `NO_PROXY`, including their lowercase forms, now affect the next `fetch()` instead of proxy configuration being fixed at process startup.

### Experimental HTTP/2 and HTTP/3 `fetch()` *(since 1.3.14)*

The Bun-specific `RequestInit.protocol` can force `"http1.1"`/`"h1"`, `"http2"`/`"h2"`, or `"http3"`/`"h3"`; forced HTTP/2 rejects with `HTTP2Unsupported` when unavailable, while HTTP/3 remains an early preview. `--experimental-http2-fetch` enables multiplexed HTTP/2 negotiation globally, while `--experimental-http3-fetch` enables per-origin upgrades after an `Alt-Svc: h3` response; HTTP/2 proxies, Unix sockets, and h2c are not supported.

```ts
await fetch("https://example.com", { protocol: "http2" });
await fetch("https://example.com", { protocol: "http3" });
```

## HTTP protocols and Node-compatible clients

### HSTS headers behind TLS proxies *(since 1.2.5)*

`Bun.serve()` and `node:http` no longer remove `Strict-Transport-Security` from responses sent over backend HTTP, allowing the header to survive when a reverse proxy terminates HTTPS.

### Node HTTP body-write rejection *(since 1.2.10)*

`node:http` now implements `rejectNonStandardBodyWrites` consistently with Node.js. When it is `true`, writing a response body for a `HEAD` request throws; when it is `false`, `undefined`, or omitted, the write is ignored.

```js
import http from "node:http";

http.createServer({ rejectNonStandardBodyWrites: true }, (req, res) => {
  if (req.method === "HEAD") res.write("body"); // throws
});
```

### HTTP/2 server and client controls *(since 1.2.14)*

`node:http2` servers now accept `maxSendHeaderBlockLength` to cap a single outgoing header block, and client sessions support `setNextStreamID()`.

```js
import http2 from "node:http2";
const server = http2.createServer({
  maxSendHeaderBlockLength: 1024 * 1024,
});
```

### Node HTTP parser binding *(since 1.2.16)*

For packages that depend on Node's internal HTTP parser surface, Bun now exposes `process.binding("http_parser").HTTPParser` and also exports `HTTPParser` from `node:_http_common`.

```js
const { HTTPParser } = process.binding("http_parser");
const parser = new HTTPParser();
parser.initialize(HTTPParser.REQUEST, {});
parser.execute(Buffer.from("GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"));
```

### HTTP client compatibility *(since 1.2.18)*

An HTTP/2 client now emits `remoteSettings` even when the server sends an empty `SETTINGS` frame to select defaults, preventing consumers such as `grpc-js` from waiting indefinitely. Calling `flushHeaders()` on a `node:http` client request also no longer prevents its request body from being sent.

### Closing idle HTTP connections *(since 1.2.22)*

Node-compatible HTTP servers implement `closeIdleConnections()`, allowing graceful shutdown to immediately drop idle keep-alive sockets while active requests finish.

```ts
server.close();
server.closeIdleConnections();
```

### Node HTTP keep-alive pooling *(since 1.3.4)*

`node:http` agents configured with `{ keepAlive: true }` now reuse pooled connections across requests. Bun also handles `Connection: keep-alive` headers case-insensitively, matching HTTP header semantics.

### Increased HTTP header count *(since 1.3.7)*

The maximum number of request or response headers increased from 100 to 200.

### HTTP/2 handoff from `net.Server` *(since 1.3.9)*

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

### Experimental HTTP/3 servers *(since 1.3.14)*

`Bun.serve({ tls, http3: true })` binds TCP for HTTP/1.1 and HTTP/2 plus UDP for HTTP/3 on the same port, reuses the same handlers, and advertises the QUIC endpoint with `Alt-Svc`. This is explicitly not production-ready yet and does not support WebSockets over HTTP/3, 0-RTT, trailers, or `Expect: 100-continue`.

```ts
Bun.serve({
  port: 443,
  tls: { cert, key },
  http3: true,
  fetch: () => new Response("hello"),
});
```

### HTTP and HTTPS client caveats *(nodejs-compatibility)*

Although `node:http` is listed as fully implemented, outgoing client request bodies are buffered rather than streamed. `node:https` APIs are implemented, but `Agent` is not always used, so code whose behavior depends on an agent is not fully compatible.

## TCP, UDP, DNS, and Unix sockets

### Native UDP sockets *(1.2-guide)*

`Bun.udpSocket()` is the Bun-native alternative to `node:dgram`; its `socket.data` callback receives datagrams, `send()` transmits one, and `sendMany()` batches multiple datagrams into one syscall. A `socket.drain` callback signals that operating-system backpressure has cleared.

### Node-compatible socket addresses *(since 1.2.4)*

`node:net` now exports `SocketAddress`; `SocketAddress.parse()` parses an IP endpoint and exposes its `family`, `address`, and `port`.

```ts
import { SocketAddress } from "node:net";

const address = SocketAddress.parse("[::1]:1234");
console.log(address.family, address.address, address.port);
```

### Socket error objects *(since 1.2.4)*

`node:net` socket `"error"` handlers now always receive JavaScript `Error` instances rather than leaked engine-internal exception objects, so `error instanceof Error` is reliable.

### Abortable `node:net` servers *(since 1.2.5)*

`net.Server.listen()` accepts an `AbortSignal`; aborting it closes the server, while a signal that is already aborted closes it immediately.

```js
import { createServer } from "node:net";

const controller = new AbortController();
const server = createServer();
server.listen({ port: 3000, signal: controller.signal });
controller.abort();
```

### Expanded `Bun.connect()` socket addresses *(since 1.2.9)*

Sockets passed to `Bun.connect()` handlers now expose `localAddress`, `localFamily`, `remoteFamily`, and `remotePort`, matching the same-named `node:net.Socket` properties; `localPort` and `remoteAddress` remain available.

### `TLSSocket.allowHalfOpen` compatibility *(since 1.2.11)*

When `TLSSocket` wraps a `net.Socket` or `stream.Duplex`, an `allowHalfOpen: true` option is ignored and the resulting property is `false`, matching Node.js.

```js
import { Socket } from "node:net";
import { TLSSocket } from "node:tls";

const socket = new TLSSocket(new Socket(), { allowHalfOpen: true });
console.log(socket.allowHalfOpen); // false
```

### `node:net` block lists *(since 1.2.12)*

`node:net` now implements `BlockList` for matching individual IP addresses, address ranges, and subnets.

```js
import { BlockList } from "node:net";

const blocked = new BlockList();
blocked.addRange("10.0.0.1", "10.0.0.10");
blocked.addSubnet("8.8.8.8", 24);
blocked.check("8.8.8.9"); // true
```

### String ports in `net.Server.listen()` *(since 1.2.13)*

Node-compatible networking now coerces a numeric string passed as the port to a number, so `server.listen("3000")` listens on TCP port 3000.

### `node:net` compatibility controls *(since 1.2.16)*

`node:net` now honors `server.maxConnections`, resolves hostnames through `dns.lookup()` in the Node-compatible path, and supports applying a `net.BlockList` to `net.Socket` and `net.Server`.

### `node:net` validation and rejection handling *(since 1.2.18)*

Non-string `host` or IPC `path` options now throw `ERR_INVALID_ARG_TYPE`; nonexistent IPC paths emit `ENOENT`, and a custom lookup returning a non-string address emits `ERR_INVALID_IP_ADDRESS`. With `events.captureRejections` enabled, a rejected async `net.Server` connection listener is emitted as an error on and destroys the incoming socket instead of becoming an unhandled rejection.

### IPv6 interface scope identifiers *(since 1.2.19)*

`os.networkInterfaces()` now exposes the Node-compatible IPv6 property `scopeid`; the previous `scope_id` property is no longer present.

### Node-compatible socket descriptors *(since 1.3.3)*

Sockets from `node:net` and `node:tls` now expose their file descriptor as `_handle.fd`, enabling packages that depend on this Node.js compatibility surface.

### Correct `Socket.reload()` shape *(since 1.3.9)*

The TypeScript signature for `Socket.reload()` now matches runtime behavior: the replacement handler must be wrapped in a `socket` property.

```js
function replaceSocketHandler(socket, handler) {
  socket.reload({ socket: handler });
}
```

### UDP socket compatibility changes *(since 1.3.11)*

`node:dgram` now supports `reusePort: true` on macOS and implicitly binds an unbound UDP socket when `send()` is first called there. UDP sockets also no longer enable `SO_REUSEADDR` by default, so pass `reuseAddr: true` explicitly when port reuse is intended.

### UDP errors and truncation metadata *(since 1.3.12)*

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

### Node-compatible Unix socket lifecycle *(since 1.3.12)*

`Bun.listen()`, `Bun.serve()`, and `net.Server` now throw `EADDRINUSE` instead of unlinking an existing Unix socket, and remove their own socket file when closed. Unix socket paths beyond macOS's normal 104-byte limit are also supported.

### Node DNS promise APIs *(since 1.3.12)*

`node:dns/promises` now exports `getDefaultResultOrder()` and `getServers()`; the former returns the configured `"ipv4first"`, `"ipv6first"`, or `"verbatim"` string. The callback-based `node:dns.getDefaultResultOrder()` now returns that string as well.

## TLS certificates and trust stores

### Runtime CA certificate bundles *(since 1.2.3)*

Bun now loads complete CA bundles from `NODE_EXTRA_CA_CERTS=/path/to/full/bundle.crt` for TLS connections, matching Node.js rather than requiring certificate-by-certificate configuration.

### Bundled CA certificate inspection *(since 1.2.17)*

`tls.getCACertificates()` returns Bun's bundled trusted root certificates as PEM strings. It does not yet include system-wide CA certificates.

```js
import { getCACertificates } from "node:tls";

const bundledRoots = getCACertificates();
```

### Operating-system CA roots *(since 1.2.23)*

`--use-system-ca` or `NODE_USE_SYSTEM_CA=1` adds the operating system's trusted roots to Bun's built-in Mozilla CA store, allowing TLS connections to corporate or locally installed authorities.

```sh
bun run --use-system-ca index.js
```

### System CA inspection and Windows trust stores *(since 1.3.14)*

`tls.getCACertificates("system")` now returns operating-system certificates without requiring `--use-system-ca`; that flag still controls whether system roots join the default trust set. On Windows, opting into system CAs now reads `ROOT`, `CA`, and `TrustedPeople` stores across user, machine, Group Policy, and enterprise locations, allowing locally cached intermediates to complete certificate chains.

```ts
import tls from "node:tls";
const systemCertificates = tls.getCACertificates("system");
```
