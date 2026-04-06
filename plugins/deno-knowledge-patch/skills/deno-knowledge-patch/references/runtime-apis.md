# Runtime APIs

## `Deno.spawn()` Subprocess APIs (2.7+, unstable)

Convenience shorthands for `Deno.Command`. Three variants:
```ts
const child = Deno.spawn("deno", ["fmt", "--check"], { stdout: "inherit" });
const output = await Deno.spawnAndWait("git", ["status"]);
const result = Deno.spawnAndWaitSync("echo", ["done"]);
```

## `FsFile.tryLock()` (2.7+)

Non-blocking file lock — returns boolean instead of blocking:
```ts
const file = await Deno.open("data.db", { read: true, write: true });
if (await file.tryLock(true)) {
  await file.write(data);
  await file.unlock();
}
```

## Brotli in CompressionStream/DecompressionStream (2.7+)

`"brotli"` format now supported alongside `"gzip"` and `"deflate"`:
```ts
const stream = new CompressionStream("brotli");
```

## SHA3 in `crypto.subtle` (2.7+)

SHA3-256, SHA3-384, SHA3-512 supported for RSA-OAEP `generateKey`/`encrypt`/`decrypt`.

## OpenTelemetry

### Built-in (2.2+, stable since 2.4)

Auto-instruments `console.log`, `Deno.serve`, `fetch` for logs, metrics, traces:
```bash
OTEL_DENO=1 deno --allow-net server.ts
```
Exports to any OTLP endpoint. Custom instrumentation via `npm:@opentelemetry/api`.

Previously required `--unstable-otel` (2.2–2.3), now stable with just `OTEL_DENO=1` (2.4+).

## ChildProcess Stdio Convenience Methods (2.5+)

`Deno.ChildProcess` stdout/stderr streams now have `Response`-like methods:
```ts
const sub = new Deno.Command("cat", { args: ["file"], stdout: "piped" }).spawn();
const text = await sub.stdout.text();   // also: .json(), .bytes(), .arrayBuffer()
```

## WebSocket Custom Headers (2.5+)

```ts
const ws = new WebSocket("wss://api.example.com/socket", {
  headers: new Headers({ "Authorization": `Bearer ${token}` }),
});
```
Server-side only (not in browsers).

## QUIC and WebTransport (2.2+, unstable)

New APIs behind `--unstable-net`: `Deno.QuicEndpoint`, `Deno.upgradeWebTransport`, and `WebTransport` client support.

## `deno compile --self-extracting` (2.7+)

Extracts embedded files to disk at runtime — enables native addons in compiled binaries:
```bash
deno compile --self-extracting -A main.ts -o my-app
```
