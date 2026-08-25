# Runtime APIs and platforms

Use this reference for Bun-native runtime APIs, JavaScript and Web APIs, shell and subprocess behavior, data formats, profiling, operating systems, and deployment environments.

## `Bun.$` as a TypeScript type

*Batch: `1.2.11`.*

The shell API can now be named directly as the type of a configured shell instance.

```ts
class Wrapper {
  shell: Bun.$ = Bun.$.nothrow();
}
```

## `Bun.write()` destination behavior

*Batch: `1.2.8`.*

`Bun.write(path, "")` now creates missing parent directories even when the content is empty. Conversely, a `Blob` backed by a `Buffer` or `TypedArray` is read-only as a destination, and attempting to write to it throws.

```ts
await Bun.write("./new/directory/empty.txt", "");
```

## `DOMException` options

*Batch: `1.2.13`.*

`DOMException` accepts an options object containing `name` and `cause`, making the causal error available on the resulting exception.

```js
const error = new DOMException("Request failed", {
  name: "CustomError",
  cause: new Error("Connection closed"),
});
```

## `TextDecoder` compatibility

*Batch: `1.2.12`.*

Encoding labels now follow WHATWG behavior: labels containing null bytes throw, and `encoding` returns the normalized name for every supported encoding. The `fatal` option also uses normal boolean coercion instead of requiring a literal boolean.

```js
new TextDecoder("utf-8\0"); // throws RangeError
new TextDecoder("utf-16be").encoding; // "utf-16be"
new TextDecoder("utf-8", { fatal: 1 }).fatal; // true
```

## Abort controllers as promise-timer options

*Batch: `1.2.16`.*

The promise-based timers accept an `AbortController` itself as their options object, using its `signal` property to cancel the timer.

```js
import { setTimeout } from "node:timers/promises";

const controller = new AbortController();
const pending = setTimeout(100, undefined, controller);
controller.abort();
await pending; // rejects with AbortError
```

## Additional libuv symbols for native add-ons

*Batch: `1.2.9`.*

N-API modules can now use `uv_mutex_destroy`, `uv_mutex_init`, `uv_mutex_init_recursive`, `uv_mutex_lock`, `uv_mutex_trylock`, `uv_mutex_unlock`, `uv_hrtime`, and `uv_once`.

## ANSI Markdown rendering

*Batch: `1.3.12`.*

Running `bun ./file.md` renders a Markdown file directly to terminal-friendly ANSI output. `Bun.markdown.ansi()` provides the same rendering programmatically, with controls for colors, hyperlinks, wrapping width, and Kitty-protocol inline images.

```ts
const output = Bun.markdown.ansi("# Status\n\n[Details](https://example.com)", {
  columns: 60,
  hyperlinks: true,
});
process.stdout.write(output);
```

## ANSI- and grapheme-aware string slicing

*Batch: `1.3.11`.*

`Bun.sliceAnsi()` slices by terminal columns while preserving SGR styles, OSC 8 hyperlinks, and whole grapheme clusters. It supports negative indices, an optional truncation marker, and `{ ambiguousIsNarrow }` width handling consistent with `Bun.stringWidth()` and `Bun.wrapAnsi()`.

```ts
Bun.sliceAnsi("\x1b[31mhello\x1b[39m", 1, 4); // styled "ell"
Bun.sliceAnsi("unicorn", 0, 4, "…");           // "uni…"
Bun.sliceAnsi("unicorn", -4, undefined, "…"); // "…orn"
```

## Array-buffer heap snapshots

*Batch: `1.3.10`.*

`Bun.generateHeapSnapshot("v8", "arraybuffer")` returns the snapshot's UTF-8 JSON as an `ArrayBuffer`, avoiding the size and conversion costs of the string result and allowing it to be written directly.

```ts
const snapshot = Bun.generateHeapSnapshot("v8", "arraybuffer");
await Bun.write("heap.heapsnapshot", snapshot);
```

## Async line iteration from file handles

*Batch: `1.3.1`.*

`FileHandle.readLines()` from `node:fs/promises` provides backpressure-aware async iteration, handles empty and CRLF lines, and accepts `createReadStream` options such as `encoding`.

```ts
import { open } from "node:fs/promises";
const file = await open("file.txt");
try {
  for await (const line of file.readLines({ encoding: "utf8" })) console.log(line);
} finally {
  await file.close();
}
```

## Async stack traces

*Batch: `1.2.22`.*

