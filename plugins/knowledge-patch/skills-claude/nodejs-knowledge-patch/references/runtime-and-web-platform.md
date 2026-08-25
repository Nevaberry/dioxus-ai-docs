# Runtime and Web Platform

Use this reference for runtime and web platform work.

## 24.14.1 security hardening (`24.14.0`)

In 24.14.1, HTTP `headersDistinct` and `trailersDistinct` become null-prototype objects, and the Permission Model adds missing checks for affected `node:fs/promises` operations and `fs.realpath.native()`; use `Object.hasOwn()` for these header collections and grant the required filesystem permissions. The release also hardens WebCrypto HMAC and KMAC comparisons, HTTP/2 flow-control error handling, URL handling, and array-index hash collisions, so deployments on 24.14.0 should upgrade.

## 24.4.1 security fixes (`24.4.0`)

Node.js 24.4.1 fixes CVE-2025-27209, a V8 HashDoS involving RapidHash, and CVE-2025-27210, where Windows reserved device names could bypass path-traversal protection in `path.normalize()`. Deployments on 24.4.0 should upgrade to 24.4.1.

## `URLSearchParams(null)` string conversion (`26.4.0`)

`new URLSearchParams(null).toString()` now produces `null=` as required by the URL standard instead of treating `null` as no parameters.

## Aborted readline promises (`23.8.0`)

Aborting a promise-based readline operation no longer leaves its promise unresolved.

## Custom REPL error handling (`25.9.0`)

Programmatic REPLs can now customize error handling, and the REPL no longer depends on `node:domain`. Embedded REPLs should use the explicit error-handling facility instead of relying on domain interception.

## Deep-comparison and inspection corrections (`24.13.0`)

Node.js 24.13.1 corrects deep comparison for `Map` and `Set` values containing mixed types. `util.inspect()` now limits property output to own properties, so diagnostics and snapshots that exposed inherited state can change.

## Default Web APIs (`25.0.0`)

Web Storage is enabled without `--experimental-webstorage`, and `ErrorEvent` is available as a global. Code using these browser-compatible APIs no longer needs the Web Storage opt-in flag or an `ErrorEvent` polyfill.

## Deprecated process feature probes (`23.4.0`)

`process.features.ipv6`, `process.features.uv`, and the `process.features.tls_*` properties are deprecated and should no longer be used for capability checks.

## Detectable missing Web Storage (`26.0.0`)

Accessing `globalThis.localStorage` without a configured storage file now returns `undefined`. `QuotaExceededError` is also derived from `DOMException`, allowing standard DOM-exception checks.

```js
if (globalThis.localStorage !== undefined) localStorage.setItem('key', 'value');
```

## Disposable readline interfaces (`23.10.0`)

Readline interfaces now support `Symbol.dispose`, enabling protocol-based cleanup with `rl[Symbol.dispose]()`.

## DOMException serialization (`24.3.0`)

`DOMException` values are now supported by Node's serialization and deserialization machinery, so they can round-trip through APIs backed by it.

## Float16Array V8 serialization (`23.5.0`)

The `node:v8` serialization APIs now handle `Float16Array` values.

## Legacy API removals and runtime deprecations (`23.0.0`)

`process.assert()` and `zlib.bytesRead` are removed, while many legacy scalar `util.is*()` predicates are moved to end-of-life status. The `crypto.fips` property is runtime-deprecated in favor of `crypto.getFips()` and `crypto.setFips()`, and `fs.Dirent.path` is runtime-deprecated in favor of `parentPath`.

## Legacy API retirements (`24.0.0`)

`tls.createSecurePair()`, `tls.Server.prototype.setOptions()`, and the private `OutgoingMessage._headers` and `_headersList` fields are removed. `url.parse()` is runtime-deprecated, while constructing REPL or zlib classes without `new` is deprecated.

## Legacy JavaScript API removals (`25.0.0`)

`SlowBuffer`, `assert.CallTracker`, the multi-argument form of `assert.fail()`, the `process` `multipleResolves` event, and callback-based `worker.terminate()` are end-of-life. Use `Buffer.allocUnsafeSlow()`, a single-message `assert.fail()`, and the promise returned by `worker.terminate()`; child-process code must also use the public `channel` property instead of `_channel`.

## Loose equality for nullish array elements (`24.14.0`)

`assert.deepEqual()` now correctly handles loose comparisons of arrays containing `undefined` and `null`. Use `deepStrictEqual()` when those values must remain distinct.

## Missing and undefined Error causes differ (`23.3.0`)

Assertion comparisons now distinguish an `Error` with no `cause` from one whose `cause` property is explicitly `undefined`.

```js
import assert from 'node:assert/strict';

assert.deepStrictEqual(
  new Error('boom'),
  new Error('boom', { cause: undefined }),
); // throws
```

## Native-error detection migration (`24.2.0`)

`util.isNativeError()` is deprecated in favor of `Error.isError()`.

```js
if (Error.isError(value)) {
  console.error(value);
}
```

