# Tooling, debugging, and testing

## Startup, imports, and interactive tools

### Import-startup switches (`3.13.0`)

`PYTHON_PRESITE=package.module` imports a module before `site.py`, but only in a
debug build. `PYTHON_FROZEN_MODULES` mirrors `-X frozen_modules` and controls
whether import machinery ignores frozen modules.

### `.pth` loading

`site` decodes `.pth` files as UTF-8 first and falls back to the locale encoding
on `UnicodeDecodeError`. Dot-prefixed files and files with the hidden attribute
are skipped.

### Nested import resources

`importlib.resources.is_resource()`, `open_binary()`, `open_text()`, `path()`,
`read_binary()`, and `read_text()` accept multiple positional path components
and are no longer deprecated. Text helper `encoding` and `errors` parameters
are keyword-only.

```python
read_text(pkg, "templates", "page.txt", encoding="utf-8")
```

### Contained embedded REPL exits

`code.interact(local_exit=True)` keeps `exit()` and `quit()` local to the
interactive session rather than closing `sys.stdin` or raising `SystemExit` in
the embedding process.

### Command-line source and import timing

`python -c` dedents its source before compilation. `-X importtime=2` reports
imports satisfied from already-loaded modules.

### Auditable package startup files

Python 3.15 `.start` files contain `package.module:callable` entries that
`site` invokes with no arguments after static path additions. Executable
`import` lines in `.pth` files are silently deprecated and ignored when a
matching `.start` file exists. `site.StartupState` provides the same batched
path-then-code processing to custom callers.

### Importer-defined discovery

In Python 3.15.0b3, `MetaPathFinder.discover()` and
`PathEntryFinder.discover()` let custom importers enumerate module and
submodule names without assuming a filesystem layout.

### Import metadata surface

`importlib.metadata` 7 adds `Distribution.origin`, `EntryPoints.__repr__`, and a
`diagnose` script, and removes deprecated numeric indexing of `EntryPoint`
objects. In Python 3.15, a distribution directory without its metadata file
raises `MetadataNotFound`.

## Command-line parsing, logging, and user interfaces

### Optional and ordered `getopt`

`getopt` supports options with optional arguments and can return intermixed
options and operands in their original order.

### Changed argparse defaults

Python 3.15 `ArgumentParser(suggest_on_error=...)` defaults to `True`.
`BooleanOptionalAction` supports single-dash long options and alternate prefix
characters. For `add_argument("-f", "-foo")`, the inferred destination is
`foo` rather than `f`; set `dest` explicitly to preserve the old name.

### Inline-code help markup

In Python 3.15.0b3, backticks in parser descriptions, epilogs, and option help
mark inline code for highlighting when colored help is active.

### Queue listener lifecycle

`logging.handlers.QueueListener` is a context manager in Python 3.14. Calling
`start()` on an already-started listener raises `RuntimeError`.

```python
with QueueListener(queue, handler):
    run_application()
```

### Formatter objects

Python 3.15.0b3 `logging.basicConfig(formatter=...)` accepts a formatter object,
and `unittest.TestCase.assertLogs(..., formatter=...)` controls captured
formatting. `logging.Formatter` and `Filter` have informative representations.

### Typed Tk callbacks and text search

`tkinter.wantobjects` defaults to `2`, so callbacks receive appropriate Python
values such as `int`, `float`, `bytes`, or `tuple` rather than always `str`.
In 3.15.0b3, `tkinter.Text.search()` supports `-nolinestop` and `-strictlimits`,
and `Text.search_all()` exposes Tcl's `-all` and `-overlap` modes.

### IDLE behavior

In Python 3.15.0b3, IDLE saves Shell and Output windows as `.txt` by default,
reads configuration and breakpoints as UTF-8, and does not add `idlelib` to the
user process path. User-installed extensions can read settings and key bindings
from `~/.idlerc`.

## Profiling, monitoring, and diagnostics

### Exception events

`sys.setprofile()` and `cProfile` account for generator `PY_THROW` events.
`sys.monitoring` adds a `RERAISE` event for explicit and implicit re-raises.

### Unified profilers

Python 3.15 introduces deterministic `profiling.tracing` and attachable
`profiling.sampling`; `cProfile` remains an alias and `profile` is deprecated
for removal in 3.17. The sampler can attach, run, or dump processes; sample
wall, CPU, GIL, or exception time; reconstruct async tasks; and emit pstats,
collapsed stacks, flame graphs, Gecko profiles, or heatmaps.

### Sampling capture workflows

In Python 3.15.0b3, `profiling.sampling` follows child processes with
`--subprocesses`, records adaptive bytecode operations with `--opcodes`, and
stores compact `--binary` captures for later `replay`. It also supports
sequential `--jsonl` output and differential flame graphs.

### Native thread diagnostics

On Linux, `threading.Thread` propagates its name to the operating-system thread,
and `faulthandler` includes thread names. Native stacks are available through
`faulthandler.dump_c_stack()` or `faulthandler.enable(c_stack=True)`.

### Bounded traceback dumps

Python 3.15.0b3 `faulthandler.dump_traceback()`, `dump_traceback_later()`,
`enable()`, and `register()` accept `max_threads=` to cap emitted stacks.

### Garbage-collector telemetry

Python 3.15.0b3 GC debug output again includes elapsed collection time and the
unreachable-object count. `_remote_debugging.GCMonitor.get_gc_stats()` reads
statistics from another Python process without constructing a full remote
unwinder.

### Colored representations

`ast.dump(color=...)` and `difflib.unified_diff(color=...)` provide opt-in
colored diagnostic output in Python 3.15.0b3.

### Configurable timeit targets

`Timer.autorange()` has a configurable target duration, exposed by the
command-line interface as `--target-time`.

## Debugging

### Broader pdb targets

Pdb can debug zipapps, accepts arguments with `pdb -m`, and resolves
`break package.module`, allowing packaged and module-based targets without
unpacking or rewriting them.

### Live and async debugging

Python 3.14 Pdb accepts `-p PID` for same-version process attachment and offers
`await pdb.set_trace_async()` inside coroutines. `python -m asyncio ps PID` and
`pstree PID` inspect live task relationships; `asyncio.capture_call_graph()`
and `print_call_graph()` provide in-process views.

### Pdb console and targets

In Python 3.15.0b3, Pdb runs scripts supplied through anonymous
process-substitution pipes and resolves async functions by name for breakpoints.
Its CLI accepts the standard `--` separator, and PyREPL is the default input
console.

## Tests and common-library failures

### Warning assertions

Python 3.15 `TestCase.assertWarns()` and `assertWarnsRegex()` propagate warnings
that do not match the requested category or expression and support nesting.
Tests that relied on incidental suppression need explicit filters or another
assertion.

### Complete module-cleanup failures

`unittest.doModuleCleanups()` raises an `ExceptionGroup` when multiple cleanups
fail instead of discarding every exception after the first.

### Warning-filter regular expressions

Python 3.15 treats message and module fields in `-W` and `PYTHONWARNINGS` as
regular expressions when enclosed in `/.../`. `compile()`, `ast.parse()`, and
`symtable.symtable()` accept a module name so syntax warnings can be filtered
unambiguously.

### Deferred backend failures

Guaranteed `hashlib` constructors remain present as attributes even when their
backend is unavailable; they fail when called. Code that needs a particular
algorithm should exercise construction, not only test attribute presence.
