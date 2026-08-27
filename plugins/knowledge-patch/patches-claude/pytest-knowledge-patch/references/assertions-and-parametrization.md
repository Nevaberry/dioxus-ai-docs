# Assertions, Parametrization, and Subtests

## Structured Exception Groups

Since 8.4.0, `pytest.RaisesGroup` matches the members and nesting of an
`ExceptionGroup`. `pytest.RaisesExc` provides the matcher for one exception
and can be nested inside `RaisesGroup`. A group matcher can express multiple
expected exceptions and `except*`-style matching:

```python
with pytest.RaisesGroup(ValueError, TypeError):
    raise ExceptionGroup("errors", [ValueError(), TypeError()])
```

Both matcher objects are accepted by `pytest.mark.xfail(raises=...)`.

For precise `ExceptionInfo` typing, `pytest.raises` also accepts
`ExceptionGroup[Exception]` and `BaseExceptionGroup[BaseException]`.
Other parameterized exception types remain invalid.

## Predicate Checks in `pytest.raises`

Since 8.4.0, `pytest.raises(..., check=fn)` applies `fn` after the exception
type and message have matched:

```python
with pytest.raises(OSError, check=lambda exc: exc.errno == 13):
    operation()
```

If the predicate is false, the exception is rejected and propagates. Passing
`match=""` warns because it matches every message; use `match="^$"` to require
an empty message. When a regex is fully anchored and otherwise escaped, a
match failure now produces a string diff.

## Hidden Parameter IDs

Since 8.4.0, use `pytest.HIDDEN_PARAM` as the `id` of a `pytest.param` or as an
entry in `Metafunc.parametrize(..., ids=...)` to omit that parameter set from
the generated test name:

```python
@pytest.mark.parametrize("value", [
    pytest.param(1, id=pytest.HIDDEN_PARAM),
    pytest.param(2, id="two"),
])
def test_value(value):
    ...
```

## Single-Parameter Tuple Unpacking

Since 9.1.0, an argname string ending in a comma behaves like a one-element
argname tuple. Each tuple is unpacked into the single parameter:

```python
@pytest.mark.parametrize("arg,", [(1,), (2,)])
def test_arg(arg):
    ...
```

## Approximate Comparisons

Since 8.4.0, `pytest.approx` can compare collections containing both numeric
and non-numeric values.

Since 9.1.0, it also supports `datetime.datetime` and `datetime.timedelta`.
Supply an explicit `abs` or `rel` tolerance as a `timedelta`; datetime values
do not support relative tolerance:

```python
from datetime import timedelta

assert actual == pytest.approx(
    expected,
    abs=timedelta(milliseconds=50),
)
```

## Built-In Subtests

Since 9.0.0, the `subtests` fixture runs dynamically discovered cases inside
`subtests.test(...)`, catching and reporting each failure separately:

```python
def test_values(subtests: pytest.Subtests):
    for value in [1, 2, 3]:
        with subtests.test(value=value):
            assert value > 0
```

Core pytest also supports `unittest.TestCase.subTest`.

