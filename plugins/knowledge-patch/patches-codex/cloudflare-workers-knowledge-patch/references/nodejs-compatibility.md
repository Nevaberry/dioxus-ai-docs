# Node.js Compatibility

Use this reference when selecting compatibility flags, importing Node.js
modules, adapting code to Node-like globals, or generating runtime types.

Relevant source batches: `2025`, `2026`, `nodejs-runtime`, and
`2026-07-30-2026-08-14`.

## Default enablement

Compatibility dates from `2026-08-04` enable the `nodejs_compat` and
`nodejs_compat_v2` behaviors without flags. Earlier dates are unchanged.
Explicit positive flags remain accepted but local tools treat them as
redundant. Fully opt out on a new date with both negative flags:

```jsonc
{
  "compatibility_date": "2026-08-04",
  "compatibility_flags": ["no_nodejs_compat", "no_nodejs_compat_v2"]
}
```

Use the narrower `nodejs_als` flag when the Worker needs only
`AsyncLocalStorage` rather than the complete compatibility surface:

```jsonc
{
  "compatibility_flags": ["nodejs_als"]
}
```

## Binding values in `process.env`

With `nodejs_compat`, compatibility date `2025-04-01` populates `process.env`
from text and JSON bindings, including variables, secrets, and version
metadata. Use `nodejs_compat_do_not_populate_process_env` to opt out.

The undated `disallow_importable_env` flag also prevents environment imports
from `cloudflare:workers` and blocks this `process.env` population.

## Process v2 and end-of-life APIs

With `nodejs_compat`, compatibility date `2025-09-15` replaces the small
`nextTick`/`env`/`exit`-oriented process shim with a broader v2 implementation.
Unsupported exports on the broader object have value `undefined`. Use
`disable_nodejs_process_v2` to retain the earlier shim.

From `2025-09-01`, `nodejs_compat` also applies the roll-up removal of Node.js
APIs that have reached end of life, including version-specific removals such as
Node.js 23 APIs. `add_nodejs_compat_eol` is a temporary escape hatch, not a
long-term compatibility setting.

## Implemented, partial, and import-only modules

Native runtime coverage includes assertion testing, Buffer, Crypto, Events,
Net, Path, query strings, String Decoder, URL, Utilities, and Zlib. Debugging
is available through Chrome DevTools. DNS, Module, the test runner, and TLS/SSL
are only partially supported.

The 2025 compatibility-date rollouts add:

- client `node:http` and `node:https`;
- `node:http2` stubs and HTTP server APIs;
- `node:fs` and Web File System APIs;
- `node:os` and `node:console`;
- a `node:vm` stub; and
- `node:cluster`, `node:domain`, `node:punycode`, `node:trace_events`, and
  `node:wasi` as implementations or stubs.

Compatibility date `2026-01-29` adds import-compatible stubs for
`node:_stream_wrap`, `node:dgram`, `node:inspector`, and `node:sqlite`.
Compatibility date `2026-03-17` adds stubs for `node:child_process`,
`node:readline`, `node:repl`, `node:tty`, `node:v8`, and
`node:worker_threads`, and implements `node:perf_hooks`.

An import-only stub makes the module resolvable; it does not provide the
underlying host facility. Do not mistake successful import for runtime support.

## Per-module stub overrides

Enable a stub before, or disable it after, its automatic compatibility date
with module-specific flags:

```jsonc
{
  "compatibility_flags": ["nodejs_compat", "enable_nodejs_sqlite_module"]
}
```

The forms are `enable_nodejs_<name>_module` and
`disable_nodejs_<name>_module`. Omit the leading underscore from
`node:_stream_wrap`, as in `disable_nodejs_stream_wrap_module`.

## `require()` interoperability

From compatibility date `2026-01-22`, `require()` returns a module's default
export when it has one. Otherwise it returns a mutable copy of the namespace
object. Set `require_returns_namespace` to retain the earlier behavior in which
`require()` always returned a namespace.

Audit CommonJS call sites that assume either `.default` or a frozen namespace
when advancing this date.

## Timers and performance globals

With `nodejs_compat` from `2026-02-10`, global timer functions return
Node-compatible `Timeout` objects. They support `refresh()`, `ref()`, `unref()`,
and `hasRef()`.

From `2026-03-17`, the global scope also exposes:

- `PerformanceEntry`
- `PerformanceMark`
- `PerformanceMeasure`
- `PerformanceResourceTiming`
- `PerformanceObserver`
- `PerformanceObserverEntryList`

Enabling `node:perf_hooks` implicitly enables these globals.

## API compatibility corrections

With `nodejs_compat` from `2026-05-19`, `Channel.hasSubscribers` and
`TracingChannel.hasSubscribers` in `node:diagnostics_channel` are read-only
boolean properties, not methods.

From `2026-06-16`, unsupported options such as `checkServerIdentity` passed to
`tls.connect()` or `new TLSSocket()` throw `ERR_OPTION_NOT_IMPLEMENTED` instead
of being ignored. Remove or conditionally avoid unsupported TLS options.

## Configuration-derived types

`wrangler types` generates `worker-configuration.d.ts` from the Worker's
compatibility date, flags, bindings, and module rules. Include that file through
`compilerOptions.types`, add `@types/node` when using the Node.js surface, and
run this in CI to detect stale committed output:

```sh
wrangler types --check
```

`@cloudflare/workers-types` v5 exposes the latest stable types at its package
root and experimental APIs at `/experimental`. Dated package entrypoints have
been removed.

## Builds runtime

Workers Builds defaults to Node.js 24.18.0. Its build image preinstalls Node.js
22.23.2 and 24.18.0. Override selection with `NODE_VERSION`, `.nvmrc`, or
`.node-version` when the build needs a different release.