Error stack traces now retain the asynchronous `await` call chain leading to a throw instead of showing only the final synchronous frame. This makes the originating path visible without changing application code.

## Async stacks from native APIs

*Batch: `1.3.12`.*

Failures from native APIs such as `node:fs`, `node:http`, `node:dns`, and `Bun.write()` now retain the asynchronous JavaScript call chain. `Error.captureStackTrace()` also includes async frames.

## Automatic file-writer flushing

*Batch: `1.2.2`.*

Pending writes from `Bun.file(path).writer()` are now flushed automatically before the process exits. An explicit `flush()` is no longer required solely to ensure queued writes reach the filesystem at shutdown.

## Broader deployment baselines

*Batch: `1.4-2`.*

Linux builds now run with glibc 2.17 and kernels as old as 3.10. On Windows, Bun can run inside an AppContainer and from read-only directories or shares, including package installation, subprocesses, and terminals.

## Built-in image processing

*Batch: `1.3.14`.*

`Bun.Image` is a chainable image pipeline accepting paths, typed buffers, blobs, `BunFile`/`S3File`, and data URLs; it can resize, rotate, flip, modulate, encode, inspect metadata, generate thumbhash placeholders, and write or return body-compatible output. JPEG, PNG, WebP, GIF, and BMP work on every platform, while TIFF, HEIC, and AVIF rely on macOS or Windows system codecs, with AVIF encoding on macOS limited to Apple Silicon.

```ts
return new Response(
  Bun.file("photo.jpg").image().resize(200).webp({ quality: 85 }),
);
```

## Built-in Markdown-to-HTML rendering

*Batch: `1.3.8`.*

`Bun.markdown.html()` parses CommonMark and returns HTML. GFM tables, strikethrough, task lists, and permissive autolinks are enabled by default; additional options include `wikiLinks`, `latexMath`, `headingIds`, and `autolinkHeadings`.

```ts
const html = Bun.markdown.html("## Hello", { headingIds: true });
// '<h2 id="hello">Hello</h2>\n'
```

## Bun Shell behavior and controls

*Batch: `1.4-4`.*

`new $.Shell()` inherits the environment, working-directory, and throw defaults, while `.quiet(boolean)` can toggle quiet mode. The built-in `ls` now has a real `-l` listing, `echo` supports `-e`/`-E`, empty arguments are preserved, and bare `cd` changes to `$HOME`.

## Callback-driven Markdown rendering

*Batch: `1.3.8`.*

`Bun.markdown.render()` invokes callbacks for Markdown elements, passing rendered children and element metadata such as a heading's level. Callbacks can produce custom markup or terminal text, and returning `null` omits an element.

```ts
const output = Bun.markdown.render("# Title\n\nHello **world**", {
  heading: (children, { level }) => `<h${level}>${children}</h${level}>`,
  paragraph: (children) => `<p>${children}</p>`,
  strong: (children) => `<b>${children}</b>`,
  image: () => null,
});
```

## Cgroup-aware concurrency values

*Batch: `1.3.12`.*

On Linux, `availableParallelism` and `hardwareConcurrency` now reflect cgroup CPU limits rather than physical core count. Bun's thread pool and JIT worker counts honor the same limits in containers.

## Compile C through `bun:ffi`

*Batch: `1.2-guide`.*

The experimental `cc()` API compiles C on demand with Bun's embedded compiler and exposes declared symbols without a separate build step. Its symbol descriptors specify argument and return FFI types, including N-API types.

```ts
import { cc } from "bun:ffi";
const { symbols: { random } } = cc({
  source: "./random.c",
  symbols: { random: { args: [], returns: "int" } },
});
```

## Complete and streaming JSONL parsing

*Batch: `1.3.7`.*

`Bun.JSONL.parse()` parses a complete JSONL string or `Uint8Array`. `parseChunk()` returns complete `values`, the consumed `read` offset, a `done` flag, and any `error`, so callers can retain an incomplete suffix between chunks.

```ts
const values = Bun.JSONL.parse('{"id":1}\n{"id":2}\n');
let buffer = '{"id":3}\n{"id":4';
const { values: ready, read, done, error } = Bun.JSONL.parseChunk(buffer);
buffer = buffer.slice(read);
```

## Complete WHATWG text decoding

*Batch: `1.4-3`.*

`TextDecoder` now recognizes all 228 Encoding Standard labels and implements every required encoding, including the previously missing single-byte families and correct streaming behavior for EUC-JP, Big5, and ISO-2022-JP.

## Compression dictionaries

