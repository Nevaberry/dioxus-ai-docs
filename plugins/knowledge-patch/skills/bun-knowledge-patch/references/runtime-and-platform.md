# Runtime APIs and platforms

Use this reference for runtime behavior, processes, data formats, terminal APIs, profiling, language features, native interfaces, scheduling, and platform support.

Entries are grouped by developer task. When entries describe evolving behavior, the later attribution supersedes earlier defaults or limitations.

## Runtime and CLI behavior

### Eval and print argument layout *(since 1.2.4)*

`bun --eval` and `bun --print` no longer insert a synthetic `[eval]` path into `process.argv`. The executable is followed directly by user arguments, matching Node.js.

```sh
bun --print "process.argv" arg1 arg2
# ["/path/to/bun", "arg1", "arg2"]
```

### Preloading through the environment *(since 1.2.11)*

`BUN_INSPECT_PRELOAD` specifies a module to load before the entry script and is equivalent to passing `--preload`.

```sh
BUN_INSPECT_PRELOAD=./setup.js bun run index.js
```

### Process-wide CLI options *(since 1.2.15)*

`BUN_OPTIONS` supplies persistent arguments to every Bun command without changing scripts or `bunfig.toml`. Its value follows shell-like quoting rules and is prepended to the explicit command-line arguments.

```sh
BUN_OPTIONS="--config='./my config.toml' --silent" bun run dev.ts
```

### Disabling automatic `.env` loading *(since 1.3.3)*

`bun run --no-env-file` skips Bun's default `.env` discovery, and root-level `env = false` in `bunfig.toml` makes that behavior persistent. Files explicitly supplied with `--env-file` are still loaded.

```sh
bun run --no-env-file index.ts
```

```toml
env = false
```

## Processes, resources, and event-loop behavior

### Explicit resource management *(1.2-guide)*

Bun supports `using`/`await using` and implements disposal for APIs including `Bun.spawn()`, `Bun.serve()`, `Bun.connect()`, `Bun.listen()`, and `bun:sqlite`. Those resources are closed at scope exit even when an exception is thrown.

### Automatic file-writer flushing *(since 1.2.2)*

Pending writes from `Bun.file(path).writer()` are now flushed automatically before the process exits. An explicit `flush()` is no longer required solely to ensure queued writes reach the filesystem at shutdown.

### Spawn timeouts *(since 1.2.6)*

The `timeout` option for spawned processes terminates a command after the specified milliseconds; synchronous results expose `exitedDueToTimeout` so callers can distinguish this exit path.

```ts
const result = Bun.spawnSync({ cmd: ["sleep", "1000"], timeout: 1_000 });
console.log(result.exitedDueToTimeout); // true
```

### `Bun.write()` destination behavior *(since 1.2.8)*

`Bun.write(path, "")` now creates missing parent directories even when the content is empty. Conversely, a `Blob` backed by a `Buffer` or `TypedArray` is read-only as a destination, and attempting to write to it throws.

```ts
await Bun.write("./new/directory/empty.txt", "");
```

### Subprocess output limits *(since 1.2.9)*

`maxBuffer` caps subprocess output in bytes and kills the process when the cap is exceeded. It works with `Bun.spawn()`, `Bun.spawnSync()`, `node:child_process.spawn()`, and `node:child_process.spawnSync()`.

```ts
const result = Bun.spawnSync({ cmd: ["yes"], maxBuffer: 100 });
```

### Configurable unhandled rejections *(since 1.2.17)*

The Node-compatible `--unhandled-rejections` flag accepts `throw`, `strict`, `warn`, and `none`; Bun also emits the `process` `rejectionHandled` event when a previously unhandled promise later gains a handler.

```sh
bun --unhandled-rejections=warn app.ts
```

### Direct `ReadableStream` consumption and subprocess input *(since 1.2.18)*

`ReadableStream` now directly provides async `.text()`, `.json()`, `.bytes()`, and `.blob()` methods. `Bun.spawn()` also accepts a `ReadableStream` as `stdin`, allowing input to be piped without buffering it first.

