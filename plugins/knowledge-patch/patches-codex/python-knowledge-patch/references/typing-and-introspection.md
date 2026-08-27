# Typing and introspection

## Syntax trees and compiler metadata

### Strict and optimized AST construction

Omitted optional, list, and expression-context fields default to `None`, `[]`,
and `ast.Load()` respectively. Missing required fields and unknown constructor
keywords warn now and become errors in Python 3.15. Custom `ast.AST` subclasses
opt in with `_field_types`. Use `ast.parse(source, optimize=2)` or
`ast.PyCF_OPTIMIZED_AST` to obtain optimized trees.

### Compiler-generated class metadata

Classes expose `__static_attributes__`, a tuple of names assigned through
`self.<name>` by functions in the class body, and `__firstlineno__`, the first
line of the class definition. These expose static assignments and source
location without disassembling methods.

## Annotations and type expressions

### Forward-reference reevaluation

`annotationlib.ForwardRef` no longer caches a successful evaluation. Repeated
`evaluate()` calls can return different values, and equality and hashing now
consider every forward-reference attribute.

### Type-alias introspection (`3.15.0b3`)

`typing.TypeAliasType` gains `__qualname__` and a writable `__module__`.
`inspect.signature()` accepts lazy evaluator callables attached to type aliases
and type parameters.

### Values representing type expressions

Python 3.15 adds `typing.TypeForm[T]` for a runtime value that is itself a type
expression describing `T`; `TypeForm(x)` returns `x`. This lets APIs precisely
accept `int`, `str | None`, `list[int]`, or a `TypedDict` class.

### Closed and extensible typed dictionaries

`TypedDict` accepts `closed=True` to reject unspecified keys and
`extra_items=T` to allow additional keys whose values have type `T`.
`@typing.disjoint_base` describes bases that cannot be multiply inherited with
unrelated disjoint bases. `TypeVarTuple` accepts bounds and variance keywords,
although bound semantics remain unspecified.

## Frames, generators, signatures, and symbols

### Direct generator execution state

Generators, coroutines, and async generators expose `gi_state`, `cr_state`,
and `ag_state` in Python 3.15.0b3. The corresponding
`inspect.get*state()` helpers return these attributes.

### Public frame-locals proxy type

`types.FrameLocalsProxyType` exposes the runtime type of PEP 667 write-through
frame-local proxies, enabling reliable type checks.

### Expanded inspection controls

In Python 3.15.0b3, `inspect.getdoc()` accepts `inherit_class_doc` and
`fallback_to_class_doc`, and `getfullargspec()` accepts `annotation_format`.
Symbol tables expose `Function.get_cells()` and `Symbol.is_cell()`.
`python -m inspect --details` reports useful metadata for non-source targets
instead of failing.

## Structural I/O types and runtime metadata

### Reader and writer protocols

`io.Reader` and `io.Writer` provide structural alternatives to `typing.IO`,
`TextIO`, and `BinaryIO` for code that only needs simple read or write
behavior.

### Runtime ABI and monitoring inspection

`sys.abi_info` exposes structured ABI information in Python 3.15.
Exception-related `sys.monitoring` events can be enabled per code object, and
returning `DISABLE` from a callback disables that event for the current tool
and code object.
