# Runtime and Web Platform

## Removed and deprecated JavaScript APIs

- In 23.0.0, `process.assert()` is removed and many legacy scalar `util.is*()`
  predicates reach end-of-life. `fs.Dirent.path` is runtime-deprecated in favor
  of `parentPath`.
- In 24.0.0, `url.parse()` is runtime-deprecated. Constructing REPL or zlib
  classes without `new` is deprecated. The 24.0.1 release reverses 24.0.0's
  end-of-life classification for `SlowBuffer`; it remains runtime-deprecated on
  24.x.
- In 24.2.0, `util.isNativeError()` is deprecated; use `Error.isError()`.
- In 23.4.0, `process.features.ipv6`, `process.features.uv`, and the
  `process.features.tls_*` properties are deprecated and should not be used for
  capability checks.
- In 25.0.0, `SlowBuffer`, `assert.CallTracker`, multi-argument
  `assert.fail()`, the process `multipleResolves` event, and callback-based
  `worker.terminate()` are end-of-life. Use `Buffer.allocUnsafeSlow()`, a single
  assertion message, and the termination promise. Child-process code must use
  public `channel` instead of `_channel`, and `Module._debug` is removed.
- In 24.14.0, string input to legacy `url.format()` is deprecated under
  DEP0169; use the WHATWG `URL` API.
- In 25.2.0, `util.deprecate()` accepts options in addition to its existing
  function, message, and code inputs, extending library control over deprecated
  wrappers.
- In 26.0.0, stream behavior covered by DEP0201 and crypto APIs covered by
  DEP0203 and DEP0204 become runtime deprecations.
- In 26.0.0, private `_stream_wrap`, `_stream_readable`, `_stream_writable`,
  `_stream_duplex`, `_stream_transform`, and `_stream_passthrough` modules are
  removed; use public `node:stream` APIs.

## Equality and assertion-visible semantics

- In 23.0.0, distinct `WeakMap` and `WeakSet` instances compare unequal under
  deep strict comparison; only the same instance compares equal.
- In 23.3.0, an `Error` with no `cause` differs from one with an explicit own
  `cause: undefined`.
- In 23.6.0, partial deep strict comparison distinguishes `0` and `-0`.
- In 23.7.0, partial deep strict comparison correctly handles `URL` instances
  and `File` prototypes.
- In 25.0.0, promises compare by identity, while two invalid `Date` values
  compare equal.
- In 24.9.0, `util.isDeepStrictEqual()` accepts a third `skipPrototype`
  boolean; `true` compares structure without requiring matching constructors or
  prototypes.
- In 25.4.0, invalid dates retain own-property semantics, so invalid dates with
  different attached properties compare unequal.
- In 24.14.0, loose `assert.deepEqual()` correctly handles arrays containing
  `undefined` and `null`; use strict comparison when those must remain distinct.
- In 24.13.0, 24.13.1 corrects deep comparison of `Map` and `Set` values that
  contain mixed types.

## Errors, events, and cancellation

- In 23.0.0, negative or `NaN` timer delays emit a warning.
- In 23.0.0, dependent abort signals are marked aborted before source abort
  listeners run, so a listener sees the updated `AbortSignal.any()` state.
- In 23.1.0, `util.getSystemErrorMessage(err)` returns the system message for an
  error code.
- In 23.5.0, `AbortSignal` does not use the default listener-count warning.
- In 23.8.0, `events.getMaxListeners()` recognizes an explicitly configured
  maximum of `0`. Aborting a promise-based readline operation settles its
  promise rather than leaving it unresolved.
- In 24.10.0, passive event listeners follow standard behavior:
  `preventDefault()` inside `{ passive: true }` does not cancel the event.
- In 25.4.0, module-level `events.listenerCount()` accepts `EventTarget` as well
  as event emitters.

## Explicit resource management

- In 23.10.0, readline interfaces support `Symbol.dispose`.
- In 24.0.0, V8 13.6 enables JavaScript explicit resource management and
  `Float16Array`.
- In 24.2.0, `Symbol.dispose` and `Symbol.asyncDispose` are no longer
  experimental. Workers support async disposal and event-loop delay histograms
  support disposal.
- Directory, temporary-directory, `AsyncLocalStorage`, SQLite session, and
  module-hook disposal details are in their topic references.

## Web-compatible globals and values

- In 23.8.0, `URLPattern` is exported from `node:url`; it is not a global on
  Node.js 23 but becomes global on Node.js 24.
- In 25.0.0, Web Storage is enabled without `--experimental-webstorage`, and
  `ErrorEvent` is global.
- In 25.2.0, `localStorage` access throws when its storage path is missing in
  25.2.0, but 25.2.1 reverts that behavior. Code supporting both patch releases
  must not assume the same access outcome.
- In 26.0.0, `globalThis.localStorage` without a configured storage file
  returns `undefined`. `QuotaExceededError` derives from `DOMException`.
- In 24.3.0, `DOMException` participates in Node serialization and
  deserialization.
- In 26.4.0, `new URLSearchParams(null).toString()` produces `null=` instead of
  treating `null` as an empty parameter set.

## JavaScript and V8 features

- In 23.5.0, V8 serialization supports `Float16Array`.
- In 25.0.0, standard `Uint8Array` base64 and hexadecimal helpers are
  available, including `fromBase64()`, `fromHex()`, `toBase64()`, and
  `toHex()`.
- In 26.0.0, global `Temporal` is enabled. `Map` and `WeakMap` have
  `getOrInsert()` and `getOrInsertComputed()`, and `Iterator.concat()` sequences
  multiple iterables.
- In 24.12.0, Node-specific `performance` extensions belong to the
  `node:perf_hooks` export rather than the browser-compatible global.

## Time zones, URLs, and inspection output

- In 23.8.0, bundled time-zone data is 2025a, including Paraguay's permanent
  UTC−03 and improved pre-1991 Philippines data.
- In 25.9.0, bundled time-zone data moves to 2026a; civil-time calculations can
  change after upgrading.
- In 24.13.0, 24.13.1 adds Unicode 17 URL support, which can change
  internationalized URL handling.
- In 24.13.0, 24.13.1 limits `util.inspect()` property output to own
  properties. In 26.0.0, inspection identifies proxied objects as proxies.

## REPL customization

- In 25.9.0, programmatic REPLs can customize error handling and the REPL no
  longer depends on `node:domain`. Embedded REPLs should use the explicit
  error-handling facility instead of domain interception.
