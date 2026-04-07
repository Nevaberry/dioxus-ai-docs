# New Modules and APIs

## `copy.replace()` and `__replace__()` protocol (3.13)

Generic way to create modified copies of objects:

```python
import copy
from datetime import date

d2 = copy.replace(date(2024, 1, 1), year=2025)  # date(2025, 1, 1)
```

Works with: namedtuples, dataclasses, datetime objects, `SimpleNamespace`. For custom classes, implement `__replace__(self, **changes)`.

## `warnings.deprecated()` decorator (3.13, PEP 702)

```python
from warnings import deprecated

@deprecated("Use new_function() instead")
def old_function(): ...
```

Emits `DeprecationWarning` at runtime and signals deprecation to type checkers.

## `locals()` semantics change (3.13, PEP 667)

In optimized scopes (functions, generators, comprehensions), `locals()` now returns an **independent snapshot** each call. Breaking change for `exec()`/`eval()` in functions:

```python
# BROKEN on 3.13+: exec() runs against a snapshot, changes not visible
def f():
    exec("x = 1")
    print(locals())  # "x" is NOT here


# FIX: pass an explicit namespace
def f():
    ns = {}
    exec("x = 1", ns)
    print(ns["x"])  # Works
```

`frame.f_locals` now returns a **write-through proxy** in optimized scopes (useful for debuggers).

## `compression` package (3.14, PEP 784)

New top-level `compression` package with Zstandard support:

```python
from compression import zstd

compressed = zstd.compress(data)
original = zstd.decompress(compressed)
```

The package also re-exports existing compression modules under new names:

| New import | Old import |
|-----------|-----------|
| `compression.zstd` | — (new) |
| `compression.lzma` | `lzma` |
| `compression.bz2` | `bz2` |
| `compression.gzip` | `gzip` |
| `compression.zlib` | `zlib` |

Old import names are NOT deprecated (no removal planned for at least 5 years).

Zstd compression also supported in `tarfile`, `zipfile`, and `shutil`.

## `annotationlib` module (3.14, PEP 749)

For introspecting deferred annotations:

```python
from annotationlib import get_annotations, Format

get_annotations(obj, format=Format.VALUE)  # Evaluate annotations (may raise NameError)
get_annotations(obj, format=Format.FORWARDREF)  # ForwardRef markers for unknowns
get_annotations(obj, format=Format.STRING)  # Annotations as strings
```

Use `Format.FORWARDREF` for robust annotation reading (handles forward references gracefully).

## `concurrent.interpreters` module (3.14, PEP 734)

See [concurrency.md](concurrency.md) for full details.

## `string.templatelib` module (3.14, PEP 750)

See [new-syntax.md](new-syntax.md) for t-string details.

## `functools.Placeholder` (3.14)

Sentinel for reserving positional argument slots in `partial()`:

```python
from functools import partial, Placeholder

# Fix 2nd arg to 2, leave 1st open
f = partial(pow, Placeholder, 2)
f(3)  # pow(3, 2) == 9

# Fix 2nd and 3rd args, leave 1st open
f = partial(pow, Placeholder, 2, 10)
f(3)  # pow(3, 2, 10) == 9
```

## Remote debugging (3.14, PEP 768)

Attach debugger to running processes without stopping them:

```python
import sys

sys.remote_exec(pid, "/path/to/debug_script.py")  # Execute in target process
```

CLI: `python -m pdb -p 1234`. Disable with `PYTHON_DISABLE_REMOTE_DEBUG=1` or `-X disable-remote-debug`.

## `io.Reader` / `io.Writer` (3.14)

Simpler protocol alternatives to `typing.IO` / `typing.TextIO`.

## `uuid.uuid7()` (3.14)

Time-ordered UUID per RFC 9562. Also `uuid6()` and `uuid8()`.

## `heapq` max-heap functions (3.14)

`heapify_max()`, `heappush_max()`, `heappop_max()`, `heapreplace_max()`, etc.
