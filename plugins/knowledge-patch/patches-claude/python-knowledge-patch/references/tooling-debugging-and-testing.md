# Tooling, debugging, and testing

## Imports, startup, and packaging

### Nested import resources (`whatsnew-3.13`)

`importlib.resources.is_resource()`, `open_binary()`, `open_text()`, `path()`,
`read_binary()`, and `read_text()` accept multiple positional path components
and are no longer deprecated. For text helpers, pass `encoding` and `errors` by
keyword:

```python
read_text(pkg, "templates", "page.txt", encoding="utf-8")
```

### Import-startup switches (`3.13.0`)

`PYTHON_PRESITE=package.module` imports a module before `site.py`, but only in a
debug build. `PYTHON_FROZEN_MODULES` mirrors `-X frozen_modules` to control
whether import machinery ignores frozen modules.

### `.pth` loading (`3.13.0`)

`site` decodes `.pth` files as UTF-8 first and falls back to locale encoding on
`UnicodeDecodeError`. Dot-prefixed and hidden-attribute files are skipped.

### Import metadata surface (`3.13.0`)

`importlib.metadata` 7 adds `Distribution.origin`, `EntryPoints.__repr__`, and a
`diagnose` script. Deprecated numeric indexing of `EntryPoint` is removed.

### Command-line code and import timing (`3.14.0`)

`python -c` dedents its source string before compilation. `-X importtime=2`
reports imports satisfied from already-loaded modules as well as new imports.

### Explicit lazy imports (`whatsnew-3.15`, `3.15.0b3`)

The `lazy` soft keyword defers loading until first use. It supports both import
forms only as direct module-level statements, not inside `try` and not for star
or future imports:

```python
lazy import json
lazy from pathlib import Path
```

Control global mode with `-X lazy_imports=all`, `PYTHON_LAZY_IMPORTS=all`, or
`sys.set_lazy_imports()`. Use `sys.set_lazy_imports_filter()` for selection,
`types.LazyImportType` for detection, and module-level `__lazy_modules__` for
source shared with older runtimes.

In 3.15.0b3, `sys.lazy_modules` is a set and `all` includes imports executed by
`exec()` inside functions. `none` is not a supported mode spelling.

### Auditable package startup (`whatsnew-3.15`)

`.start` files contain `package.module:callable` entries that `site` invokes
without arguments after static path additions. Executable `import` lines in
`.pth` files are silently deprecated and ignored when a matching `.start` file
exists. `site.StartupState` exposes the same batched path-then-code processing.

### Import and hashing failures (`whatsnew-3.15`)

`importlib.metadata` raises `MetadataNotFound` when a distribution directory
lacks its metadata file. Guaranteed hashlib constructors remain present as
attributes when the backend is unavailable and fail only when called.

### Isolated ensurepip lookup (`3.15.0b3`)

`ensurepip` does not search the current directory for `pip-*.whl`, preventing
ambient files from replacing the bundled wheel.

### Path initialization diagnostics (`3.15.0b3`)

Startup warns when path initialization cannot find a valid standard library.
Control this with `-X pathconfig_warnings` or
`PYTHON_PATHCONFIG_WARNINGS`.

## Command-line parsing, REPLs, and UI

### Contained embedded REPL exits (`3.13.0`)

`code.interact(local_exit=True)` keeps `exit()` and `quit()` within the
interactive session instead of closing `sys.stdin` or raising `SystemExit` in
the embedding process.

### Pdb targets (`3.13.0`)

Pdb debugs zipapps, accepts arguments with `pdb -m`, and resolves
`break package.module`, allowing packaged and module programs to be debugged
without unpacking or target rewrites.

### Typed Tk callbacks (`3.13.0`)

`tkinter.wantobjects` defaults to `2`, so callback arguments arrive as suitable
Python values such as `int`, `float`, `bytes`, or `tuple` rather than always as
`str`.

### Optional and ordered getopt (`whatsnew-3.14`)

`getopt` supports options with optional arguments and can return intermixed
options and operands in their original order.

### Argparse defaults and inference (`whatsnew-3.15`)

`ArgumentParser(suggest_on_error=...)` defaults to `True`.
`BooleanOptionalAction` supports single-dash long options and alternative
prefix characters. With `add_argument("-f", "-foo")`, the inferred destination
is `foo`, not `f`; specify `dest` to retain the old name.

