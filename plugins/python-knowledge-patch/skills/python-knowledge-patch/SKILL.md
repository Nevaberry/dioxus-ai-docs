---
name: python-knowledge-patch
description: "Python 3.14 features since training cutoff: t-strings (PEP 750), deferred annotations (PEP 649), subinterpreters (PEP 734), compression.zstd (PEP 784), functools.Placeholder, uuid7, pathlib copy/move, breaking changes (asyncio, multiprocessing, removals). Load before writing Python 3.14 code."
version: "3.14"
license: MIT
metadata:
  author: Nevaberry
  model: claude-opus-4-6
---

# Python Knowledge Patch

Claude's baseline knowledge covers Python through 3.12–3.13. This skill provides features from Python 3.14 (released 2025-10-07).

## Quick Reference

### New Syntax

| Feature | Example | Details |
|---------|---------|---------|
| T-strings (PEP 750) | `t"Hello {name}"` → `Template` | [new-syntax.md](references/new-syntax.md) |
| Deferred annotations (PEP 649) | Forward refs work without quotes | [new-syntax.md](references/new-syntax.md) |
| Bracketless except (PEP 758) | `except TimeoutError, OSError:` | [new-syntax.md](references/new-syntax.md) |

**T-strings** — new `t''` prefix creates `Template` objects for safe string processing:

```python
from string.templatelib import Template, Interpolation

name = "world"
template = t"Hello {name}!"  # type: Template
list(template)  # ['Hello ', Interpolation('world', 'name', None, ''), '!']


# Process templates for sanitization, SQL safety, etc.
def safe_html(template: Template) -> str:
    from html import escape

    parts = []
    for part in template:
        if isinstance(part, Interpolation):
            parts.append(escape(str(part.value)))
        else:
            parts.append(part)
    return "".join(parts)
```

**Deferred annotations** — forward references just work, no quotes needed:

```python
from annotationlib import get_annotations, Format

def func(x: UndefinedType) -> list[UndefinedType]:  # no NameError at definition
    pass

get_annotations(func, format=Format.VALUE)       # evaluates (raises if undefined)
get_annotations(func, format=Format.FORWARDREF)  # ForwardRef markers for unknowns
get_annotations(func, format=Format.STRING)       # {'x': 'UndefinedType', ...}
```

See `references/new-syntax.md` for t-string Interpolation attributes, safe_sql example, bracketless except details, PEP 765 finally warnings.

### New Modules & APIs

| Module / API | Purpose | Details |
|-------------|---------|---------|
| `compression.zstd` | Zstandard compression | [new-modules.md](references/new-modules.md) |
| `concurrent.interpreters` | Subinterpreters in stdlib | [concurrency.md](references/concurrency.md) |
| `InterpreterPoolExecutor` | Thread pool using subinterpreters | [concurrency.md](references/concurrency.md) |
| `functools.Placeholder` | Reserve positional args in `partial()` | [new-modules.md](references/new-modules.md) |
| `uuid.uuid7()` | Time-sortable UUID (RFC 9562) | [new-modules.md](references/new-modules.md) |
| `pathlib.Path.copy/move()` | Copy/move files and directory trees | [new-modules.md](references/new-modules.md) |
| `sys.remote_exec()` | Execute code in another Python process | [new-modules.md](references/new-modules.md) |
| `io.Reader` / `io.Writer` | Protocols replacing `typing.IO` | [new-modules.md](references/new-modules.md) |
| `map(strict=True)` | Check iterables equal length | [new-modules.md](references/new-modules.md) |
| `heapq.*_max()` | Max-heap operations | [new-modules.md](references/new-modules.md) |

**Zstandard compression:**

```python
from compression import zstd

compressed = zstd.compress(b"data to compress")
original = zstd.decompress(compressed)

# New preferred imports (old names still work, not deprecated):
from compression import lzma, bz2, gzip, zlib

# tarfile/zipfile/shutil support zstd archives
import tarfile
with tarfile.open("archive.tar.zst", "w:zst") as tar:
    tar.add("myfile.txt")
```

**Subinterpreters** — true multi-core parallelism without GIL contention:

```python
import concurrent.interpreters as interpreters

interp = interpreters.create()
interp.exec("print('hello from subinterpreter')")

# Or use the pool executor
from concurrent.futures import InterpreterPoolExecutor
with InterpreterPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(cpu_bound_fn, data))
```