```ts
const input = new Blob(["hello"]).stream();
const child = Bun.spawn({ cmd: ["cat"], stdin: input, stdout: "pipe" });
console.log(await child.stdout.text());
```

### Synchronous subprocess isolation *(since 1.3.2)*

`Bun.spawnSync()` and `child_process.spawnSync()` now run on an event loop isolated from the rest of the process. JavaScript timers and microtasks no longer fire during the blocking call, bringing stdio interaction and timeout behavior in line with Node.js.

### Subprocess option typings *(since 1.3.2)*

The subprocess declarations now expose the runtime-supported `detached`, `onDisconnect`, and `lazy` options; `lazy` defers stdout and stderr reads until accessed. Common option shapes use `Bun.Spawn.BaseOptions`, and the older `Bun.Spawn.OptionsObject` alias is deprecated.

```ts
const child = Bun.spawn({
  cmd: ["worker"],
  detached: true,
  lazy: true,
  onDisconnect() {},
});
```

### Pseudo-terminal subprocesses *(since 1.3.5)*

`Bun.spawn()` accepts a `terminal` option that attaches a real PTY, so interactive programs see TTY streams and can use prompts, colors, and cursor control. The spawned process exposes the terminal for input, resizing, raw-mode control, event-loop ref control, and closing; PTY support is limited to Linux and macOS.

```ts
const proc = Bun.spawn(["bash"], {
  terminal: {
    cols: 80,
    rows: 24,
    data(_terminal, data) {
      process.stdout.write(data);
    },
  },
});

proc.terminal.write("echo hello\n");
proc.terminal.resize(100, 30);
await proc.exited;
proc.terminal.close();
```

A standalone `new Bun.Terminal()` can instead be passed to multiple sequential subprocesses; it supports `await using` for automatic disposal.

### Parent-death process cleanup *(since 1.3.14)*

`--no-orphans` makes Bun exit when its parent dies, even from `SIGKILL`, and recursively kills its own descendants on exit; nested Bun processes inherit the mode. It is available on Linux and macOS, is a no-op on Windows, and can also be set with `[run] noOrphans = true` or `BUN_FEATURE_FLAG_NO_ORPHANS=1`.

```sh
bun --no-orphans run app.ts
```

### In-place process replacement *(since 1.3.14)*

The POSIX-only `process.execve(execPath, args, env)` replaces the current process image and never returns on success, preserving standard streams while marking other descriptors close-on-exec. It emits an experimental warning and is unavailable in workers and on Windows.

```ts
process.execve("/usr/bin/echo", ["echo", "hello"], {
  PATH: process.env.PATH,
});
```

## Terminal, console, and REPL APIs

### TTY streams after standard input closes *(since 1.2.22)*

After piped `stdin` reaches EOF, an application can open and read `/dev/tty` without an `ESPIPE` error, enabling the usual pipe-then-interact TUI pattern. `tty.ReadStream` also supports `ref()` and `unref()` for event-loop control.

### Windows terminal resize events *(since 1.3.3)*

On Windows, `process.stdout` now emits `resize` events and Bun delivers `SIGWINCH`, allowing terminal applications to use the same resize handling as on other platforms.

```ts
process.stdout.on("resize", () => console.log(process.stdout.columns));
```

### JSON console formatting *(since 1.3.4)*

`console.log()` and related console methods now support Node-compatible `%j` formatting, which JSON-stringifies the corresponding value.

```js
console.log("%j", { status: "ok" }); // {"status":"ok"}
```

### Unicode-accurate terminal widths *(since 1.3.5)*

`Bun.stringWidth()` now treats additional Unicode formatting and combining characters as zero-width, ignores complete CSI and OSC escape sequences, and measures emoji by grapheme rather than code point. Flags, skin-tone sequences, ZWJ emoji, keycaps, and variation selectors therefore produce terminal-cell widths rather than inflated component totals.