*Batch: `1.4-3`.*

`node:zlib` accepts Brotli and Zstandard dictionaries, and its `reset()` behavior now matches Node. Asynchronous writes also accept growable `SharedArrayBuffer` inputs.

## Concrete DOM-free global typings

*Batch: `1.2.19`.*

When TypeScript's `dom` library is absent, the global `EventSource` and `Performance` declarations now extend their concrete Node-compatible types instead of becoming empty interfaces.

## Configurable console inspection depth

*Batch: `1.2.19`.*

`--console-depth=N` controls how deeply `console.log` inspects nested objects; `[run] console.depth` persists the setting in `bunfig.toml`, while the CLI flag takes precedence. The default remains `2`.

```toml
[run]
console.depth = 4
```

## Configurable CPU profiling interval

*Batch: `1.3.9`.*

`--cpu-prof-interval` sets the CPU profiler sampling interval in microseconds; it defaults to 1000 and warns unless `--cpu-prof` or `--cpu-prof-md` is also enabled.

```sh
bun --cpu-prof --cpu-prof-interval 500 index.js
```

## Configurable unhandled rejections

*Batch: `1.2.17`.*

The Node-compatible `--unhandled-rejections` flag accepts `throw`, `strict`, `warn`, and `none`; Bun also emits the `process` `rejectionHandled` event when a previously unhandled promise later gains a handler.

```sh
bun --unhandled-rejections=warn app.ts
```

## CPU profiling

*Batch: `1.3.2`.*

`--cpu-prof` writes a Chrome DevTools-compatible `.cpuprofile` that can also be opened in VS Code. `--cpu-prof-name` selects its filename and `--cpu-prof-dir` selects its output directory.

```sh
bun --cpu-prof --cpu-prof-dir ./profiles --cpu-prof-name app.cpuprofile app.ts
```

## Debian Bookworm Docker base

*Batch: `1.2.10`.*

The `oven/bun:latest` and versioned `oven/bun:1.2.10` images now use Debian Bookworm instead of Debian Bullseye. Container builds therefore inherit Bookworm's system packages and compatibility baseline.

## Direct-stream backpressure contract

*Batch: `1.4-4`.*

For `ReadableStream({ type: "direct" })`, `controller.write()` returns a negative value under backpressure and `await controller.flush(true)` waits for the sink to drain. `FileSink.write()` now has the matching `number | Promise<number>` return type.

```ts
const body = new ReadableStream({
  type: "direct",
  async pull(controller) {
    if (controller.write(new TextEncoder().encode("data")) < 0) {
      await controller.flush(true);
    }
    controller.close();
  },
});
```

## Disabling automatic `.env` loading

*Batch: `1.3.3`.*

`bun run --no-env-file` skips Bun's default `.env` discovery, and root-level `env = false` in `bunfig.toml` makes that behavior persistent. Files explicitly supplied with `--env-file` are still loaded.

```sh
bun run --no-env-file index.ts
```

```toml
env = false
```

## Disabling native addons

*Batch: `1.2.13`.*

The `--no-addons` flag prevents native addon loading: `process.dlopen()` throws `ERR_DLOPEN_DISABLED`, and package resolution disables the `"node-addons"` export condition so packages can select a non-native fallback.

```sh
bun --no-addons app.js
```

## Disposable stack globals

*Batch: `1.3-guide`.*

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

## Embedded native libraries

*Batch: `1.4-3`.*

Native libraries embedded by `bun build --compile` can be opened with `dlopen()`, allowing compiled applications to ship FFI dependencies inside the executable.

## Environment and DOM-free TypeScript declarations

*Batch: `1.2.8`.*

An augmentation of `Bun.Env` now applies to `process.env` as well, keeping custom environment-variable types consistent across both access paths. The ambient definitions for `AbortSignal`, `BroadcastChannel`, and `URLSearchParams` also work when `lib.dom` is omitted.

## Eval and print argument layout

*Batch: `1.2.4`.*

`bun --eval` and `bun --print` no longer insert a synthetic `[eval]` path into `process.argv`. The executable is followed directly by user arguments, matching Node.js.

```sh
bun --print "process.argv" arg1 arg2
# ["/path/to/bun", "arg1", "arg2"]
```

## Event-loop delay histograms

*Batch: `1.2.22`.*

`monitorEventLoopDelay()` from `node:perf_hooks` returns an `IntervalHistogram` that samples event-loop delay in nanoseconds and supports `enable()`, `disable()`, percentile queries, and `reset()`.

