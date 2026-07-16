# Runtime and Web Platform

V8 and JavaScript features, Web-compatible globals, events, URLs, timers, utilities, and REPL behavior.

## Contents

- [JavaScript and V8](#javascript-and-v8)
- [Web-compatible globals and storage](#web-compatible-globals-and-storage)
- [Events, aborts, and timers](#events-aborts-and-timers)
- [URLs, readline, REPL, and utilities](#urls-readline-repl-and-utilities)
- [Runtime semantics](#runtime-semantics)
- [Core runtime behavior](#core-runtime-behavior)

## JavaScript and V8

### 24.4.1 security update (since 24.4.0)

Node.js 24.4.1 fixes CVE-2025-27209, a V8 RapidHash HashDoS, and CVE-2025-27210, in which Windows reserved device names such as `CON`, `PRN`, and `AUX` could bypass path-traversal protection in `path.normalize()`. Deployments on 24.4.0 should upgrade to 24.4.1.

### `Float16Array` V8 serialization (since 23.5.0)

The `node:v8` serializer and deserializer can now round-trip `Float16Array` values.

### Built-in `Uint8Array` base64 and hex conversion (since 25.0.0)

V8 14.1 adds direct base64 and hexadecimal conversion methods to `Uint8Array`, avoiding intermediate `Buffer` or string conversion.

```js
const bytes = Uint8Array.fromHex('deadbeef');
console.log(bytes.toBase64()); // 3q2+7w==
console.log(Uint8Array.fromBase64('SGVsbG8=').toHex()); // 48656c6c6f
```

### Other stability promotions (since 25.4.0)

The one-shot `crypto.hash()` API and `v8.queryObjects()` are now stable. The `--heapsnapshot-near-heap-limit`, `--build-snapshot`, and `--build-snapshot-config` CLI options are stable as well.

### Temporal enabled by default (since 26.0.0)

The global `Temporal` date/time API is enabled by default, so applications can use it without a startup flag.

```js
const release = Temporal.PlainDate.from('2026-05-05');
console.log(release.add({ months: 1 }).toString());
```

### V8 13.6 built-ins (since 24.0.0)

The V8 update exposes `Float16Array` and adds `RegExp.escape()` and `Error.isError()`. `RegExp.escape()` safely turns arbitrary text into a literal pattern fragment, while `Error.isError()` provides a built-in error-brand check.

```js
const samples = new Float16Array([1 / 3, 2 / 3]);
const input = 'a+b';
const exact = new RegExp(`^${RegExp.escape(input)}$`);
console.log(samples.length, exact.test('a+b'), Error.isError(new Error()));
```

### V8 14.6 collection and iterator APIs (since 26.0.0)

`Map` and `WeakMap` now provide `getOrInsert()` and `getOrInsertComputed()` for eager or lazy insertion on a miss. `Iterator.concat()` sequences multiple iterables into one iterator.

```js
const cache = new Map();
const value = cache.getOrInsertComputed('answer', () => 42);
const values = [...Iterator.concat([1, 2], new Set([3]))];
```


## Web-compatible globals and storage

### DOM-compatible quota errors (since 26.0.0)

`QuotaExceededError` is now a `DOMException`-derived interface, so quota failures can be handled through the standard DOM exception hierarchy.

### Global `CloseEvent` (since 23.0.0)

`CloseEvent` is now available as a global Web API, so close events can be constructed without an import.

```js
const event = new CloseEvent('close', { code: 1000, reason: 'done' });
```

### Global `ErrorEvent` (since 25.0.0)

`ErrorEvent` is now exposed globally, so browser-compatible error events can be constructed without another implementation.

```js
const event = new ErrorEvent('error', {
  message: 'request failed',
  error: new Error('request failed'),
});
```

### Missing `localStorage` is now detectable (since 26.0.0)

When no local-storage file is configured, accessing the global `localStorage` now returns `undefined` rather than throwing. Code can feature-detect it before use: `if (globalThis.localStorage !== undefined) localStorage.setItem('key', 'value');`.

### Missing `localStorage` paths (since 25.2.0)

Accessing the global `localStorage` getter now throws when no storage path is configured. Start processes that use it with a storage path, for example `node --localstorage-file=./local-storage.json app.js`.

### Serializable `DOMException` values (since 24.3.0)

Node's serialization and deserialization machinery now supports `DOMException` values and treats them as native errors, so they can round-trip instead of being rejected or degraded.

### Web Storage enabled by default (since 25.0.0)

The Web Storage implementation, including the global `localStorage`, is now enabled without `--experimental-webstorage`.

```js
localStorage.setItem('theme', 'dark');
console.log(localStorage.getItem('theme'));
```


## Events, aborts, and timers

### `AbortSignal` listener warnings (since 23.5.0)

`AbortSignal` no longer emits the default memory-leak warning when many listeners are attached.

### Dependent `AbortSignal` ordering (since 23.0.0)

When a source signal aborts, dependent signals are now marked aborted before the source's abort listeners run. An observer can therefore rely on an `AbortSignal.any()` result already reflecting the state change:

```js
const controller = new AbortController();
const dependent = AbortSignal.any([controller.signal]);
controller.signal.addEventListener('abort', () => {
  console.assert(dependent.aborted);
});
controller.abort();
```

### EventTarget listener counts (since 25.4.0)

`events.listenerCount()` now accepts an `EventTarget` as well as an `EventEmitter`, so `listenerCount(target, 'message')` can count listeners registered with `addEventListener()`.

### Invalid timer delays (since 23.0.0)

Passing a negative or `NaN` delay to timer APIs now emits a warning. Normalize untrusted delay values before passing them to `setTimeout()` or `setInterval()`.

### Passive event listeners (since 24.10.0)

Node's `EventTarget` now honors `{ passive: true }`: calling `preventDefault()` from a passive listener does not cancel the event, so listeners that must suppress default behavior cannot be passive.

### Removed `multipleResolves` event (since 25.0.0)

The deprecated `process` `multipleResolves` event has been removed, so promise-settlement diagnostics cannot rely on that event.

### Zero maximum-listener settings (since 23.8.0)

`events.getMaxListeners()` now recognizes and reports a configured maximum of `0` instead of treating that value as absent.


## URLs, readline, REPL, and utilities

### `URLPattern` in `node:url` (since 23.8.0)

The standard `URLPattern` constructor is now exported from `node:url`; it is not yet a global in Node 23.8, with global availability beginning in Node 24.

```js
import { URLPattern } from 'node:url';

const pattern = new URLPattern({ pathname: '/users/:id' });
console.log(pattern.exec('https://example.com/users/42').pathname.groups.id);
```

### `URLSearchParams(null)` serialization (since 26.4.0)

For standards compatibility, constructing `URLSearchParams` with `null` now serializes as `null=`.

```js
new URLSearchParams(null).toString(); // 'null='
```

### An explicit no-style format (since 24.2.0)

`util.styleText()` now accepts the `none` format, so dynamic styling code can deliberately request no ANSI styling with `styleText('none', text)`.

### Cloneable `File` objects (since 23.0.0)

Node's `File` objects can now pass through structured cloning, including worker messaging, without losing their `File` identity.

```js
import { File } from 'node:buffer';

const copy = structuredClone(new File(['data'], 'data.txt'));
console.log(copy.name); // data.txt
```

### Configurable `util.deprecate()` wrappers (since 25.2.0)

`util.deprecate()` now accepts an options argument, allowing each deprecation wrapper to be configured beyond its function, message, and code inputs.

### Custom REPL error handling (since 25.9.0)

Embedded REPLs can now customize error handling instead of relying solely on the built-in handling path.

### Disposable readline interfaces (since 23.10.0)

Readline interfaces now support `Symbol.dispose`; call `rl[Symbol.dispose]()` when an interface should participate in explicit resource cleanup.

### Multiline REPL editing (since 24.1.0)

The REPL now supports vertical cursor movement and editing multiline commands while they are still being entered, complementing the multiline history support added in 24.0.0.

### New API deprecations (since 24.2.0)

`util.isNativeError()` is deprecated in favor of `Error.isError()`. Passing an empty string as child-process `options.shell` is also deprecated, and classes exported by `node:http` should be constructed with `new` rather than called as functions.

### Proxy inspection output (since 26.0.0)

`util.inspect()` now marks proxied objects as proxies. Logged output and snapshots that include proxies can therefore differ after upgrading.

### Removed legacy `util` helpers (since 23.0.0)

`util.log()` and the legacy `util.isBoolean()`, `isBuffer()`, `isDate()`, `isError()`, `isFunction()`, `isNull()`, `isNullOrUndefined()`, `isNumber()`, `isObject()`, `isPrimitive()`, `isRegExp()`, `isString()`, `isSymbol()`, and `isUndefined()` helpers have reached end-of-life. Replace them with language checks, `Buffer.isBuffer()`, or the corresponding `util.types` predicate where one exists; `util._extend()` was not removed in this release.

### Runtime-deprecated legacy APIs (since 24.0.0)

`url.parse()` is now runtime-deprecated; use the WHATWG `URL` constructor. Calling REPL and zlib classes without `new` is deprecated, and `repl.builtinModules` is deprecated in favor of `module.builtinModules`.

After the 24.0.1 reversal, `SlowBuffer` remains available but runtime-deprecated rather than removed; use `Buffer.allocUnsafeSlow()` instead.

### Stable terminal text styling (since 23.5.0)

`util.styleText()` is now stable rather than experimental.

### Unicode lines and multiline REPL history (since 24.0.0)

Readline now recognizes Unicode line-separator characters as line boundaries. The REPL also stores multiline input as a multiline history entry, allowing it to be recalled and edited as a unit.


## Runtime semantics

### Explicit resource management (since 24.0.0)

The `using` and `await using` declarations are available for deterministic cleanup through `Symbol.dispose` and `Symbol.asyncDispose`. A resource is disposed automatically when control leaves its declaration scope.

```js
{
  using resource = {
    [Symbol.dispose]() {
      console.log('disposed');
    },
  };
}
```

### Removed and corrected error codes (since 23.0.0)

`ERR_CRYPTO_SCRYPT_INVALID_PARAMETER` has been removed, so callers must not depend on that code for invalid scrypt options. The misspelled `ERR_TLS_PSK_SET_IDENTIY_HINT_FAILED` code is now `ERR_TLS_PSK_SET_IDENTITY_HINT_FAILED`.


## Core runtime behavior

### Empty `NO_COLOR` values (since 24.4.0)

An empty `NO_COLOR` environment variable is now treated as absent and no longer disables color; set it to a non-empty value when color should be suppressed.

### Runtime deprecations (since 23.0.0)

`crypto.fips` is runtime-deprecated; use `crypto.getFips()` and `crypto.setFips()`. `fs.Dirent.prototype.path` is runtime-deprecated in favor of `dirent.parentPath`, and short GCM authentication tags now trigger DEP0182 unless `authTagLength` is supplied when creating the decipher.

### Stability promotions (since 26.4.0)

Connection block-list APIs are now release candidates, while the Argon2 and key encapsulation/decapsulation crypto APIs are stable.

### Stable disposal symbols (since 24.2.0)

Node's `Symbol.dispose` and `Symbol.asyncDispose` support has graduated from experimental status.

### Time-zone data 2025a (since 23.8.0)

Bundled time-zone data now models Paraguay as permanently `-03` from spring 2024 and improves pre-1991 data for the Philippines.

### Time-zone data 2025b (since 24.0.0)

The bundled time-zone database is updated to release 2025b, so `Date` and `Intl` calculations use that ruleset rather than the 2025a data shipped in Node.js 23.8.

### Updated trust and time-zone data (since 25.4.0)

The bundled root certificate set now follows NSS 3.117, and the bundled time-zone database is updated to 2025c. TLS trust decisions and `Date` or `Intl` results use those updated datasets.

### Updated trust and time-zone data (since 25.9.0)

The bundled root certificate set now follows NSS 3.121, and the bundled time-zone database is updated to 2026a.
