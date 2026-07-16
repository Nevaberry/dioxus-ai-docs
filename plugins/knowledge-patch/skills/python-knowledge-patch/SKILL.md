---
name: python-knowledge-patch
description: Python 3.14 compatibility. Use for Python work.
license: MIT
version: "3.14"
metadata:
  author: Nevaberry
---

# Python Knowledge Patch

Baseline: Python through 3.12. Covered range: Python 3.13 and 3.14, plus the Python 3.15.0b3 preview.

Included batches: `whatsnew-3.13`, `3.13.0`, `whatsnew-3.14`, `3.14.0`, `whatsnew-3.15`, and `3.15.0b3`.

Use the quick reference for migration-sensitive decisions, then open the topic reference that matches the code being changed. Treat every Python 3.15 item as preview behavior and gate it by the actual runtime version.

## Reference index

| Reference | Topics |
| --- | --- |
| [Language and runtime](references/language-and-runtime.md) | Syntax and execution, built-ins, object model, text and numeric behavior, garbage collection, removals |
| [Typing and introspection](references/typing-and-introspection.md) | Deferred annotations, typing, ASTs, frames and locals, signatures, symbols, runtime metadata |
| [Concurrency and asyncio](references/concurrency-and-asyncio.md) | Asyncio, threads and queues, multiprocessing, executors, subinterpreters, free-threading |
| [Data, I/O, and serialization](references/data-io-and-serialization.md) | Configuration, SQLite and dbm, serialization, compression, archives, streams, codecs, TOML and JSON |
| [Networking and security](references/networking-and-security.md) | TLS, HTTP, URLs, email, sockets, protocol validation, parser hardening |
| [Filesystems, OS, and platforms](references/filesystem-os-and-platforms.md) | pathlib, OS APIs, mmap, resources, virtual environments, locale, platform behavior |
| [Tooling, debugging, and testing](references/tooling-debugging-and-testing.md) | REPL, pdb, profiling, monitoring, CLI parsing, logging, tests, imports and packaging |
| [C API and extensions](references/c-api-and-extensions.md) | Compatibility, references and errors, types and modules, free-threading, Stable/Limited APIs, embedding |
| [Build and distribution](references/build-and-distribution.md) | Build prerequisites, configure controls, JIT, cross-builds, platform targets, artifacts |

## Compatibility first

### Runtime and language changes

- In optimized scopes, each `locals()` call returns an independent snapshot. `frame.f_locals` is instead a write-through proxy; copy it when a stable dictionary is needed.
- An implicit `exec()` or `eval()` namespace no longer makes newly assigned optimized locals observable afterward. Pass explicit globals and locals when retrieving results.
- AST constructors currently warn for missing required fields or unknown keyword fields and make them errors in 3.15. Python 3.14 removes the old constant-node aliases; use `ast.Constant.value` and `visit_Constant()`.
- Python 3.14 makes annotations lazy. Annotation readers should use `annotationlib` instead of assuming values are eagerly present in `__annotations__` or a class namespace.
- `int()` no longer falls back to `__trunc__()`, and Boolean evaluation of `NotImplemented` raises `TypeError` in 3.14.
- `return`, `break`, or `continue` that exits a `finally` block emits a compile-time `SyntaxWarning` in 3.14.
- The default pickle protocol is 5 in 3.14. Choose an older protocol explicitly when older readers must consume the data.
- Python 3.14.0–3.14.4 used the incremental garbage collector; 3.14.5 and later reverted to the 3.13 generational collector. Do not infer collector behavior from the minor version alone.
- `functools.partial` used directly as a class attribute warns in 3.13; wrap it in `staticmethod()` to retain non-binding behavior.
- Regular-expression `maxsplit`, `count`, and `flags` parameters are becoming keyword-only. Name them now.

```python
namespace = {}
exec("answer = 42", globals(), namespace)
answer = namespace["answer"]

parts = re.split(pattern, text, maxsplit=1, flags=re.ASCII)
```

### Asyncio and process behavior

- `asyncio.get_event_loop()` raises `RuntimeError` when no current loop exists in 3.14. Use `asyncio.run()`, `get_running_loop()`, or `asyncio.Runner` as appropriate.
- Event-loop policy APIs are deprecated for removal in 3.16. Select an implementation with `loop_factory` on `asyncio.run()` or `Runner`.
- Task creation APIs pass arbitrary keyword arguments to the task constructor or task factory in 3.14. Custom factories must accept `name`, `context`, and future keywords.
- On Unix other than macOS, multiprocessing and `ProcessPoolExecutor` default to `forkserver` in 3.14, not `fork`. Explicitly request a context if inherited globals are required.
- `queue.Queue` and `asyncio.Queue` have explicit `shutdown()` methods and raise `ShutDown` or `QueueShutDown` at termination.
- `Server.wait_closed()` now waits for closure and all active connections. A Unix server removes its socket when it closes.
- Third-party asyncio task implementations must implement `Task.set_name()`; `_set_task_name()` is removed.

```python
tasks = [asyncio.create_task(fetch(url)) for url in urls]
async for task in asyncio.as_completed(tasks):
    # Async iteration preserves supplied task/future identity.
    result = await task
```