```ts
Bun.stringWidth("🇺🇸"); // 2
Bun.stringWidth("👋🏽"); // 2
Bun.stringWidth("👨‍👩‍👧"); // 2
Bun.stringWidth("\u2060"); // 0
```

### Native REPL interface *(since 1.3.10)*

Bun's REPL is now built in rather than downloaded as a third-party package. Its terminal UI adds persistent history in `~/.bun_repl_history`, tab completion, multiline editing, syntax highlighting, Emacs-style line editing, `.copy`/`.load`/`.save`/`.editor` commands, and `_`/`_error` values for the last result and error.

### ANSI- and grapheme-aware string slicing *(since 1.3.11)*

`Bun.sliceAnsi()` slices by terminal columns while preserving SGR styles, OSC 8 hyperlinks, and whole grapheme clusters. It supports negative indices, an optional truncation marker, and `{ ambiguousIsNarrow }` width handling consistent with `Bun.stringWidth()` and `Bun.wrapAnsi()`.

```ts
Bun.sliceAnsi("\x1b[31mhello\x1b[39m", 1, 4); // styled "ell"
Bun.sliceAnsi("unicorn", 0, 4, "…");           // "uni…"
Bun.sliceAnsi("unicorn", -4, undefined, "…"); // "…orn"
```

### Windows pseudo-terminals *(since 1.3.14)*

`Bun.Terminal` and `Bun.spawn({ terminal })` now work on Windows through ConPTY, including TTY detection, input, output callbacks, and resizing. POSIX termios flags remain zero-valued no-ops there, and ConPTY output may use escape sequences that are semantically equivalent but not byte-identical to the child's output.

## Data formats, compression, text, and media

### `TextDecoder` compatibility *(since 1.2.12)*

Encoding labels now follow WHATWG behavior: labels containing null bytes throw, and `encoding` returns the normalized name for every supported encoding. The `fatal` option also uses normal boolean coercion instead of requiring a literal boolean.

```js
new TextDecoder("utf-8\0"); // throws RangeError
new TextDecoder("utf-16be").encoding; // "utf-16be"
new TextDecoder("utf-8", { fatal: 1 }).fatal; // true
```

### Zstandard compression *(since 1.2.14)*

`fetch()` now advertises `gzip, deflate, br, zstd` by default and transparently decompresses `Content-Encoding: zstd` responses. Bun also provides synchronous and asynchronous Zstandard helpers.

```ts
const compressed = Bun.zstdCompressSync("hello world", { level: 5 });
const restored = Bun.zstdDecompressSync(compressed);
const asyncCompressed = await Bun.zstdCompress("hello world");
const asyncRestored = await Bun.zstdDecompress(asyncCompressed);
```

### Native YAML imports and parsing *(since 1.2.21)*

`.yaml` and `.yml` files can be default-imported as parsed data, while `Bun.YAML.parse()` parses YAML strings at runtime.

```ts
import config from "./config.yaml";
import { YAML } from "bun";
const items = YAML.parse("- one\n- two");
```

### YAML serialization and binary parsing *(since 1.2.22)*

`Bun.YAML.stringify()` serializes JavaScript values to YAML. `Bun.YAML.parse()` now also accepts `Buffer`, `ArrayBuffer`, typed arrays, `DataView`, and `Blob` input.

```ts
const text = Bun.YAML.stringify({ enabled: true });
const value = Bun.YAML.parse(new TextEncoder().encode(text));
```

### Streaming compression Web APIs *(since 1.3.3)*

Bun now implements `CompressionStream` and `DecompressionStream`, allowing data to be compressed through `ReadableStream` pipelines without buffering the full payload. In addition to `gzip`, `deflate`, and `deflate-raw`, Bun accepts `brotli` and `zstd`.

```ts
const input = new Blob(["payload"]).stream();
const compressed = input.pipeThrough(new CompressionStream("zstd"));
const output = compressed.pipeThrough(new DecompressionStream("zstd"));
console.log(await new Response(output).text()); // "payload"
```

