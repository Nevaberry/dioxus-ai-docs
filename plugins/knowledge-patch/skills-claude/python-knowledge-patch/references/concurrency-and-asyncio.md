# Concurrency and asyncio

## Threads, contexts, and queues

### Task-factory maintenance compatibility (`whatsnew-3.13`)

Python 3.13.3 accidentally forwarded arbitrary `**kwargs` through task
creation, breaking the established custom-factory contract. Python 3.13.4 and
later restore that contract while retaining the extra keyword channel for
`Task` and custom factories. Guard workarounds by maintenance release.

### Thread join completion (`3.13.0`)

`Thread.join()` waits until the underlying operating-system thread exits,
making a subsequent `fork()` from a multithreaded process safer.

### Free-threaded context contracts (`whatsnew-3.14`)

`context_aware_warnings` and `thread_inherit_context` default on in
free-threaded builds and off in GIL-enabled builds. Audit warning filters and
context propagation across threads.

### Queue-listener lifecycle (`3.14.0`)

`logging.handlers.QueueListener` is a context manager. Calling `start()` on an
already started listener raises `RuntimeError`:

```python
with QueueListener(queue, handler):
    run_application()
```

### Native thread diagnostics (`3.14.0`)

On Linux, `threading.Thread` propagates its name to the OS thread, and
`faulthandler` output includes thread names. Use `faulthandler.dump_c_stack()`
or `faulthandler.enable(c_stack=True)` to include native stacks.

### Context decorators and deferred execution (`whatsnew-3.15`)

`ContextDecorator`, `AsyncContextDecorator`, `contextmanager()`, and
`asynccontextmanager()` used as decorators keep their contexts active while a
returned generator iterates or a coroutine awaits, instead of exiting when the
deferred object is created.

### Concurrent iterator helpers (`whatsnew-3.15`)

`threading.serialize_iterator`, `synchronized_iterator()`, and
`concurrent_tee()` are supported ways to share iterators and generators among
concurrent callers.

### Free-threaded iterator guarantees (`3.15.0b3`)

One `range` iterator and shared `itertools` chain, cycle, combinations,
combinations-with-replacement, permutations, product, `zip_longest`, and
accumulate iterators support concurrent iteration in free-threaded builds.

## Asyncio lifecycle and observability

### Unix server socket cleanup (`3.13.0`)

Closing a server created by `loop.create_unix_server()` automatically removes
its Unix-domain socket path.

### Live and asynchronous debugging (`3.14.0`)

Use `await pdb.set_trace_async()` inside a coroutine. `python -m asyncio ps PID`
and `pstree PID` inspect live task relationships; `asyncio.capture_call_graph()`
and `print_call_graph()` provide in-process views.

### Direct task-group cancellation (`whatsnew-3.15`)

`asyncio.TaskGroup.cancel()` terminates a group without adding a task whose
sole purpose is to raise a sentinel exception.

### Quiet and isolated asyncio REPL (`3.15.0b3`)

The asyncio REPL honors `-q` and `-I`, handles exceptions raised from
`PYTHONSTARTUP`, and closes its event loop when the session ends.

## Processes and interpreters

### Shared-memory resource lifecycle (`3.13.0`)

`SharedMemory(..., track=False)` opts out of POSIX resource-tracker cleanup.
The tracker exits nonzero when it detects a leak, and `atexit` handlers run for
every multiprocessing start method.

### Safer first extension import (`3.13.0`)

When a built-in or extension module is first imported from a subinterpreter,
its initializer first runs in the main interpreter. A single-phase module thus
fails in an isolated subinterpreter before leaving global state or callbacks
there.

### Isolated-interpreter capability (`3.15.0b3`)

`sys.implementation.supports_isolated_interpreters` reports whether the
runtime supports isolated interpreters.

### Multiprocessing startup controls (`3.15.0b3`)

`freeze_support()` works on every spawn-based platform and no longer selects a
global start method. Creating a process from a spawn context likewise leaves
the global method unchanged. `set_forkserver_preload(on_error=...)` accepts
`ignore`, `warn`, or `fail`; spawned children inherit every command-line `-X`
option.

## Native free-threading rules

### Dictionary iteration (`3.14.0`)

`PyDict_Next()` does not lock in free-threaded builds. Hold a single critical
section around the entire traversal, not one lock per step.

### Locale changes are process-wide (`whatsnew-3.14`)

`locale.nl_langinfo()` may temporarily change `LC_CTYPE`. Concurrent
locale-sensitive code can observe the transient process-wide change.
