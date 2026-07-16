# Language and runtime

Use this reference for syntax and execution, built-ins and the object model, text and numeric behavior, garbage collection, and compatibility migrations.

## Compatibility, deprecations, and failure changes

### Finalization-specific failures (Python 3.13)
`PythonFinalizationError`, a `RuntimeError` subclass, now distinguishes operations blocked during interpreter shutdown; `_thread.start_new_thread()`, `os.fork()`, `os.forkpty()`, and `subprocess.Popen` raise it instead of a generic `RuntimeError`.

### Regular-expression arguments becoming keyword-only (Python 3.13)
Passing `maxsplit` to `re.split()`, `count` to `re.sub()` or `re.subn()`, or their `flags` arguments positionally is deprecated; name these arguments now.

```python
parts = re.split(pattern, text, maxsplit=1, flags=re.ASCII)
```

### Cleanup of invalid generator context managers (3.13.0)
Context managers created by `contextmanager()` or `asynccontextmanager()` now close their underlying generator when it invalidly yields more than once.

### More specific `dataclasses.replace()` failures (3.13.0)
`dataclasses.replace()` raises `TypeError`, rather than `ValueError`, when passed an `init=False` field or when a required `InitVar` is omitted.

### Lesser-known legacy API cleanup (3.13.0)
Python 3.13 removes the no-op `Path` context-manager protocol, the `cafile`, `capath`, and `cadefault` arguments of `urlopen()`, the `logging.warn()` aliases, `re.template`/`re.T`/`re.TEMPLATE`, and the deprecated `typing.io` and `typing.re` namespaces. Passing arguments to `threading.RLock()`, copying or pickling itertools objects, using `glob.glob0()`/`glob.glob1()`, and Decimal's undocumented `N` format are now deprecated.

### Built-in protocol breaks (Python 3.14)
`int()` no longer falls back to `__trunc__()`, so custom numeric classes need `__int__()` or `__index__()`. Using `NotImplemented` as a Boolean now raises `TypeError` rather than merely warning.

### Removed legacy library APIs (Python 3.14)
Resource ABCs were removed from `importlib.abc` in favor of `importlib.resources.abc`; `pkgutil.get_loader()`/`find_loader()`, `pty.master_open()`/`slave_open()`, and the old `urllib.request.URLopener` classes are gone. `sqlite3.version`/`version_info` are removed in favor of `sqlite_version` values, and itertools iterators no longer support copying or pickling.

### New library migration warnings (Python 3.14)
`argparse.FileType` is deprecated in favor of opening resources after parsing, `codecs.open()` in favor of `open()`, `os.popen()` and `os.spawn*()` in favor of `subprocess`, and `PurePath.as_uri()` in favor of `Path.as_uri()`. Passing unsupported false-valued objects such as `0` or `[]` to `urllib.parse.parse_qs()`/`parse_qsl()`, or a complex number as the `real` or `imag` component of two-argument `complex()`, is also deprecated.

### New failure behavior in common libraries (Python 3.15 preview)
Email generation raises when a non-ASCII mailbox cannot be flattened accurately unless an appropriate UTF-8 email policy is used. `importlib.metadata.metadata()` and `Distribution.metadata()` now raise `MetadataNotFound` when a distribution directory lacks its metadata file, and guaranteed `hashlib` algorithms remain present as attributes even when a missing backend makes calls fail at runtime.

`unittest.assertWarns()` and `assertWarnsRegex()` no longer swallow unrelated warnings and can be nested; tests may therefore expose warnings that previously disappeared and should filter or assert them explicitly.

### Python-level removals and enforced migrations (Python 3.15 preview)
Python 3.15 removes `ctypes.SetPointerType()`, `http.server.CGIHTTPRequestHandler` and `--cgi`, `platform.java_ver()`, the `sre_compile`/`sre_constants`/`sre_parse` modules, and `typing.no_type_check_decorator()`. It also removes `PurePath.is_reserved()` in favor of `os.path.isreserved()`, `code.co_lnotab` in favor of `co_lines()`, and `zipimporter.load_module()` in favor of `exec_module()`.

`datetime.strptime()` now raises `ValueError` for a day-of-month `%d` without a year; the corresponding `%e` form is deprecated for removal in 3.17. The `package=` spelling for `importlib.resources.files()` is gone, and `wave` marker methods are removed.

