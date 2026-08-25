# Language and runtime

## Execution, syntax, and object behavior

### Optimized syntax validation

Optimization no longer hides syntax errors in code that `-O` removes. Writes
to `__debug__`, invalid `await`, and asynchronous comprehensions outside async
functions are rejected in optimized and normal builds alike.

### Deferred generator-expression startup

Creating `(item for item in source)` no longer invokes `source.__iter__()` once
at construction and again during execution. Iteration starts when the generator
runs, so a non-iterable source now raises then rather than at construction.

### Unpacking comprehensions

Python 3.15 allows `*` and `**` unpacking in list, set, and dict comprehensions
and in synchronous or asynchronous generator expressions.

```python
flat = [*part for part in parts]
merged = {**mapping for mapping in mappings}
```

### Context decorators cover deferred execution

`ContextDecorator`, `AsyncContextDecorator`, `contextmanager()`, and
`asynccontextmanager()` used as decorators keep their context active while a
returned generator or async generator iterates or a coroutine awaits. The
context no longer exits as soon as the deferred object is created.

### Lazy imports (`whatsnew-3.15`)

The `lazy` soft keyword defers loading until the imported name is first used.
Both import forms are supported, but only as direct module-level statements;
they cannot appear in `try` blocks and cannot be star or future imports.

```python
lazy import json
lazy from pathlib import Path
```

Global mode uses `-X lazy_imports=all`, `PYTHON_LAZY_IMPORTS`, or
`sys.set_lazy_imports()`. Use `sys.set_lazy_imports_filter()` for selection,
`types.LazyImportType` for detection, and module-level `__lazy_modules__` for
source that must remain compatible with older interpreters.

In 3.15.0b3, `sys.lazy_modules` is a set and
`PYTHON_LAZY_IMPORTS=all` also permits imports performed by `exec()` inside
functions. `none` is not a supported lazy-import mode.

### T-string concatenation boundaries

In 3.15.0b3, `Interpolation.expression` defaults to the empty string. A
`Template` cannot concatenate with `str`, and a t-string literal cannot
implicitly concatenate with a string or f-string literal.

### Mutable bases and broader slots

Python 3.15 allows tuple subclasses to define arbitrary `__slots__`, and any
class may explicitly slot `__dict__` and `__weakref__`. In 3.15.0b3,
`__bases__` may be reassigned on direct subclasses of built-in classes.

### Serializable built-ins and superclass dispatch

`super` objects are copyable and pickleable in Python 3.14, preserving bound
superclass-dispatch state. Python 3.15's `frozendict` is an insertion-ordered,
immutable mapping rather than a `dict` subclass. It is hashable only when all
keys and values are hashable; equality and hashing ignore insertion order.
APIs that accept general mappings should use `collections.abc.Mapping`.
Serialization modules, `eval()`, `exec()`, `type()`, and `str.maketrans()`
accept `frozendict` directly.

### Built-in sentinels

The Python 3.15 `sentinel` type creates concise unique markers whose identity
survives copying. Sentinels can participate in `|` type expressions and can be
pickled when importable by module and name. In 3.15.0b3, `sentinel()` accepts
`repr=` and the sentinel's `__module__` is writable.

### Method binding with `functools.partial` (`whatsnew-3.13`)

A `partial` stored directly on a class emits `FutureWarning` because its
binding behavior will change. Wrap it in `staticmethod()` to retain non-binding
behavior.

```python
class Handler:
    parse = staticmethod(functools.partial(parse, strict=True))
```

### Repeatable topological preparation

`graphlib.TopologicalSorter.prepare()` may be called repeatedly until sorting
starts, allowing multiple cycle preflights without rebuilding the graph.

## Numbers, text, dates, and collections

### Protocol-based fractions and reflected powers

`Fraction` accepts any object implementing `as_integer_ratio()`, so custom
exact numeric types need not convert through `float`. Three-argument
`pow(base, exponent, modulus)` now tries `__rpow__()` when the left operand
cannot handle the operation.

### Broader real-number inputs

In 3.15.0b3, functions taking timestamps or timeouts accept real-valued objects
such as `Decimal` and `Fraction`, not only `int` and `float`. This broadens
accepted types without increasing precision.

### Integer mathematics and generic slices

Python 3.15 adds `math.integer` for mathematical functions over integer
arguments. `slice` is subscriptable as a generic type, and unary `+` is
accepted in match literal patterns.

### Complex-number call migration

`functools.reduce()` accepts `initial=` by keyword, but `function=` and
`sequence=` are deprecated and become errors in 3.16. A string passed to
`complex()` must be positional, and passing a complex value as either the
`real` or `imag` component is deprecated.

### ISO and `strptime()` parsing