## Non-throwing `statSync` probes for `ENOTDIR` (`23.9.0`)

`fs.statSync(path, { throwIfNoEntry: false })` now treats `ENOTDIR` like a missing entry and returns `undefined` when an intermediate path component is not a directory.

## Options for `util.deprecate()` (`25.2.0`)

`util.deprecate()` now accepts options in addition to its existing function, message, and code inputs, extending what libraries can control when creating a deprecated wrapper.

## Partial comparisons of URLs and Files (`23.7.0`)

`assert.partialDeepStrictEqual()` now handles `URL` instances and `File` prototypes correctly.

## Partial error comparisons (`23.11.0`)

`assert.partialDeepStrictEqual()` now supports partial comparison of `Error` objects, so expected error details can match a subset of the actual error.

```js
import assert from 'node:assert/strict';

const actual = new Error('failed', { cause: new Error('disk') });
assert.partialDeepStrictEqual(actual, new Error('failed'));
```

## Passive event listeners follow spec behavior (`24.10.0`)

For listeners registered with `{ passive: true }`, `preventDefault()` no longer cancels the event.

```js
const target = new EventTarget();
const event = new Event('work', { cancelable: true });
target.addEventListener('work', (value) => value.preventDefault(), {
  passive: true,
});
target.dispatchEvent(event);
console.log(event.defaultPrevented); // false
```

## Patch-level `localStorage` access change (`25.2.0`)

Node.js 25.2.0 made `localStorage` access throw when its storage path was missing. Node.js 25.2.1 reverted that behavior as too breaking for an experimental API, so applications supporting both patch releases must not assume property access has the same outcome.

## Runtime deprecation warnings (`26.0.0`)

Calling the dedicated-thread `module.register()` API now emits a runtime deprecation warning; prefer `module.registerHooks()` where synchronous hooks are suitable. The stream behavior covered by DEP0201 and crypto APIs covered by DEP0203 and DEP0204 also advance to runtime deprecations.

## Runtime precise-coverage startup (`24.18.0`)

Inspector precise coverage can now be started from JavaScript at runtime, allowing coverage tooling to begin precise collection without requiring it to be active from process startup.

## Runtime security hardening (`24.13.0`)

Stack-overflow exceptions in `async_hooks` are now rethrown (CVE-2025-59466), and unsafe Buffer creation no longer relies on the zero-fill toggle (CVE-2025-55131). These are security fixes; affected deployments should upgrade rather than attempt application-level workarounds.

## Stability changes in 24.13.1 (`24.13.0`)

`--heapsnapshot-near-heap-limit`, `--build-snapshot`, `--build-snapshot-config`, `crypto.hash()`, and `v8.queryObjects()` are stable in 24.13.1. Synchronous `module.registerHooks()` is release candidate, while dedicated-thread `module.register()` is classified as active development.

## Stable and expanded explicit disposal (`24.2.0`)

`Symbol.dispose` and `Symbol.asyncDispose` support is no longer experimental. `Worker` now supports async disposal, and event-loop delay histograms support disposal, allowing both resources to be managed with `await using` or `using`.

```js
import { monitorEventLoopDelay } from 'node:perf_hooks';
import { Worker } from 'node:worker_threads';

await using worker = new Worker(new URL('./worker.mjs', import.meta.url));
using delay = monitorEventLoopDelay();
delay.enable();
```

## Stricter timer and pipeline handling (`23.0.0`)

Negative or `NaN` timer delays now emit a warning. `stream.pipeline()` also rejects piping into an already closed or destroyed destination, so callers must replace or reopen such a destination rather than reusing it.

## String input to `url.format()` is deprecated (`24.14.0`)

The legacy `url.format(urlString)` form is documented as deprecated under DEP0169. Migrate string URL handling to the WHATWG `URL` API.

## System error messages (`23.1.0`)

`util.getSystemErrorMessage(err)` provides the system error message for an error code.

```js
import { getSystemErrorMessage } from 'node:util';

console.log(getSystemErrorMessage(-2));
```

## Temporal and V8 14.6 collection APIs (`26.0.0`)

The global `Temporal` API is enabled by default. `Map` and `WeakMap` gain `getOrInsert()` and `getOrInsertComputed()`, while `Iterator.concat()` sequences multiple iterables.

```js
const cache = new Map();
cache.getOrInsertComputed('answer', () => 42);
const values = [...Iterator.concat([1, 2], new Set([3]))];
```

## Time-zone data 2025a (`23.8.0`)

The bundled time-zone data is updated to 2025a, including Paraguay's permanent UTC−03 offset and improved pre-1991 data for the Philippines.

## URL Pattern API (`23.8.0`)

`URLPattern` is now exported from `node:url`; it is not a global in Node.js 23, but becomes one in Node.js 24.

```js
import { URLPattern } from 'node:url';
const route = new URLPattern({ pathname: '/users/:id' });
```

## Zero listener limits (`23.8.0`)

`events.getMaxListeners()` now correctly recognizes an explicitly configured maximum of `0` instead of treating it as absent.