```ts
import { monitorEventLoopDelay } from "node:perf_hooks";
const delay = monitorEventLoopDelay({ resolution: 20 });
delay.enable();
await Bun.sleep(100);
delay.disable();
console.log(delay.percentile(99));
```

## Expanded WebAssembly proposals

*Batch: `1.3.14`.*

The runtime now supports Relaxed SIMD instructions, and Memory64 support extends to atomics, bulk-memory operations, memory growth, and memory-size queries.

## Experimental global virtual store

*Batch: `1.3.14`.*

The isolated package linker can share eligible immutable packages through one global `<cache>/links/` store instead of materializing them separately per project; the feature is off by default, and packages with patches, trusted lifecycle scripts, or an ineligible dependency closure fall back to project-local copies. Enable it in `bunfig.toml` and install with the isolated linker, or set `BUN_INSTALL_GLOBAL_STORE=1`.

```toml
[install]
globalStore = true
```

## Experimental stream iterators

*Batch: `1.4-3`.*

The `node:stream/iter` and `node:zlib/iter` modules provide iterator-oriented helpers such as `map()` and `filter()` when Bun is started with `--experimental-stream-iter`.

## Explicit resource management

*Batch: `1.2-guide`.*

Bun supports `using`/`await using` and implements disposal for APIs including `Bun.spawn()`, `Bun.serve()`, `Bun.connect()`, `Bun.listen()`, and `bun:sqlite`. Those resources are closed at scope exit even when an exception is thrown.

## FFI C-string migration

*Batch: `1.4-2`.*

In `bun:ffi`, a `cstring` return or callback argument is now a JavaScript string, with a null pointer represented as `null`; `new CString(ptr)` likewise returns a string without `.ptr`, `.byteLength`, or `.arrayBuffer`. Keep the original pointer separately when native code must free it.

## FFI compiler search paths

*Batch: `1.3.7`.*

The C compiler used by `bun:ffi` now honors `C_INCLUDE_PATH` and `LIBRARY_PATH`, enabling headers and libraries in nonstandard layouts such as Nix store paths.

## Fluent `BroadcastChannel.unref()`

*Batch: `1.2.14`.*

`BroadcastChannel.prototype.unref()` now returns the channel instance rather than `undefined`, so it can be used in a method chain.

## FreeBSD and Android builds

*Batch: `1.3.14`.*

Bun now provides first-party native builds for FreeBSD and Android.

## Glob literal-segment behavior

*Batch: `1.4-4`.*

An explicitly named dotfile segment matches without `dot: true`, and literal path segments traverse symlinked directories without `followSymlinks: true`.

## Heap profiling

*Batch: `1.3.7`.*

`--heap-prof` writes a V8-compatible `.heapsnapshot`, while `--heap-prof-md` emits a searchable Markdown report with retained sizes, object listings, and retainer chains. Use `--heap-prof-name` and `--heap-prof-dir` to control the output.

## Import attributes

*Batch: `1.2-guide`.*

Static and dynamic imports support `with { type: ... }`; Bun-specific useful types include `json`, `text`, `toml`, and `file`. Dynamic import places the same object under an options object's `with` key.

```ts
import config from "./bunfig.toml" with { type: "toml" };
const { default: text } = await import("./note.txt", { with: { type: "text" } });
```

## In-process cron scheduling

*Batch: `1.3.12`.*

`Bun.cron(expression, callback)` runs non-overlapping callbacks in-process on a UTC schedule; the next invocation is not scheduled until a returned promise settles. Jobs are disposable, support `ref()`/`unref()`, and are cleared during `--hot` reevaluation; thrown errors and rejections follow `setTimeout`-style process error handling.

```ts
Bun.cron("0 9 * * *", async () => {
  await sendDailyReport();
});
```

## IPv6 interface scope identifiers

*Batch: `1.2.19`.*

`os.networkInterfaces()` now exposes the Node-compatible IPv6 property `scopeid`; the previous `scope_id` property is no longer present.

## Iterator membership helper

*Batch: `1.4-4`.*

`Iterator.prototype.includes()` is enabled by default, so iterator membership can be tested without first collecting its values.

```js
["a", "b"].values().includes("b"); // true
```

## JSON console formatting

*Batch: `1.3.4`.*

`console.log()` and related console methods now support Node-compatible `%j` formatting, which JSON-stringifies the corresponding value.

```js
console.log("%j", { status: "ok" }); // {"status":"ok"}
```

