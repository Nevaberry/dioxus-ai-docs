# Deno 2 Migration
Apply removals, replacements, changed defaults, and compatibility transitions when modernizing a project.
## Contents
- [Removed commands and APIs](#removed-commands-and-apis)
- [Configuration and CLI changes](#configuration-and-cli-changes)
- [Changed defaults and behavior](#changed-defaults-and-behavior)
- [Runtime and toolchain baselines](#runtime-and-toolchain-baselines)

## Removed commands and APIs

### FFI and runtime property adjustments (2.0.0)

The deprecated `UnsafeFnPointer` constructor signature taking an untyped `Deno.PointerObject` is removed. `globalThis.location` is configurable, and `Deno.FsWatcher.prototype.return()` is no longer deprecated.

### Removed commands and broad flags (2.0.0)

Deno 2 removes `deno bundle` and `deno vendor`. It also removes `--allow-hrtime`, `--allow-none`, `--jobs`, `--trace-ops`, `--ts`, the generic `--unstable` flag, and `--lock-write`, so 1.x automation using them must be revised.

### Resource-oriented API removals (2.0.0)

`Deno.File`, `Deno.Buffer`, the reader, writer, closer, and seeker interfaces, direct `new Deno.FsFile()` construction, and resource `.rid` properties are gone. The removed free functions include `close`, `copy`, `iter`, `read`, `readAll`, `seek`, `shutdown`, `write`, `writeAll`, and the `fdatasync`, `flock`, `fstat`, `fsync`, `ftruncate`, `funlock`, and `futime` families, including their synchronous forms.

### Soft-removed legacy runtime APIs (2.0.0)

`Deno.run()`, `Deno.isatty()`, and `Deno.serveHttp()` are soft-removed, while `Deno.run()` no longer supports `clearEnv`, `gid`, or `uid`. `Deno.customInspect` is removed outright.

### TLS and window-surface option changes (2.0.0)

`Deno.ConnectTlsOptions` no longer has `certChain`, `certFile`, or `privateKey`, and `Deno.ListenTlsOptions` no longer has `certChain`, `certFile`, or `keyFile`. WebGPU window `width` and `height` options now belong on the `UnsafeWindowSurface` constructor.

## Configuration and CLI changes

### CLI path escaping and runtime logging (2.0.0)

In path-based flags, a doubled comma escapes a literal comma inside a value. Runtime logging is configured with `DENO_LOG` instead of `RUST_LOG`.

```sh
deno run --allow-read=/tmp/with,,comma main.ts
```

### Configuration validation (2.0.0)

Supported `compilerOptions` are now an allowlist and unsupported options produce errors. Remote import maps and the deprecated `files` configuration are no longer supported in `deno.json`.

## Changed defaults and behavior

### Lockfile and cache changes (2.0.0)

Lockfile v4 is the default and stores normalized version constraints in a terser form. The remote-module cache directory is renamed from `deps` to `remote`.

### Machine-readable and server output (2.0.0)

Every `--json` output now includes the Deno version, while `deno info` output no longer includes `emit` or `map`. The server's `Listening on` message is written to stderr instead of stdout.

### Required 2.3.1 follow-up (2.3.0)

The 2.3.0 release was produced with incorrect version metadata and can report the wrong version. Upgrade to 2.3.1 rather than remaining on this build.

```sh
deno upgrade 2.3.1
```

### Type-checking defaults (2.0.0)

Deno 2 uses TypeScript 5.6 and `npm:@types/node@22`, and enables `noImplicitOverride` and `useUnknownInCatchVariables` during checking. Overrides therefore need the `override` modifier, and caught values are `unknown` unless narrowed.

## Runtime and toolchain baselines

### Runtime baseline (2.6-guide)

Deno 2.6 embeds V8 14.2, establishing the JavaScript-language compatibility baseline for the release.

### Toolchain and lint baseline (2.8-guide)

Deno 2.8 embeds TypeScript 6.0.3 and V8 14.9; `deno check`, the language server, bundling, and compilation all use the new TypeScript version. The `no-process-global` and `no-node-globals` lint rules are no longer enabled by default and must be included explicitly for browser-portable code.

```json
{ "lint": { "rules": { "include": ["no-process-global", "no-node-globals"] } } }
```

### Toolchain baseline (2.5-guide)

Deno 2.5 embeds V8 14.0 and TypeScript 5.9.2. Its Temporal implementation was substantially overhauled but remains behind `--unstable-temporal`.

### TypeScript and V8 versions (2.3-guide)

Deno 2.3 embeds TypeScript 5.8 and V8 13.5, which sets the checker, language-feature, and JavaScript-runtime compatibility baseline for this release.
