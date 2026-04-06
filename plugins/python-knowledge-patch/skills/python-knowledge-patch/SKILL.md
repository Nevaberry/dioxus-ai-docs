---
name: python-knowledge-patch
description: "Python changes since training cutoff (latest: 3.14) — t-strings, deferred annotations, free-threaded CPython, subinterpreters, zstd compression, dead battery removals. Load before working with Python."
license: MIT
version: "3.14"
metadata:
  author: Nevaberry
---

# Python 3.13+ Knowledge Patch

Claude's baseline knowledge covers Python through 3.12. This skill provides features from 3.13 (Oct 2024) onwards.

**Source**: Python "What's New" documentation at https://docs.python.org/3/whatsnew/

## 3.13 Breaking Changes

| Change | Impact |
|--------|--------|
| 19 "dead battery" modules removed (PEP 594) | `ImportError` for `cgi`, `crypt`, `imghdr`, `telnetlib`, etc. See [removals](references/removals.md) |
| `locals()` returns snapshots in functions (PEP 667) | `exec()`/`eval()` in functions need explicit namespace. See [new-modules](references/new-modules.md) |
| `TypedDict("T", x=int)` keyword syntax removed | Use class syntax or `TypedDict("T", {"x": int})` |
| `pathlib.Path.glob("**")` returns files AND dirs | Add trailing `/` for dirs only: `glob("**/")` |
| Docstring leading whitespace stripped | May affect `doctest` tests |

## 3.13 New Features

| Feature | Quick reference |
|---------|----------------|
| Free-threaded CPython (PEP 703) | `python3.13t`, `sys._is_gil_enabled()`, `PYTHON_GIL=0`. See [concurrency](references/concurrency.md) |
| `copy.replace()` protocol | `copy.replace(obj, field=val)`, implement `__replace__()`. See [new-modules](references/new-modules.md) |
| `warnings.deprecated()` (PEP 702) | `@deprecated("msg")` — runtime warning + type checker signal. See [new-modules](references/new-modules.md) |

## 3.14 New Syntax

| Feature | Quick reference |
|---------|----------------|
| T-strings (PEP 750) | `t"Hello {name}"` → `Template` object. `from string.templatelib import Template, Interpolation`. See [new-syntax](references/new-syntax.md) |
| Deferred annotations (PEP 649/749) | Forward refs no longer need quotes. `from annotationlib import get_annotations, Format`. See [new-syntax](references/new-syntax.md) |
| `except` without brackets (PEP 758) | `except A, B:` (no parens, no `as`). Parens still needed with `as`. |

## 3.14 New Modules

| Module | Quick reference |
|--------|----------------|
| `compression.zstd` (PEP 784) | `from compression import zstd; zstd.compress(data)`. See [new-modules](references/new-modules.md) |
| `concurrent.interpreters` (PEP 734) | Subinterpreters + `InterpreterPoolExecutor`. See [concurrency](references/concurrency.md) |
| `annotationlib` | `get_annotations(obj, format=Format.FORWARDREF)` |
| `functools.Placeholder` | `partial(func, Placeholder, fixed_arg)` — reserve positional slots |

## 3.14 Breaking Changes

| Change | Impact |
|--------|--------|
| `asyncio.get_event_loop()` raises `RuntimeError` | Must use `asyncio.run()` or `asyncio.Runner` |
| `multiprocessing` default → `'forkserver'` on Linux | May cause pickling errors; use `get_context('fork')` |
| `int()` no longer uses `__trunc__()` | Must implement `__int__()` or `__index__()` |
| `functools.partial` is method descriptor | Wrap in `staticmethod()` for classes |
| `from __future__ import annotations` deprecated | Unchanged behavior; removal after 2029 |
| `ast.Num`/`Str`/`Bytes` removed | Use `ast.Constant` |
| `asyncio` child watcher classes removed | Use `asyncio.run()` |
| SyntaxWarning in `finally` (PEP 765) | `return`/`break`/`continue` in `finally` now warns |

## 3.14 New APIs

| API | Quick reference |
|-----|----------------|
| `sys.remote_exec(pid, script)` (PEP 768) | Attach debugger to running process; `python -m pdb -p PID`. See [new-modules](references/new-modules.md) |
| `io.Reader` / `io.Writer` | Simpler protocol alternatives to `typing.IO` |
| `uuid.uuid7()` | Time-ordered UUID (RFC 9562); also `uuid6()`, `uuid8()` |
| `heapq.*_max()` | `heapify_max()`, `heappush_max()`, `heappop_max()`, etc. |
| Free-threading (PEP 779) | Now officially supported; 5-10% overhead |

## Reference Files

For detailed patterns, code examples, and migration guidance, consult:

- **[`references/new-syntax.md`](references/new-syntax.md)** — T-strings (template processors, API), deferred annotations (`annotationlib`), `except` without brackets
- **[`references/new-modules.md`](references/new-modules.md)** — `compression.zstd`, `functools.Placeholder`, `copy.replace()`, `warnings.deprecated()`, `locals()` semantics, remote debugging, `io.Reader`/`Writer`, `uuid.uuid7()`, `heapq` max-heap
- **[`references/concurrency.md`](references/concurrency.md)** — Free-threaded CPython (GIL-free mode), subinterpreters, `InterpreterPoolExecutor`
- **[`references/removals.md`](references/removals.md)** — Dead batteries (19 modules), 3.13/3.14 removals, breaking behavior changes
