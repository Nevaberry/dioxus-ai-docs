# Typing and introspection

Use this reference for annotations and typing, ASTs, frames and locals, signatures, symbols, and runtime metadata.

## Annotations and typing

### Richer annotation scopes (Python 3.13)
Annotation scopes nested in classes may now contain lambdas and comprehensions, including references to their type parameters.

```python
class C[T]:
    type Factory = lambda: T
```

### Empty and keyword-based typing factories deprecated (3.13.0)
`TypedDict("TD")` and `TypedDict("TD", None)` are deprecated; use `{}` or a class body for an empty definition. Keyword fields in `NamedTuple("NT", x=int)` and its empty `NamedTuple("NT")` or `NamedTuple("NT", None)` forms are likewise deprecated in favor of a field sequence or class syntax, and become errors in 3.15.

### Context-manager and generator type parameters (3.13.0)
`typing.ContextManager` and `AsyncContextManager` accept a second type argument for the return type of `__exit__()` or `__aexit__()`, defaulting to `bool | None`. `typing.Generator` and `AsyncGenerator` now have defaults for their trailing type parameters, and nested forms such as `Final[ClassVar[int]]` are supported.

### Deferred annotations and `annotationlib` (Python 3.14)
Function, class, and module annotations are now evaluated lazily, so forward references no longer need quotes. Use `annotationlib.get_annotations()` with `Format.VALUE`, `FORWARDREF`, or `STRING` to choose whether missing names raise, become `ForwardRef` objects, or remain source-like strings.

```python
from annotationlib import Format, get_annotations
def parse(value: Missing): ...
hints = get_annotations(parse, format=Format.FORWARDREF)
```

### Annotation-reader migrations (Python 3.14)
Annotation consumers should use `annotationlib` rather than reading class namespace dictionaries; instances no longer accidentally expose their class annotations, and `inspect.signature()` accepts `annotation_format`. `from __future__ import annotations` keeps its old behavior in 3.14 but is deprecated, with removal deferred until after Python 3.13 reaches end of life in 2029.

### Unified runtime union types (Python 3.14)
`types.UnionType` and `typing.Union` are now aliases, so `Union[int, str]` and `int | str` share a runtime type and repr, and `isinstance(int | str, typing.Union)` works. Old-style unions are no longer identity-cached and their `__args__` is not writable, so introspection should use `==`, `typing.get_origin()`, and `typing.get_args()` rather than identity or private classes.

### Values that represent type expressions (Python 3.15 preview)
`typing.TypeForm[T]` annotates a runtime value that is itself a type expression describing `T`, such as `int`, `str | None`, a `TypedDict` class, or `list[int]`; calling `TypeForm(x)` returns `x` unchanged.

```python
from typing import Any, TypeForm

def cast[T](typ: TypeForm[T], value: Any) -> T: ...
```

### Closed and extensible typed dictionaries (Python 3.15 preview)
`TypedDict` accepts `closed=True` to forbid unspecified keys, or `extra_items=ValueType` to permit arbitrary extra keys whose values have that type.

```python
class Headers(TypedDict, extra_items=str):
    content_length: int
```

### Disjoint bases and variadic type parameters (Python 3.15 preview)
`@typing.disjoint_base` marks bases, chiefly built-ins and extension types, that cannot participate together in unrelated multiple-inheritance branches, allowing type checkers to model runtime layout restrictions. `TypeVarTuple` now accepts `bound`, variance, and inferred-variance keywords like `TypeVar` and `ParamSpec`, although bound semantics remain unspecified.

### Type-alias and typing-factory metadata (3.15.0b3)
`typing.TypeAliasType` now has `__qualname__` and permits assignment to `__module__`; functional `NamedTuple` creation accepts any iterable of field/type pairs rather than only a sequence. Method parameters declared by `typing.IO` and `typing.BinaryIO` are now positional-only.

## AST and compiler representation

