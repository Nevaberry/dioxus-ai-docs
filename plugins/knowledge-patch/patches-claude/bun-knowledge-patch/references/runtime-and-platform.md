# Runtime APIs and platforms

## CLI and process configuration

### Command behavior (`1.2-guide`, `1.2.4`)

- `bun run <script>` changes cwd to the directory containing `package.json`,
  matching npm and Yarn rather than the invoking shell.
- `bun -p` is `--print`, not `--port`.
- Under `-p`/`-e`, `process.argv` omits the old cwd `[eval]` slot and keeps the
  first user argument.
- `test.only()` no longer needs a CLI `--only`; testing details are separate.

### Global runtime options (`1.2.11`, `1.2.15`)

`BUN_INSPECT_PRELOAD` is the environment equivalent of `--preload`.
`BUN_OPTIONS` parses shell-like quoting and prepends its flags to every Bun
invocation.

```sh
BUN_INSPECT_PRELOAD=./setup.js bun run index.js
BUN_OPTIONS="--config='./my config.toml' --silent" bun run app.ts
```

### Environment loading (`1.3.3`, `1.4-2`)

`--no-env-file` and bunfig `env = false` disable implicit `.env` discovery but
do not prevent explicitly named `--env-file` files.

When Bun is acting as Node through `bun --bun`, `bunx --bun`, or a `node`
symlink, it does not auto-load `.env`, `.env.local`, or environment-specific
files. A normal `bun file.js` still does.

### Rejection and warning modes (`1.2.17`, `1.4-3`)

`--unhandled-rejections` accepts `throw`, `strict`, `warn`, and `none`; Bun's
default remains different from Node's warning mode. `rejectionHandled` events
work. Warning flags for suppression, stack traces, redirects, and disabling
selected warnings are wired up.

### Inspection depth and CPU profiling (`1.2.19`, `1.3.2`, `1.3.9`, `1.4`)

- `--console-depth=N` or `[run] console.depth` sets object inspection depth;
  default is 2 and CLI wins.
- `--cpu-prof`, optional name/directory, writes Chrome `.cpuprofile` at 1ms
  sampling. `--cpu-prof-interval` changes microseconds.
- `--cpu-prof-md` can add a Markdown form.
- `BUN_CPU_PROFILE=1` enables profiling when command flags cannot be changed.

### Heap profiling (`1.3.7`, `1.3.10`)

`--heap-prof` emits V8-compatible snapshots with name/directory controls;
`--heap-prof-md` adds Markdown. `Bun.generateHeapSnapshot("v8",
"arraybuffer")` returns UTF-8 JSON bytes without large-string limits and can be
passed directly to `Bun.write()`.

### REPL (`1.3.7`, `1.3.10`, `1.4-2`)

`Bun.Transpiler({ replMode: true })` preserves declarations between inputs,
turns const into redeclarable let, captures the trailing value, interprets an
object literal correctly, and switches to async for top-level await.

`bun repl` is native and provides `_`, `_error`, copy/load/save/editor/clear,
completion, and persistent history. `bun repl -e` evaluates; `-p` evaluates and
prints. `bun --interactive` enters the ported Node REPL (`1.4-3`).

## Files, blobs, streams, and globs

### Bun file operations (`1.2-guide`, `1.2.2`, `1.2.3`)

`Bun.file()` supports `delete`/`unlink`, Node-style `stat`, and `bytes`; bytes
also exist on Response and Blob. File writers flush pending bytes at process
exit. Ending a writer created from a caller-owned file descriptor does not close
that descriptor.

### Blob mutation errors (`1.2.20`)

Calling write, writer, unlink, or delete on a byte-backed Blob throws rather
than silently doing nothing. Those operations are for file-backed blobs.

### Direct streams and sink backpressure (`1.4-4`)

For `ReadableStream` with `type: "direct"`, controller `write()` returns a
negative number under backpressure; `await flush(true)` waits for drain. Data
written after a flush in `pull()` reaches pipeTo, pipeThrough, tee, async
iteration and `Response.textStream()`. `FileSink.write()` may return a promise.

```ts
new ReadableStream({
  type: "direct",
  async pull(controller) {
    if (controller.write(chunk) < 0) await controller.flush(true);
  },
});
```

### Text streams (`1.4`)

`Response.textStream()` returns a UTF-8 `ReadableStream<string>`.

### `Bun.Glob` semantics (`1.4-4`)

Literal dot segments such as `.env` match without `dot: true`, and literal
segments traverse a symlinked directory without `followSymlinks: true`.
Wildcard patterns that assumed dotfiles were hidden can return more results.

### Memory mapping (`1.4-2`)

