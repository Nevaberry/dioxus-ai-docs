# Processes, Workers, Async Context, and Permissions

Process lifecycle, worker threads, async context, resource lifetime, and the Permission Model.

## Contents

- [Permission Model](#permission-model)
- [Workers and locks](#workers-and-locks)
- [Async context and hooks](#async-context-and-hooks)
- [Process lifecycle and signals](#process-lifecycle-and-signals)

## Permission Model

### Addon permission queries (since 24.4.0)

`process.permission.has()` now accepts the `addon` scope, allowing code to test native-addon permission with `process.permission.has('addon')`.

### Implicit permission for the entry point (since 24.2.0)

Under the Permission Model, Node now implicitly grants filesystem read access to the application's entry-point file. The entry point no longer needs to be repeated in `--allow-fs-read`; other filesystem reads remain restricted.

### Network and inspector permissions (since 25.0.0)

The Permission Model adds `--allow-net` for explicitly permitted network destinations and `--allow-inspector` for inspector access. Restricted processes that need either capability must grant it rather than assuming it remains available.

```console
node --permission --allow-net=api.example.com \
  --allow-inspector --inspect app.js
```

### Network permission checks for pipe connections (since 25.3.0)

With the Permission Model enabled, connections made through Node's pipe wrapper now undergo a network permission check (CVE-2026-21636). Restricted applications must no longer assume that pipe-backed connections bypass network policy and should handle permission denial when connecting.

### Permission checks for pipe operations (since 26.3.1)

With the Permission Model enabled, opening a pipe or changing its mode with `chmod` now checks the `net` permission scope. Restricted processes must grant the relevant network permission or handle a permission denial instead of assuming these pipe operations bypass policy.

### Permission checks in filesystem paths (since 25.8.2)

The Permission Model now applies previously missing checks to `fs.realpath.native()` and affected promise-based filesystem paths (CVE-2026-21715 and CVE-2026-21716). Restricted applications should expect these operations to fail when the corresponding filesystem permission has not been granted.

### Permission flags in spawned children (since 24.4.0)

Permission Model flags are now propagated on spawn, so child Node processes retain the active restrictions instead of silently starting with broader access.

### Permission Model filesystem restrictions (since 24.13.0)

With the Permission Model enabled, file-descriptor timestamp updates (`futimes`) are disabled (CVE-2025-55132), while symlink APIs require full read and write access (CVE-2025-55130). Permission-restricted applications must account for both constraints when updating timestamps or manipulating symlinks.

### Permission Model filesystem restrictions (since 24.17.0)

With the Permission Model enabled, `FileHandle.utimes()` is now disabled. Permission checks while writing diagnostic reports also account for changes made by `process.chdir()`.

### Stable Permission Model (since 23.5.0)

The Permission Model and the `--permission` CLI switch are now stable, so restricted processes no longer need the experimental switch spelling.

```console
node --permission --allow-fs-read=./config app.js
```


## Workers and locks

### Async-disposable workers (since 24.2.0)

`Worker` now implements `Symbol.asyncDispose`, allowing `await using worker = new Worker(...)` to terminate the worker automatically when its scope exits.

### Internal worker detection (since 23.7.0)

`node:worker_threads` now exports `isInternalThread`, which identifies Node-created internal worker threads separately from the main thread and user-created workers.

### OS-visible thread names (since 23.8.0)

Threads created by Node now receive names that improve debugger and profiler output. A worker thread uses the `name` option passed to its `Worker` constructor.

```js
import { Worker } from 'node:worker_threads';

new Worker(new URL('./worker.mjs', import.meta.url), { name: 'indexer' });
```

### Posting after worker messaging is closed (since 23.0.0)

Calling `postMessage()` on a closed worker-thread messaging object now throws `InvalidStateError` instead of silently accepting the call.

### Promise-only worker termination (since 25.0.0)

The callback form of `worker.terminate()` has been removed. Await the promise returned by `terminate()` when shutdown must complete before continuing.

```js
await worker.terminate();
```

### Web Locks for worker threads (since 24.5.0)

`node:worker_threads` now exposes the Web Locks API for coordinating access to resources shared between threads.

```js
import { locks } from 'node:worker_threads';

await locks.request('cache-update', async () => {
  console.log('lock held');
});
```

### Worker inspection in Chrome DevTools (since 24.1.0)

The inspector now supports inspecting Node worker threads in Chrome DevTools.


## Async context and hooks

### Async context in `stream.finished()` (since 24.0.0)

Callbacks registered with `stream.finished()` now run in the `AsyncLocalStorage` context in which `finished()` was called, preserving request-local state through stream completion.

### Disposable `AsyncLocalStorage` (since 25.9.0)

`AsyncLocalStorage` now supports `using` scopes, allowing an instance to be disabled automatically when its lexical scope exits.

```js
import { AsyncLocalStorage } from 'node:async_hooks';

using storage = new AsyncLocalStorage();
```

### Named and default `AsyncLocalStorage` values (since 24.0.0)

`AsyncLocalStorage` accepts `name` and `defaultValue` constructor options. The default is returned by `getStore()` when no other store is active, and the name is exposed as `storage.name`.

```js
import { AsyncLocalStorage } from 'node:async_hooks';

const storage = new AsyncLocalStorage({
  name: 'requests',
  defaultValue: { requestId: 'none' },
});
console.log(storage.name, storage.getStore().requestId);
```

### Removed bound-function async-resource metadata (since 25.0.0)

Functions returned by `AsyncResource.bind()` no longer expose the legacy `asyncResource` property. Code must not recover the underlying resource through `bound.asyncResource`.

### Selective promise tracking in async hooks (since 24.14.0)

`createHook()` now accepts a `trackPromises` option, allowing an async hook to control whether promise resources are tracked. Hooks that do not need promise lifecycle events can disable that tracking.


## Process lifecycle and signals

### Deprecated process feature probes (since 23.4.0)

`process.features.ipv6`, `process.features.uv`, and the `process.features.tls_*` properties are deprecated and should no longer be used as capability checks.

### Disabling SIGUSR1 activation (since 23.7.0)

The new `--disable-sigusr1` flag prevents Node from starting its SIGUSR1 signal I/O thread; run `node --disable-sigusr1 app.js` when that activation path must be disabled.

### Optional `process.execve()` arguments (since 24.5.0)

The `args` array passed to `process.execve()` is now optional, so a replacement process that needs no arguments no longer requires an explicit empty array.

### Process-level reference controls (since 23.6.0)

The new `process.ref()` and `process.unref()` methods provide process-level control over whether supported resources keep the event loop alive.

### Process-signal exit codes (since 25.4.0)

`convertProcessSignalToExitCode()` from `node:util` converts a process signal to its conventional numeric exit status; for example, `convertProcessSignalToExitCode('SIGINT')` returns `130`.

### Replacing the current process (since 23.11.0)

The new `process.execve(file, args, env)` executes another program in place of the current process; a successful call does not return. For example, `process.execve('/usr/bin/env', [], { ...process.env, MODE: 'worker' })` replaces the running program with `env`.

### Shell-mode child-process arguments (since 23.11.0)

Passing a separate `args` array to `spawn()` or `execFile()` while `shell: true` is deprecated. Avoid shell mode where possible; when it is required, pass the shell command without a separate arguments array.
