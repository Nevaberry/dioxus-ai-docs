# Concurrency and asyncio

Use this reference for asyncio, multiprocessing and executors, threads and queues, subinterpreters, and the free-threaded runtime.

## Asyncio

### Identity-preserving `asyncio.as_completed()` (Python 3.13)
`asyncio.as_completed()` now supports both synchronous and asynchronous iteration. When tasks or futures are supplied, asynchronous iteration can yield those original objects, allowing completion results to stay associated with task metadata.

```python
tasks = [asyncio.create_task(fetch(url)) for url in urls]
async for task in asyncio.as_completed(tasks):
    result = await task
```

### Asyncio server closure semantics (3.13.0)
`loop.create_unix_server()` now removes its Unix socket when the server closes. `Server.wait_closed()` waits until the server is closed and all active connections are gone, rather than returning merely because no connection is active.

### Third-party asyncio task naming (3.13.0)
Third-party task implementations must now implement `Task.set_name()`; the deprecated undocumented `_set_task_name()` helper has been removed.

### Asyncio transport and callback behavior (3.13.0)
`DatagramTransport.sendto(b"")` now transmits a zero-length datagram, and exceptions from an `asyncio.start_server()` `client_connected_cb` are passed to the loop exception handler. `Future.set_exception(StopIteration(...))` converts that exception to `RuntimeError` instead of risking a hang.

### Configurable loops in isolated async tests (3.13.0)
`unittest.IsolatedAsyncioTestCase` now supports configuring the `loop_factory` used by its `asyncio.Runner`, allowing tests to avoid the asyncio policy system.

### Async task-graph introspection (Python 3.14)
`python -m asyncio ps PID` prints running tasks and awaiters, while `pstree PID` renders their coroutine hierarchy and detects cycles. In-process tools can inspect and render a program's call graph with `asyncio.capture_call_graph()` and `print_call_graph()`.

### Async task-factory keyword passthrough (Python 3.14)
`asyncio.create_task()`, loop `create_task()`, and `TaskGroup.create_task()` accept arbitrary keyword arguments and pass all of them to `Task` or the configured task factory; custom factories must therefore handle `name`, `context`, and any additional keywords.

### No implicit event-loop creation (Python 3.14)
`asyncio.get_event_loop()` now raises `RuntimeError` when no current loop exists instead of creating one. Use `asyncio.run()` for a complete async entry point, `get_running_loop()` inside async code, or an `asyncio.Runner` when several runs must share a loop.

### Event-loop policy retirement (Python 3.14)
The asyncio policy classes and `get_event_loop_policy()`/`set_event_loop_policy()` are deprecated for removal in 3.16. Select a loop implementation with the `loop_factory` argument to `asyncio.run()` or `Runner` instead.

### Direct task-group cancellation (Python 3.15 preview)
`asyncio.TaskGroup.cancel()` requests early cancellation of every task in the group, replacing the workaround of adding a task that raises a sentinel exception once the group's goal has been reached.

```python
async with asyncio.TaskGroup() as group:
    group.create_task(worker())
    group.cancel()
```

### Quiet and isolated asyncio REPLs (3.15.0b3)
The asyncio REPL honors `-q` by suppressing its copyright and version banner and honors `-I` by not loading `PYTHONSTARTUP`.

## Multiprocessing and executors

### Current-environment process spawning (3.13.0)
`os.posix_spawn(..., env=None)` now inherits the current process environment instead of requiring an explicit environment mapping.

### Forkserver becomes the Unix process default (Python 3.14)
On Unix other than macOS, `multiprocessing` and `ProcessPoolExecutor` now default to `forkserver` instead of `fork`; Windows and macOS remain on `spawn`. Code relying on inherited mutable globals or unpicklable state must be adapted or explicitly request a `fork` context through `get_context()` or `mp_context`.

### Executor backpressure and forced shutdown (Python 3.14)
`Executor.map(..., buffersize=n)` limits submitted results that have not yet been yielded, pausing input consumption when full. `ProcessPoolExecutor.terminate_workers()` and `kill_workers()` provide explicit whole-pool termination levels.

### Interruptible child processes (Python 3.14)
`multiprocessing.Process.interrupt()` sends `SIGINT` to the child, allowing its normal `KeyboardInterrupt`, traceback, and `finally` cleanup path instead of immediately terminating or killing it.