## Linux garbage-collection signal

*Batch: `1.2.2`.*

Bun now uses `SIGPWR` instead of `SIGUSR1` to suspend threads for garbage collection on Linux. Applications can use `SIGUSR1` for reload or other logic without colliding with the runtime; `SIGPWR` is now used internally.

## Local-time cron and literal shell globs

*Batch: `1.4-2`.*

`Bun.cron.parse()` and in-process `Bun.cron()` now interpret schedules in local time; pass `{ tz: "UTC" }` as the final argument to retain UTC. `Bun.$` expands only `*`, `**`, and braces written literally in the template, not patterns supplied through interpolation, variables, command substitution, or quotes, and a redirect expanding to multiple words now fails as ambiguous.

## Low-memory notifications

*Batch: `1.4`.*

The cross-platform `memoryPressure` process event lets applications shed caches, idle connections, or workers before the operating system kills them. Its level is `"warning"` or `"critical"` on macOS and `"critical"` on Linux and Windows.

```ts
process.on("memoryPressure", (level) => {
  cache.clear();
  pool.drainIdle();
});
```

## Markdown CPU profiles

*Batch: `1.3.7`.*

`--cpu-prof-md` writes a Markdown CPU profile with hot functions, call trees, caller/callee details, and per-file time. It can be used alone or alongside `--cpu-prof`, and honors `--cpu-prof-name` and `--cpu-prof-dir`.

## Markdown list callback metadata

*Batch: `1.3.11`.*

`Bun.markdown.render()` now always passes `listItem` callbacks metadata containing zero-based `index`, `depth`, `ordered`, `start`, and `checked`; `list` callbacks now receive `depth`. Always passing the `listItem` metadata object is a breaking change for callbacks that depended on it being absent outside task lists.

```ts
Bun.markdown.render(markdown, {
  listItem: (children, { index, depth, ordered, start, checked }) => children,
  list: (children, { depth }) => children,
});
```

## musl Linux builds

*Batch: `1.2-guide`.*

Bun now ships x64 and aarch64 musl builds for distributions such as Alpine, including the `oven/bun:alpine` container image. The glibc build remains recommended unless musl compatibility or a smaller image is specifically needed.

## Native headless browser automation

*Batch: `1.3.12`.*

`Bun.WebView` drives the system WebKit view on macOS or Chrome/Chromium through CDP cross-platform. Selector actions wait for visible, stable, unobscured elements and dispatch trusted OS-level input; the API also covers navigation, evaluation, screenshots, scrolling, page state, events, and raw CDP calls.

```ts
await using view = new Bun.WebView({ width: 800, height: 600 });
await view.navigate("https://example.com");
await view.click("a.docs");
const title = await view.evaluate("document.title");
await Bun.write("page.png", await view.screenshot({ format: "png" }));
```

## Native JSON5 parsing and imports

*Batch: `1.3.7`.*

`Bun.JSON5` provides `parse()` and `stringify()`, and `.json5` files can be imported directly.

```ts
const config = Bun.JSON5.parse(`{ host: 'localhost', port: 5432, }`);
import settings from "./config.json5";
```

## Native JSONC parsing

*Batch: `1.3.6`.*

`Bun.JSONC.parse()` accepts line and block comments plus trailing commas, so JSONC configuration files no longer need a third-party parser.

```ts
const config = Bun.JSONC.parse(`{
  // Local service
  "port": 3000,
}`);
```

## Native REPL interface

*Batch: `1.3.10`.*

Bun's REPL is now built in rather than downloaded as a third-party package. Its terminal UI adds persistent history in `~/.bun_repl_history`, tab completion, multiline editing, syntax highlighting, Emacs-style line editing, `.copy`/`.load`/`.save`/`.editor` commands, and `_`/`_error` values for the last result and error.

## Native resource-management syntax in Bun output

*Batch: `1.3.14`.*

`bun run`, `Bun.Transpiler({ target: "bun" })`, and `bun build --target=bun` now preserve `using` and `await using` instead of lowering them to helper calls. Browser and Node targets continue to lower the syntax.

## Native XML and TOML

*Batch: `1.4-2`.*

`Bun.XML.parse()`/`stringify()` provide native XML conversion, and importing `.xml` now returns the parsed document at runtime and during builds; use `--loader .xml:file` to retain path imports. `Bun.TOML` now implements TOML 1.1 parsing and stringification, with invalid syntax reported as `SyntaxError`.

## Native YAML imports and parsing

*Batch: `1.2.21`.*