### Standard-library migrations

- `dbm` now selects the SQLite backend by default. Select a backend explicitly when file format or implementation stability matters.
- `ssl.create_default_context()` enables `VERIFY_X509_PARTIAL_CHAIN` and `VERIFY_X509_STRICT`; previously accepted malformed certificates can fail verification.
- `Path.glob()` and `rglob()` patterns ending in `**` return files and directories. Add a trailing slash for directories only, and use `recurse_symlinks` deliberately.
- On Windows, a path beginning with exactly one slash or backslash is no longer absolute. Mode `0o700` now applies access control in `mkdir()` and `makedirs()`.
- `Path.exists()` and the `Path.is_*()` predicates suppress every `OSError` in 3.14. Use `stat()` when the failure must be visible.
- Passing filesystem paths to `mimetypes.guess_type()` is soft-deprecated; use `guess_file_type()`.
- Email address parsing is strict by default, generated headers are verified, and invalid field names raise `ValueError`.
- Unclosed `sqlite3.Connection`, `NamedTemporaryFile`, and `GzipFile` objects can emit `ResourceWarning`. Use explicit closure, not only transaction context management.
- `gzip.compress()` defaults to `mtime=0` in 3.14 for reproducibility. Pass `mtime=None` to record the current time.
- `ZipFile.writestr()` respects `SOURCE_DATE_EPOCH`; Python 3.15 preview lowers gzip and gzip-tar default compression from 9 to 6.
- SQLite named placeholders require a mapping in 3.14; supplying a sequence raises `ProgrammingError`. Several connect parameters become keyword-only in 3.15.
- `urllib.parse.parse_qs()` and `parse_qsl()` deprecate unsupported false values such as `0` and `[]`; bytes handling and lossless component options also changed.
- `argparse.ArgumentParser.suggest_on_error` defaults to true in the 3.15 preview, and inferred destinations for overlapping short/long forms can change.
- Python 3.15 removes CGI support from `http.server`, legacy `sre_*` modules, `PurePath.is_reserved()`, `code.co_lnotab`, `zipimporter.load_module()`, and several other deprecated APIs. Review both removal sections before targeting it.

### C extensions and embedding

- Free-threaded 3.13 uses `python3.13t` or `--disable-gil`. Extensions declare support with `Py_mod_gil` or `PyUnstable_Module_SetGIL()`; undeclared extensions normally re-enable the GIL.
- Python 3.14 supports free-threaded builds officially but optionally. Windows backends targeting them must define `Py_GIL_DISABLED` themselves.
- Python 3.15 preview adds the `abi3t` Stable ABI. Use opaque per-type storage and the new module export/slot machinery; publish a separate `cp315t` build for APIs outside `abi3t`.
- `PyDict_Next()` does not lock in free-threaded builds. Hold one critical section around the whole iteration.
- `PyModule_Add()` always steals the supplied reference, including on failure.
- `Python.h` no longer supplies several system headers transitively. Include every declaration's owning header directly.
- `PY_SSIZE_T_CLEAN` is obsolete, and removed trashcan macros must become `Py_TRASHCAN_BEGIN(object, deallocator)` / `Py_TRASHCAN_END`.
- Removed buffer, call, and initialization entry points must migrate to `PyObject_GetBuffer()` plus `PyBuffer_Release()`, `PyObject_Call*()`, and `PyConfig` initialization.
- Borrowed operand-stack references make refcount-based uniqueness checks unsafe. Use the appropriate `PyUnstable_Object_Is*Referenced()` API.
- `Py_Finalize()` deletes interned strings in 3.14. Embedders that reinitialize must release extension-held interned references during shutdown.
- In the 3.15 preview, finalization-safe interpreter guards and attach/detach APIs replace check-then-attach patterns; the `PyGILState` family is soft-deprecated.

## High-value features

### Deferred annotations and runtime typing

Python 3.14 evaluates function, class, and module annotations lazily. Choose the representation required by the consumer:

```python
from annotationlib import Format, get_annotations

def parse(value: Missing): ...

hints = get_annotations(parse, format=Format.FORWARDREF)
```

- `Format.VALUE` evaluates values and can raise for missing names.
- `Format.FORWARDREF` preserves unresolved names as `ForwardRef` objects.
- `Format.STRING` returns source-like strings.
- `inspect.signature()` accepts `annotation_format`.
- `types.UnionType` and `typing.Union` are aliases in 3.14; compare unions by equality or use `get_origin()` / `get_args()`, not identity.
- The 3.15 preview adds `TypeForm`, closed or extensible `TypedDict`, richer `TypeVarTuple`, and more metadata on type aliases.

### T-strings and structured interpolation

A `t`-prefixed literal creates `string.templatelib.Template`, retaining static strings and interpolation objects for safe DSL-specific rendering:

```python
name = "Ada"
template = t"Hello {name}"
for part in template:
    process(part)
```

Templates do not concatenate with `str`, and t-string literals do not implicitly concatenate with string or f-string literals in 3.15.0b3.

### Free-threading and subinterpreters

