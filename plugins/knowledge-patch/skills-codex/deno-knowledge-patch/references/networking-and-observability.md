# Networking, Servers, and Observability

Use this reference for the following topic-specific compatibility details.

## Abortable and source-bound connections (2.3.0)

`Deno.connect()` accepts an abort signal, while custom HTTP clients accept `localAddress` to bind outbound `fetch` connections to a chosen local address.

```ts
const controller = new AbortController();
await Deno.connect({
  hostname: "example.com",
  port: 80,
  signal: controller.signal,
});
const client = Deno.createHttpClient({ localAddress: "192.0.2.10" });
```

## Brotli negotiation preference (2.1.0)

HTTP content negotiation now prefers Brotli when a request offers `gzip, deflate, br, zstd`, which can change the selected response encoding.

## Browser-opening server mode (2.3.0)

`deno serve --open` launches the served address in the browser when the server starts.

```sh
deno serve --open main.ts
```

## Built-in CPU profiles (2.8-guide)

`--cpu-prof` writes a V8 `.cpuprofile`; `--cpu-prof-flamegraph` adds an interactive SVG and `--cpu-prof-md` adds a terminal-friendly Markdown hot-function and call-tree report.

```sh
deno run --cpu-prof --cpu-prof-flamegraph --cpu-prof-md main.ts
```

## Cron OpenTelemetry spans (2.7-guide)

With Deno's OpenTelemetry integration enabled, every `Deno.cron` invocation is automatically traced with its job name and execution status.

## Custom `fetch` method casing (2.5.0)

`fetch` now uppercases only known HTTP methods. Extension methods retain the supplied casing instead of being rewritten, which matters because custom method tokens are case-sensitive.

## Custom WebSocket handshake headers (2.5-guide)

Deno's `WebSocket` constructor accepts a `headers` option for authentication, session state, or metadata during the opening handshake; this extension is not available in browsers.

```ts
const socket = new WebSocket("wss://api.example.com/socket", {
  headers: new Headers({
    Authorization: "Bearer token",
    "X-Custom": "value",
  }),
});
```

## Expanded OpenTelemetry integration (2.3-guide)

The built-in integration now records span events, propagates span context between services, auto-instruments requests made through `node:http`, and collects standard V8 runtime metrics. Custom events use the normal OpenTelemetry span API, for example `span.addEvent("cache_miss", { key })`.

## Experimental WebTransport and QUIC (2.2-guide)

Experimental `WebTransport`, `Deno.connectQuic`, and `Deno.QuicEndpoint` support requires `--unstable-net`; WebTransport endpoints require HTTPS. A QUIC listener can accept connections and pass them to `Deno.upgradeWebTransport()`, with bidirectional streams, unidirectional streams, and datagrams exposed as Web streams.

```ts
const endpoint = new Deno.QuicEndpoint({ hostname: "localhost", port: 8000 });
const listener = endpoint.listen({ cert, key, alpnProtocols: ["h3"] });
for await (const connection of listener) {
  const transport = await Deno.upgradeWebTransport(connection);
  await transport.ready;
}
```

## Happy Eyeballs connections (2.9-guide)

`Deno.connect()` and `Deno.connectTls()` use Happy Eyeballs v2 by default on dual-stack hosts; `autoSelectFamily: false` disables racing, while `autoSelectFamilyAttemptDelay` changes the default 250 ms stagger.

```ts
await Deno.connect({
  hostname: "example.com",
  port: 443,
  autoSelectFamilyAttemptDelay: 100,
});
```

## Incoming QUIC listener values (2.5.0)

The unstable `QuicListener` async iterator now yields `QuicIncoming`. Code that treated each yielded value as an established connection must update to the incoming-connection flow.

## Inspector network traffic (2.8-guide)

When an inspector flag is active, Chrome DevTools' Network panel and other CDP clients can inspect `fetch`, `node:http`, `node:https`, and WebSocket traffic, including headers, bodies, status, and timings.

```sh
deno run --inspect-wait --allow-net main.ts
```

## Integer signals and proxied WebSockets (2.6-guide)

`Deno.kill()` and child-process kill methods accept integer signals. A `WebSocket` can use a `Deno.HttpClient`, including one configured with a TCP proxy.

```ts
const client = new Deno.HttpClient({
  allowHost: true,
  proxy: { url: new URL("http://proxy.example.com:8080") },
});
const socket = new WebSocket("wss://api.example.com/socket", { httpClient: client });
```

## IPv6 hosts in `node:http` (2.7.0)

The Node HTTP compatibility layer now supports IPv6 host values.

## Language-server configuration behavior (2.1-guide)

Project-local `deno.json` formatting settings take precedence over editor settings. The language server also completes relative manifest dependencies, npm dependencies, and `@deno-types` directives.

## Language-server framework support (2.2-guide)

The language server now understands `compilerOptions.rootDirs` and `compilerOptions.types`, ambient imports, wildcard module augmentation, and npm `<reference types>` augmentation. It also completes `.wasm` imports, uses `node:` for Node built-in auto-imports, improves npm auto-imports, and formats SCSS, Sass, Less, SQL, Svelte, Vue, and other component files.

## Linux virtual sockets (2.3-guide)

Deno programs can now communicate through Linux virtual sockets (vsock), adding a Linux-specific transport option.

## Machine-readable and server output (2.0.0)

Every `--json` output now includes the Deno version, while `deno info` output no longer includes `emit` or `map`. The server's `Listening on` message is written to stderr instead of stdout.

## Native WebSockets from Node HTTP upgrades (2.8-guide)

`Deno.upgradeWebSocket()` can consume `node:http` upgrade events, allowing a Node-style HTTP server to hand a connection to Deno's native WebSocket implementation.

## Node cryptography and TLS (2.8.0)

