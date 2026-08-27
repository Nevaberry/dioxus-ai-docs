# Language and runtime

## Object model and execution

### Compiler-generated class metadata (`whatsnew-3.13`)

Classes expose `__static_attributes__`, the names assigned through
`self.<name>` by functions in the class body, and `__firstlineno__`, the first
line of the class definition. These avoid disassembling methods for assignment
or source-location metadata.

### Finalization-specific failures (`whatsnew-3.13`)

`PythonFinalizationError`, a `RuntimeError` subclass, is raised when shutdown
blocks `_thread.start_new_thread()`, `os.fork()`, `os.forkpty()`, or
`subprocess.Popen`.

### `functools.partial` descriptors (`whatsnew-3.13`)

A `partial` stored directly on a class emits `FutureWarning` because its binding
behavior will change. Preserve non-binding behavior explicitly:

```python
class Handler:
    parse = staticmethod(functools.partial(parse, strict=True))
```

### Optimized syntax validation (`whatsnew-3.14`)

`-O` no longer masks syntax errors in optimized-away code. Assignments to
`__debug__`, invalid `await`, and async comprehensions outside async functions
are rejected in optimized and ordinary builds.

### Copyable `super` (`whatsnew-3.14`)

`super` objects are copyable and pickleable, so bound superclass-dispatch state
can survive copying or serialization.

### Deferred generator-expression startup (`3.14.0`)

Creating `(item for item in source)` no longer calls `source.__iter__()` both at
construction and execution. Iteration starts when the generator runs, so a
non-iterable source raises then rather than during construction.

### Mutable bases and execution state (`3.15.0b3`)

Direct subclasses of built-in classes may reassign `__bases__`. Generators,
coroutines, and async generators expose `gi_state`, `cr_state`, and `ag_state`;
the matching `inspect.get*state()` helpers return these attributes.

## Numbers, collections, and expressions

### Protocol-based fractions (`whatsnew-3.14`)

`Fraction` accepts any object implementing `as_integer_ratio()`, allowing
custom exact numeric types without an intermediate `float` conversion.

### Reflected modular exponentiation (`3.14.0`)

Three-argument `pow(base, exponent, modulus)` tries `__rpow__()` when the left
operand cannot implement the operation.

### Call-style migrations (`3.14.0`)

`functools.reduce()` accepts `initial=` by keyword, but `function=` and
`sequence=` are deprecated and become errors in 3.16. A string argument to
`complex()` must be positional; passing a complex value as either `real` or
`imag` is deprecated.

### Immutable mappings (`whatsnew-3.15`)

`frozendict` is insertion ordered and immutable, but is not a `dict` subclass.
It is hashable when all keys and values are hashable, and equality and hashing
ignore insertion order. Accept general mappings through
`collections.abc.Mapping`. Serialization modules, `eval()`, `exec()`, `type()`,
and `str.maketrans()` accept it directly.

### Sentinel values (`whatsnew-3.15`, `3.15.0b3`)

The built-in `sentinel` type creates concise unique markers whose identity
survives copying. A sentinel can appear in `|` type expressions and can be
pickled when importable by module and name. In 3.15.0b3, `sentinel()` accepts
`repr=`, and the resulting object's `__module__` is writable.

### Unpacking comprehensions (`whatsnew-3.15`)

List, set, and dict comprehensions plus synchronous and asynchronous generator
expressions accept `*` and `**` unpacking:

```python
flat = [*part for part in parts]
merged = {**mapping for mapping in mappings}
```

### Slots, slices, and match literals (`whatsnew-3.15`)

`tuple` subclasses may define arbitrary `__slots__`; any class may explicitly
slot `__dict__` and `__weakref__`. `slice` is subscriptable as a generic type,
and unary `+` is valid in match literal patterns.

### Integer and binary numeric surfaces (`whatsnew-3.15`)

`math.integer` contains mathematics for integer inputs. `array` adds half-float
`e` and complex `Zf` / `Zd` type codes and changes `array.typecodes` from a
string to a tuple. `memoryview` accepts `Zf` / `Zd`; ctypes complex `_type_`
codes are `Zf`, `Zd`, and `Zg`. The one-letter `struct` complex codes `F` and
`D` are soft-deprecated for the two-letter forms.

### Additional collection and numeric behavior (`3.15.0b3`)

`collections.Counter` supports symmetric difference. Timestamp and timeout
APIs accept real-valued objects such as `Decimal` and `Fraction`, although that
does not increase precision. `statistics.stdev()` and `pstdev()` raise
`ValueError` for infinity or NaN inputs.

## Text, dates, and regular expressions

### UTF-8 default encoding (`whatsnew-3.15`)

Text I/O without an explicit encoding uses UTF-8 independently of locale. Use
`encoding="locale"` for locale behavior, or temporarily retain the old default
with `-X utf8=0` or `PYTHONUTF8=0`.