`.yaml` and `.yml` files can be default-imported as parsed data, while `Bun.YAML.parse()` parses YAML strings at runtime.

```ts
import config from "./config.yaml";
import { YAML } from "bun";
const items = YAML.parse("- one\n- two");
```

## Nested `.env` defaults

*Batch: `1.4-4`.*

Bun's `.env` parser now handles nested expansions inside the `${VAR:-default}` form.

```dotenv
ORIGIN=${PUBLIC_ORIGIN:-https://${HOST}:${PORT}}
```

## New JavaScript built-ins

*Batch: `1.2-guide`.*

Bun now implements `Promise.withResolvers()`, `Promise.try()`, `Error.isError()`, `Float16Array`, and iterator helpers `map`, `flatMap`, `filter`, `take`, `drop`, `reduce`, `toArray`, `forEach`, and `find`. `Uint8Array` also gains static `fromBase64()`/`fromHex()` and instance `toBase64()`/`toHex()` conversions.

## New Web API coverage

*Batch: `1.2-guide`.*

Newly supported APIs include `TextDecoderStream`, `TextEncoderStream`, streaming `TextDecoder.decode(..., { stream: true })`, `URL.createObjectURL()` for blobs, `AbortSignal.any()`, and functional `console.group()`/`groupEnd()`. `Response`, `Blob`, and `Bun.file()` gain `bytes()` returning `Uint8Array`, while `fetch()` request bodies can be async iterables for streaming uploads.

## Official Alpine image baseline

*Batch: `1.3.2`.*

The official Alpine images for x64 and arm64 musl now use Alpine 3.22, changing the base packages and compatibility environment inherited by container builds.

## OpenTelemetry and Datadog instrumentation

*Batch: `1.4`.*

OpenTelemetry's HTTP and filesystem instrumentations now export spans, while `shimmer` and `require-in-the-middle` can patch bundled code. `dd-trace` can trace applications and `@datadog/pprof` can profile them continuously.

## OS-level cron jobs and expression parsing

*Batch: `1.3.11`.*

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

## Performance histograms

*Batch: `1.2.15`.*

`createHistogram()` from `node:perf_hooks` records sampled integer distributions with configured bounds and precision, exposing statistics such as minimum, maximum, mean, standard deviation, count, and percentiles.

```js
import { createHistogram } from "perf_hooks";

const histogram = createHistogram({ lowest: 1, highest: 1_000_000, figures: 3 });
histogram.record(100);
histogram.record(200);
console.log(histogram.percentile(50), histogram.totalCount);
```

## Precise numeric summation

*Batch: `1.2.18`.*

Bun now implements the Stage 3 `Math.sumPrecise()` API, which sums numeric iterables with substantially better floating-point accuracy than a naive reduction.

```js
Math.sumPrecise([0.1, 0.2, 0.3, -0.5, 0.1]); // 0.2
```

## Preloading through the environment

*Batch: `1.2.11`.*

`BUN_INSPECT_PRELOAD` specifies a module to load before the entry script and is equivalent to passing `--preload`.

```sh
BUN_INSPECT_PRELOAD=./setup.js bun run index.js
```

## React elements from Markdown

*Batch: `1.3.8`.*

`Bun.markdown.react()` returns a React Fragment and accepts element overrides such as `h1`. Its default element format targets React 19; pass `reactVersion: 18` when using React 18 or older.

```tsx
function Markdown({ text }: { text: string }) {
  return Bun.markdown.react(text, {
    h1: ({ children }) => <h1 className="title">{children}</h1>,
  });
}
```

## Recursive Linux file watching

*Batch: `1.3.14`.*

On Linux, `fs.watch(path, { recursive: true })` now begins watching directories created after the watcher starts. Deleting and recreating a watched file also re-establishes its watch, so later modifications emit `change` events again.

## REPL transforms with `Bun.Transpiler`

*Batch: `1.3.7`.*

`replMode: true` transforms input for persistent interactive evaluation: declarations are hoisted, `const` becomes redeclarable, the final expression is captured, object literals are recognized, and top-level await is wrapped appropriately.

```ts
const transpiler = new Bun.Transpiler({ loader: "tsx", replMode: true });
const transformed = transpiler.transformSync("await Promise.resolve(42)");
```

## Scoped async context

*Batch: `1.4-3`.*

`AsyncLocalStorage` accepts the Node 26 `name` and `defaultValue` constructor options, while `withScope(value)` returns a disposable scope that restores the prior store when it is disposed.

