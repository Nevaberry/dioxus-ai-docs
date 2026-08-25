# Processes, Workers, Async Context, and Permissions

Use this reference for processes, workers, async context, and permissions work.

## `process.execve()` inherits the environment by default (`24.10.0`)

When its `env` argument is omitted, `process.execve()` now uses the corrected default environment.

```js
import { execve } from 'node:process';

execve('/usr/bin/env', ['env']); // uses the current process environment
```

## AbortSignal listener warnings (`23.5.0`)

`AbortSignal` instances no longer use the default memory-leak warning for listener counts, avoiding spurious warnings for signals with many consumers.

## Dedicated-thread module-hook deprecation (`25.9.0`)

`module.register()` is documentation-deprecated as DEP0205. Prefer the synchronous, in-thread `module.registerHooks()` API when a dedicated loader-hooks thread is not required.

## Dependent AbortSignals update before listeners run (`23.0.0`)

When a source signal aborts, its dependent signals are marked aborted before abort events are dispatched. A source listener can therefore observe the up-to-date state of an `AbortSignal.any()` signal.

```js
const controller = new AbortController();
const dependent = AbortSignal.any([controller.signal]);
controller.signal.addEventListener('abort', () => {
  console.log(dependent.aborted); // true
});
controller.abort();
```

## Detecting internal worker threads (`23.7.0`)

`node:worker_threads` now exposes `isInternalThread`, allowing code to distinguish a Node-created internal worker from the main thread and user-created workers.

```js
import { isInternalThread } from 'node:worker_threads';
console.log(isInternalThread);
```

## Disabling SIGUSR1 handling (`23.7.0`)

The new `--disable-sigusr1` flag prevents Node from creating its SIGUSR1 signal I/O thread, which is useful when the process must not support signal-triggered inspector activation.

```sh
node --disable-sigusr1 app.js
```

## Disposable `AsyncLocalStorage` (`25.9.0`)

`AsyncLocalStorage` now supports `using` scopes, so an instance can be disposed automatically when its lexical scope ends.

```js
import { AsyncLocalStorage } from 'node:async_hooks';

using requestContext = new AsyncLocalStorage();
await requestContext.run({ requestId: 1 }, handleRequest);
```

## Empty child-process shell values are deprecated (`24.2.0`)

Passing an empty string as `options.shell` to child-process APIs is deprecated. Omit `shell` when no shell is wanted, or supply a valid shell selection.

## Entry points have implicit read permission (`24.2.0`)

With the Permission Model enabled, the application entry point receives implicit filesystem-read permission. It no longer needs to be repeated in `--allow-fs-read`.

```sh
node --permission app.mjs
```

## EventTarget listener counts (`25.4.0`)

The module-level `events.listenerCount()` helper now accepts `EventTarget` instances as well as event emitters.

```js
import { listenerCount } from 'node:events';

const target = new EventTarget();
target.addEventListener('ready', () => {});
console.log(listenerCount(target, 'ready')); // 1
```

## Frozen signal constants (`24.13.0`)

`os.constants.signals` is frozen in 24.13.1, so code that needs an augmented signal map must copy it before adding entries.

## In-place process replacement (`23.11.0`)

`process.execve()` starts another executable by replacing the current process rather than spawning a child. A successful call never returns, so normal JavaScript exit handlers and cleanup do not run.

```js
import { execve } from 'node:process';

execve('/usr/bin/env', ['env'], { ...process.env, APP_MODE: 'worker' });
```

## Named `AsyncLocalStorage` with a default store (`24.0.0`)

The `AsyncLocalStorage` constructor accepts `defaultValue` and `name` options. Outside an active context, `getStore()` returns the configured default instead of `undefined`.

```js
import { AsyncLocalStorage } from 'node:async_hooks';

const context = new AsyncLocalStorage({
  defaultValue: { requestId: null },
  name: 'request',
});
```

## Named Node.js threads (`23.8.0`)

Node-created threads now have names visible to debugging tools, and worker threads use the `name` passed to the `Worker` constructor.

```js
import { Worker } from 'node:worker_threads';
new Worker(new URL('./worker.mjs', import.meta.url), { name: 'indexer' });
```

## Native-addon permission checks (`24.4.0`)

`process.permission.has()` now accepts the `addon` scope, allowing restricted applications to test whether native-addon loading is permitted with `process.permission.has('addon')`.

## Network and inspector permissions (`25.0.0`)

The Permission Model adds separate `--allow-net` and `--allow-inspector` grants. Restricted applications must opt in before using the network or starting the inspector.

```sh
node --permission --allow-net app.mjs
node --permission --allow-inspector --inspect app.mjs
```

## Per-thread CPU usage (`23.9.0`)

`process.threadCpuUsage()` reports CPU consumption for the calling thread, allowing main-thread and worker-thread CPU costs to be measured independently of process-wide usage.

```js
const usage = process.threadCpuUsage();
```

## Per-worker CPU profiles (`24.8.0`)

`Worker.prototype.startCpuProfile()` starts profiling a particular worker and returns a handle whose `stop()` method resolves to the captured profile.

```js
const handle = await worker.startCpuProfile();
await runWork(worker);
const profile = await handle.stop();
```

