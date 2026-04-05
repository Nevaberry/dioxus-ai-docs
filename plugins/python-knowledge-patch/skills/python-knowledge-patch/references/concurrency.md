# Concurrency: Interpreters, Free-Threading, GIL

## concurrent.interpreters (PEP 734) — Python 3.14

New module exposing subinterpreters — isolated Python instances in the same process. Each interpreter has its own GIL, enabling true multi-core parallelism.

### Basic Usage

```python
import concurrent.interpreters as interpreters

# Create and run code in a subinterpreter
interp = interpreters.create()
interp.exec("print('hello from subinterpreter')")

# Pass data via channels (CSP-style)
# Note: only simple types and memoryview can be shared
```

### InterpreterPoolExecutor

```python
from concurrent.futures import InterpreterPoolExecutor


def cpu_work(n):
    return sum(i * i for i in range(n))


with InterpreterPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(cpu_work, 10_000_000) for _ in range(4)]
    results = [f.result() for f in futures]
```

### Key Properties

- **Isolation**: Each interpreter has its own globals, modules, GIL — like processes but in-process
- **Efficiency**: Lower overhead than `multiprocessing` (no IPC, shared memory space)
- **Sharing**: Limited to `memoryview` and simple types currently
- **Compatibility**: All stdlib extension modules work; many PyPI extensions don't yet

### vs Other Concurrency

| | `threading` | `multiprocessing` | `interpreters` |
|---|---|---|---|
| Isolation | None (shared memory) | Full (separate process) | High (separate GIL, opt-in sharing) |
| Parallelism | No (GIL) | Yes | Yes |
| Overhead | Low | High (process spawn) | Medium |
| Data sharing | Direct | Pickle/shared memory | memoryview, channels |

## Free-Threaded Python — Python 3.14

Free-threaded mode (no-GIL, PEP 703) is now officially supported (PEP 779) in 3.14. Performance penalty is ~5-10% for single-threaded code.

### Notable 3.14 Changes

- Specializing adaptive interpreter enabled in free-threaded mode
- `asyncio` supports parallel event loops across threads
- `Py_GIL_DISABLED` must be set explicitly by build backends on Windows
- `-X context_aware_warnings` flag (defaults to true for free-threaded builds)
- `-X thread_inherit_context` flag — new threads inherit caller's `Context` (defaults to true for free-threaded builds)

## multiprocessing Default Start Method Change — Python 3.14

**Breaking on Linux/Unix (not macOS)**: Default start method changed from `'fork'` to `'forkserver'`.

### Impact

- Code relying on shared mutable globals after fork may break
- Objects must be picklable to pass to child processes
- More similar to `'spawn'` behavior (already default on Windows/macOS)

### If You Need fork

```python
import multiprocessing

# Option 1: explicit context (preferred)
ctx = multiprocessing.get_context('fork')
p = ctx.Process(target=fn)

# Option 2: change default (affects entire program)
multiprocessing.set_start_method('fork')

# Also affects ProcessPoolExecutor:
from concurrent.futures import ProcessPoolExecutor
executor = ProcessPoolExecutor(mp_context=multiprocessing.get_context('fork'))
```
