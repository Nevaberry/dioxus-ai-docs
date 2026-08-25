# Fixtures, plugins, and hooks

## Doctest and autouse fixture interaction

In 9.1.0, `--doctest-modules` may cause an autouse fixture defined in a Python
test module to execute once for the normal module collector and once for the
doctest collector. This affects module-, package-, and session-scoped
fixtures.

Move such fixtures to `conftest.py` when duplicate execution is undesirable.
Doctests do not support parametrized fixtures, including parametrized autouse
fixtures.

## Imperative fixture registration

Since 9.1.0, plugins can call `pytest.register_fixture()` when collection-time
discovery of a declarative `@pytest.fixture` is impractical. Decorator-based
registration remains the normal interface.

## Fixture override precedence

Since 9.1.0, when plugins register multiple fixtures with the same name, a
fixture visible to a more specific collection node wins over a fixture for a
more general node, even if the general fixture was registered later.

For fixtures with equal or incomparable visibility, the last registration
continues to win.

## Numeric plugin configuration

Since 8.4.0, `parser.addini()` accepts `type="int"` and `type="float"`, and
returns converted numeric values to plugins:

```python
def pytest_addoption(parser):
    parser.addini("retries", type="int", default=2, help="retry count")
    parser.addini("ratio", type="float", default=4.2, help="test ratio")
```

## Configuration aliases

Since 9.0.0, `Parser.addini()` accepts an `aliases` parameter. Plugins can
rename an option while retaining its old names. If both an alias and the
canonical name are configured, the canonical value wins.

## Public plugin API types

`pytest.TerminalReporter` became public in 8.4.0 because it appears in the
`pytest_terminal_summary` hook signature.

`pytest.ScopeName` became public in 9.1.0 and can be used in plugin and hook
function annotations.
