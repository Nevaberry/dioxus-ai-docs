# Concurrency

## Free-threaded CPython (3.13+, PEP 703)

Experimental support for running without the GIL (Global Interpreter Lock), enabling true parallel execution of Python threads.

### Setup

| What | How |
|------|-----|
| Install | Use "free-threaded" installer variant or build with `--disable-gil` |
| Executable | `python3.13t` (note the `t` suffix) |
| Re-enable GIL | `PYTHON_GIL=1` or `-X gil=1` |
| Force disable GIL | `PYTHON_GIL=0` or `-X gil=0` |
| Check at runtime | `sys._is_gil_enabled()` → `False` when GIL disabled |
| Detect build | `python -VV` includes "experimental free-threading build" |

### C extension compatibility

- Extensions must declare free-threading support via `Py_mod_gil` slot
- Extensions without this declaration **silently re-enable the GIL** on import
- Exception: `PYTHON_GIL=0` forces GIL off even with incompatible extensions
- pip 24.1+ required to install C extensions for free-threaded builds

### Performance notes

- **3.13**: Notable single-threaded performance penalty (experimental)
- **3.14**: Penalty reduced to ~5-10%; free-threaded mode officially supported (PEP 779)

## Subinterpreters (3.14, PEP 734)

Multiple isolated Python interpreters in one process. Like threads with opt-in sharing, or multiprocessing without process overhead.

### `concurrent.interpreters` module

```python
import concurrent.interpreters as interpreters

# Create and run code in an interpreter
interp = interpreters.create()
interp.exec("print('hello from subinterpreter')")
interp.close()
```

### `InterpreterPoolExecutor`

```python
from concurrent.futures import InterpreterPoolExecutor

with InterpreterPoolExecutor() as executor:
    results = list(executor.map(cpu_bound_func, data))
```

### Key properties

- **Isolation**: Each interpreter has its own GIL and global state (like separate processes)
- **Efficiency**: All in one process (like threads), no IPC overhead
- **Sharing**: Opt-in only via `memoryview`; data typically passed by copy

### Current limitations (expected to improve)

- Interpreter startup not optimized yet
- Each interpreter uses more memory than needed
- Limited options for sharing objects between interpreters
- Many third-party C extensions not yet compatible