`Bun.mmap(path, { offset })` returns a view whose index zero is exactly that
offset. Remove page-offset compensation used for the previous rounded view.

## Subprocesses and terminals

### Timeouts, limits, and streaming (`1.2.6`, `1.2.9`, `1.2.18`)

- Bun spawn/sync accepts `timeout` in milliseconds and reports
  `exitedDueToTimeout`.
- `maxBuffer` kills a child once buffered output exceeds the byte limit.
- `stdin` accepts a ReadableStream and streams without full buffering.

### Argument validation (`1.3.6`, `1.4-2`)

NUL bytes in spawn arguments, environment values, and shell template literals
are rejected. Bun.spawn also rejects `timeout: NaN`, signal zero, NUL in
`argv0`/`cwd`, and an already-aborted signal without creating a process.

### PTY API (`1.3.5`, `1.3.14`)

`Bun.spawn({ terminal })` attaches a pseudo-terminal. `proc.terminal` supports
write, resize, raw mode, ref/unref, and close. A standalone disposable
`Bun.Terminal` may be reused across spawns.

The API was POSIX-only when introduced and later gained Windows ConPTY. On
Windows terminal flag fields read zero and ignore writes, there is no unattached
kernel echo, and equivalent escape output may not be byte-identical.

### Stdio slots and path lookup (`1.4-4`)

`Bun.file(path|fd)` works in `stdio[3+]`, and caller descriptors are returned in
`proc.stdio[N]`. `"ignore"` above fd 2 closes the descriptor rather than opening
`/dev/null`. `spawnSync` honors detached. Relative PATH entries resolve against
the spawn `cwd`, not the parent cwd.

### Cgroups and orphan control (`1.3.14`, `1.4`)

`--no-orphans`, bunfig `run.noOrphans`, or
`BUN_FEATURE_FLAG_NO_ORPHANS=1` exits when the parent dies and SIGKILLs all
descendants. It is inherited on Linux/macOS and a no-op on Windows.

`Bun.spawn({ cgroup })` places a Linux child into a cgroup before execution.

## Shell

### Shell typing and glob rules (`1.2.11`, `1.4-2`)

`Bun.$` is both a value and a type. Shell glob expansion applies only to literal
`*`, `**`, and braces. Patterns from interpolation, variables, substitution, or
quotes are literal; `?`, brackets, and leading `!` never expand.

### Builtins (`1.3.10`, `1.4-4`)

Shell `echo` parses `-e`, `-E`, and combined flags. `.quiet()` takes a boolean,
bare `cd` uses HOME, `ls -l` emits a long listing, and empty interpolated
arguments survive. `{abc}` without a comma is literal; a redirect target
expanding to several words is an error.

### Print completion (`1.4-3`)

`bun -p '(await 1) + 1'` prints the module's final completion value rather than
the first awaited value.

## Built-in data formats

### YAML (`1.2.21`, `1.2.22`, `1.2.23`, `1.3.5`, `1.4-2`)

`.yaml`/`.yml` imports and `Bun.YAML.parse()` provide parsed values. Stringify
is supported, and parse accepts Buffer, ArrayBuffer, typed arrays, DataView, and
Blob. Invalid input produces `SyntaxError`; NUL input is rejected.

YAML follows 1.2 booleans: yes/no/on/off/y variants are strings and only
true/false are booleans. Stringify quotes colon-ending strings for round trips.

### JSONC (`1.3.6`, `1.4-2`)

`Bun.JSONC.parse()` accepts comments and trailing commas. Invalid input and an
empty string throw `SyntaxError`; the empty string no longer returns `{}`.

### JSON5 (`1.3.7`)

`Bun.JSON5.parse/stringify` and `.json5` imports cover comments, trailing
commas, unquoted keys, single quotes and hexadecimal numbers.

### JSON Lines (`1.3.7`)

`Bun.JSONL.parse()` consumes a string or Uint8Array, skipping a UTF-8 BOM.
`parseChunk()` returns values plus consumed-character `read`, `done`, and error,
allowing the incomplete suffix to carry to the next chunk.

### XML and TOML (`1.4`, `1.4-2`)

`Bun.XML` parses/serializes and `.xml` imports parse directly. `Bun.TOML`
tracks TOML 1.1.0 and stringifies.

TOML parsing and bunfig are strict: unquoted strings, missing newlines between
pairs, and unsafe integers throw `SyntaxError` rather than `BuildMessage`.

## Markdown and terminal text

### Width and ANSI removal (`1.2.21`, `1.3.5`, `1.3.7`)

`Bun.stripANSI()` removes escapes. `Bun.stringWidth()` is grapheme-aware: emoji
sequences count as width 2, zero-width characters as 0, and CSI/OSC—including
OSC 8 links—are excluded. Indic conjunct GB9c handling counts one cluster.