## Slow-filesystem warning control

*Batch: `1.4-4`.*

Set `BUN_DISABLE_SLOW_FILESYSTEM_WARNING=1` to suppress Bun's slow-filesystem notice.

## Spawn timeouts

*Batch: `1.2.6`.*

The `timeout` option for spawned processes terminates a command after the specified milliseconds; synchronous results expose `exitedDueToTimeout` so callers can distinguish this exit path.

```ts
const result = Bun.spawnSync({ cmd: ["sleep", "1000"], timeout: 1_000 });
console.log(result.exitedDueToTimeout); // true
```

## Streaming compression Web APIs

*Batches: `1.3.3`, `1.4`.*

Bun now implements `CompressionStream` and `DecompressionStream`, allowing data to be compressed through `ReadableStream` pipelines without buffering the full payload. In addition to `gzip`, `deflate`, and `deflate-raw`, Bun accepts `brotli` and `zstd`.

The streams compress or decompress incrementally and interoperate with fetch, file, and subprocess streams.

```ts
const input = new Blob(["payload"]).stream();
const compressed = input.pipeThrough(new CompressionStream("zstd"));
const output = compressed.pipeThrough(new DecompressionStream("zstd"));
console.log(await new Response(output).text()); // "payload"
```

```ts
const decoded = response.body!
  .pipeThrough(new DecompressionStream("gzip"))
  .pipeThrough(new TextDecoderStream());
```

## Streaming decoded text

*Batch: `1.4-2`.*

`Request.textStream()` and `Response.textStream()` return `ReadableStream<string>` values decoded as UTF-8, preserving split multibyte characters, stripping a leading BOM, and replacing invalid sequences. This avoids manually piping a byte body through `TextDecoderStream`.

## Streaming WebAssembly compilation

*Batch: `1.2.20`.*

`WebAssembly.compileStreaming()` and `WebAssembly.instantiateStreaming()` now compile directly from a response body instead of first buffering the complete Wasm module.

```js
const { instance } = await WebAssembly.instantiateStreaming(
  fetch("http://localhost:3000/add.wasm"),
);
```

## Stricter deep equality

*Batch: `1.2.2`.*

`Bun.deepEquals()` no longer treats objects as equal merely because their indexed properties or prototypes match when their internal types differ. Because `bun:test`'s `toEqual()` uses the same comparison, tests that depended on the looser behavior may now fail.

```ts
Bun.deepEquals({ 0: 5, 1: 6, 2: 7 }, new Uint8Array([5, 6, 7])); // false
```

## Structured-clone identity

*Batch: `1.4-2`.*

`structuredClone()` now preserves repeated identity for special objects including dates, regular expressions, errors, DOM exceptions, crypto keys, certificates, blobs, and files. Two references to the same such source object therefore become two references to one cloned object.

## Structured-data parser changes

*Batch: `1.4-2`.*

`Bun.YAML` follows YAML 1.2, so `yes`, `no`, `on`, and `off` are strings while only `true` and `false` spellings are booleans; parsing also supports cyclic aliases. `Bun.JSONC.parse()` now throws `SyntaxError` for invalid or empty input, and TOML rejects unquoted strings, adjacent key/value pairs without a newline, and integers beyond `Number.MAX_SAFE_INTEGER`.

## Temporal enabled by default

*Batch: `1.4-2`.*

`Temporal` and `Date.prototype.toTemporalInstant` are defined by default, and Bun's deep-equality and test matchers compare Temporal values rather than treating all instances of one Temporal class as equal. Set `BUN_JSC_useTemporal=0` to disable the globals.

## Timer cancellation boundaries

*Batch: `1.2.18`.*

`clearImmediate()` no longer clears timeouts or intervals. `clearTimeout()` and `clearInterval()` continue to clear either kind of timer.

## Type environment auto-detection

*Batch: `1.3-guide`.*

`@types/bun` now selects Node.js or DOM types from the project's enabled libraries to reduce conflicts. When DOM types are enabled they take precedence, so Bun-specific extensions such as extra `WebSocket` constructor options may still produce type errors.

## TypeScript 7 and transform semantics

*Batch: `1.4-2`.*

New `bun init` projects use TypeScript 7-compatible configuration and install `typescript@^7`. Bun now honors `useDefineForClassFields: false`, while `"jsx": "react-jsx"` selects the production `jsx`/`jsxs` runtime and `"react-jsxdev"` explicitly selects `jsxDEV`.

