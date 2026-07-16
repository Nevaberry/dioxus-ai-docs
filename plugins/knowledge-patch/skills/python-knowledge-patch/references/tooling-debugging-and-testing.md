# Tooling, debugging, and testing

Use this reference for interactive shells and pdb, profiling and monitoring, CLI parsing, logging and testing, imports, and diagnostics.

## Interactive shell and debugger

### Interactive-shell controls (Python 3.13)
The new terminal REPL supports multiline editing, F1 help, F2 history browsing without output or prompts, and F3 paste mode. Set `PYTHON_BASIC_REPL` to fall back to the basic REPL, use `PYTHON_HISTORY` to relocate `.python_history`, and control color with `PYTHON_COLORS`, `NO_COLOR`, or `FORCE_COLOR`.

### `pdb` stops at the call site (Python 3.13)
`breakpoint()` and `pdb.set_trace()` now enter the debugger immediately instead of waiting for the next executed line, avoiding jumps outside a just-finished context. During post-mortem debugging, the new `exceptions [number]` command navigates chained exceptions.

### Interactive embedding controls (3.13.0)
`readline.backend` identifies `readline` versus `editline`. `code.interact(local_exit=True)` keeps `exit()` and `quit()` local to the interactive console instead of closing `sys.stdin` and propagating `SystemExit`.

### Broader `pdb` commands and expression evaluation (3.13.0)
`pdb` can execute arbitrary statements against current-frame locals, including in generators and nested functions; `.pdbrc` and `-c` accept any valid debugger command. Breakpoints accept `package.module` targets, `pdb -m` accepts target arguments, post-mortem mode handles `SyntaxError`, and `$_exception` exposes the active post-mortem exception.

### Safe remote process debugging (Python 3.14)
`sys.remote_exec(pid, script_path)` schedules a file for execution in another Python process at its next safe execution point, and `python -m pdb -p PID` builds an interactive attach flow on it. Access can be disabled with `PYTHON_DISABLE_REMOTE_DEBUG`, `-X disable-remote-debug`, or `--without-remote-debug`; a target blocked in a system call will not attach until it executes bytecode or receives a signal.

### Highlighted and import-aware REPL (Python 3.14)
The default REPL now highlights syntax and completes module and submodule names in `import` statements; attribute completion is not included, and the highlighting is disabled by basic-REPL or no-color settings.

### Async-aware `pdb` (Python 3.14)
`await pdb.set_trace_async()` permits `await` expressions while debugging a coroutine, and `$_asynctask` exposes the current asyncio task. Inline breakpoints also reuse the most recent `Pdb` instance, preserving displays and command lists between stops.

### Scripted inline debugger entry (3.14.0)
`pdb.set_trace(commands=[...])` can execute debugger commands supplied by source code when entering the breakpoint.

```python
pdb.set_trace(commands=["p request", "continue"])
```

### `pdb` console and CLI behavior (3.15.0b3)
`pdb` uses PyREPL as its default input console, accepts the standard `--` end-of-options separator, and can set a breakpoint on an async function by function name.

## Profiling, monitoring, and diagnostics

### Changed disassembly representation (Python 3.13)
`dis` output now uses logical labels for jump targets and exception handlers; request offsets with CLI `-O` or `show_offsets=True`. `dis.get_instructions()` no longer emits inline caches as separate instructions, placing them in `Instruction.cache_info` instead, and its `show_caches` argument is deprecated and ineffective.

### Exception-group traceback formatting (Python 3.13)
`TracebackException.format_exception_only(show_group=True)` now recursively includes nested exceptions from a `BaseExceptionGroup`; `TracebackException.exc_type_str` provides the display name as `exc_type` begins deprecation.

### Monitoring and profiling exception events (3.13.0)
`sys.setprofile()` now receives `PY_THROW`, while `sys.monitoring` adds `RERAISE`, supplies the exception as the third `PY_UNWIND` callback argument, and raises `ValueError` if a callback returns `DISABLE` for an event that cannot be disabled locally.

### Frame-pointer-free Linux perf profiling (3.13.0)
Linux perf integration can use advanced JIT support without frame pointers when `PYTHON_PERF_JIT_SUPPORT` is set or Python is started with `-X perf_jit`.

### Multiple profiler sort keys (3.13.0)
`Profile.print_stats()` now accepts multiple sort arguments, allowing deterministic secondary ordering in one call.

### Directional monitoring branch events (Python 3.14)
`sys.monitoring.BRANCH_LEFT` and `BRANCH_RIGHT` replace the deprecated undirected `BRANCH` event. Native monitoring tools emit them with `PyMonitoring_FireBranchLeftEvent()` and `PyMonitoring_FireBranchRightEvent()`.

### Unified tracing and sampling profilers (Python 3.15 preview)
The new `profiling` package contains deterministic `profiling.tracing` (the implementation formerly exposed as `cProfile`) and the new `profiling.sampling` profiler; `cProfile` remains an alias, while pure-Python `profile` is deprecated for removal in 3.17. The sampling CLI can attach to a PID, run a script or module, or dump stacks, and supports wall, CPU, GIL, and exception modes plus pstats, collapsed stacks, flame graphs, Gecko profiles, heatmaps, live TUI, async-aware, and opcode views.

