# Runtime and Web APIs

Use Deno runtime APIs, Web APIs, WebAssembly, cryptography, files, subprocesses, and platform primitives.

## Abortable subprocess output (2.8.0)

`Deno.Command.output()` now respects its command's `AbortSignal`, so aborting a command also cancels an in-progress buffered-output operation.

## Additional cryptography and feature detection (2.9-guide)

New algorithms include `"ChaCha20-Poly1305"`, SHAKE and cSHAKE, TurboSHAKE, KangarooTwelve, KMAC, and Argon2 key derivation. Synchronous `SubtleCrypto.supports()` reports whether a method and algorithm combination is available before use.

```ts
SubtleCrypto.supports("encapsulateKey", "ML-KEM-768");
SubtleCrypto.supports("sign", "ML-DSA-65");
```

## Additional Web API surface (2.8-guide)

Web Crypto digesting accepts `SHA3-256`, `SHA3-384`, and `SHA3-512`, and P-521 works for signing, verification, and ECDH derivation. The Cache API now implements `CacheStorage.keys()` and `Cache.keys()`.

## Brotli compression streams (2.7-guide)

`CompressionStream` and `DecompressionStream` accept `"brotli"` in addition to `"gzip"` and `"deflate"`.

```ts
const compressed = body.pipeThrough(new CompressionStream("brotli"));
```

## Brotli negotiation preference (2.1.0)

HTTP content negotiation now prefers Brotli when a request offers `gzip, deflate, br, zstd`, which can change the selected response encoding.

## Concrete `ArrayBuffer` response types (2.5.0)

`Response.body`, `Response.bytes()`, and `TextEncoder.encode()` now type their emitted `Uint8Array` values with `ArrayBuffer` backing. Code using generic typed arrays can therefore retain `Uint8Array<ArrayBuffer>` instead of widening these results to `ArrayBufferLike`.

```ts
const encoded: Uint8Array<ArrayBuffer> = new TextEncoder().encode("data");
const bytes: Uint8Array<ArrayBuffer> = await new Response("data").bytes();
```

## Continued Web event dispatch after exceptions (2.6.0)

When an event listener throws, dispatch now reports the exception and continues invoking the remaining listeners instead of stopping the dispatch.

## Correct HKDF results for typed-array views (2.5.0)

`node:crypto`'s `hkdfSync()` now produces correct output when passed typed-array inputs other than `Uint8Array`. Cryptographic code should no longer preserve workarounds for the earlier incorrect result.

## Cryptographic key support (2.0.0)

The crypto implementation can import and export P-521 keys and supports X448.

## CSS module imports (2.9-guide)

CSS files can be imported as constructable `CSSStyleSheet` values with a `type: "css"` import attribute, allowing browser-oriented modules to load and type-check without a bundler. This remains gated by `--unstable-raw-imports` in 2.9.

```ts
import sheet from "./styles.css" with { type: "css" };
document.adoptedStyleSheets = [sheet];
```

## Data URL preloads (2.5.0)

`--preload` no longer splits a data URL at its comma, so an inline startup module can be passed directly.

```sh
deno run --preload='data:text/javascript,globalThis.ready=true' main.ts
```

## Deferred module evaluation (2.8-guide)

Deno supports static `import defer`, which fetches and parses a module immediately but waits to run its top-level code until an export is first accessed. `import.defer()` provides the same semantics for dynamic imports.

```ts
import defer * as optional from "./optional.ts";
const dynamic = await import.defer("./other.ts");
console.log(optional.value, dynamic.value);
```

## Deno-native CPU usage (2.2.0)

`Deno.cpuUsage()` is available alongside `process.cpuUsage()`, allowing Deno-native code to query process CPU consumption without importing `node:process`.

```ts
const usage = Deno.cpuUsage();
```

## Detached Deno commands (2.4.0)

`Deno.Command` accepts `detached: true`, allowing a spawned child process to run independently of its parent.

```ts
const child = new Deno.Command("worker", { detached: true }).spawn();
```

## Direct, typed Wasm imports (2.1-guide)

Deno can import a `.wasm` file as a normal module without read or network permission; Wasm exports participate in type checking, and a Wasm module may itself import JavaScript or TypeScript modules.

```ts
import { add } from "./add.wasm";
console.log(add(1, 2));
```

## Error API typings (2.3.0)

Runtime types now expose `Error.isError` and `ErrorConstructor.stackTraceLimit`, so TypeScript code can use those V8 APIs without local type augmentation.

## FFI and runtime property adjustments (2.0.0)

The deprecated `UnsafeFnPointer` constructor signature taking an untyped `Deno.PointerObject` is removed. `globalThis.location` is configurable, and `Deno.FsWatcher.prototype.return()` is no longer deprecated.

## File change-time metadata (2.1.0)