### New migration warnings (Python 3.15 preview)
Creating abstract AST base nodes is deprecated for removal in 3.20, `-b`/`-bb` are deprecated and become no-ops in 3.17, and hash constructors deprecate the inconsistent `string=` initial-data keyword in favor of a positional argument. Many standard-library `__version__`, `version`, and `VERSION` attributes are deprecated for removal in 3.20; use `sys.version_info` for the Python version and documented module-specific constants where provided.

### Additional Python-level removals (3.15.0b3)
Python 3.15 removes `glob.glob0()`/`glob.glob1()` in favor of `glob(..., root_dir=...)`, arbitrary arguments to `threading.RLock()`, `importlib.util.cache_from_source(debug_override=...)`, `sysconfig.is_python_build(check_home=...)`, and the `isxid*()` methods on `unicodedata.ucd_3_2_0`. The import machinery removes all remaining `load_module()` definitions in favor of `exec_module()`, and non-desktop Windows builds no longer expose unsupported `os.listdrives()`, `listvolumes()`, or `listmounts()`.

### Additional migration warnings (3.15.0b3)
`os.path.commonprefix()` is deprecated in favor of segment-aware `commonpath()`, and merely importing or accessing `collections.abc.ByteString` or `typing.ByteString` now warns; both byte-string aliases are absent from `__all__` and scheduled for removal in 3.17. Runtime-checkable status must be applied to each `Protocol` rather than inherited accidentally; bare `struct.Struct.__new__()` and reinitializing a `Struct` are deprecated, as are the external string-hash definition hook, cookie `js_output()`, `webbrowser.MacOSXOSAScript`, altering `IMAP4.file`, the legacy Tk variable trace methods, and non-ASCII names passed to `encodings.normalize_encoding()`.

## Syntax and execution

### Additional keyword-call support (3.13.0)
`str.replace()` accepts `count` by keyword, and the `globals` and `locals` arguments of `exec()` and `eval()` can now be passed by keyword.

```python
text = "one two two".replace("two", "three", count=1)
exec("answer = 42", globals={}, locals={})
```

### Template string literals (Python 3.14)
A `t`-prefixed literal produces `string.templatelib.Template` rather than `str`; iterating it preserves static strings and `Interpolation` objects separately so processors can safely render SQL, HTML, logging, or other DSLs.

```python
name = "Ada"
parts = list(t"Hello {name}")
```

### Parenthesis-free multiple exceptions (Python 3.14)
Multiple exception types may now follow `except` or `except*` without parentheses when there is no `as` clause; parentheses remain required when binding the exception.

```python
try:
    connect()
except TimeoutError, ConnectionRefusedError:
    recover()
```

### Control flow leaving `finally` (Python 3.14)
The compiler now emits `SyntaxWarning` when `return`, `break`, or `continue` exits a `finally` block; because this happens at compilation, suppress it before importing affected code, for example with `-Wignore::SyntaxWarning`.

### Deferred generator-expression validation (3.14.0)
A generator expression no longer calls its source's `__iter__()` once at creation and again at execution. Consequently, a non-iterable source now raises only when the generator starts running.

```python
items = (item for item in 42)  # construction succeeds
next(items)                    # TypeError
```

### Explicit lazy imports (Python 3.15 preview)
The new `lazy` soft keyword defers a module import until the bound name is first used; failures are consequently raised at first use, with a traceback that also identifies the original import. It works only at module scope with ordinary `import` and `from` forms, not in functions, classes, `try` blocks, star imports, or future imports.

```python
lazy import json
lazy from pathlib import Path

print("startup complete")  # neither module has loaded yet
data = json.loads('{"answer": 42}')
```

`-X lazy_imports=all` or `PYTHON_LAZY_IMPORTS=all` makes imports lazy by default; `normal` respects only explicit declarations. `sys.get_lazy_imports()`/`sys.set_lazy_imports()` control the mode, `sys.set_lazy_imports_filter()` can veto laziness per importer/imported module/fromlist, and a module can use `__lazy_modules__` for source compatible with older Python versions; proxies have type `types.LazyImportType`.

### Unpacking comprehensions (Python 3.15 preview)
List, set, and dictionary comprehensions and synchronous or asynchronous generator expressions now accept `*` and `**`, flattening each produced iterable or mapping without an extra nested loop.

```python
flat = [*items for items in ([1, 2], [3, 4])]
merged = {**mapping for mapping in ({"a": 1}, {"b": 2})}
stream = (*items for items in ([1, 2], [3, 4]))
```

