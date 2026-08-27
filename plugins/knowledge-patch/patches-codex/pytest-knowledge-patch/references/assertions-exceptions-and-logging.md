# Assertions, exceptions, and logging

## Structured exception-group matching

Since 8.4.0, `pytest.RaisesGroup` matches the members and nesting of an
`ExceptionGroup`. `pytest.RaisesExc` supplies single-exception matching logic
and can be nested inside a group matcher.

```python
with pytest.RaisesGroup(ValueError, TypeError):
    raise ExceptionGroup("errors", [ValueError(), TypeError()])
```

`RaisesGroup` can express multiple expected exceptions and `except*`-style
matching. Both matcher objects are accepted by
`pytest.mark.xfail(raises=...)`.

`pytest.raises` also accepts `ExceptionGroup[Exception]` and
`BaseExceptionGroup[BaseException]` to retain precise `ExceptionInfo` typing.
Other parameterized exception types remain invalid.

## Predicate checks in `pytest.raises`

Since 8.4.0, `pytest.raises(..., check=fn)` applies the predicate after type
and message matching:

```python
with pytest.raises(OSError, check=lambda exc: exc.errno == 13):
    operation()
```

When the predicate returns false, the exception is rejected and propagates.

Passing `match=""` warns because an empty pattern matches every message. Use
`match="^$"` to require an empty message. When a fully anchored, otherwise
escaped pattern fails, pytest produces a string diff.

## Approximate comparisons

Since 8.4.0, `pytest.approx` can compare collections containing a mixture of
numeric and non-numeric values.

Since 9.1.0, it also supports `datetime.datetime` and `datetime.timedelta`.
Supply an explicit `abs` or `rel` tolerance as a `timedelta`; datetime
comparisons do not support relative tolerance:

```python
from datetime import timedelta

assert actual == pytest.approx(
    expected,
    abs=timedelta(milliseconds=50),
)
```

## Selectable text diffs

Since 9.1.0, `assertion_text_diff_style` can render failed string equality
assertions as separate `Left:` and `Right:` blocks instead of `ndiff` output.

## Non-propagating logger capture

Since 9.1.0, logging capture, including `caplog`, receives records from loggers
whose `propagate` attribute is false. Records no longer have to reach the root
logger to be captured.
