# Networking, HTTP, and TLS

## TCP, UDP, DNS, and blocking

- In 23.1.0, networking supports `UV_TCP_REUSEPORT` and
  `UV_UDP_REUSEPORT` for TCP and UDP port reuse.
- In 23.4.0, `net.connect()` and `net.Server` accept `blockList`, allowing a
  `net.BlockList` to reject outbound destinations and inbound peers during
  connection setup. In 23.5.0, UDP sockets gain block-list support.
- In 24.5.0, `net.BlockList` can persist and manage rules in files. In 26.4.0,
  the API reaches release-candidate stability.
- In 23.9.0, `node:dns` can query and parse TLSA records.
- In 24.5.0, the DNS resolver can cap the maximum total query timeout.
- In 25.2.0, the default network-family autoselection timeout becomes 500 ms,
  so fallback between address families waits longer unless configured.
- In 26.4.0, `net.Socket.setKeepAlive()` supports `TCP_KEEPINTVL` and
  `TCP_KEEPCNT` in addition to the initial delay.
- In 26.4.0, `net.BoundSocket` can synchronously bind a TCP endpoint before
  later asynchronous work. In 26.7.0, it also supports synchronous connection
  and `AF_UNIX` paths.
- In 24.19.0, `node:dgram` sockets add synchronous `bindSync()` and
  `connectSync()`.
- In 26.7.0, TCP `Server` and `Socket` objects are transferable across worker
  threads, including TCP handle transfer on Windows.

## Core HTTP proxies

- In 24.0.0, `NODE_USE_ENV_PROXY=1` makes built-in `fetch()` use standard
  proxy environment variables.
- In 24.5.0, `http.request()`, `https.request()`, and their default global
  agents support environment proxies. Enable globally with
  `NODE_USE_ENV_PROXY=1` or `--use-env-proxy`; the agents read upper- and
  lowercase `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY`. Custom `http.Agent`
  and `https.Agent` instances accept `proxyEnv`.
- In 25.4.0, `http.setGlobalProxyFromEnv()` activates environment proxy
  handling for global core HTTP clients at runtime.
- In 24.17.0, tunnel errors redact proxy credentials.

## HTTP/1 requests and servers

- In 23.5.0, `http.request()` accepts `setDefaultHeaders`, allowing callers to
  control whether Node supplies default request headers.
- In 24.2.0, calling `node:http` classes without `new` is deprecated. Use
  documented factories or normal construction.
- In 24.6.0, an HTTP server's `keepAliveTimeoutBuffer` is added to
  `keepAliveTimeout` when calculating the socket timeout, reducing boundary-
  time resets.
- In 24.7.0, agents accept `agentKeepAliveTimeoutBuffer`, subtracting a buffer
  from the server-provided keep-alive lifetime before deciding a socket is
  reusable.
- In 24.9.0, `shouldUpgradeCallback(request)` on server creation decides which
  incoming requests enter upgrade handling before the `'upgrade'` listener.
- In 25.1.0, server creation accepts `optimizeEmptyRequests` for optimized
  requests with no body.
- In 25.5.0, `rawHeaders` respects `maxHeadersCount`.
- In 22.23.2, HTTP rejects requests exceeding the maximum header count. HTTPS
  agents distinguish object-array PFX values in agent keys so distinct client-
  certificate configurations do not share a key.
- In 24.18.0, `ServerResponse.writeInformation()` sends arbitrary 1xx
  responses. `writeEarlyHints()` validates auxiliary non-`link` headers as
  well as link values.
- In 26.4.0, `http.Server.closeIdleConnections()` also closes accepted sockets
  that have not yet received a request.
- In 24.19.0, the `httpValidation` option configures header-value validation
  without replacing Node's validation path.

## HTTP API removals and input validation

- In 24.0.0, private outgoing-message `_headers` and `_headersList` are
  removed.
- In 24.6.0, direct imports of private `_http_*` modules are documentation-
  deprecated; use public `node:http` and `node:https` APIs.
