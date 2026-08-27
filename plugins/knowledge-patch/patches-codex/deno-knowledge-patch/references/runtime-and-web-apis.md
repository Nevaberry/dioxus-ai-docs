# Runtime and Web APIs

Use this reference for the following topic-specific compatibility details.

## `deno serve` startup callbacks (2.4-guide)

A default-export server may define `onListen()` to run after the listener is ready and receive its bound address.

```ts
export default {
  fetch() {
    return new Response("Hello");
  },
  onListen({ hostname, port }) {
    console.log(`Listening on ${hostname}:${port}`);
  },
} satisfies Deno.ServeDefaultExport;
```

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

## Automatic `deno eval` module detection (2.8-guide)

`deno eval` now detects CommonJS versus ES module syntax in the supplied snippet without requiring the caller to select a mode.

## Bare configured entry points (2.4-guide)

`deno run` resolves bare entry-point specifiers through the project's `imports` map, including npm, JSR, and prefix mappings. The `run` subcommand itself may still be omitted.

```json
{
  "imports": {
    "file-server": "jsr:@std/http/file-server"
  }
}
```

```sh
deno run file-server
```

## Brotli compression streams (2.7-guide)

`CompressionStream` and `DecompressionStream` accept `"brotli"` in addition to `"gzip"` and `"deflate"`.

```ts
const compressed = body.pipeThrough(new CompressionStream("brotli"));
```

## Compatibility mode and sloppy imports (2.4-guide)

`DENO_COMPAT=1` enables CommonJS detection, Node globals, bare Node built-ins, and sloppy-import compatibility together. The extension-inference flag is also available in stable form as `--sloppy-imports` instead of `--unstable-sloppy-imports`.

```sh
DENO_COMPAT=1 deno run app.js
deno run --sloppy-imports app.js
```

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

## Decompressed response headers (2.9.0)

Automatically decompressed fetch responses retain their `content-encoding` and `content-length` headers. Consumers must not assume that `content-length` is the byte length of the decoded body.

## Default `deno serve` address (2.3-guide)

`DENO_SERVE_ADDRESS` sets the default `host:port` used by the `deno serve` command.

```sh
DENO_SERVE_ADDRESS=127.0.0.1:8080 deno serve main.ts
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

## Environment-controlled automatic serving (2.4.0)

`DENO_AUTO_SERVE` is an environment-level switch for automatic serving, allowing an execution environment to enable that mode without changing the invoked command.

```sh
DENO_AUTO_SERVE=1 deno run app.ts
```

## Error API typings (2.3.0)

Runtime types now expose `Error.isError` and `ErrorConstructor.stackTraceLimit`, so TypeScript code can use those V8 APIs without local type augmentation.

## Expanded `tsconfig.json` project support (2.4-guide)

`tsconfig.json` handling now honors `references`, `extends`, `files`, `include`, and `exclude`, so referenced projects and configured file boundaries participate in Deno tooling.

## Experimental `tsgo` and type-tooling support (2.6-guide)

`deno check` can use the experimental Go-based checker through `--unstable-tsgo` or `DENO_UNSTABLE_TSGO=1`. Checking now supports `compilerOptions.paths` and `isolatedDeclarations` and applies `skipLibCheck` to graph errors; the language server adds `source.organizeImports` and recognizes individual `describe`/`it` tests.

```sh
deno check --unstable-tsgo main.ts
```

## FFI and runtime property adjustments (2.0.0)

The deprecated `UnsafeFnPointer` constructor signature taking an untyped `Deno.PointerObject` is removed. `globalThis.location` is configurable, and `Deno.FsWatcher.prototype.return()` is no longer deprecated.

## File change-time metadata (2.1.0)

Results from Deno's stat APIs now include `ctime`, and the Node compatibility layer uses that value too.

```ts
const { ctime } = await Deno.stat("data.txt");
console.log(ctime);
```

## Forced terminal color (2.3-guide)

Deno now honors `FORCE_COLOR`, allowing color output to be enabled even when automatic terminal detection would disable it.

## Framework-aware compilation (2.8-guide)

`deno compile .` detects Next.js, Astro, Fresh, Remix, SvelteKit, Nuxt, SolidStart, TanStack Start, and Vite SSR projects, runs `deno task build`, and generates the framework entry point for the executable.

```sh
deno compile .
```

## GIF and WebP bitmap decoding (2.7-guide)

`createImageBitmap()` can now decode GIF and WebP blobs in addition to PNG, JPEG, and BMP.

## Graceful watch restarts (2.8-guide)

Before replacing a watched process, Deno sends `SIGTERM` and dispatches `unload` and `process.exit` so cleanup handlers can run; the hard-kill grace period is 500 milliseconds. `--watch-exclude` now applies to every change event.

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

## JSON trailing-comma policy (2.9-guide)

`fmt.json.trailingCommas` accepts `"never"` (the default), `"always"`, `"maintain"`, or `"jsonc"`; the last choice adds commas in JSONC and omits them in JSON.

```json
{
  "fmt": {
    "json": { "trailingCommas": "jsonc" }
  }
}
```

## Named import and export sorting (2.9-guide)

`sortNamedImports` and `sortNamedExports` select `"caseInsensitive"` (the default), `"caseSensitive"`, or `"maintain"` ordering for named specifiers.

```json
{
  "fmt": {
    "sortNamedImports": "maintain",
    "sortNamedExports": "caseSensitive"
  }
}
```

## Named import and export spacing (2.5-guide)

When `fmt.spaceSurroundingProperties` is `false`, the formatter now removes spaces inside named import and export braces as well as property braces, producing forms such as `import {foo} from "bar"`. The option still defaults to `true`.

## Native JavaScript explicit resource management (2.3-guide)

V8 now supports `using` natively in JavaScript, so disposable Deno resources such as files are closed automatically when their scope exits without a manual `try`/`finally`.

```js
{
  using file = Deno.createSync("data.txt");
  file.writeSync(new TextEncoder().encode("data\n"));
}
```

## Native source-map application (2.6-guide)

When formatting an exception stack, the runtime now detects `//# sourceMappingURL=...` comments and applies their source maps; internal frames are also filtered and project paths are shown relatively.

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