### Warning-filter regular expressions (Python 3.15 preview)
The message and module fields of `-W` and `PYTHONWARNINGS` filters are treated as regular expressions when enclosed in `/.../`. Compilation and parsing APIs including `compile()`, `ast.parse()`, `symtable.symtable()`, and `InspectLoader.source_to_code()` can also receive the module name so syntax warnings can be filtered unambiguously.

### Context decorators span deferred execution (Python 3.15 preview)
`ContextDecorator`, `AsyncContextDecorator`, `contextmanager()`, and `asynccontextmanager()` used as decorators now keep their context open while a generated iterator runs or a coroutine is awaited, rather than closing it as soon as the generator or coroutine object is created. `ExitStack` and `AsyncExitStack` also honor arbitrary descriptors implementing the enter/exit methods, matching `with` statement lookup.

### T-string concatenation boundaries (3.15.0b3)
`string.templatelib.Template` cannot be concatenated with `str`, and a t-string literal cannot be implicitly concatenated with a string or f-string literal; render or combine their structured parts explicitly.

## Built-ins and the object model

### `functools.partial` used as a method (Python 3.13)
Using a bare `functools.partial` as a class attribute now emits `FutureWarning`; wrap it in `staticmethod()` to preserve the prior non-binding behavior.

```python
class C:
    operation = staticmethod(functools.partial(function, fixed_arg))
```

### Positional `SimpleNamespace` initialization (Python 3.13)
`types.SimpleNamespace` now accepts one positional mapping or iterable of key-value pairs, as in `SimpleNamespace({'x': 1})`, in addition to keyword initialization.

### Empty functional enums (3.13.0)
Creating an empty enum through the functional API now requires `names=()` or `type=...`; an otherwise underspecified empty functional call raises `TypeError`.

### Strict `map()` iteration (Python 3.14)
`map(function, *iterables, strict=True)` checks all input iterables have equal length instead of silently stopping at the shortest.

### Reflected modular powers (Python 3.14)
Three-argument `pow(base, exp, mod)` now tries `__rpow__()` when the left operand cannot handle the operation, matching reflected dispatch already used by two-argument power.

### Positional holes in partial calls (Python 3.14)
`functools.Placeholder` reserves arbitrary positional slots in `partial()` and `partialmethod()`, rather than only pre-filling arguments from the left.

```python
from functools import Placeholder as _, partial
square = partial(pow, _, 2)
assert square(5) == 25
```

### Serializable `super` objects (3.14.0)
`super` objects now support pickling and copying, allowing bound `super` state to pass through serialization or copy-based workflows.

### Built-in immutable mappings (Python 3.15 preview)
`frozendict` is an insertion-ordered immutable mapping, not a `dict` subclass; equality ignores order and it is hashable when every key and value is hashable. Serialization and copying modules understand it, and `eval()`, `exec()`, `type()`, and `str.maketrans()` accept it in mapping roles; generic consumers should test `collections.abc.Mapping` rather than only `dict`.

```python
options = frozendict(timeout=10, retries=3)
cache = {options: "result"}
```

### Built-in sentinel values (Python 3.15 preview)
The new `sentinel` built-in creates uniquely identifiable, concisely represented marker values. Sentinels retain identity through copying, may appear in unions such as `str | MISSING`, and are pickleable when importable by module and name.

```python
MISSING = sentinel("MISSING")
```

### Broader slots and generic slices (Python 3.15 preview)
Classes derived from `tuple`, including named-tuple classes, may now define arbitrary `__slots__`, and `__dict__` and `__weakref__` slots may be defined for any class. `slice` is also subscriptable for runtime type expressions such as `slice[int]`, and unary `+` is accepted in match-statement literal patterns.

### Lazy-import state refinements (3.15.0b3)
`sys.lazy_modules` is a set rather than the dictionary originally proposed by PEP 810. Under `PYTHON_LAZY_IMPORTS=all`, imports executed by `exec()` inside functions can also be lazy.

### Custom sentinel metadata (3.15.0b3)
`sentinel()` accepts `repr=` for a custom representation, and a sentinel's `__module__` attribute is writable so dynamically created sentinels can be made importable and pickleable under the intended module.

### Mutable bases for built-in subclasses (3.15.0b3)
The `__bases__` tuple may now be reassigned on a direct subclass of a built-in class, subject to the usual compatible-layout checks.

## Text, numbers, dates, and collections