- Query free-threaded runtime state with `sys._is_gil_enabled()` and control it with `PYTHON_GIL` or `-X gil` where supported.
- `concurrent.interpreters` exposes isolated interpreters in 3.14, while `InterpreterPoolExecutor` provides a true-multicore executor inside one process.
- Sharing between interpreters is opt-in and limited. Gate portable use with `sys.implementation.supports_isolated_interpreters` in 3.15.0b3.
- `-X context_aware_warnings` and `sys.flags.thread_inherit_context` default on for free-threaded builds and off for GIL-enabled builds.
- Use object critical sections, `PyMutex`, and the documented iterator synchronization APIs rather than assuming the GIL serializes access.

### Asyncio lifecycle and observability

- Asynchronous iteration over `asyncio.as_completed()` can yield the original task or future objects.
- `Executor.map(buffersize=n)` applies submission backpressure; process pools can terminate or kill all workers explicitly.
- `multiprocessing.Process.interrupt()` sends `SIGINT`, allowing normal `KeyboardInterrupt` and `finally` cleanup.
- `python -m asyncio ps PID` and `pstree PID` inspect remote task graphs; in-process code can use `capture_call_graph()` and `print_call_graph()`.
- `await pdb.set_trace_async()` supports `await` while debugging a coroutine.
- The 3.15 preview adds `TaskGroup.cancel()` for direct group cancellation.

### Data, archives, and I/O

- `compression.zstd` and the preferred `compression.{gzip,bz2,lzma,zlib}` namespace arrive in 3.14; tar, ZIP, and shutil understand Zstandard archives.
- `marshal` format 5 serializes slices; `allow_code=False` blocks code-object serialization and deserialization.
- `mmap(..., trackfd=False)` avoids retaining a duplicate descriptor on Unix and, in the 3.15 preview, on Windows.
- `Path.info` caches type/stat information, including details obtained during `iterdir()`.
- `tomllib.TOMLDecodeError` exposes structured location fields in 3.14; the 3.15 preview accepts TOML 1.1.
- The 3.15 preview adds `json`'s `array_hook`, shelf serializer hooks, `bytearray.take_bytes()`, and stricter/canonical base-encoding controls.

### Debugging and profiling

- `breakpoint()` and `pdb.set_trace()` stop at the call site in 3.13. Pdb can execute statements against current-frame locals and attach remotely in 3.14.
- Remote execution and attach can be disabled with `PYTHON_DISABLE_REMOTE_DEBUG`, `-X disable-remote-debug`, or `--without-remote-debug`.
- The 3.15 preview introduces `profiling.tracing` and `profiling.sampling`; `cProfile` remains an alias, while pure-Python `profile` is deprecated.
- Sampling supports PID attach, scripts/modules, wall/CPU/GIL/exception modes, flame graphs, pstats, heatmaps, live TUI, async-aware views, and compact replayable captures.
- `sys.monitoring` gains directional branch events in 3.14 and per-code exception-event control in 3.15.

### Python 3.15 preview features

Explicit lazy imports defer loading until first use and report failures at that point:

```python
lazy import json
lazy from pathlib import Path

data = json.loads('{"answer": 42}')
```

- Lazy declarations are module-scope only and exclude functions, classes, `try`, star imports, and future imports.
- `-X lazy_imports=all` or `PYTHON_LAZY_IMPORTS=all` changes the default; inspect and control it through `sys.get_lazy_imports()`, `set_lazy_imports()`, and filters.
- `frozendict` is immutable, insertion-ordered, and conditionally hashable; test generic mappings with `collections.abc.Mapping`.
- `sentinel()` creates identity-stable marker values that survive copying and can be pickleable when importable by name.
- Comprehensions and generator expressions accept `*` and `**` unpacking.
- `map(..., strict=True)` is a 3.14 feature; the preview additionally supplies synchronized/concurrent iterator utilities and expands free-threaded iterator guarantees.

## Upgrade workflow

1. Confirm the exact interpreter and maintenance release; distinguish 3.14.0–3.14.4 from 3.14.5+ for garbage collection and treat 3.15.0b3 as preview-only.
2. Search for removals and deprecations first: asyncio policies, implicit event-loop creation, AST aliases, old import-loader APIs, positional regex/SQLite arguments, C API removals, and 3.15 standard-library removals.
3. Audit defaults that can silently change output or behavior: multiprocessing start method, pickle protocol, dbm backend, TLS verification flags, gzip timestamps/compression, argparse suggestions, and URL/base64 parsing.
4. Review concurrency assumptions for free-threading, context inheritance, task-factory keyword forwarding, queue shutdown, iterator sharing, and native critical sections.
5. Update annotation consumers before enabling 3.14, and gate lazy imports, frozendict, sentinels, unpacking comprehensions, and `abi3t` behind 3.15 checks.
6. Run tests with warnings enabled and `ResourceWarning` visible; exercise filesystem errors, malformed protocol fields, nonblocking streams, serialization compatibility, interpreter shutdown, and extension imports.
7. Open the indexed topic references for the complete API-level details; the quick reference intentionally prioritizes migration-sensitive changes.