### ISO parsing (`3.14.0`, `3.15.0b3`)

`datetime.datetime.fromisoformat()` and `datetime.time.fromisoformat()` accept
`24:00`. In 3.15.0b3, `datetime.datetime.strptime()`,
`datetime.time.strptime()`, and `time.strptime()` accept `%:z`, while
`strptime()` also supports `%F`, `%D`, `%n`, and `%t`.

### Regular-expression boundaries and matching (`3.14.0`, `whatsnew-3.15`)

`\B` is always the inverse of `\b`, including for empty input; use
`(?!\A\Z)\B` for the former nonempty-only behavior. `re.prefixmatch()` and
`Pattern.prefixmatch()` explicitly mean prefix matching. The old `match()`
names are soft-deprecated for new code but have no removal plan.

### Unicode identifiers and graphemes (`whatsnew-3.15`)

The Unicode database is 17.0.0. `isxidstart()` and `isxidcontinue()` implement
UAX 31 identifier checks; `iter_graphemes()` implements UAX 29 grapheme
iteration. Other APIs expose grapheme-break properties and Unicode blocks.

### Localized month forms (`3.15.0b3`)

`calendar.standalone_month_name` and `standalone_month_abbr` expose the
locale's nominative standalone month form. Text, HTML, and command-line
calendars use these names.

### T-string concatenation boundaries (`3.15.0b3`)

`Interpolation.expression` defaults to an empty string. A `Template` cannot
concatenate with `str`, and t-string literals do not implicitly concatenate
with string or f-string literals.

## Garbage collection and algorithms

### Collector maintenance-release split (`whatsnew-3.14`)

Python 3.14.0 through 3.14.4 use the two-generation incremental collector, and
`gc.collect(1)` performs an increment. Python 3.14.5 and later revert to the
3.13 generational collector after the incremental design caused production
memory pressure.

### Garbage-collector telemetry (`3.15.0b3`)

GC debug output again includes collection elapsed time and unreachable-object
count. `_remote_debugging.GCMonitor.get_gc_stats()` reads another process's GC
statistics without constructing a complete remote unwinder.

### Repeatable topological preparation (`3.14.0`)

`graphlib.TopologicalSorter.prepare()` can be called repeatedly until sorting
starts, allowing multiple cycle-check preflights without rebuilding the graph.

## Removal checklist

### Iterator serialization (`whatsnew-3.14`)

Copy, deep-copy, and pickle support is removed from `itertools` iterator
objects after its earlier deprecation.

### Python-level removals (`whatsnew-3.15`)

Migrate all of the following:

- `CGIHTTPRequestHandler` and `http.server --cgi` are removed.
- Replace `PurePath.is_reserved()` with `os.path.isreserved()`.
- `sre_compile`, `sre_constants`, `sre_parse`, `CodeType.co_lnotab`,
  `zipimporter.load_module()`, `glob0()`, and `glob1()` are removed.
- `importlib.resources.files()` no longer accepts `package=`.
- `platform.java_ver()`, `typing.no_type_check_decorator()`,
  `ctypes.SetPointerType()`, and arbitrary arguments to `RLock()` are removed.
- WAVE `getmark()`, `setmark()`, and `getmarkers()` are removed.
- `datetime.strptime()` rejects `%d` without a year.
- Keyword-field `NamedTuple(...)` and fieldless `TypedDict("T")` require class
  syntax or an explicit field mapping.

### Further removals (`3.15.0b3`)

All remaining importer `load_module()` definitions and
`importlib.util.cache_from_source(debug_override=...)` are removed, as are
`argparse.HelpFormatter(color=...)`,
`unicodedata.ucd_3_2_0.isxidstart()` / `isxidcontinue()`, and one-letter `F` /
`D` complex formats in `array` and `memoryview`.

### Migration warnings (`whatsnew-3.15`, `3.15.0b3`)

`-b` and `-bb` are deprecated and become no-ops in 3.17. Pass hashlib initial
data positionally instead of as `string=`. Replace standard-library
`__version__`, `version`, or `VERSION` attributes with `sys.version_info` (or
`decimal.SPEC_VERSION`). Abstract AST-node construction, `+` or `/` in an
alternative Base64 alphabet, cookie JavaScript helpers, and
`webbrowser.MacOSXOSAScript` begin removal migrations.

In 3.15.0b3, prefer `os.path.commonpath()` to deprecated `os.path.commonprefix()` and
ASCII names for `encodings.normalize_encoding()`. Apply `@runtime_checkable`
locally rather than inheriting it. Do not call `Struct.__new__()` without its
required argument, call `__init__()` on an initialized `Struct`, mutate
`IMAP4.file`, or provide an external string-hash implementation.