## Unicode-accurate terminal widths

*Batch: `1.3.5`.*

`Bun.stringWidth()` now treats additional Unicode formatting and combining characters as zero-width, ignores complete CSI and OSC escape sequences, and measures emoji by grapheme rather than code point. Flags, skin-tone sequences, ZWJ emoji, keycaps, and variation selectors therefore produce terminal-cell widths rather than inflated component totals.

```ts
Bun.stringWidth("🇺🇸"); // 2
Bun.stringWidth("👋🏽"); // 2
Bun.stringWidth("👨‍👩‍👧"); // 2
Bun.stringWidth("\u2060"); // 0
```

## Vercel Functions runtime

*Batch: `release-index`.*

Vercel Functions can now run on the Bun Runtime with full access to Bun APIs. This makes Vercel a deployment target for functions that depend on Bun-specific runtime features.

## Watch-mode restart signals

*Batch: `1.4-3`.*

`--watch-kill-signal` delivers the configured signal to JavaScript signal listeners before watch mode restarts the process.

## Web-stream interoperability and typings

*Batch: `1.4-4`.*

`stream.finished()` now accepts WHATWG `ReadableStream` and `WritableStream` instances. Bun's `ReadableStream` types no longer advertise the nonexistent `.formData()` and `.arrayBuffer()` methods; use a `Response` wrapper for those conversions.

## WebAssembly promise integration

*Batch: `1.4-3`.*

JavaScript Promise Integration is enabled by default through `WebAssembly.Suspending` and `WebAssembly.promising`, allowing Wasm calls to suspend directly on JavaScript promises. Bun also supports multi-memory and accepts `compileOptions` in `WebAssembly.compileStreaming()` and `instantiateStreaming()`.

## Windows long-path support

*Batch: `1.2.20`.*

Bun now consistently supports Windows file paths longer than 260 characters through its application manifest, so deeply nested paths work without special path namespacing.

## Windows native-library compatibility

*Batch: `1.4-4`.*

`bun:ffi` now works on Windows ARM64, and `dlopen()` accepts library paths containing non-ASCII characters on Windows.

## Windows pseudo-terminals

*Batch: `1.3.14`.*

`Bun.Terminal` and `Bun.spawn({ terminal })` now work on Windows through ConPTY, including TTY detection, input, output callbacks, and resizing. POSIX termios flags remain zero-valued no-ops there, and ConPTY output may use escape sequences that are semantically equivalent but not byte-identical to the child's output.

## Windows recursive-mkdir return paths

*Batch: `1.2.13`.*

On Windows, recursive `fs.mkdirSync()` with an absolute path now returns the first created directory with its NT path prefix, such as `\\?\C:\path`, matching newer Node.js versions. Code comparing or reusing that return value must account for the prefixed form.

## Windows terminal resize events

*Batch: `1.3.3`.*

On Windows, `process.stdout` now emits `resize` events and Bun delivers `SIGWINCH`, allowing terminal applications to use the same resize handling as on other platforms.

```ts
process.stdout.on("resize", () => console.log(process.stdout.columns));
```

## X25519 key generation

*Batch: `1.2.1`.*

`node:crypto` key-pair generation now supports X25519 for Diffie-Hellman key exchange; both encoded keys can be requested with the usual Node options.

```ts
import crypto from "node:crypto";

const keys = crypto.generateKeyPairSync("x25519", {
  publicKeyEncoding: { type: "spki", format: "der" },
  privateKeyEncoding: { type: "pkcs8", format: "der" },
});
```

## YAML serialization and binary parsing

*Batch: `1.2.22`.*

`Bun.YAML.stringify()` serializes JavaScript values to YAML. `Bun.YAML.parse()` now also accepts `Buffer`, `ArrayBuffer`, typed arrays, `DataView`, and `Blob` input.

```ts
const text = Bun.YAML.stringify({ enabled: true });
const value = Bun.YAML.parse(new TextEncoder().encode(text));
```

## Zstandard compression

*Batch: `1.2.14`.*

`fetch()` now advertises `gzip, deflate, br, zstd` by default and transparently decompresses `Content-Encoding: zstd` responses. Bun also provides synchronous and asynchronous Zstandard helpers.

```ts
const compressed = Bun.zstdCompressSync("hello world", { level: 5 });
const restored = Bun.zstdDecompressSync(compressed);
const asyncCompressed = await Bun.zstdCompress("hello world");
const asyncRestored = await Bun.zstdDecompress(asyncCompressed);
```