### Per-code exception monitoring (Python 3.15 preview)
`sys.monitoring` exception events such as `PY_THROW`, `PY_UNWIND`, `RAISE`, `EXCEPTION_HANDLED`, and `RERAISE` may now be enabled or disabled per code object. Returning `DISABLE` from one of their callbacks disables that event for the current tool and code object instead of raising `ValueError`.

### Sampling-profiler capture workflows (3.15.0b3)
`profiling.sampling` adds subprocess following, blocking capture, compact `--binary` recordings replayable into other formats, and sequential `--jsonl` output. Its flamegraph tooling can invert stacks or compare two runs with `--diff-flamegraph`; binary capture currently rejects `--async-aware`.

### Configurable `timeit` target duration (3.15.0b3)
`timeit.Timer.autorange()` has a configurable target duration, and `python -m timeit --target-time ...` exposes the same control for benchmarks that need longer or shorter calibration runs.

### Bounded faulthandler dumps (3.15.0b3)
`faulthandler.dump_traceback()`, `dump_traceback_later()`, `enable()`, and `register()` accept keyword-only `max_threads` to cap the number of thread stacks emitted.

### Programmatic colored representations (3.15.0b3)
`difflib.unified_diff()` accepts `color` for git-like colored diffs, and `ast.dump()` has a corresponding color control for syntax-tree output.

## CLI parsing

### `optparse` support status reversed (Python 3.13)
`optparse` is no longer soft-deprecated: `argparse` remains preferred for new applications, but `optparse` is explicitly recognized as a viable lower-level base for Unix-style argument-processing libraries.

### Optional `getopt` arguments and ordered GNU parsing (3.14.0)
Short options ending in `::` and long options ending in `=?` accept optional arguments. Prefixing the GNU short-option specification with `-` also returns non-options in their original position as `(None, value)` entries.

```python
options, rest = getopt.gnu_getopt(argv, "-o::", ["output=?"])
```

### Changed `argparse` defaults and inference (Python 3.15 preview)
`ArgumentParser(..., suggest_on_error=...)` now defaults to `True`, so mistyped argument suggestions are enabled unless explicitly disabled. `BooleanOptionalAction` supports single-dash long options and alternative prefix characters; when both `-f` and `-foo` name one argument, inferred `dest` is now `foo` rather than `f`, so pass `dest=` to preserve the old result.

### Inline-code markup in `argparse` (3.15.0b3)
Backticks in an `ArgumentParser` description, epilog, or option help mark inline code for highlighting when colored help is enabled; color is controlled by the parser rather than `HelpFormatter`.

## Logging and testing

### Queue-listener lifecycle management (3.14.0)
`logging.handlers.QueueListener` is now a context manager, and calling `start()` on an already-started listener raises `RuntimeError`.

```python
with logging.handlers.QueueListener(queue, handler):
    run_application()
```

### Formatter objects in logging and tests (3.15.0b3)
`logging.basicConfig(formatter=...)` accepts a prebuilt `Formatter`, and `unittest.TestCase.assertLogs(..., formatter=...)` uses one to format captured output.

### Complete module-cleanup failures (3.15.0b3)
`unittest.doModuleCleanups()` raises an `ExceptionGroup` when several cleanup callbacks fail instead of discarding every exception after the first.

## Imports, packaging, and discovery

### Frozen-module and pre-site startup controls (3.13.0)
`PYTHON_FROZEN_MODULES` mirrors `-X frozen_modules` to control whether imports ignore frozen modules. Debug builds also support `PYTHON_PRESITE=package.module` to import a module before `site.py` runs.

### Dedented `-c` code and cached import timing (Python 3.14)
The interpreter automatically applies `textwrap.dedent()`-like handling to the argument of `python -c`, and `-X importtime=2` includes already-loaded modules with `cached` in place of timing values.

### Auditable package startup files (Python 3.15 preview)
Site directories may contain `.start` files whose lines are `package.module:callable` entry points invoked with no arguments at startup. Executable `import` lines in `.pth` files are silently deprecated and are ignored when the matching `.start` file exists, while ordinary `.pth` path-extension lines remain supported.

```text
my_package.bootstrap:initialize
```

`site.StartupState` lets custom startup code collect path changes across several site directories and execute all entry points only after those static paths have been applied.

### Importer-defined module discovery (3.15.0b3)
`importlib.abc.MetaPathFinder.discover()` and `PathEntryFinder.discover()` let custom importers enumerate module and submodule names without pretending they live in a conventional filesystem tree.

### Isolated `ensurepip` wheel lookup (3.15.0b3)
`ensurepip` no longer searches the current working directory for `pip-*.whl`, preventing an unrelated local wheel from changing bootstrap behavior.

### Environment-clearing audit event (3.15.0b3)
`os.environ.clear()` emits the `os._clearenv` auditing event, allowing audit hooks to observe bulk environment removal.

### IDLE file and import behavior (3.15.0b3)
IDLE reads its configuration and breakpoint files as UTF-8, defaults Shell and Output saves to `.txt`, and no longer adds `idlelib` itself to the user process path, so names such as `idlelib/help.py` cannot be imported as accidental top-level modules.