### Zero-valued geometric means (3.13.0)
`statistics.geometric_mean()` now returns zero when its input contains zero; it previously raised an exception.

### Symmetric date/datetime comparison dispatch (3.13.0)
The comparison methods for a `date` and a `datetime` now return `NotImplemented` instead of silently ignoring the time and zone or forcing a result, allowing subclass comparison methods to participate symmetrically.

### ASCII-buffer hex parsing (Python 3.14)
`bytes.fromhex()` and `bytearray.fromhex()` now accept ASCII `bytes` and other bytes-like inputs, avoiding a preliminary decode to `str`.

### Fractional digit grouping (Python 3.14)
Comma and underscore grouping options in `format()` and formatted string literals now group digits after the decimal point as well as the integer part for floating-point presentation types.

### Regular-expression end and boundary semantics (Python 3.14)
`\z` is accepted as an unambiguous synonym for `\Z`, and `\B` now matches the empty input, making it consistently the opposite of `\b` and changing results for patterns that previously rejected an empty string.

### ISO 8601 end-of-day parsing (3.14.0)
`datetime.datetime.fromisoformat()` and `datetime.time.fromisoformat()` accept `24:00` as the ISO spelling of midnight at the end of the day.

```python
assert datetime.fromisoformat("2025-01-01T24:00") == datetime(2025, 1, 2)
```

### Integer mathematics namespace (Python 3.15 preview)
The new `math.integer` module provides mathematical functions specifically for integer arguments.

### Explicit regular-expression prefix matching (Python 3.15 preview)
`re.prefixmatch()` and `Pattern.prefixmatch()` are clearer aliases for the longstanding `match()` behavior of anchoring at the beginning. The old names are only soft-deprecated and will not be removed; code supporting older Python versions should continue using them.

### Unicode identifiers and grapheme clusters (Python 3.15 preview)
Alongside Unicode 17 data, `unicodedata.isxidstart()` and `isxidcontinue()` test UAX 31 identifier positions, and `iter_graphemes()` iterates user-perceived grapheme clusters according to UAX 29. New property helpers expose grapheme-cluster breaks, Indic conjunct breaks, extended pictographs, and Unicode blocks.

### Counter symmetric difference (3.15.0b3)
`collections.Counter` supports the `^` operator for multiset symmetric difference, complementing its existing union and intersection operations.

```python
changed = before ^ after
```

### Broader real-number inputs (3.15.0b3)
APIs taking timestamps or timeouts accept arbitrary real numbers such as `Decimal` and `Fraction`, although doing so does not increase their precision. `math.log()` also handles arbitrarily large integer-like objects without first requiring a lossless float conversion.

### Additional `strptime()` directives (3.15.0b3)
`datetime.datetime.strptime()`, `datetime.time.strptime()`, and `time.strptime()` accept `%:z` for a colon-separated UTC offset; `strptime()` also adds `%F`, `%D`, `%n`, and `%t` support.

```python
parsed = datetime.strptime("2026-06-23 +03:00", "%F %:z")
```

### Standalone localized month names (3.15.0b3)
`calendar.standalone_month_name` and `standalone_month_abbr` provide the grammatical form used when a month name stands alone, when the locale distinguishes it. The HTML calendar CLI also accepts a year and month to render one selected month.

### Non-finite standard deviations (3.15.0b3)
`statistics.stdev()` and `pstdev()` now raise `ValueError` when their input contains an infinity or NaN rather than producing a non-finite or inconsistent result.

## Memory management and finalization

### Incremental two-generation cyclic GC (3.13.0)
The cyclic collector is now incremental and has two generations instead of three; each collection combines the young generation with part of the pending old-generation space, avoiding full old-heap scans.

### Version-dependent 3.14 garbage collection (Python 3.14)
Python 3.14.0 through 3.14.4 used the incremental collector, where `gc.collect(1)` performed an increment rather than collecting generation 1. Python 3.14.5 and later reverted to the 3.13 generational collector after production memory-pressure reports, so code must not assume one collector for every 3.14 maintenance release.

### Collectible Python-interned strings (3.14.0)
Strings passed to `sys.intern()` can again be garbage-collected when no live reference remains, so interning no longer guarantees a process-lifetime identity.

### Garbage-collector telemetry (3.15.0b3)
`gc.get_stats()` and the information passed to `gc.callbacks` now expose `"candidates"` and `"duration"`, allowing monitoring code to report how much work a collection considered and how long it took.