### Tar archives with `Bun.Archive` *(since 1.3.6)*

`Bun.Archive` creates and reads tar archives from file maps, blobs, typed arrays, or array buffers. It can list entries with an optional glob, extract to disk, emit bytes or a blob, and gzip output at levels 1–12; an archive can be passed directly to `Bun.write()` for local or S3 output.

```ts
const archive = new Bun.Archive(
  { "hello.txt": "Hello" },
  { compress: "gzip", level: 6 },
);
await Bun.write("bundle.tar.gz", archive);
await new Bun.Archive(await Bun.file("input.tar.gz").bytes()).extract("./out");
```

### Native JSONC parsing *(since 1.3.6)*

`Bun.JSONC.parse()` accepts line and block comments plus trailing commas, so JSONC configuration files no longer need a third-party parser.

```ts
const config = Bun.JSONC.parse(`{
  // Local service
  "port": 3000,
}`);
```

### Native JSON5 parsing and imports *(since 1.3.7)*

`Bun.JSON5` provides `parse()` and `stringify()`, and `.json5` files can be imported directly.

```ts
const config = Bun.JSON5.parse(`{ host: 'localhost', port: 5432, }`);
import settings from "./config.json5";
```

### Complete and streaming JSONL parsing *(since 1.3.7)*

`Bun.JSONL.parse()` parses a complete JSONL string or `Uint8Array`. `parseChunk()` returns complete `values`, the consumed `read` offset, a `done` flag, and any `error`, so callers can retain an incomplete suffix between chunks.

```ts
const values = Bun.JSONL.parse('{"id":1}\n{"id":2}\n');
let buffer = '{"id":3}\n{"id":4';
const { values: ready, read, done, error } = Bun.JSONL.parseChunk(buffer);
buffer = buffer.slice(read);
```

### Built-in Markdown-to-HTML rendering *(since 1.3.8)*

`Bun.markdown.html()` parses CommonMark and returns HTML. GFM tables, strikethrough, task lists, and permissive autolinks are enabled by default; additional options include `wikiLinks`, `latexMath`, `headingIds`, and `autolinkHeadings`.

```ts
const html = Bun.markdown.html("## Hello", { headingIds: true });
// '<h2 id="hello">Hello</h2>\n'
```

### Callback-driven Markdown rendering *(since 1.3.8)*

`Bun.markdown.render()` invokes callbacks for Markdown elements, passing rendered children and element metadata such as a heading's level. Callbacks can produce custom markup or terminal text, and returning `null` omits an element.

```ts
const output = Bun.markdown.render("# Title\n\nHello **world**", {
  heading: (children, { level }) => `<h${level}>${children}</h${level}>`,
  paragraph: (children) => `<p>${children}</p>`,
  strong: (children) => `<b>${children}</b>`,
  image: () => null,
});
```

### React elements from Markdown *(since 1.3.8)*

`Bun.markdown.react()` returns a React Fragment and accepts element overrides such as `h1`. Its default element format targets React 19; pass `reactVersion: 18` when using React 18 or older.

```tsx
function Markdown({ text }: { text: string }) {
  return Bun.markdown.react(text, {
    h1: ({ children }) => <h1 className="title">{children}</h1>,
  });
}
```

### Markdown list callback metadata *(since 1.3.11)*

`Bun.markdown.render()` now always passes `listItem` callbacks metadata containing zero-based `index`, `depth`, `ordered`, `start`, and `checked`; `list` callbacks now receive `depth`. Always passing the `listItem` metadata object is a breaking change for callbacks that depended on it being absent outside task lists.

```ts
Bun.markdown.render(markdown, {
  listItem: (children, { index, depth, ordered, start, checked }) => children,
  list: (children, { depth }) => children,
});
```

### ANSI Markdown rendering *(since 1.3.12)*