### ANSI wrapping and slicing (`1.3.7`, `1.3.11`)

`Bun.wrapAnsi(text, columns, options)` wraps without breaking escapes,
hyperlinks, wide characters, or emoji. `Bun.sliceAnsi` slices by display
columns, supports negative indices and optional ellipsis, retains styles, and
places the ellipsis outside links.

### Markdown parser (`1.3.8`)

`Bun.markdown.html()` renders CommonMark with GFM tables, strikethrough, task
lists, and autolinks enabled; wiki links, math, heading IDs and linked headings
are optional.

`render()` calls user handlers per element with rendered children and metadata;
return `null` to omit an element. `react()` returns a Fragment in React 19
format and accepts component overrides or `reactVersion: 18`.

### List callback change (`1.3.11`)

`listItem` always receives metadata, not only for task items. It contains index,
depth, ordered, start, and checked with undefined where irrelevant; `list` also
gets depth.

### ANSI Markdown (`1.3.12`)

`Bun.markdown.ansi()` supports colors, hyperlinks, wrapping columns and Kitty
images. Running `bun ./README.md` prints ANSI without starting the JS VM.

## Scheduling and browser automation

### OS-level cron (`1.3.11`)

`Bun.cron(path, expression, title)` registers crontab, launchd, or Task
Scheduler work and calls the default export's `scheduled()` when fired.
Re-registering a title replaces it; `Bun.cron.remove(title)` removes it.

`Bun.cron.parse()` handles five-field expressions, names, standard nicknames,
Sunday 7, and POSIX day-of-month/day-of-week OR semantics; it returns the next
Date or null when none appears in roughly four years.

### In-process cron (`1.3.12`, `1.4-2`)

`Bun.cron(schedule, callback)` keeps state in-process, never overlaps runs, and
reschedules after handlers settle. It is disposable, ref-counted, and cleared
before hot reload. Sync errors emit uncaughtException; async errors emit
unhandledRejection and exit without a listener.

Both parse and in-process scheduling now use the process's local time zone.
Pass `{ tz: "UTC" }` as the final argument for UTC. OS-level jobs continue to
follow system local time.

### WebView (`1.3.12`)

`Bun.WebView` exposes Playwright-style navigation, evaluation, screenshots,
native click/type/press/scroll, history/reload/resize, and raw CDP. Selectors
auto-wait for actionability and input is trusted OS input.

The method surface is `navigate`, `evaluate`, `screenshot({ format, quality,
encoding })`, coordinate- or selector-based `click`, `type`, `press` with
modifiers, `scroll`, `scrollTo`, `goBack`, `goForward`, `reload`, `resize`, and
`cdp`. `url`, `title`, and `loading` expose state.

Backends are macOS WKWebView or Chrome/Chromium over CDP. Constructor options
select backend/path/args, console capture, and persistent data store. Chrome
events are MessageEvents containing params. One browser process is shared and
additional views open tabs. Instances are disposable.

## Runtime utility APIs

### CSRF (`1.2.5`, `1.4-2`)

`Bun.CSRF.generate()` and `verify()` provide tokens. Both accept a `sessionId`
binding through HMAC associated data; verification fails closed when only one
side supplies it.

### Color, DNS, inspection, and IDs (`1.2-guide`)

- `Bun.color(input, format)` converts to CSS, ANSI, ANSI-16m/256, number, or
  RGBA-object forms.
- `Bun.dns.prefetch()` warms DNS and `getCacheStats()` reports cache metrics.
- `Bun.inspect.table(rows)` returns the console-table string.
- `Bun.randomUUIDv7()` generates sortable UUIDs.

UUIDv7 now throws RangeError after 2^48 milliseconds and for NaN, invalid, or
pre-1970 dates (`1.4-2`). `Bun.color`, Cookie Expires serialization, and
FileSystemRouter match output also changed; update exact-output assertions.

### Import attributes (`1.2-guide`)

Bun accepts `with { type: "text" }` and `with { type: "toml" }` alongside JSON.

### Resource disposal (`1.2-guide`, `1.3-guide`)

`using` works with serve, spawn, connect, listen, and sqlite.
`DisposableStack` and `AsyncDisposableStack` dispose several resources and
collect disposal errors before rethrowing.

### Hashes and strings (`1.2.16`)

`Bun.hash.rapidhash(input)` returns a non-cryptographic bigint hash.

### Native compression (`1.2.14`)

`Bun.zstdCompressSync`/`zstdDecompressSync` and async variants provide zstd
outside Fetch or node:zlib.

### Archive and image APIs

`Bun.Archive` (`1.3.6`) and `Bun.Image` (`1.3.14`) are described in
[databases and storage](databases-and-storage.md) because they directly consume
files, blobs, and S3 handles.

