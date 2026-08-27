# Node.js compatibility

This reference consolidates date-gated Node.js behavior from batches `2025`
and `2026` with the module-focused `nodejs-runtime` guidance.

## Default enablement

Compatibility dates from `2026-08-04` enable `nodejs_compat` and
`nodejs_compat_v2` behavior without flags. Earlier dates are unchanged.
Explicit positive flags remain accepted on new dates but local tooling treats
them as redundant. Fully opting out requires both negative flags:

```jsonc
{
  "compatibility_date": "2026-08-04",
  "compatibility_flags": ["no_nodejs_compat", "no_nodejs_compat_v2"]
}
```

Use `nodejs_als` when the only needed feature is `AsyncLocalStorage` and the
full Node.js compatibility surface is unnecessary:

```jsonc
{
  "compatibility_flags": ["nodejs_als"]
}
```

## Environment and process behavior

### Binding values in `process.env`

With `nodejs_compat`, compatibility date `2025-04-01` populates `process.env`
from text and JSON bindings, including variables, secrets, and version
metadata. Use `nodejs_compat_do_not_populate_process_env` to opt out.

The undated `disallow_importable_env` flag both prevents environment imports
from `cloudflare:workers` and blocks `process.env` population.

### Process v2

From `2025-09-15`, process v2 replaces the small `nextTick`, `env`, and
`exit`-oriented shim with a broader implementation. Unsupported exports are
`undefined`. Use `disable_nodejs_process_v2` to retain the old shim.

### End-of-life API removal

From `2025-09-01`, Node.js compatibility enables roll-up removal of APIs that
have reached end of life, including version-specific removals such as Node.js
23 APIs. `add_nodejs_compat_eol` is a temporary escape hatch, not a permanent
compatibility setting.

## Module behavior

### Native and partial coverage

Native runtime coverage includes assertions, Buffer, Crypto, Events, Net,
Path, query strings, String Decoder, URL, Utilities, and Zlib. Debugging uses
Chrome DevTools. DNS, Module, the test runner, and TLS/SSL are only partially
supported.

The 2025 compatibility-date rollouts add client `node:http` and `node:https`,
`node:http2` stubs and HTTP server APIs, `node:fs` plus the Web File System
APIs, `node:os`, `node:console`, a `node:vm` stub, and `node:cluster`,
`node:domain`, `node:punycode`, `node:trace_events`, and `node:wasi` modules or
stubs.

### Import-only stubs

With `nodejs_compat`, `2026-01-29` enables import-compatible stubs for
`node:_stream_wrap`, `node:dgram`, `node:inspector`, and `node:sqlite`.
`2026-03-17` adds stubs for `node:child_process`, `node:readline`, `node:repl`,
`node:tty`, `node:v8`, and `node:worker_threads`, plus an implemented
`node:perf_hooks`.

Stub modules make imports succeed but do not provide the underlying host
facilities. Each rollout can be enabled early or disabled after its automatic
date with `enable_nodejs_<name>_module` or
`disable_nodejs_<name>_module`. Omit the leading underscore in the
`node:_stream_wrap` flag name:

```jsonc
{
  "compatibility_flags": ["nodejs_compat", "enable_nodejs_sqlite_module"]
}
```

For example, the rollback flag for `_stream_wrap` is
`disable_nodejs_stream_wrap_module`.

### `require()` interoperability

From `2026-01-22`, `require()` returns a module's default export when present;
otherwise it returns a mutable copy of the namespace object. Use
`require_returns_namespace` to restore the former always-namespace result.

## Timers, performance, diagnostics, and TLS

With `nodejs_compat` from `2026-02-10`, global timer functions return
Node-compatible `Timeout` objects with `refresh()`, `ref()`, `unref()`, and
`hasRef()`.

From `2026-03-17`, the global scope exposes `PerformanceEntry`,
`PerformanceMark`, `PerformanceMeasure`, `PerformanceResourceTiming`,
`PerformanceObserver`, and `PerformanceObserverEntryList`. Enabling
`node:perf_hooks` also enables those globals.

From `2026-05-19`, `Channel.hasSubscribers` and
`TracingChannel.hasSubscribers` in `node:diagnostics_channel` are read-only
boolean properties, not methods.

From `2026-06-16`, unsupported TLS options such as `checkServerIdentity`
passed to `tls.connect()` or `new TLSSocket()` throw
`ERR_OPTION_NOT_IMPLEMENTED` instead of being ignored.

## Configuration-derived types

Run `wrangler types` to derive `worker-configuration.d.ts` from the Worker's
compatibility date, flags, bindings, and module rules. Include the generated
file through `compilerOptions.types`, and add `@types/node` when using Node.js
compatibility. Use `wrangler types --check` in CI to detect stale committed
output.

`@cloudflare/workers-types` v5 exposes current stable declarations from its
root and experimental APIs from `/experimental`; dated package entrypoints
have been removed.
