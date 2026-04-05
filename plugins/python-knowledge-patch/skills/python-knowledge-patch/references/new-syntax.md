# New Syntax and Language Changes

## Template String Literals (PEP 750) — Python 3.14

T-strings use the `t''` prefix (like f-strings use `f''`) but return a `Template` object instead of a `str`. This gives you access to static parts and interpolations before they're combined, enabling safe string processing for HTML, SQL, shell commands, etc.

### Basic Usage

```python
from string.templatelib import Template, Interpolation

name = "world"
template = t"Hello {name}!"
# type(template) → <class 'string.templatelib.Template'>

# Iterate to get parts in order:
list(template)
# ['Hello ', Interpolation('world', 'name', None, ''), '!']
```

### Interpolation Object

Each `Interpolation` has attributes:
- `value` — the evaluated expression result
- `expression` — the source text (e.g., `'name'`)
- `conversion` — `None`, `'r'`, `'s'`, or `'a'` (like f-string `!r`)
- `format_spec` — format specification string (like f-string `:.2f`)

### Processing Templates

```python
from string.templatelib import Template, Interpolation


def safe_sql(template: Template) -> tuple[str, list]:
    """Convert t-string to parameterized SQL."""
    query_parts = []
    params = []
    for part in template:
        if isinstance(part, Interpolation):
            query_parts.append("?")
            params.append(part.value)
        else:
            query_parts.append(part)
    return "".join(query_parts), params


user_id = 42
query, params = safe_sql(t"SELECT * FROM users WHERE id = {user_id}")
# query = "SELECT * FROM users WHERE id = ?"
# params = [42]
```

### Key Differences from F-strings

- `f"..."` → `str` (eagerly concatenated)
- `t"..."` → `Template` (lazy, inspectable)
- T-strings support the same syntax as f-strings (expressions, `!r`, `:.2f`, nested braces)
- T-strings are in `string.templatelib`, not a builtin

## Deferred Evaluation of Annotations (PEP 649/749) — Python 3.14

Annotations on functions, classes, and modules are no longer evaluated at definition time. They're stored as special annotate functions and evaluated on demand.

### What Changed

```python
# This now works without quotes — no NameError at definition time:
def process(items: list[TreeNode]) -> TreeNode:
    pass

class TreeNode:
    children: list[TreeNode]  # forward reference just works
```

### annotationlib Module

```python
from annotationlib import get_annotations, Format

def func(x: UndefinedType) -> int:
    pass

# VALUE — evaluates annotations (raises if undefined)
get_annotations(func, format=Format.VALUE)
# NameError: name 'UndefinedType' is not defined

# FORWARDREF — replaces unknowns with ForwardRef markers
get_annotations(func, format=Format.FORWARDREF)
# {'x': ForwardRef('UndefinedType', ...), 'return': <class 'int'>}

# STRING — returns annotation source text
get_annotations(func, format=Format.STRING)
# {'x': 'UndefinedType', 'return': 'int'}
```

### Migration Notes

- `typing.get_type_hints()` continues to work for most cases
- `from __future__ import annotations` still works (converts to strings)
- Code that reads `__annotations__` directly: accessing `cls.__annotations__` still works but now triggers evaluation
- Libraries doing runtime annotation processing should use `annotationlib.get_annotations()` for more control

## Bracketless except (PEP 758) — Python 3.14

Multiple exception types no longer require parentheses when there's no `as` clause:

```python
# New (3.14+):
try:
    connect()
except TimeoutError, ConnectionRefusedError:
    handle_network_error()

# With as clause still requires parens:
except (TimeoutError, ConnectionRefusedError) as e:
    handle(e)

# Also works with except*:
except* TimeoutError, ConnectionRefusedError:
    handle_network_error()
```

## finally Control Flow Warning (PEP 765) — Python 3.14

`return`, `break`, or `continue` that would exit a `finally` block now emit `SyntaxWarning`:

```python
def bad():
    try:
        return 1
    finally:
        return 2  # SyntaxWarning: 'return' in 'finally' block

# Suppress if needed:
# python -Werror -Wignore::SyntaxWarning
```
