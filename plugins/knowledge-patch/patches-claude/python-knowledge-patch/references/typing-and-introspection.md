# Typing and introspection

## AST construction and diagnostics

### Strict and optimized AST construction (`whatsnew-3.13`)

Omitted optional, list, and expression-context fields default to `None`, `[]`,
and `ast.Load()`. Missing required fields and unknown constructor keywords warn
and become errors in 3.15. Custom `ast.AST` subclasses opt in with
`_field_types`. Use `ast.parse(source, optimize=2)` or
`ast.PyCF_OPTIMIZED_AST` to obtain optimized trees.

### Warning context and colored AST output (`whatsnew-3.15`, `3.15.0b3`)

`compile()`, `ast.parse()`, and `symtable.symtable()` accept a module name so
syntax-warning filters can identify the source module. `ast.dump(color=...)`
provides opt-in colored diagnostic output in 3.15.0b3.

## Annotations and signatures

### Forward-reference reevaluation (`3.14.0`)

`annotationlib.ForwardRef` no longer caches successful evaluations; repeated
`evaluate()` calls may return different values. Equality and hashing consider
all forward-reference attributes.

### Values representing type expressions (`whatsnew-3.15`)

`typing.TypeForm[T]` annotates a runtime value that is itself a type expression
describing `T`. `TypeForm(x)` returns `x`, allowing APIs to precisely accept
values such as `int`, `str | None`, `list[int]`, or a `TypedDict` class.

### Closed and extensible typed dictionaries (`whatsnew-3.15`)

`TypedDict(closed=True)` rejects unspecified keys; `extra_items=T` permits
additional keys with values of `T`. `@typing.disjoint_base` models bases that
cannot be multiply inherited with unrelated disjoint bases. `TypeVarTuple`
accepts bounds and variance keywords, although bound semantics remain
unspecified.

### Type-alias metadata (`3.15.0b3`)

`typing.TypeAliasType` has `__qualname__` and a writable `__module__`.
`inspect.signature()` accepts lazy evaluator callables attached to type aliases
and type parameters.

## Frames, symbols, and runtime metadata

### Structural I/O protocols (`whatsnew-3.14`)

`io.Reader` and `io.Writer` are simple structural alternatives to `typing.IO`,
`TextIO`, and `BinaryIO` for APIs that need only read or write behavior.

### Runtime ABI and monitoring inspection (`whatsnew-3.15`)

`sys.abi_info` exposes structured ABI information. Exception-related
`sys.monitoring` events can be enabled per code object, and returning `DISABLE`
from a callback disables that event for the current tool/code pair.

### Public frame-locals proxy (`3.15.0b3`)

`types.FrameLocalsProxyType` exposes the concrete PEP 667 write-through
frame-locals proxy type for reliable runtime checks.

### Inspection and symbol tables (`3.15.0b3`)

`inspect.getdoc()` accepts `inherit_class_doc` and `fallback_to_class_doc`, and
`getfullargspec()` accepts `annotation_format`. Symbol tables add
`Function.get_cells()` and `Symbol.is_cell()`. `python -m inspect --details`
reports metadata for non-source targets rather than failing.

### Importer-defined discovery (`3.15.0b3`)

`MetaPathFinder.discover()` and `PathEntryFinder.discover()` let custom
importers enumerate modules and submodules without assuming a filesystem
layout.