Results from Deno's stat APIs now include `ctime`, and the Node compatibility layer uses that value too.

```ts
const { ctime } = await Deno.stat("data.txt");
console.log(ctime);
```

## GIF and WebP bitmap decoding (2.7-guide)

`createImageBitmap()` can now decode GIF and WebP blobs in addition to PNG, JPEG, and BMP.

## Half-precision typed arrays (2.6.0)

Deno now supports the `Float16Array` built-in for half-precision numeric storage.

```ts
const samples = new Float16Array([0.5, 1, 1.5]);
```

## Headless canvas and geometry globals (2.8-guide)

Stable `OffscreenCanvas` supports `"bitmaprenderer"` and `"webgpu"` contexts plus `convertToBlob()` and worker transfer; 2D and WebGL contexts are not implemented. `DOMPoint`, `DOMRect`, `DOMQuad`, `DOMMatrix`, and their readonly variants are available behind `--unstable-webgpu`.

```ts
const canvas = new OffscreenCanvas(640, 480);
const context = canvas.getContext("bitmaprenderer");
const point = new DOMPoint(10, 0).matrixTransform(new DOMMatrix().scale(2));
```

## Ignored filesystem-watch paths (2.9-guide)

`Deno.watchFs()` accepts an `ignore` list for paths such as VCS metadata and generated output.