### Subprocess `posix_spawn` selection knob (3.14.0)
The new `_PYTHON_SUBPROCESS_USE_POSIX_SPAWN` environment variable controls whether `subprocess` uses `os.posix_spawn()`, providing a process-wide compatibility escape hatch.

### Multiprocessing startup controls (3.15.0b3)
`multiprocessing.set_forkserver_preload(..., on_error=)` accepts `'ignore'`, `'warn'`, or `'fail'` for preload import failures. Spawned children now inherit every `-X` option, while creating a spawn-context process and calling `freeze_support()` no longer select the process-wide start method as a side effect.

## Threads, queues, and contexts

### Explicit queue shutdown (Python 3.13)
Both `queue.Queue` and `asyncio.Queue` now have `shutdown()` lifecycle APIs, with termination reported through `queue.ShutDown` and `asyncio.QueueShutDown`, respectively.

### Context-safe warnings and inherited thread contexts (Python 3.14)
`-X context_aware_warnings` makes `warnings.catch_warnings()` use a context variable, preventing concurrent threads or tasks from corrupting one another's filters. `sys.flags.thread_inherit_context` controls whether `Thread.start()` copies its caller's `Context`; both flags default on in free-threaded builds and off in GIL-enabled builds.

### Operating-system thread names (Python 3.14)
`threading.Thread.start()` now sets the operating-system thread name from `Thread.name`, making Python-assigned names visible to system debuggers and process tools.

### Locale queries can affect other threads (Python 3.14)
`locale.nl_langinfo()` now temporarily changes `LC_CTYPE` for some queries, and that process-global transition is observable by concurrent threads.

### Interruptible synchronization on Windows (3.14.0)
On Windows, Ctrl-C can now interrupt `threading.Lock.acquire()`, `RLock.acquire()`, and `Thread.join()` with `KeyboardInterrupt`, matching their behavior on macOS and Linux.

### Concurrent iterator utilities (Python 3.15 preview)
`threading.serialize_iterator`, `synchronized_iterator()`, and `concurrent_tee()` provide supported synchronization for sharing generators and iterators across threads rather than relying on ad hoc locks around every `next()` call.

## Subinterpreters and free-threading

### Free-threaded runtime and extension opt-in (Python 3.13)
Free-threaded CPython uses a separate `python3.13t` executable or a build configured with `--disable-gil`; `PYTHON_GIL=1` or `-X gil=1` re-enables the GIL, while `sys._is_gil_enabled()` reports its runtime state. Multi-phase C extensions declare support with `Py_mod_gil`, single-phase extensions use `PyUnstable_Module_SetGIL()`, and importing an undeclared extension enables the GIL unless it was explicitly forced off with `PYTHON_GIL=0` or `-X gil=0`; installing C extensions requires pip 24.1 or newer.

### Safer first imports in subinterpreters (3.13.0)
When a built-in or extension module is first imported while a subinterpreter is active, its initialization function runs in the main interpreter first. A single-phase module therefore fails in an isolated subinterpreter without first executing there and leaving inconsistent process-global state.

### Standard-library subinterpreters (Python 3.14)
The new `concurrent.interpreters` module exposes isolated interpreters in Python, while `concurrent.futures.InterpreterPoolExecutor` provides the executor interface and true multicore parallelism within one process. Sharing is opt-in and currently limited, and many third-party extension modules are not yet compatible even though standard-library extensions are.

### Free-threaded support status (Python 3.14)
The free-threaded build is now an officially supported, still-optional configuration rather than experimental. Windows extension build backends must now define `Py_GIL_DISABLED` themselves when targeting it; the running build's value is available from `sysconfig.get_config_var()`.

### Isolated-interpreter capability detection (3.15.0b3)
`sys.implementation.supports_isolated_interpreters` reports whether the running implementation supports isolated subinterpreters, so portable tools can gate their use without assuming CPython behavior.

### Free-threaded iterator guarantees (3.15.0b3)
Concurrent iteration over the same `range` iterator and the same `itertools` `chain`, `combinations`, `combinations_with_replacement`, `permutations`, `product`, `cycle`, `zip_longest`, or `accumulate` iterator is now safe in free-threaded builds. `BytesIO`, `mmap`, `cProfile`, `csv`, `heapq`, and `json` also received explicit free-threaded safety support.
