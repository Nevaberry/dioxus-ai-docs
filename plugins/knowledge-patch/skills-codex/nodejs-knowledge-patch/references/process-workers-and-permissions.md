# Processes, Workers, Async Context, and Permissions

## Process execution and signals

- In 23.7.0, `--disable-sigusr1` prevents Node from creating its SIGUSR1 I/O
  thread and disables signal-triggered Inspector activation.
- In 23.11.0, `process.execve()` replaces the current process with another
  executable rather than spawning a child. A successful call never returns, so
  normal JavaScript exit handlers and cleanup do not run.
- In 23.11.0, passing a separate `args` array to `spawn()` or `execFile()` with
  `shell: true` is deprecated. Keep the shell disabled when supplying separate
  arguments to avoid unsafe shell concatenation.
- In 24.2.0, an empty string for child-process `options.shell` is deprecated.
  Omit the option when no shell is wanted or provide a valid shell selection.
- In 24.10.0, omitting `env` from `process.execve()` correctly inherits the
  current process environment.
- In 24.14.0, `util.convertProcessSignalToExitCode()` converts a signal name to
  its conventional numeric exit status.
- In 24.13.0, the 24.13.1 release freezes `os.constants.signals`; copy the map
  before augmenting it.

## Worker identity, transfer, and lifecycle

- In 23.7.0, `worker_threads.isInternalThread` distinguishes Node-created
  internal workers from the main thread and user-created workers.
- In 23.8.0, Node-created threads have debugger-visible names, and a worker uses
  the `name` passed to its constructor.
- In 24.2.0, `Worker` supports async explicit disposal with `await using`.
- In 24.6.0, `Worker.prototype.cpuUsage()` reports a worker's CPU consumption
  from its parent. In 24.8.0, `startCpuProfile()` captures its CPU profile; in
  24.9.0, `startHeapProfile()` captures its heap profile. Each profiling method
  returns a handle whose `stop()` resolves to the profile.
- In 24.7.0, diagnostic reports include the configured worker name.
- In 25.0.0, callback-based `worker.terminate()` is end-of-life; use the
  returned promise.
- In 26.7.0, TCP `Server` and `Socket` objects can transfer across workers,
  including TCP handle transfer on Windows.

## Structured clone and abort signals

- In 23.0.0, `File` is cloneable and `worker_threads.markAsUncloneable()` can
  deliberately make an object fail cloning. Calling `postMessage()` after a
  port closes throws `InvalidStateError`.
- In 23.0.0, when a source signal aborts, its dependent signals are marked
  aborted before abort events dispatch. A source listener can observe the
  current state of an `AbortSignal.any()` dependent.
- In 23.1.0, streams preserve the caller-supplied abort reason.
- In 23.5.0, `AbortSignal` no longer uses the default listener-count leak
  warning, avoiding spurious warnings for many consumers.

## Async context and hooks

- In 24.0.0, `AsyncLocalStorage` accepts `defaultValue` and `name`. Outside an
  active context, `getStore()` returns the configured default.
- Also in 24.0.0, `stream.finished()` preserves the current
  `AsyncLocalStorage` context.
- In 24.14.0, `createHook()` accepts `trackPromises`, allowing callers that do
  not need promise lifecycle events to disable promise-resource tracking.
- In 25.9.0, `AsyncLocalStorage` implements explicit disposal and can be scoped
  with `using`.

## Worker coordination

- In 24.5.0, `node:worker_threads` exposes the Web Locks API for coordinating
  access to named resources across threads.
- In 25.9.0, diagnostics channels expose Web Lock activity.

## Permission Model basics

- In 24.0.0, enable the Permission Model with `--permission`;
  `--experimental-permission` is removed.
- In 24.2.0, the application entry point receives implicit filesystem-read
  permission and need not be repeated in `--allow-fs-read`.
- In 24.4.0, active permission flags propagate to spawned Node processes. The
  `addon` scope is accepted by `process.permission.has()` so code can check
  whether native-addon loading is allowed.
- In 25.0.0, network and Inspector grants are separate: restricted processes
  need `--allow-net` for networking and `--allow-inspector` to start Inspector.
- In 25.4.0, JSON configuration supports Permission Model settings; declaring
  the permission namespace implicitly enables the model.

## Permission hardening

- In 24.13.0, 24.13.1 disables `futimes` under `--permission`
  (CVE-2025-55132). Symlink APIs require filesystem-read and filesystem-write
  permissions (CVE-2025-55130), so grant both for relevant paths.
- In 25.3.0, the network permission check applies when `pipe_wrap` connects
  (CVE-2026-21636). Restricted pipe clients require network permission.
- In 24.14.0, 24.14.1 adds missing Permission Model checks to affected
  `node:fs/promises` operations and `fs.realpath.native()`.
- In 24.17.0, `FileHandle.utimes()` is disabled under the Permission Model.
  Filesystem permission checks during diagnostic-report writes account for
  `process.chdir()`.
- In 26.3.1, network permission guards pipe opening and mode changes.
- In 22.23.2, filesystem radix-node splits no longer over-authorize paths.
  Trace-event output and the final diagnostic-report path require explicit
  filesystem-write permission.
- In 26.7.0, denied access in permission-audit mode does not throw, and each
  permission warning has a unique code. Audit tools can classify violations
  without treating them as enforcement exceptions.