## FFI and native extensions

### Inline C and native plugins (`1.2-guide`, `1.3.7`)

`cc()` from `bun:ffi` compiles C source and exposes declared symbols without
node-gyp. N-API arg/return kinds are available there. It honors
`C_INCLUDE_PATH` and `LIBRARY_PATH` for non-FHS systems.

### JavaScriptCore FFI (`1.4`)

The FFI backend is JavaScriptCore's native FFI rather than TinyCC, and hot calls
can become direct C calls. `buffer_length` passes a typed-array length alongside
its pointer by passing the same value twice. `returns: "cstring"` yields a
plain string or null.

### CString and JIT constraints (`1.4-2`)

`new CString(ptr)` returns a plain string with no pointer, byteLength, or
arrayBuffer; retain the original pointer when freeing memory. `napi_env` and
`napi_value` types throw outside `cc()`, and `dlopen()` throws with JIT disabled.
Shared libraries embedded into a compiled binary can be opened (`1.4-3`).

## Signals, errors, and runtime semantics

### Linux user signal (`1.2.2`)

JavaScriptCore uses SIGPWR for GC suspension, leaving SIGUSR1 available to
applications. Do not take over SIGPWR.

### Async stacks (`1.3-guide`)

Async call chains appear in rejection stacks through `at async` caller frames,
changing logs and parsers.

### Error types and strict values (`1.2.20`, `1.4-2`)

- `Bun.resolve` and resolveSync always throw Error objects.
- `Response.redirect()` throws RangeError for an invalid status.
- Environment values longer than 4096 bytes are no longer truncated.
- Callback exceptions in fs, DNS and `crypto.pbkdf2` surface as
  uncaughtException rather than unhandledRejection.
- X509 serial numbers, legacy modulus, and peer-certificate hex are uppercase.
- Argon2 `Bun.password.hash()` requires `memoryCost >= 8`; existing lower-cost
  hashes still verify.

### Temporal (`1.4-2`)

Temporal and `Date.prototype.toTemporalInstant` are defined by default;
`BUN_JSC_useTemporal=0` disables them.

### Windows console signals (`1.3.14`)

SIGHUP and SIGBREAK listeners receive Windows console close/break events rather
than acting as inert EventEmitter names.

### Memory pressure (`1.4`)

`process` emits `memoryPressure` for OS low-memory notifications. Levels are
warning/critical on macOS and critical elsewhere, allowing caches and idle pools
to be released before termination.

## Platform support and deployment

### Linux and containers (`1.2-guide`, `1.2.10`, `1.3.12`, `1.4-2`)

- musl/Alpine x64 and aarch64 builds ship through `oven/bun:alpine`; they are
  slightly slower than glibc.
- Docker images moved from Debian Bullseye to Bookworm.
- Linux CPU-count APIs and Bun thread pools honor cgroup quotas.
- The glibc minimum is 2.17, with a kernel 3.10 fallback controlled by
  `BUN_FEATURE_FLAG_DISABLE_MEMFD`. x64 releases are baseline-only, though old
  baseline artifact names resolve.

### Windows, FreeBSD, and Android (`1.2.20`, `1.3.10`, `1.3.14`, `1.4-2`)

Windows supports paths longer than 260 characters and native ARM64. First-party
FreeBSD x86_64/aarch64 builds support the full runtime on 14.3+, and Android
builds are experimental. Bun works in Windows AppContainer and read-only
directories.

### Runtime implementation (`release-index`)

Bun's source and contributor toolchain are Rust rather than Zig. This does not
change JavaScript APIs or the N-API ABI used by addons written in Zig, C, or
Rust, but Bun-internal advice based on a Zig source tree is stale.

### Vercel (`release-index`)

Vercel Functions can select Bun as the runtime and use Bun-specific APIs such as
file, serve, and sqlite without reshaping the application for Node.

### Slow-filesystem warning (`1.4-4`)

Set `BUN_DISABLE_SLOW_FILESYSTEM_WARNING=1` to suppress the notice.

## Additional behavior changes

- Files with an unknown extension are executed by `require()` as JavaScript,
  not returned as path strings (`1.3-guide`).
- `Bun.stringWidth` and terminal output are grapheme-aware as described above.
- `HTMLRewriter.getAttribute()` returns `""` for present empty/boolean
  attributes; invalid set/remove arguments throw rather than returning Error
  (`1.4-4`).
- Cyclic array stringification throws RangeError instead of returning empty
  text, and iterator `includes()` is available (`1.4-4`).
- `BUN_DISABLE_SLOW_FILESYSTEM_WARNING` affects only the warning, not
  filesystem behavior.