- In 25.0.0, `response.writeHeader()` is deprecated in favor of `writeHead()`.
  Falsy DNS lookup hostnames, IP-address TLS `servername` values, and invalid
  ports in the legacy URL API reach end-of-life and require explicit valid
  inputs. Imports of `_tls_common` and `_tls_wrap` are deprecated.
- In 26.0.0, `response.writeHeader()` is removed; use `writeHead()`.

## HTTP/2 operation

- In 23.0.0, HTTP/2 options expose nghttp2's stream-reset rate limiter for
  configuring how aggressively reset streams are limited.
- In 23.5.0, HTTP/2 server options accept `ALPNCallback` for application-
  defined ALPN selection.
- In 24.0.0, HTTP/2 servers track sessions for graceful shutdown, and
  `ClientHttp2Session.request()` accepts raw alternating name/value header
  arrays.
- In 24.2.0, HTTP/2 priority signaling is removed after nghttp2 removed the
  deprecated RFC 9113 feature. Obsolete `options.selectPadding` is also
  removed.
- In 24.6.0, raw-array requests populate `Http2Stream.sentHeaders`.
- In 24.7.0, `Http2Stream.respond()` accepts raw alternating response-header
  arrays.
- In 25.5.0, `initialWindowSize` is validated according to the protocol and
  out-of-range values can be rejected.
- In 24.17.0, HTTP/2 caps its origin set to prevent unbounded memory growth,
  and `http.Agent` prevents response-queue poisoning.
- In 24.14.0, the 24.14.1 release hardens HTTP/2 flow-control error handling.
- In 24.18.0, an HTTP/2 session emits `close` before its streams. Stream-close
  cleanup must account for an already closed session.

## HTTP instrumentation

- In 23.2.0, diagnostics channels expose `http.client.request.created` and
  `http.server.response.created`.
- In 24.1.0, HTTP/2 diagnostics add client-stream `created` and `start`.
- In 24.2.0, channels cover server-stream `created`, `start`, `error`, and
  `finish`, and client-stream `close`, `error`, and `finish`.
- In 24.3.0, `http2.server.stream.close` reports server-stream closure.
- In 24.4.0, Inspector network tools cover Undici. In 24.7.0, they gain initial
  WebSocket traffic support. In 24.8.0, they cover HTTP/2 client calls.
- In 25.2.0, inspector tooling covers HTTP response bodies and HTTP/2 request
  and response bodies, while diagnostics channels expose HTTP/2 client-stream
  request bodies.

## TLS certificates and errors

- In 23.10.0, `tls.getCACertificates()` exposes CA certificates available to
  TLS. See the crypto reference for trust-store revisions and replacement.
- In 24.9.0, `X509Certificate.signatureAlgorithm` exposes a certificate's
  signature algorithm.
- In 24.13.0, 24.13.1 gives `TLSSocket` a default error handler and routes
  exceptions from TLS callbacks through error handlers. Attach explicit error
  listeners for application logging or recovery.
- In 24.17.0, DNS and network APIs reject embedded-NUL hostnames. TLS
  normalizes hostnames for server identity checks, matches SNI contexts without
  case sensitivity, and binds reusable sessions to the authenticated host.
- In 26.4.0, TLS accepts `certificateCompression` and OpenSSL builds include
  compressed-certificate negotiation support. Exceptions from TLS event
  listeners pass through TLS error handlers.
- In 26.5.0, a TLS connection reports its negotiated group for diagnostics and
  policy checks.

## QUIC

- In 23.8.0, `module.builtinModules` omits `node:quic` while its feature flag is
  inactive.
- In 25.9.0, QUIC session-key options no longer accept WebCrypto `CryptoKey`
  values.
- In 26.4.0, `node:quic` adds `listEndpoints()`, and QUIC certificates are
  exposed as JavaScript `X509Certificate` objects rather than raw handles.
