# Deno 2 Migration

Replace removed Deno 1 surfaces and account for compatibility changes and changed defaults.

## CLI path escaping and runtime logging (2.0.0)

In path-based flags, a doubled comma escapes a literal comma inside a value. Runtime logging is configured with `DENO_LOG` instead of `RUST_LOG`.

```sh
deno run --allow-read=/tmp/with,,comma main.ts
```

## Configuration validation (2.0.0)

Supported `compilerOptions` are now an allowlist and unsupported options produce errors. Remote import maps and the deprecated `files` configuration are no longer supported in `deno.json`.

## Decompressed response headers (2.9.0)

Automatically decompressed fetch responses retain their `content-encoding` and `content-length` headers. Consumers must not assume that `content-length` is the byte length of the decoded body.

## Default minimum dependency age (2.9-guide)

The npm `min-release-age` policy is now enabled by default at 24 hours; explicit configuration still takes precedence. Set another duration in `.npmrc`, or use `0` to opt out.

```ini
min-release-age=0
```

## Explicit target for config-free formatting (2.5.0)

When no files are passed and no configuration file is discovered, `deno fmt` now prompts for or requires an explicit current-directory target. Scripts that relied on argument-free formatting should pass `.`.

```sh
deno fmt .
```

## Import permissions (2.0.0)

The new `--allow-import` flag controls permitted module imports; `cdn.jsdelivr.net` is importable by default. Reading `Deno.mainModule` itself no longer requires a permission grant.

```sh
deno run --allow-import main.ts
```

## Machine-readable and server output (2.0.0)

Every `--json` output now includes the Deno version, while `deno info` output no longer includes `emit` or `map`. The server's `Listening on` message is written to stderr instead of stdout.

## Node-style timers by default (2.6.0)

Global `setTimeout()` and `setInterval()` now return Node-compatible timer objects by default rather than Web-style numeric IDs. Code can call methods such as `unref()` without enabling `--unstable-node-globals`, but code that assumes timer handles are numbers must be updated.

```ts
const timer = setTimeout(() => {}, 1_000);
timer.unref();
```

## Opt-in server compression (2.9-guide)

`Deno.serve()` no longer compresses response bodies automatically; enable it per server with `automaticCompression: true` or process-wide with `DENO_SERVE_AUTOMATIC_COMPRESSION=1`.

```ts
Deno.serve(
  { automaticCompression: true },
  () => new Response("hello"),
);
```

## Permission errors and subprocess environments (2.0.0)

Permission failures now use the `NotCapable` error kind. Launching a subprocess with any `LD_`- or `DYLD_`-prefixed environment variable requires unrestricted `--allow-run`, not a command allowlist.

## Removed commands and broad flags (2.0.0)

Deno 2 removes `deno bundle` and `deno vendor`. It also removes `--allow-hrtime`, `--allow-none`, `--jobs`, `--trace-ops`, `--ts`, the generic `--unstable` flag, and `--lock-write`, so 1.x automation using them must be revised.

## Required 2.3.1 follow-up (2.3.0)

The 2.3.0 release was produced with incorrect version metadata and can report the wrong version. Upgrade to 2.3.1 rather than remaining on this build.

```sh
deno upgrade 2.3.1
```

## Resource-oriented API removals (2.0.0)

`Deno.File`, `Deno.Buffer`, the reader, writer, closer, and seeker interfaces, direct `new Deno.FsFile()` construction, and resource `.rid` properties are gone. The removed free functions include `close`, `copy`, `iter`, `read`, `readAll`, `seek`, `shutdown`, `write`, `writeAll`, and the `fdatasync`, `flock`, `fstat`, `fsync`, `ftruncate`, `funlock`, and `futime` families, including their synchronous forms.

## Soft-removed legacy runtime APIs (2.0.0)

`Deno.run()`, `Deno.isatty()`, and `Deno.serveHttp()` are soft-removed, while `Deno.run()` no longer supports `clearEnv`, `gid`, or `uid`. `Deno.customInspect` is removed outright.

## Test sanitizers are opt-in (2.8-guide)

`sanitizeOps` and `sanitizeResources` now default to `false`. Enable them per test with the existing options, for a whole module with `Deno.test.sanitizer()`, or globally under the `test` configuration.

```ts
Deno.test.sanitizer({ ops: true, resources: true });
Deno.test("strict test", () => {});
```

## TLS and window-surface option changes (2.0.0)

`Deno.ConnectTlsOptions` no longer has `certChain`, `certFile`, or `privateKey`, and `Deno.ListenTlsOptions` no longer has `certChain`, `certFile`, or `keyFile`. WebGPU window `width` and `height` options now belong on the `UnsafeWindowSurface` constructor.

## Type-checking defaults (2.0.0)

Deno 2 uses TypeScript 5.6 and `npm:@types/node@22`, and enables `noImplicitOverride` and `useUnknownInCatchVariables` during checking. Overrides therefore need the `override` modifier, and caught values are `unknown` unless narrowed.

## UDP listener default (2.8-guide)

`Deno.listenDatagram()` now defaults its hostname to `0.0.0.0`, matching `Deno.listen()` and changing which interfaces an omitted hostname binds.

## URL serialization (2.9.1)

`URL` and `URLSearchParams` are no longer serializable. Code using serialization-dependent APIs should pass their string forms and reconstruct the objects at the destination.