Limitations: startup not optimized yet, limited object sharing (mainly `memoryview`), many PyPI extensions not yet compatible.

**functools.Placeholder:**

```python
from functools import partial, Placeholder as _

pow_of_2 = partial(pow, _, 2)  # first arg is placeholder
pow_of_2(10)  # pow(10, 2) = 100
```

**UUID versions 6, 7, 8 (RFC 9562):**

```python
import uuid
uuid.uuid6()  # time-ordered (like v1, better sorting)
uuid.uuid7()  # Unix timestamp + random (recommended for new designs)
uuid.uuid8()  # custom/user-defined
uuid.NIL      # 00000000-0000-0000-0000-000000000000
uuid.MAX      # ffffffff-ffff-ffff-ffff-ffffffffffff
```

**pathlib copy and move:**

```python
from pathlib import Path
Path("src").copy("dst")           # copy file or directory tree
Path("src").copy_into("dst_dir")  # copy into directory
Path("src").move("dst")           # move file or directory tree
Path("src").move_into("dst_dir")  # move into directory
```

**Remote debugging (PEP 768):**

```python
import sys
sys.remote_exec(pid, "/path/to/script.py")  # execute in target process
# Or: python -m pdb -p 1234
```

See `references/new-modules.md` for streaming zstd, io.Reader/Writer, heapq max-heap, and other additions.

### Concurrency Changes

| Feature | Details |
|---------|---------|
| Subinterpreters (PEP 734) | [concurrency.md](references/concurrency.md) |
| Free-threaded Python (PEP 779) | Officially supported, ~5-10% single-thread penalty |
| multiprocessing default `'forkserver'` | **Breaking on Linux** |

See `references/concurrency.md` for concurrency comparison table, free-threaded build flags, and multiprocessing migration.

### Breaking Changes

| Change | Impact | Details |
|--------|--------|---------|
| `asyncio.get_event_loop()` raises | Use `asyncio.run()` or `asyncio.Runner` | [removals.md](references/removals.md) |
| multiprocessing default `'forkserver'` | Linux fork-dependent code breaks | [concurrency.md](references/concurrency.md) |
| `int()` ignores `__trunc__()` | Implement `__int__()` or `__index__()` | [removals.md](references/removals.md) |
| pickle default protocol 5 | Can't be read by Python < 3.8 | [removals.md](references/removals.md) |
| `ast.Num/Str/Bytes` removed | Use `ast.Constant` | [removals.md](references/removals.md) |
| `bool(NotImplemented)` raises | `TypeError` instead of `True` | [removals.md](references/removals.md) |

**asyncio.get_event_loop() fix:**

```python
# BROKEN in 3.14:
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# FIX:
asyncio.run(main())

# For multiple sequential runs:
with asyncio.Runner() as runner:
    runner.run(operation_one())
    blocking_code()
    runner.run(operation_two())
```

**multiprocessing — if you need fork explicitly:**

```python
import multiprocessing
ctx = multiprocessing.get_context('fork')
p = ctx.Process(target=fn)
```

See `references/removals.md` for full list of removed APIs, deprecations, and planned removals in 3.16+.

### Other Notable Changes

- `datetime.date.strptime()` and `datetime.time.strptime()` class methods
- `http.server.HTTPSServer` — `python -m http.server --tls-cert cert.pem`
- `python -m json` replaces `python -m json.tool` (soft deprecated)
- `os.path.realpath(strict=os.path.ALLOW_MISSING)` — resolve symlinks, allow missing tail
- `types.UnionType` is now alias for `typing.Union` — both syntaxes produce same type
- `asyncio` introspection: `python -m asyncio ps PID`, `asyncio.capture_call_graph()`
- Free-threaded Python officially supported (PEP 779), ~5-10% single-thread penalty

## Reference Files

| File | Contents |
|------|----------|
| [new-syntax.md](references/new-syntax.md) | T-strings, deferred annotations, bracketless except, finally warnings |
| [new-modules.md](references/new-modules.md) | compression.zstd, functools.Placeholder, uuid 6/7/8, pathlib copy/move, remote debugging, io protocols |
| [concurrency.md](references/concurrency.md) | Subinterpreters, InterpreterPoolExecutor, free-threaded Python, multiprocessing start method change |
| [removals.md](references/removals.md) | asyncio breaking changes, removed APIs (ast, itertools, pkgutil, urllib), deprecations |
