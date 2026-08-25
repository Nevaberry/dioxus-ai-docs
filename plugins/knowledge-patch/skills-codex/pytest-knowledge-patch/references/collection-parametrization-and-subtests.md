# Collection, parametrization, and subtests

## Imported test-like objects

Since 8.4.0, `collect_imported_tests = false` limits collection of test-looking
classes and functions to objects defined in the test file. Use it to avoid
collecting imported production objects accidentally:

```ini
[pytest]
collect_imported_tests = false
```

## Namespace packages with `--pyargs`

Since 9.0.0, when `consider_namespace_packages` is true, `--pyargs` can
discover tests in PEP 420 implicit namespace packages. The setting previously
affected imports but not `--pyargs` discovery.

## Path argument normalization

Since 9.0.0:

- Overlapping path arguments are collapsed to their common prefix regardless
  of argument order.
- Repeating the same file does not run it twice.

Use `--keep-duplicates` to preserve the earlier duplicate-path behavior. This
also preserves the old overlap bug, so enable it only when duplicate execution
is intentional.

## `conftest.py` boundaries

Since 9.1.0, when `testpaths` points outside `rootdir`, fixtures from a nested
`conftest.py` no longer leak into sibling directories.

## Hidden parameter IDs

Since 8.4.0, use `pytest.HIDDEN_PARAM` as a
`pytest.param(..., id=...)` value or in
`Metafunc.parametrize(..., ids=...)` to omit that set from the generated test
name:

```python
@pytest.mark.parametrize("value", [
    pytest.param(1, id=pytest.HIDDEN_PARAM),
    pytest.param(2, id="two"),
])
def test_value(value):
    ...
```

## Reusable parameter collections

Since 9.1.0, generators, iterators, and other non-`Collection` iterables passed
as `argvalues` to `pytest.mark.parametrize` or `Metafunc.parametrize` are
deprecated. Repeated collection can exhaust them and skip tests. Materialize
the values first:

```python
values = list(generate_values())

@pytest.mark.parametrize("value", values)
def test_value(value):
    ...
```

## Single-parameter tuple unpacking

Since 9.1.0, a trailing comma in a one-name argname string makes it behave like
a one-element argname tuple. Each tuple value is unpacked into the argument:

```python
@pytest.mark.parametrize("arg,", [(1,), (2,)])
def test_arg(arg):
    ...
```

## `usefixtures` diagnostics

Since 8.4.0, an empty `pytest.mark.usefixtures()` warns. Applying
`pytest.mark.usefixtures` to `pytest.param` errors because that placement never
had an effect.

## Built-in subtests

Since 9.0.0, the `subtests` fixture runs dynamically discovered cases inside
`subtests.test(...)`, catching and reporting each failure independently:

```python
def test_values(subtests: pytest.Subtests):
    for value in [1, 2, 3]:
        with subtests.test(value=value):
            assert value > 0
```

Core pytest also supports `unittest.TestCase.subTest`.