`datetime.datetime.fromisoformat()` and `datetime.time.fromisoformat()` accept
`24:00` as ISO 8601 midnight. In 3.15.0b3, datetime and time `strptime()`
support `%:z`, and `strptime()` also supports `%F`, `%D`, `%n`, and `%t`.

### Empty-string and prefix regular expressions

In Python 3.14, `\B` is always the inverse of `\b`, including for empty input.
Use `(?!\A\Z)\B` for the prior non-empty behavior. Python 3.15 adds
`re.prefixmatch()` and `Pattern.prefixmatch()` as explicit aliases for
prefix-only matching. The longstanding `match()` names are soft-deprecated for
new code but have no planned removal.

### Unicode identifiers and graphemes

Python 3.15 uses Unicode 17.0.0. `isxidstart()` and `isxidcontinue()` implement
UAX 31 identifier checks, while `iter_graphemes()` follows UAX 29. Other APIs
expose grapheme-break properties and Unicode blocks.

### Localized standalone month names

In 3.15.0b3, `calendar.standalone_month_name` and
`standalone_month_abbr` expose the locale's nominative month form. Text, HTML,
and command-line calendars use these values.

### Counter and statistics behavior

`collections.Counter` supports symmetric difference in 3.15.0b3.
`statistics.stdev()` and `pstdev()` raise `ValueError` when the input contains
an infinity or NaN.

## Garbage collection and shutdown

### Collector behavior by maintenance release (`whatsnew-3.14`)

Python 3.14.0 through 3.14.4 use the two-generation incremental collector, and
`gc.collect(1)` performs an increment. Python 3.14.5 and later revert to the
3.13 generational collector because the incremental design caused significant
production memory pressure.

### Finalization-specific exceptions

`PythonFinalizationError`, a `RuntimeError` subclass, replaces generic
`RuntimeError` when shutdown prevents `_thread.start_new_thread()`, `os.fork()`,
`os.forkpty()`, or `subprocess.Popen`.

## Removed and deprecated Python surfaces

### Python 3.14 removals

Copy, deep-copy, and pickle support is removed from `itertools` iterator
objects. Removed library APIs include `pkgutil.get_loader()` and
`find_loader()`, `pty.master_open()` and `slave_open()`, and
`urllib.request.URLopener` and `FancyURLopener`. Import resource ABCs from
`importlib.resources.abc`, not `importlib.abc`.

### Python 3.14 deprecations

`argparse.FileType` and `codecs.open()` are deprecated. `os.popen()` and the
`os.spawn*()` family are soft-deprecated in favor of `subprocess`. Replace
`PurePath.as_uri()` with `Path.as_uri()`, and stop passing false values other
than empty strings, bytes-like objects, or `None` to `parse_qs()` or
`parse_qsl()`.

### Python 3.15 enforced migrations

Python 3.15 removes `CGIHTTPRequestHandler` and `http.server --cgi`,
`PurePath.is_reserved()` (use `os.path.isreserved()`), `sre_compile`,
`sre_constants`, `sre_parse`, `CodeType.co_lnotab`,
`zipimporter.load_module()`, and the `package=` name for
`importlib.resources.files()`. It also removes `glob0()` and `glob1()`,
`platform.java_ver()`, `typing.no_type_check_decorator()`, WAVE `getmark()`,
`setmark()`, and `getmarkers()`, `ctypes.SetPointerType()`, and arbitrary
arguments to `RLock()`.

`datetime.strptime()` rejects `%d` without a year. Keyword-field
`NamedTuple(...)` and fieldless `TypedDict("T")` forms must become class syntax
or supply an explicit field mapping.

### Additional Python 3.15 removals

By 3.15.0b3, all remaining import-loader `load_module()` definitions and
`importlib.util.cache_from_source(debug_override=...)` are removed. Also gone
are `argparse.HelpFormatter(color=...)`,
`unicodedata.ucd_3_2_0.isxidstart()` and `isxidcontinue()`, and the one-letter
`F` and `D` complex formats in `array` and `memoryview`.

### Migration warnings

Python 3.15 deprecates `-b` and `-bb`; they become no-ops in 3.17. Pass
`hashlib` initial data positionally instead of as `string=`. Many standard
library `__version__`, `version`, and `VERSION` attributes are deprecated in
favor of `sys.version_info`, except that decimal code uses
`decimal.SPEC_VERSION`. Abstract AST construction, accepting `+` and `/` with
an alternative Base64 alphabet, cookie JavaScript output helpers, and
`webbrowser.MacOSXOSAScript` also begin removal migrations.

In 3.15.0b3, `os.path.commonprefix()` is deprecated in favor of `commonpath()`,
and non-ASCII names passed to `encodings.normalize_encoding()` are deprecated.
So are inherited runtime-checkability without a local `@runtime_checkable`,
calling `Struct.__new__()` without its required argument, calling `__init__()`
on an initialized `Struct`, mutating `IMAP4.file`, and providing an external
string-hash implementation.
