# New Syntax

## Template strings / t-strings (3.14, PEP 750)

New string prefix `t` that produces a `Template` object instead of `str`. Like f-strings but with access to parts before rendering.

### Syntax

```python
name = "world"
template = t"Hello, {name}!"
# type: string.templatelib.Template
```

Supports same expressions as f-strings: `t"{x + 1}"`, `t"{x!r:.2f}"`, `t"{'nested'}"`.

### API

```python
from string.templatelib import Template, Interpolation

template = t"Hello, {name}!"

# Iterate to get parts in order
for part in template:
    if isinstance(part, str):
        ...  # Static text
    elif isinstance(part, Interpolation):
        part.value       # Evaluated result (e.g. "world")
        part.expr        # Source expression (e.g. "name")
        part.conv        # Conversion: None, "r", "s", "a"
        part.format_spec # Format spec (e.g. ".2f"), "" if none
```

### Writing processors

```python
from string.templatelib import Template, Interpolation


def sql(template: Template) -> tuple[str, list]:
    """Safe SQL query builder."""
    parts, params = [], []
    for part in template:
        if isinstance(part, Interpolation):
            parts.append("?")
            params.append(part.value)
        else:
            parts.append(part)
    return "".join(parts), params


user_id = 42
query, params = sql(t"SELECT * FROM users WHERE id = {user_id}")
# query = "SELECT * FROM users WHERE id = ?"
# params = [42]
```

## Deferred evaluation of annotations (3.14, PEP 649/749)

Annotations are no longer evaluated eagerly — they are stored as functions and evaluated on access.

### Key changes

- Forward references no longer need quotes: `def f() -> MyClass` works even if `MyClass` defined later
- `from __future__ import annotations` is deprecated (unchanged behavior in 3.14, removal after 2029)
- New `annotationlib` module for introspection

### `annotationlib` API

```python
from annotationlib import get_annotations, Format

# Three formats for reading annotations:
get_annotations(
    obj, format=Format.VALUE
)  # Evaluate to runtime values (may raise NameError)
get_annotations(
    obj, format=Format.FORWARDREF
)  # Replace unknowns with ForwardRef markers
get_annotations(obj, format=Format.STRING)  # Return as strings
```

### Migration

Most code works unchanged. If you read `__annotations__` directly, consider using `annotationlib.get_annotations()` with `Format.FORWARDREF` for robustness (like `dataclasses` now does).

## except without brackets (3.14, PEP 758)

Multiple exception types no longer need parentheses when `as` is not used:

```python
# 3.14+: no parens needed
except TimeoutError, ConnectionRefusedError:
    ...

# Parens still required with `as`:
except (TimeoutError, ConnectionRefusedError) as e:
    ...
```

Note: This is NOT Python 2's `except Type, variable:` syntax — that assigned the exception to `variable`. In 3.14, the comma separates exception types.
