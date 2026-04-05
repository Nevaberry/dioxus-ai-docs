# Runtime APIs

## Temporal API (stable since 2.7)

`Temporal` no longer requires `--unstable-temporal`. Just use it directly.

```ts
const now = Temporal.Now.zonedDateTimeISO();
const date = Temporal.PlainDate.from("2026-01-15");
const duration = Temporal.Duration.from({ hours: 2, minutes: 30 });
```

## Deno.spawn() Convenience APIs (2.7+, unstable)

Simpler subprocess spawning — shorthand for `new Deno.Command(...).spawn()`:

```ts
const child = Deno.spawn("deno", ["fmt", "--check"], { stdout: "inherit" });
const output = await Deno.spawnAndWait("git", ["status"]); // returns CommandOutput
const result = Deno.spawnAndWaitSync("echo", ["done"]);    // sync variant
```

## FsFile.tryLock() (2.7+)

Non-blocking file lock — returns boolean instead of blocking:

```ts
const file = await Deno.open("data.db", { read: true, write: true });
if (await file.tryLock(true)) { // true = exclusive
  await file.write(data);
  await file.unlock();
}
```

## ChildProcess stdio Convenience Methods (2.5+)

`sub.stdout.text()`, `.json()`, `.bytes()`, `.arrayBuffer()` — no more `@std/streams` import needed.

## Importing Text and Bytes (2.4+, unstable)

Import non-JS files into the module graph with `--unstable-raw-imports`. Works with `deno bundle` and `deno compile`.

```ts
import message from "./hello.txt" with { type: "text" };    // string
import bytes from "./image.png" with { type: "bytes" };      // Uint8Array
```

## Wasm Source Phase Imports (2.6+)

Import a compiled `WebAssembly.Module` directly — no runtime fetch needed.

```ts
import source addModule from "./add.wasm";
const instance = WebAssembly.instantiate(addModule);
```

## Brotli in CompressionStream (2.7+)

`"brotli"` is now a valid format:

```ts
new CompressionStream("brotli");
new DecompressionStream("brotli");
```

## SHA3 in crypto.subtle (2.7+)

`SHA3-256`, `SHA3-384`, `SHA3-512` supported for RSA-OAEP `generateKey`/`encrypt`/`decrypt`.

## node:sqlite (2.2+)

`node:sqlite` module is available:

```ts
import { DatabaseSync } from "node:sqlite";
```

## Node Globals Available Everywhere (2.4+)

`Buffer`, `global`, `setImmediate`, and `clearImmediate` are now available in user code without `--unstable-node-globals`.

## `@types/node` Included by Default (2.6+)

Node.js type declarations work automatically — no need to manually install `@types/node`.

## Deno.bench Options (2.2+)

Control exact iteration counts:

```ts
Deno.bench({ warmup: 1_000, n: 100_000 }, fn);
```
