# Server & Networking

## OpenTelemetry (stable since 2.4)

No longer requires `--unstable-otel`. Just set `OTEL_DENO=1`:

```bash
OTEL_DENO=1 deno --allow-net server.ts
```

Auto-instruments `console.log`, `Deno.serve`, and `fetch`. Use `npm:@opentelemetry/api` for custom spans/metrics.

### OpenTelemetry for Deno.cron (2.7+)

`Deno.cron` jobs are automatically instrumented with OTEL spans when `OTEL_DENO=1`.

### Initial Setup (2.2–2.3)

Before 2.4, required `--unstable-otel` flag:

```bash
OTEL_DENO=true deno run --unstable-otel --allow-net server.ts
```

## Deno.serve Enhancements

### `onListen` Callback (2.4+)

```ts
export default {
  fetch(req) { return new Response("Hello"); },
  onListen(addr) { console.log(`Started on ${addr.hostname}:${addr.port}`); },
} satisfies Deno.ServeDefaultExport;
```

### `tcpBacklog` Option (2.5+)

```ts
Deno.serve({ port: 4600, tcpBacklog: 4096 }, (_req) => new Response("hello"));
```

Default backlog increased to 511.

### `DENO_SERVE_ADDRESS` (2.3+)

Set default `host:port` for `deno serve` via the `DENO_SERVE_ADDRESS` environment variable.

## WebSocket Custom Headers (2.5+)

```ts
const ws = new WebSocket("wss://api.example.com/socket", {
  headers: new Headers({ "Authorization": `Bearer ${token}` }),
});
```

## Deno.HttpClient with Proxy (2.6+)

```ts
const client = new Deno.HttpClient({
  proxy: { url: new URL("http://proxy.example.com:8080") },
});
const ws = new WebSocket("wss://api.example.com/socket", { httpClient: client });
```

## QUIC and WebTransport (2.2+, unstable)

Requires `--unstable-net`. New `Deno.QuicEndpoint` for QUIC servers and `Deno.upgradeWebTransport(conn)` to upgrade QUIC connections to WebTransport.