### Extended Tk searching (`3.15.0b3`)

`tkinter.Text.search()` supports `-nolinestop` and `-strictlimits`;
`Text.search_all()` exposes Tcl's `-all` and `-overlap` modes.

### Pdb console refinements (`3.15.0b3`)

Pdb runs scripts supplied through anonymous process-substitution pipes and
resolves async functions by name for breakpoints. Its CLI accepts `--`, and
PyREPL is the default input console.

### Argparse inline code (`3.15.0b3`)

Backticks in parser descriptions, epilogs, and option help mark inline code for
highlighting when colored help is enabled.

### IDLE behavior (`3.15.0b3`)

IDLE saves Shell and Output windows as `.txt`, reads configuration and
breakpoints as UTF-8, and no longer adds `idlelib` to the user process path.
User extensions can obtain settings and bindings from `~/.idlerc`.

## Profiling, monitoring, and diagnostics

### Exception profiling events (`3.13.0`)

`sys.setprofile()` and `cProfile` account for generator `PY_THROW` events.
`sys.monitoring` adds `RERAISE` for explicit and implicit re-raises.

### Linux perf without frame pointers (`3.13.0`)

Set `PYTHON_PERF_JIT_SUPPORT` or use `-X perf_jit` for advanced JIT integration
with Linux `perf`, allowing profiling without frame pointers.

### Live debugging (`3.14.0`)

Pdb accepts `-p PID` for same-version process attachment and supports
`await pdb.set_trace_async()` in coroutines. Async task-graph facilities are
covered in the concurrency reference.

### Unified profiling (`whatsnew-3.15`)

`profiling.tracing` provides deterministic profiling, and
`profiling.sampling` provides the attachable Tachyon sampler. `cProfile`
remains an alias; pure-Python `profile` is deprecated for removal in 3.17. The
sampler can attach, run, or dump processes; sample wall, CPU, GIL, or exception
time; reconstruct async tasks; and emit pstats, collapsed stacks, flame graphs,
Gecko profiles, or heatmaps.

### Sampling captures (`3.15.0b3`)

`profiling.sampling` follows child processes with `--subprocesses`, records
adaptive bytecode operations with `--opcodes`, and stores compact `--binary`
captures for `replay`. It emits streaming `--jsonl` and differential flame
graphs.

### Bounded faulthandler output (`3.15.0b3`)

`faulthandler.dump_traceback()`, `dump_traceback_later()`, `enable()`, and
`register()` accept `max_threads=` to cap emitted thread stacks.

### Colored diagnostics (`3.15.0b3`)

`difflib.unified_diff(color=...)` provides opt-in colored output. See the
typing reference for `ast.dump(color=...)`.

## Warnings, logging, tests, and timing

### Regular-expression warning filters (`whatsnew-3.15`)

Message and module fields in `-W` and `PYTHONWARNINGS` are regular expressions
when enclosed in `/.../`.

### Warning assertions (`whatsnew-3.15`)

`unittest.TestCase.assertWarns()` and `assertWarnsRegex()` propagate warnings
that do not match the requested category or expression, and support nesting.
Add explicit filters if a test relied on incidental suppression.

### Formatter objects (`3.15.0b3`)

`logging.basicConfig(formatter=...)` accepts a formatter object, and
`unittest.TestCase.assertLogs(..., formatter=...)` controls captured formatting.
`logging.Formatter` and `Filter` have informative representations.

### Complete module cleanup failures (`3.15.0b3`)

`unittest.doModuleCleanups()` raises an `ExceptionGroup` when multiple cleanups
fail rather than discarding every exception after the first.

### Configurable timeit duration (`3.15.0b3`)

`Timer.autorange()` accepts a target duration; the CLI exposes it as
`--target-time`.

## Library migration checklist

### Removed and deprecated surfaces (`whatsnew-3.14`)

- Replace `pkgutil.get_loader()` / `find_loader()` with modern import APIs.
- Replace `pty.master_open()` / `slave_open()` with supported PTY APIs.
- Remove `urllib.request.URLopener` and `FancyURLopener` usage.
- Import resource ABCs from `importlib.resources.abc`, not `importlib.abc`.
- Replace deprecated `argparse.FileType` and `codecs.open()`.
- Prefer `subprocess` to soft-deprecated `os.popen()` and `os.spawn*()`.
- Call `Path.as_uri()` rather than `PurePath.as_uri()`.