## Process-wide extra CA certificates (2.8-guide)

`NODE_EXTRA_CA_CERTS` augments the root certificate store used by every TLS path, including `fetch`, `Deno.connectTls`, `node:https`, and `node:tls`.

## Project-scoped `tsconfig.json` discovery (2.4.0)

Automatic `tsconfig.json` discovery is disabled when a project has neither `deno.json` nor `package.json`, and `--no-config` suppresses that discovery explicitly.

## Pull-request runtime builds (2.8-guide)

`deno upgrade pr <number>` installs the matching-platform binary built by a pull request through an installed and authenticated `gh` CLI. `--output` preserves the current installation and `--dry-run` previews the selection.

```sh
deno upgrade --output ./deno-pr pr 34227
```

## Request-signal abort transition (2.9-guide)

`Deno.serve()` warns once when a handler relies on the legacy behavior that aborts `request.signal` after a successful response; `--unstable-no-legacy-abort` opts into the replacement behavior.

## Response-style subprocess output (2.5-guide)

Piped `Deno.ChildProcess` output streams now provide `arrayBuffer()`, `bytes()`, `json()`, and `text()` convenience methods, avoiding a separate stream conversion helper.

```ts
const child = new Deno.Command("cat", {
  args: ["hello.txt"],
  stdout: "piped",
}).spawn();
const output = await child.stdout.text();
```

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

## Six-month LTS channel (2.0-guide)

Starting with Deno 2.1, an LTS branch receives backported critical fixes for six months. At the end of each six-month period, a new LTS branch is cut from the latest stable release.

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

## Temporal time-zone transitions (2.2.0)

The unstable Temporal implementation now provides `Temporal.ZonedDateTime.prototype.getTimeZoneTransition()`, allowing code to find the next or previous offset transition for a zoned date-time.

```ts
const zoned = Temporal.ZonedDateTime.from(
  "2025-02-19T12:00[Europe/Helsinki]",
);
const next = zoned.getTimeZoneTransition("next");
```

## Terminal-symlink truncation (2.9.0)

Filesystem truncation no longer follows a symlink in the terminal path component, preventing the symlink's target from being shortened unexpectedly.

## Text and byte module imports (2.4-guide)

With `--unstable-raw-imports`, import attributes can add text as a string or binary data as a `Uint8Array` directly to the module graph. These imports also work with `deno bundle` and `deno compile`, allowing the referenced assets to be embedded.

```ts
import message from "./hello.txt" with { type: "text" };
import image from "./image.png" with { type: "bytes" };
```

```sh
deno run --unstable-raw-imports main.ts
```

## URL serialization (2.9.1)

`URL` and `URLSearchParams` are no longer serializable. Code using serialization-dependent APIs should pass their string forms and reconstruct the objects at the destination.

## Wasm source-phase imports (2.6-guide)

Source-phase import syntax loads a Wasm file as its compiled `WebAssembly.Module` representation rather than instantiating it as a normal module or fetching it at runtime.

```ts
import source addModule from "./add.wasm";
```

## Watched environment files (2.5-guide)

When `--watch` and `--env-file` are used together, edits to the environment file now reload its environment variables automatically.

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

## WebGPU capture controls (2.3-guide)

WebGPU adds `deviceStartCapture` and `deviceStopCapture` methods for delimiting a GPU capture from application code.

## WebGPU fallback-adapter location (2.3.0)

`isFallbackAdapter` moves from `GPUAdapter` to `GPUAdapterInfo`; WebGPU code reading the old property must switch to the adapter-info object.

## Windows console-close signals (2.4.0)

Signal listeners on Windows can now observe Ctrl+Close events, allowing programs to perform shutdown handling when their console closes.

## Windows signal compatibility (2.8-guide)

Additional Unix-style signals, including `SIGUSR1` and `SIGUSR2`, are usable on Windows through the Node-compatible signal APIs.

## Worker and child-process compatibility (2.7-guide)

`node:worker_threads` adds worker stdin, `threadName`, `worker.cpuUsage()`, and `BroadcastChannel` `ref()`/`unref()` support; worker output, exit codes, terminal errors, and `process.exit()` now follow Node behavior. `node:child_process` accepts a `URL` in `fork()`, supports `timeout` and `killSignal` in `spawn()`, handles shell redirection in `exec()`, and exposes stdio as `Socket` instances that are unrefed by default.

## Worker debugging and inspector addresses (2.7-guide)

Chrome DevTools and VS Code can now debug Web Workers as well as the main thread. `--inspect` accepts bare ports, bare hosts, and `:0`, while `--inspect-publish-uid` supports VS Code's Node-compatible debugger discovery.

```sh
deno run --inspect=9229 main.ts
deno run --inspect=:0 main.ts
```