```ts
const watcher = Deno.watchFs(".", { ignore: [".git", "build"] });
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

## Linux pressure files and read permission (2.7.0)

On Linux, `/proc/pressure/*` files are now accessible under `--allow-read`, allowing process-pressure monitoring without a permission workaround.

## Native JavaScript explicit resource management (2.3-guide)

V8 now supports `using` natively in JavaScript, so disposable Deno resources such as files are closed automatically when their scope exits without a manual `try`/`finally`.

```js
{
  using file = Deno.createSync("data.txt");
  file.writeSync(new TextEncoder().encode("data\n"));
}
```

## Non-blocking file locks (2.7-guide)

`FsFile.tryLock(exclusive?)` returns immediately with whether it acquired the lock, unlike blocking `lock()`.

```ts
const file = await Deno.open("data.db", { read: true, write: true });
if (await file.tryLock(true)) {
  try {
    await file.write(data);
  } finally {
    await file.unlock();
  }
}
```

## Platform identification (2.7-guide)

`navigator.platform` is now available and returns values such as `"MacIntel"`, `"Win32"`, or `"Linux x86_64"` for web-library compatibility.

## Post-quantum Web Cryptography (2.9-guide)

Web Crypto adds ML-KEM 512/768/1024 key encapsulation, ML-DSA 44/65/87 signatures with JWK import/export, and all twelve SLH-DSA signature parameter sets. ML-KEM is exposed through new `encapsulateKey`, `encapsulateBits`, `decapsulateKey`, and `decapsulateBits` operations.

```ts
const keys = await crypto.subtle.generateKey(
  { name: "ML-KEM-768" },
  true,
  ["encapsulateBits", "decapsulateBits"],
);
const { ciphertext, sharedKey } = await crypto.subtle.encapsulateBits(
  { name: "ML-KEM-768" },
  keys.publicKey,
);
const recovered = await crypto.subtle.decapsulateBits(
  { name: "ML-KEM-768" },
  keys.privateKey,
  ciphertext,
);
```

## Preloaded startup modules (2.4-guide)

`--preload` executes a module before the main program, allowing it to install globals or perform other environment setup. The flag is supported by `deno run`, `deno test`, and `deno bench`.

```sh
deno run --preload setup.ts main.ts
```

## Response-style subprocess output (2.5-guide)

Piped `Deno.ChildProcess` output streams now provide `arrayBuffer()`, `bytes()`, `json()`, and `text()` convenience methods, avoiding a separate stream conversion helper.

```ts
const child = new Deno.Command("cat", {
  args: ["hello.txt"],
  stdout: "piped",
}).spawn();
const output = await child.stdout.text();
```

## Self-signalling permission (2.9-guide)

`process.kill(process.pid, signal)` no longer requires `--allow-run`; signalling any other process still does.

## SHA-3 RSA-OAEP keys (2.7-guide)

Web Crypto RSA-OAEP operations can use `SHA3-256`, `SHA3-384`, or `SHA3-512` as the key's hash algorithm.

```ts
const algorithm = {
  name: "RSA-OAEP",
  modulusLength: 2048,
  publicExponent: new Uint8Array([1, 0, 1]),
  hash: "SHA3-256",
};
const keys = await crypto.subtle.generateKey(
  algorithm,
  true,
  ["encrypt", "decrypt"],
);
```

## Stable Temporal API (2.7-guide)

`Temporal` is now stable and no longer requires `--unstable-temporal`.

```ts
const meeting = Temporal.ZonedDateTime.from(
  "2026-03-15T14:30[America/New_York]",
);
const inTokyo = meeting.withTimeZone("Asia/Tokyo");
```

## Stable text imports (2.8-guide)

Text import attributes no longer require `--unstable-raw-imports`; byte imports remain unstable.

```ts
import template from "./template.txt" with { type: "text" };
```

## Stable unsafe-prototype flag (2.9-guide)

`--unsafe-proto` is the stable alias for `--unstable-unsafe-proto`, and crashes after access to the disabled `Object.prototype.__proto__` accessor now suggest the flag.

## Structured-clone coverage (2.8-guide)

`Headers`, `Request`, and `Response` can be transferred through `structuredClone` or worker messages. `Blob`, `File`, `CryptoKey`, `DOMException`, `X509Certificate`, `EventLoopDelayHistogram`, and `RecordableHistogram` can now be deep-cloned.

```ts
const request = new Request("https://example.com");
const moved = structuredClone(request, { transfer: [request] });
```

## Temporal time-zone transitions (2.2.0)

The unstable Temporal implementation now provides `Temporal.ZonedDateTime.prototype.getTimeZoneTransition()`, allowing code to find the next or previous offset transition for a zoned date-time.

```ts
const zoned = Temporal.ZonedDateTime.from(
  "2025-02-19T12:00[Europe/Helsinki]",
);
const next = zoned.getTimeZoneTransition("next");
```

## Text and byte module imports (2.4-guide)

With `--unstable-raw-imports`, import attributes can add text as a string or binary data as a `Uint8Array` directly to the module graph. These imports also work with `deno bundle` and `deno compile`, allowing the referenced assets to be embedded.

```ts
import message from "./hello.txt" with { type: "text" };
import image from "./image.png" with { type: "bytes" };
```

```sh
deno run --unstable-raw-imports main.ts
```

## Timer and standard-library typings (2.8.0)

Timer handles are now typed as `NodeJS.Timeout`, matching the Node-style objects returned by the default timers. The bundled types also expose `Math.sumPrecise()` and `Intl.Locale.prototype.variants`.

## Unstable subprocess helpers (2.7.0)

The unstable runtime API adds `Deno.spawn()`, `Deno.spawnAndWait()`, and `Deno.spawnAndWaitSync()` for spawning a process or spawning one and waiting for its result.

## User-agent hints and fetch priority (2.9-guide)

`navigator.userAgentData` is available in window and worker scopes, including `getHighEntropyValues()`. `RequestInit.priority` accepts and validates the standard `"auto"`, `"high"`, and `"low"` values.

```ts
const details = await navigator.userAgentData.getHighEntropyValues([
  "architecture",
]);
await fetch("https://example.com", { priority: "high" });
```

## Wasm source-phase imports (2.6-guide)

Source-phase import syntax loads a Wasm file as its compiled `WebAssembly.Module` representation rather than instantiating it as a normal module or fetching it at runtime.

```ts
import source addModule from "./add.wasm";
```

## Web Locks (2.9-guide)

Deno implements the full Web Locks API in window and worker code, including shared and exclusive modes, `ifAvailable`, `steal`, cancellation, and lock-state queries. A named lock is held until the request callback's promise settles.

```ts
await navigator.locks.request("config", async () => {
  console.log("exclusive access until this callback settles");
});
```

## Web-platform API changes (2.6-guide)

`BroadcastChannel` is stable, and `ReadableStream`, `WritableStream`, and `TransformStream` can be transferred between workers without copying. `ImageData` also accepts `Float16Array` pixel data.

## WebAssembly global export values (2.9-guide)

An ESM import of a Wasm `global` export now produces its underlying value rather than a `WebAssembly.Global` wrapper, matching the WebAssembly module specification and Node behavior.

## WebAssembly stack-trace format (2.7.0)

WebAssembly stack traces now follow the W3C format, which changes the textual frames seen by log processors and debugging tools.

## WebGPU capture controls (2.3-guide)

WebGPU adds `deviceStartCapture` and `deviceStopCapture` methods for delimiting a GPU capture from application code.

## WebGPU fallback-adapter location (2.3.0)

`isFallbackAdapter` moves from `GPUAdapter` to `GPUAdapterInfo`; WebGPU code reading the old property must switch to the adapter-info object.

## WebSocket error payloads (2.1.0)

WebSocket `ErrorEvent` objects now initialize their `error` attribute, so error handlers can inspect `event.error` reliably.

## Windows console-close signals (2.4.0)

Signal listeners on Windows can now observe Ctrl+Close events, allowing programs to perform shutdown handling when their console closes.

## Windows signal compatibility (2.8-guide)

Additional Unix-style signals, including `SIGUSR1` and `SIGUSR2`, are usable on Windows through the Node-compatible signal APIs.