New compatibility includes AES Key Wrap and Key Wrap with Padding ciphers, TLS server `ALPNCallback` and `SNICallback`, `tls.getCaCertificates()`, and encrypted PKCS#8 DER import and export.

## Node HTTP compatibility (2.5.0)

`node:http` now implements `ServerResponse.setHeaders()` and honors `signal` in `server.listen()` options. Successful HTTPS requests also mark their socket as authorized, so code inspecting `socket.authorized` sees Node-compatible state.

## Node networking behavior (2.8.0)

An unspecified host in `Server.listen()` now binds the IPv6 wildcard and enables dual-stack operation. Node compatibility also adds abstract Unix-socket binds, `fs.watch` `encoding` and `signal` options, the `SocketAddress` class, and HTTP server `shouldUpgradeCallback` support.

## OpenTelemetry auto-instrumentation (2.2-guide)

The opt-in integration now auto-instruments `console.log`, `Deno.serve`, and `fetch`, and can export logs, metrics, and traces to an OTLP endpoint; custom spans and metrics use `npm:@opentelemetry/api`. It remains unstable and requires both the environment opt-in and flag.

```sh
OTEL_DENO=true deno run --unstable-otel --allow-net server.ts
```

## OpenTelemetry sampling and limits (2.9-guide)

The built-in integration honors `OTEL_TRACES_SAMPLER` plus `OTEL_TRACES_SAMPLER_ARG` for head sampling and parent-propagated decisions. `OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT` and `OTEL_SPAN_EVENT_COUNT_LIMIT` cap attributes and events at 128 by default, and auto-instrumentation now traces `node:http2` clients and servers.

## OpenTelemetry trace exporting (2.1.0)

Deno adds OpenTelemetry tracing and exporting, but the separately introduced public OTEL trace API was removed in the same release. Integrations must not depend on that development-time public API.

## OpenTelemetry trace links (2.2.0)

The unstable OpenTelemetry integration now supports trace links, allowing spans to record related traces outside their parent-child relationship.

## Opt-in server compression (2.9-guide)

`Deno.serve()` no longer compresses response bodies automatically; enable it per server with `automaticCompression: true` or process-wide with `DENO_SERVE_AUTOMATIC_COMPRESSION=1`.

```ts
Deno.serve(
  { automaticCompression: true },
  () => new Response("hello"),
);
```

## Scoped IPv6 connections (2.6.0)

`Deno.connect()` accepts an IPv6 zone identifier in the hostname, enabling connections to scoped addresses such as link-local interfaces.

```ts
await Deno.connect({ hostname: "fe80::1%eth0", port: 8080 });
```

## Server and connection shutdown (2.9.0)

Shutting down `Deno.serve()` now closes active WebSockets, and closing TCP, Unix, or vsock streams cancels their in-flight reads. The `deno serve` command also exits cleanly on `SIGTERM` and `SIGINT`.

## Socket transports from environment configuration (2.5-guide)

Proxy environment-variable parsing for `fetch` now accepts Unix-socket and vsock transports. Built-in OpenTelemetry exporting can also use vsock transport.

## Socket-backed `fetch` (2.4-guide)

`fetch` can communicate over Unix and Linux vsock sockets through a custom `Deno.HttpClient`; a Unix client uses `proxy: { transport: "unix", path }`, while vsock uses `proxy: { transport: "vsock", cid, port }`.

```ts
const client = Deno.createHttpClient({
  proxy: { transport: "unix", path: "/run/service.sock" },
});
await fetch("http://localhost/ping", { client });
```

## Stable built-in OpenTelemetry (2.4-guide)

Built-in OpenTelemetry no longer needs `--unstable-otel`, but instrumentation remains opt-in through `OTEL_DENO` because it consumes additional resources.

```sh
OTEL_DENO=1 deno run --allow-net server.ts
```

## TCP listener backlog (2.5-guide)

`tcpBacklog` sets the maximum queued incoming TCP connections for `Deno.listen()`, `Deno.listenTls()`, and `Deno.serve()`. The default backlog is now 511.

```ts
Deno.serve({ port: 4600, tcpBacklog: 4096 }, () => new Response("hello"));
```

## TLS and window-surface option changes (2.0.0)

`Deno.ConnectTlsOptions` no longer has `certChain`, `certFile`, or `privateKey`, and `Deno.ListenTlsOptions` no longer has `certChain`, `certFile`, or `keyFile`. WebGPU window `width` and `height` options now belong on the `UnsafeWindowSurface` constructor.

## TLS hostname-verification opt-out (2.5-guide)

TLS connections can disable hostname verification for development and testing with self-signed or nonstandard certificate configurations.

## TLS session-key logging (2.7-guide)

`SSLKEYLOGFILE` writes TLS session keys to a file so captured traffic can be decrypted for debugging with tools such as Wireshark.

```sh
SSLKEYLOGFILE=./keys.log deno run --allow-net main.ts
```

## UDP listener default (2.8-guide)

`Deno.listenDatagram()` now defaults its hostname to `0.0.0.0`, matching `Deno.listen()` and changing which interfaces an omitted hostname binds.

## User-agent hints and fetch priority (2.9-guide)

`navigator.userAgentData` is available in window and worker scopes, including `getHighEntropyValues()`. `RequestInit.priority` accepts and validates the standard `"auto"`, `"high"`, and `"low"` values.

```ts
const details = await navigator.userAgentData.getHighEntropyValues([
  "architecture",
]);
await fetch("https://example.com", { priority: "high" });
```

## Watch trigger logging (2.1.0)

Watch and HMR logs now identify the file whose change triggered the reload or restart.

## WebSocket error payloads (2.1.0)

WebSocket `ErrorEvent` objects now initialize their `error` attribute, so error handlers can inspect `event.error` reliably.