Running `bun ./file.md` renders a Markdown file directly to terminal-friendly ANSI output. `Bun.markdown.ansi()` provides the same rendering programmatically, with controls for colors, hyperlinks, wrapping width, and Kitty-protocol inline images.

```ts
const output = Bun.markdown.ansi("# Status\n\n[Details](https://example.com)", {
  columns: 60,
  hyperlinks: true,
});
process.stdout.write(output);
```

### Built-in image processing *(since 1.3.14)*

`Bun.Image` is a chainable image pipeline accepting paths, typed buffers, blobs, `BunFile`/`S3File`, and data URLs; it can resize, rotate, flip, modulate, encode, inspect metadata, generate thumbhash placeholders, and write or return body-compatible output. JPEG, PNG, WebP, GIF, and BMP work on every platform, while TIFF, HEIC, and AVIF rely on macOS or Windows system codecs, with AVIF encoding on macOS limited to Apple Silicon.

```ts
return new Response(
  Bun.file("photo.jpg").image().resize(200).webp({ quality: 85 }),
);
```

## Diagnostics and profiling

### Configurable console inspection depth *(since 1.2.19)*

`--console-depth=N` controls how deeply `console.log` inspects nested objects; `[run] console.depth` persists the setting in `bunfig.toml`, while the CLI flag takes precedence. The default remains `2`.

```toml
[run]
console.depth = 4
```

### Async stack traces *(since 1.2.22)*

Error stack traces now retain the asynchronous `await` call chain leading to a throw instead of showing only the final synchronous frame. This makes the originating path visible without changing application code.

### CPU profiling *(since 1.3.2)*

`--cpu-prof` writes a Chrome DevTools-compatible `.cpuprofile` that can also be opened in VS Code. `--cpu-prof-name` selects its filename and `--cpu-prof-dir` selects its output directory.

```sh
bun --cpu-prof --cpu-prof-dir ./profiles --cpu-prof-name app.cpuprofile app.ts
```

### Markdown CPU profiles *(since 1.3.7)*

`--cpu-prof-md` writes a Markdown CPU profile with hot functions, call trees, caller/callee details, and per-file time. It can be used alone or alongside `--cpu-prof`, and honors `--cpu-prof-name` and `--cpu-prof-dir`.

### Heap profiling *(since 1.3.7)*

`--heap-prof` writes a V8-compatible `.heapsnapshot`, while `--heap-prof-md` emits a searchable Markdown report with retained sizes, object listings, and retainer chains. Use `--heap-prof-name` and `--heap-prof-dir` to control the output.

### Configurable CPU profiling interval *(since 1.3.9)*

`--cpu-prof-interval` sets the CPU profiler sampling interval in microseconds; it defaults to 1000 and warns unless `--cpu-prof` or `--cpu-prof-md` is also enabled.

```sh
bun --cpu-prof --cpu-prof-interval 500 index.js
```

### Array-buffer heap snapshots *(since 1.3.10)*

`Bun.generateHeapSnapshot("v8", "arraybuffer")` returns the snapshot's UTF-8 JSON as an `ArrayBuffer`, avoiding the size and conversion costs of the string result and allowing it to be written directly.

```ts
const snapshot = Bun.generateHeapSnapshot("v8", "arraybuffer");
await Bun.write("heap.heapsnapshot", snapshot);
```

### Async stacks from native APIs *(since 1.3.12)*

Failures from native APIs such as `node:fs`, `node:http`, `node:dns`, and `Bun.write()` now retain the asynchronous JavaScript call chain. `Error.captureStackTrace()` also includes async frames.

## Language, Web APIs, and type declarations

### New JavaScript built-ins *(1.2-guide)*

Bun now implements `Promise.withResolvers()`, `Promise.try()`, `Error.isError()`, `Float16Array`, and iterator helpers `map`, `flatMap`, `filter`, `take`, `drop`, `reduce`, `toArray`, `forEach`, and `find`. `Uint8Array` also gains static `fromBase64()`/`fromHex()` and instance `toBase64()`/`toHex()` conversions.

