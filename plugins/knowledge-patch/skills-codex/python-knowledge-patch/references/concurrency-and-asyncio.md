# Concurrency and asyncio

## Threads and finalization

### Stronger thread-join completion

`Thread.join()` waits until the underlying operating-system thread exits. A
subsequent `fork()` from a multithreaded process is therefore safer.

### Finalization failures

`PythonFinalizationError` identifies attempts to start threads, fork, or spawn
subprocesses after finalization has advanced too far. Handle it separately when
shutdown cleanup may invoke those operations.

### Locale queries are process-wide

`locale.nl_langinfo()` may temporarily change `LC_CTYPE`. Other threads doing
locale-sensitive work can observe the transient process-wide change, so avoid
concurrent locale queries where deterministic behavior matters.

## Asyncio lifecycle

### Task-factory compatibility across 3.13 releases

Python 3.13.3 accidentally passed arbitrary `**kwargs` through task creation
and broke the established custom-factory contract. Python 3.13.4 and later
restore compatibility while retaining the extra keyword channel for `Task` and
custom factories. Guard temporary workarounds by the maintenance release.

### Unix server socket cleanup

Closing a server created by `loop.create_unix_server()` automatically removes
its Unix-domain socket instead of leaving the filesystem path behind.

### Direct task-group cancellation

Python 3.15 adds `asyncio.TaskGroup.cancel()` to terminate a group early without
injecting a task whose only job is to raise a sentinel exception.

### Quiet and isolated asyncio REPLs

In Python 3.15.0b3, the asyncio REPL honors `-q` and `-I`, handles exceptions
from `PYTHONSTARTUP`, and closes its event loop when the interactive session
ends.

## Processes and shared resources

### Shared-memory tracking and exit handlers

`SharedMemory(..., track=False)` opts out of POSIX resource-tracker cleanup.
The tracker exits nonzero when it detects a leak, and `atexit` handlers are
honored by every multiprocessing start method.

### Safer first import in subinterpreters

When a built-in or extension module is first imported from a subinterpreter,
its initializer first runs in the main interpreter. A single-phase module fails
in an isolated subinterpreter before its initializer can leave global state or
callbacks there.

### Isolated-interpreter capability detection

`sys.implementation.supports_isolated_interpreters` reports whether the runtime
supports isolated interpreters in Python 3.15.0b3.

### Multiprocessing startup controls

In Python 3.15.0b3, `freeze_support()` works on every spawn-based platform and
does not select a global start method. Creating a process from a spawn context
also leaves the global method unchanged. `set_forkserver_preload(on_error=...)`
accepts `ignore`, `warn`, or `fail`, and spawned children inherit every
command-line `-X` option.

## Free-threading

### Runtime context contracts

For free-threaded builds, `context_aware_warnings` and
`thread_inherit_context` default on; both default off in GIL-enabled builds.
This changes warning-filter and context inheritance across threads. Windows
build backends targeting free-threaded extensions must define
`Py_GIL_DISABLED` themselves.

### Supported concurrent iterator tools

Python 3.15 provides `threading.serialize_iterator`,
`synchronized_iterator()`, and `concurrent_tee()` for sharing generators and
iterators across concurrent callers.

### Free-threaded iterator guarantees

In Python 3.15.0b3, concurrent iteration over one `range` iterator is safe in a
free-threaded build. The same guarantee applies to shared `itertools` chain,
cycle, combinations, combinations-with-replacement, permutations, product,
`zip_longest`, and accumulate iterators.