## Per-worker CPU usage (`24.6.0`)

`Worker.prototype.cpuUsage()` reports CPU consumption for a particular worker from the parent thread, without requiring measurement code inside that worker.

```js
const usage = await worker.cpuUsage();
console.log(usage.user, usage.system);
```

## Per-worker heap profiles (`24.9.0`)

`Worker.prototype.startHeapProfile()` starts heap profiling for one worker and returns a handle whose `stop()` method resolves to the captured profile.

```js
const handle = await worker.startHeapProfile();
await runWork(worker);
const profile = await handle.stop();
```

## Permission audit behavior (`26.7.0`)

Denied access no longer throws in permission-audit mode, and permission warnings have unique warning codes. Audit tooling can observe and classify violations without treating them as enforcement exceptions.

## Permission checks for pipe connections (`25.3.0`)

The Permission Model now applies its network check when `pipe_wrap` connects (CVE-2026-21636), closing a path that could bypass network restrictions. Restricted applications using pipe connections must have the required network permission.

## Permission checks for pipe operations (`26.3.1`)

The Permission Model now guards pipe opening and mode changes with its network scope. Restricted applications using those operations must have the required network permission.

## Permission flag rename (`24.0.0`)

The Permission Model is now enabled with `--permission`; `--experimental-permission` is removed, so startup commands must use the new flag.

## Permission Model filesystem hardening (`24.13.0`)

With `--permission`, the `futimes` APIs are now disabled (CVE-2025-55132), and symlink APIs require both filesystem-read and filesystem-write permission (CVE-2025-55130). Restricted applications that create symlinks must grant both capabilities for the relevant paths.

```sh
node --permission --allow-fs-read=./links --allow-fs-write=./links app.mjs
```

## Permission Model filesystem restrictions (`24.17.0`)

With the Permission Model enabled, `FileHandle.utimes()` is now disabled. Permission checks while writing diagnostic reports also account for changes made by `process.chdir()`.

## Permission Model path and output enforcement (`22.23.2`)

Filesystem grants no longer over-authorize paths when radix permission nodes split. Trace-event output and a diagnostic report's final output path now require filesystem-write permission, so restricted processes must explicitly allow every destination they use.

## Permission restrictions propagate on spawn (`24.4.0`)

Active Permission Model flags now propagate to spawned Node.js processes, so a child no longer silently loses the restrictions applied to its parent.

## Process signals as exit codes (`24.14.0`)

`convertProcessSignalToExitCode()` from `node:util` converts a process signal to its conventional numeric exit status.

```js
import { convertProcessSignalToExitCode } from 'node:util';

console.log(convertProcessSignalToExitCode('SIGINT')); // 130
```

## Promise tracking controls for async hooks (`24.14.0`)

`createHook()` now accepts a `trackPromises` option, allowing an async hook to control whether promise resources are tracked. Hooks that do not need promise lifecycle events can disable that tracking.

## Runtime SIGINT stack-trace control (`24.6.0`)

`util.setTraceSigInt()` enables or disables the same SIGINT stack-trace behavior that was previously selected only at process startup.

```js
import { setTraceSigInt } from 'node:util';
setTraceSigInt(true);
```

## Shell argument deprecation (`23.11.0`)

Passing a separate `args` array to `child_process.spawn()` or `execFile()` with `shell: true` is deprecated. Keep the shell disabled when supplying arguments separately to avoid unsafe shell concatenation.

## Structured-clone controls (`23.0.0`)

`File` objects are now cloneable. `node:worker_threads` also adds `markAsUncloneable()` for deliberately rejecting an object during cloning, and `postMessage()` after a port is closed now throws `InvalidStateError`.

```js
import { markAsUncloneable, MessageChannel } from 'node:worker_threads';

const { port1 } = new MessageChannel();
const value = {};
markAsUncloneable(value);
port1.postMessage(value); // throws DataCloneError
```

## Synchronous, on-thread module hooks (`23.5.0`)

`module.registerHooks()` registers `resolve` and `load` functions directly in the current thread. The hooks cover modules loaded by `require()`, `import`, and `createRequire()`, including cases the asynchronous `module.register()` hooks cannot cover.

```js
import { registerHooks } from 'node:module';

registerHooks({
  resolve(specifier, context, nextResolve) {
    return nextResolve(specifier.replace('foo', 'bar'), context);
  },
});
```

## Web Lock diagnostics (`25.9.0`)

`node:diagnostics_channel` adds channels for Web Lock activity, allowing observability tooling to trace lock coordination without wrapping the lock APIs.

## Web Locks for worker coordination (`24.5.0`)

`node:worker_threads` now exposes the Web Locks API, allowing threads to coordinate access to named resources.

```js
import { locks } from 'node:worker_threads';

await locks.request('cache-update', async () => {
  await updateCache();
});
```

## Worker inspection in Chrome DevTools (`24.1.0`)

The inspector can now expose worker threads to Chrome DevTools, allowing workers associated with an inspected Node.js process to be debugged alongside the main thread.

## Worker names in diagnostic reports (`24.7.0`)

Diagnostic reports now include a worker's configured name, making failures from multiple named worker threads easier to distinguish.