### New Web API coverage *(1.2-guide)*

Newly supported APIs include `TextDecoderStream`, `TextEncoderStream`, streaming `TextDecoder.decode(..., { stream: true })`, `URL.createObjectURL()` for blobs, `AbortSignal.any()`, and functional `console.group()`/`groupEnd()`. `Response`, `Blob`, and `Bun.file()` gain `bytes()` returning `Uint8Array`, while `fetch()` request bodies can be async iterables for streaming uploads.

### Environment and DOM-free TypeScript declarations *(since 1.2.8)*

An augmentation of `Bun.Env` now applies to `process.env` as well, keeping custom environment-variable types consistent across both access paths. The ambient definitions for `AbortSignal`, `BroadcastChannel`, and `URLSearchParams` also work when `lib.dom` is omitted.

### `Bun.$` as a TypeScript type *(since 1.2.11)*

The shell API can now be named directly as the type of a configured shell instance.

```ts
class Wrapper {
  shell: Bun.$ = Bun.$.nothrow();
}
```

### Precise numeric summation *(since 1.2.18)*

Bun now implements the Stage 3 `Math.sumPrecise()` API, which sums numeric iterables with substantially better floating-point accuracy than a naive reduction.

```js
Math.sumPrecise([0.1, 0.2, 0.3, -0.5, 0.1]); // 0.2
```

### Concrete DOM-free global typings *(since 1.2.19)*

When TypeScript's `dom` library is absent, the global `EventSource` and `Performance` declarations now extend their concrete Node-compatible types instead of becoming empty interfaces.

### Disposable stack globals *(1.3-guide)*

`DisposableStack` and `AsyncDisposableStack` collect multiple disposable resources and clean all of them up together. Cleanup continues through failures, with collected errors rethrown after every resource has been attempted.

```js
const stack = new DisposableStack();
stack.use({
  [Symbol.dispose]() {
    console.log("cleanup");
  },
});
stack.dispose();
```

### Type environment auto-detection *(1.3-guide)*

`@types/bun` now selects Node.js or DOM types from the project's enabled libraries to reduce conflicts. When DOM types are enabled they take precedence, so Bun-specific extensions such as extra `WebSocket` constructor options may still produce type errors.

### `URLPattern` Web API *(since 1.3.4)*

Bun now provides the `URLPattern` Web API for declarative URL matching. It supports string or `URLPatternInit` inputs, `test()`, `exec()`, component properties, named and wildcard groups, and `hasRegExpGroups`.

```ts
const pattern = new URLPattern({ pathname: "/users/:id" });
const match = pattern.exec("https://example.com/users/123");
console.log(match?.pathname.groups.id); // "123"
```

## Native interfaces and WebAssembly

### Compile C through `bun:ffi` *(1.2-guide)*

The experimental `cc()` API compiles C on demand with Bun's embedded compiler and exposes declared symbols without a separate build step. Its symbol descriptors specify argument and return FFI types, including N-API types.

```ts
import { cc } from "bun:ffi";
const { symbols: { random } } = cc({
  source: "./random.c",
  symbols: { random: { args: [], returns: "int" } },
});
```

### Streaming WebAssembly compilation *(since 1.2.20)*

`WebAssembly.compileStreaming()` and `WebAssembly.instantiateStreaming()` now compile directly from a response body instead of first buffering the complete Wasm module.

```js
const { instance } = await WebAssembly.instantiateStreaming(
  fetch("http://localhost:3000/add.wasm"),
);
```

### FFI compiler search paths *(since 1.3.7)*

The C compiler used by `bun:ffi` now honors `C_INCLUDE_PATH` and `LIBRARY_PATH`, enabling headers and libraries in nonstandard layouts such as Nix store paths.

### Expanded WebAssembly proposals *(since 1.3.14)*

The runtime now supports Relaxed SIMD instructions, and Memory64 support extends to atomics, bulk-memory operations, memory growth, and memory-size queries.