### Stricter and optimized AST construction (Python 3.13)
Built-in AST node constructors now fill omitted optional fields with `None`, list fields with `[]`, and expression contexts with `Load()`; missing required fields and unknown keyword fields warn now and become errors in 3.15. `ast.parse(..., optimize=n)` and `compile(..., flags=ast.PyCF_OPTIMIZED_AST, optimize=n)` can return an optimized AST.

### Compiler-cleaned docstrings (3.13.0)
The compiler now strips indentation from docstrings themselves, so `__doc__` and consumers such as doctest can observe different text rather than only seeing cleanup through introspection helpers.

### Stable AST dump snapshots (3.13.0)
`ast.dump()` omits fields whose values are `None` or `[]` by default. Pass `show_empty=True` when a complete structural dump is required.

### Removed legacy AST node aliases (Python 3.14)
`ast.Bytes`, `Ellipsis`, `NameConstant`, `Num`, and `Str`, plus `Constant.n` and `.s`, have been removed; use `ast.Constant.value`. Custom visitors must implement `visit_Constant()`, because the old type-specific visitor methods are no longer invoked.

## Frames, functions, and locals

### Defined `locals()`, `exec()`, and frame-local semantics (Python 3.13)
In optimized scopes, every `locals()` call now returns an independent snapshot, so an implicit `exec()` or `eval()` namespace cannot expose newly created names afterward; pass an explicit namespace when results are needed. `frame.f_locals` and `PyFrame_GetLocals()` instead return write-through proxies in these scopes, and callers wanting a snapshot must copy them.

```python
namespace = {}
exec("answer = 42", globals(), namespace)
answer = namespace["answer"]
```

### Frame and function mutation safeguards (3.13.0)
Assigning a code object of a mismatched kind to `function.__code__` is deprecated. `frame.clear()` now rejects suspended frames and also clears an already-materialized `frame.f_locals`, preventing references from surviving there.

### Keyword defaults for constructed functions (3.13.0)
`types.FunctionType` accepts a `kwdefaults` parameter so callers constructing a function from a code object can set its keyword-only defaults directly.

### Richer frame-locals proxies (3.14.0)
`FrameLocalsProxy` now implements `collections.abc.Mapping`, participates in mapping patterns, and has `copy()` for an ordinary snapshot dictionary. `pop()` and deletion work for keys that are not fast local variables.

### Direct generator execution state (3.15.0b3)
Generators, coroutines, and async generators expose `gi_state`, `cr_state`, and `ag_state` string attributes such as `GEN_RUNNING`; the corresponding `inspect.get*state()` functions return these attributes directly.

### Public frame-locals proxy type (3.15.0b3)
The concrete proxy used for optimized frame locals is available as `types.FrameLocalsProxyType`, enabling precise runtime type checks without relying on an implementation-private name.

## Inspection and runtime metadata

### Class introspection metadata (Python 3.13)
Classes now expose `__static_attributes__`, a tuple of names assigned through `self.<name>` in functions in the class body. Their new `__firstlineno__` attribute records the first line of the class definition.

### Runtime cache and interning inspection (3.13.0)
`sys._is_interned()` reports whether a string is interned. `sys._clear_internal_caches()` clears all internal performance caches and supersedes the narrower, now-deprecated `sys._clear_type_cache()`.

### New runtime type and property metadata (3.13.0)
`types.CapsuleType` exposes the type of `PyCapsule` objects, and `property` objects now expose `__name__`.

### Explicit signature formatting (3.13.0)
`inspect.Signature.format()` formats signatures with layout options; `pydoc` uses it to render long signatures across multiple lines.

### Expanded inspection and symbol-table controls (3.15.0b3)
`inspect.getdoc()` accepts `inherit_class_doc` and `fallback_to_class_doc`, while `inspect.getfullargspec()` accepts `annotation_format`. `symtable.Function.get_cells()` and `symtable.Symbol.is_cell()` expose closure-cell information directly.
