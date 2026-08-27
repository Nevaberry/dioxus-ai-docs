# Plugin and Fixture APIs

## Typed Ini Values

Since 8.4.0, `Parser.addini()` accepts `type="int"` and `type="float"`. Plugins
receive converted numeric values directly:

```python
def pytest_addoption(parser):
    parser.addini("retries", type="int", default=2, help="retry count")
    parser.addini("ratio", type="float", default=4.2, help="test ratio")
```

## Configuration Aliases

Since 9.0.0, `Parser.addini()` accepts `aliases`, allowing a plugin to rename
a configuration option while keeping old names usable. If the canonical name
and an alias are both configured, the canonical value wins.

## Plugin Initialization and Public Reporting API

Since 8.4.0, the `pythonpath` setting is applied early enough to affect plugins
loaded with `-p`.

Also since 8.4.0, `pytest.TerminalReporter` is public because it appears in the
`pytest_terminal_summary` hook signature. It can be used in plugin annotations
without importing an internal implementation.

## Imperative Fixture Registration

Since 9.1.0, plugins can call `pytest.register_fixture()` when collection-time
discovery of a declarative `@pytest.fixture` is impractical. Declarative
registration remains the normal interface.

## Public Fixture Scope Type

Since 9.1.0, `pytest.ScopeName` is public and can be used in plugin and hook
function annotations.

## Fixture Override Precedence

Since 9.1.0, when plugins register multiple fixtures with the same name, a
fixture visible to a more specific collection node wins over one visible to a
more general node, even when the general fixture was registered later. When
visibility is equal or incomparable, the most recently registered fixture
still wins.