## Scheduling and operating-system services

### Native operating-system credential storage *(since 1.2.21)*

`Bun.secrets` asynchronously stores, retrieves, and deletes credentials in the platform credential manager using a service/name pair.

```ts
import { secrets } from "bun";
await secrets.set({ service: "my-cli", name: "token", value: "secret" });
const token = await secrets.get({ service: "my-cli", name: "token" });
```

### OS-level cron jobs and expression parsing *(since 1.3.11)*

`Bun.cron(path, expression, title)` registers a persistent job through `crontab` on Linux, `launchd` on macOS, or Task Scheduler on Windows; registering the same title replaces the existing job. When it fires, Bun imports the module and calls its default export's `scheduled(controller)` method, whose controller includes the normalized `cron` expression and `scheduledTime` in milliseconds.

```ts
// scheduler.ts
await Bun.cron("./worker.ts", "30 2 * * MON", "weekly-report");
const next = Bun.cron.parse("*/15 * * * *"); // Date or null
await Bun.cron.remove("weekly-report"); // remove it later by title

// worker.ts
export default {
  async scheduled({ cron, scheduledTime }) {
    console.log({ cron, scheduledTime });
  },
};
```

`Bun.cron.parse(expression, from?)` searches roughly four years ahead and supports standard five-field expressions, named days and months, `@yearly` through `@hourly`, Sunday as `0` or `7`, and POSIX OR semantics for restricted day-of-month and day-of-week fields.

### In-process cron scheduling *(since 1.3.12)*

`Bun.cron(expression, callback)` runs non-overlapping callbacks in-process on a UTC schedule; the next invocation is not scheduled until a returned promise settles. Jobs are disposable, support `ref()`/`unref()`, and are cleared during `--hot` reevaluation; thrown errors and rejections follow `setTimeout`-style process error handling.

```ts
Bun.cron("0 9 * * *", async () => {
  await sendDailyReport();
});
```

## Platforms, containers, and deployment

### musl Linux builds *(1.2-guide)*

Bun now ships x64 and aarch64 musl builds for distributions such as Alpine, including the `oven/bun:alpine` container image. The glibc build remains recommended unless musl compatibility or a smaller image is specifically needed.

### Linux garbage-collection signal *(since 1.2.2)*

Bun now uses `SIGPWR` instead of `SIGUSR1` to suspend threads for garbage collection on Linux. Applications can use `SIGUSR1` for reload or other logic without colliding with the runtime; `SIGPWR` is now used internally.

### Debian Bookworm Docker base *(since 1.2.10)*

The `oven/bun:latest` and versioned `oven/bun:1.2.10` images now use Debian Bookworm instead of Debian Bullseye. Container builds therefore inherit Bookworm's system packages and compatibility baseline.

### Windows long-path support *(since 1.2.20)*

Bun now consistently supports Windows file paths longer than 260 characters through its application manifest, so deeply nested paths work without special path namespacing.

### Official Alpine image baseline *(since 1.3.2)*

The official Alpine images for x64 and arm64 musl now use Alpine 3.22, changing the base packages and compatibility environment inherited by container builds.

### Windows ARM64 runtime and compile target *(since 1.3.10)*

Bun now runs natively on Windows ARM64 and standalone executables can target that platform with `bun-windows-arm64`.

```sh
bun build --compile --target=bun-windows-arm64 ./app.ts --outfile myapp
```

### Cgroup-aware concurrency values *(since 1.3.12)*

On Linux, `availableParallelism` and `hardwareConcurrency` now reflect cgroup CPU limits rather than physical core count. Bun's thread pool and JIT worker counts honor the same limits in containers.

### FreeBSD and Android builds *(since 1.3.14)*

Bun now provides first-party native builds for FreeBSD and Android.

### Vercel Functions runtime *(release-index)*

Vercel Functions can now run on the Bun Runtime with full access to Bun APIs. This makes Vercel a deployment target for functions that depend on Bun-specific runtime features.
