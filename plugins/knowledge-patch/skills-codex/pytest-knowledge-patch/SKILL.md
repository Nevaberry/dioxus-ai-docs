---
name: pytest-knowledge-patch
description: pytest
version: 9.1.0
license: MIT
metadata:
  author: Nevaberry
---


# pytest Knowledge Patch

Use this skill when maintaining pytest suites, plugins, configuration, or programmatic
integrations. Start with migration checks, then load the matching reference.

## Reference index

| Reference | Topics |
| --- | --- |
| [migrations-and-deprecations.md](references/migrations-and-deprecations.md) | Python support, invalid tests, fixture and hook migrations, removed entry points |
| [configuration-and-cli.md](references/configuration-and-cli.md) | Native TOML, strict mode, plugin loading, progress, stepwise, output, timeouts |
| [fixtures-plugins-and-hooks.md](references/fixtures-plugins-and-hooks.md) | Fixture registration and precedence, doctests, plugin ini values, public APIs |
| [collection-parametrization-and-subtests.md](references/collection-parametrization-and-subtests.md) | Collection boundaries, path arguments, parameter IDs, subtests |
| [assertions-exceptions-and-logging.md](references/assertions-exceptions-and-logging.md) | Exception groups, `raises` checks, approximate values, string diffs, `caplog` |
| [warnings-and-diagnostics.md](references/warnings-and-diagnostics.md) | Warning filters and limits, thread and unraisable errors, source display |

## Migration triage

Check these issues before changing tests or upgrading an environment.

### Respect the Python support floor

- Do not plan a pytest 9 environment on Python 3.9 or earlier; Python 3.10 is
  the minimum.
- Python 3.15 is supported for environments that have moved forward.
- For pytest 8 environments, account for the removal of Python 3.8 and
  addition of Python 3.14 support.

### Fix invalid test shapes

- An `async def` test needs an async-testing plugin; a test must return `None`.
- Do not define test functions containing `yield`; pytest reports them as
  invalid.

### Resolve async fixtures explicitly

A synchronous test must not consume an unresolved async fixture. Ensure an
async plugin or custom `pytest_fixture_setup` hook resolves it, including for
`autouse` fixtures.

### Migrate fixture patterns before they become errors

- Define class-scoped fixture methods as class methods.
- Request every fixture dependency during setup; teardown must not discover a
  new fixture through `request.getfixturevalue()`.
- Materialize generator or iterator parameter values into a reusable
  collection before parametrizing.
- Move module-, package-, or session-scoped autouse fixtures used with
  `--doctest-modules` into `conftest.py` when duplicate execution is unsafe.
- Do not parametrize fixtures used by doctests.

### Replace retiring interfaces

- Configure plugin hooks with supported hook implementation decorators, not
  markers.
- Replace built-in `--pastebin` use with the external `pytest-pastebin`
  plugin.
- Replace `pytest.console_main()` with `pytest.main()`.
- Convert `pkg_resources.declare_namespace()` packages to native PEP 420
  namespaces before using `monkeypatch.syspath_prepend()`.

## Configuration quick reference

### Prefer native TOML

Use `[tool.pytest]` in `pyproject.toml` for typed values:

```toml
[tool.pytest]
minversion = "9.0"
addopts = ["-ra", "-q"]
testpaths = ["tests", "integration"]
```

Alternatively use `[pytest]` in `pytest.toml` or `.pytest.toml`.
`[tool.pytest.ini_options]` remains valid, but it cannot coexist with
`[tool.pytest]`. Keep configuration in only one candidate file; pytest selects
one and warns when several contain configuration.

### Enable strictness deliberately

Set `strict = true` or pass `--strict` to enable:

- `strict_config` and `strict_markers`
- `strict_parametrization_ids` and `strict_xfail`

An explicit individual option overrides the global setting. Duplicate
parameter IDs become errors under `strict_parametrization_ids`. Expect new
strictness options to join unified strict mode automatically.

### Control plugin startup

- Use `--disable-plugin-autoload` to block entry-point plugin autoloading;
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD` is the environment equivalent.
- Persist the switch in `addopts` when isolation is the project default.
- A single command-line `--version` avoids plugin loading.
- Repeat it as `pytest --version --version` when plugin information is needed.
- Do not expect `--version` in `PYTEST_ADDOPTS` or configured `addopts` to get
  this early handling.

### Configure execution behavior

- `faulthandler_exit_on_timeout = true` interrupts pytest on timeout; its
  default is false and only dumps tracebacks.
- `--stepwise-reset` and `--sw-reset` discard saved stepwise state.
- `--max-warnings` and `max_warnings` fail the run after the warning count
  exceeds the configured threshold.
- Disable terminal progress updates with `-p no:terminalprogress`.

## Fixture and plugin quick reference

### Register a fixture imperatively only when needed

Plugins may call `pytest.register_fixture()` when a declarative
`@pytest.fixture` cannot be discovered during collection. Prefer the decorator
for ordinary fixtures.

When plugin fixtures share a name, the fixture visible to the more specific collection
node wins. Equal or incomparable visibility still uses last-registration-wins.

### Define typed and renamed ini options

`Parser.addini()` supports converted numeric values:

```python
def pytest_addoption(parser):
    parser.addini("retries", type="int", default=2, help="retry count")
    parser.addini("ratio", type="float", default=4.2, help="test ratio")
```

Use `aliases` when renaming an option. If both an alias and the canonical name
are configured, the canonical value wins.

### Use public annotations and reporters

- `pytest.ScopeName` is public for fixture and hook annotations.
- `pytest.TerminalReporter` is public in `pytest_terminal_summary` hooks.
- The `pythonpath` option takes effect early enough to influence plugins loaded
  with `-p`.

## Collection and parametrization quick reference

### Avoid accidental collection

Set `collect_imported_tests = false` to collect test-looking classes and
functions only when defined in the test file:

```ini
[pytest]
collect_imported_tests = false
```

With `consider_namespace_packages = true`, `--pyargs` can discover tests in
PEP 420 implicit namespace packages.

### Make parameter IDs intentional

Hide one parameter set from a generated test name with
`pytest.HIDDEN_PARAM`, either as `pytest.param(..., id=...)` or inside
`Metafunc.parametrize(..., ids=...)`:

```python
@pytest.mark.parametrize("value", [
    pytest.param(1, id=pytest.HIDDEN_PARAM),
    pytest.param(2, id="two"),
])
def test_value(value):
    ...
```

An argname string ending in a comma is unpacked as a one-element tuple:

```python
@pytest.mark.parametrize("arg,", [(1,), (2,)])
def test_arg(arg):
    ...
```

Do not put `pytest.mark.usefixtures` on `pytest.param`; it is an error. An
empty `pytest.mark.usefixtures()` also warns.

### Use built-in subtests

The `subtests` fixture reports dynamically discovered cases independently:

```python
def test_values(subtests: pytest.Subtests):
    for value in [1, 2, 3]:
        with subtests.test(value=value):
            assert value > 0
```

`unittest.TestCase.subTest` is supported as well.

## Assertion quick reference

### Match exception groups structurally

Use `pytest.RaisesGroup` for the member types and nesting of an
`ExceptionGroup`; nest `pytest.RaisesExc` for single-exception matching:

```python
with pytest.RaisesGroup(ValueError, TypeError):
    raise ExceptionGroup("errors", [ValueError(), TypeError()])
```

Both matcher objects work in `pytest.mark.xfail(raises=...)`.

### Add semantic exception checks

`pytest.raises(..., check=fn)` runs the predicate after type and message
matching:

```python
with pytest.raises(OSError, check=lambda exc: exc.errno == 13):
    operation()
```

A false predicate rejects and propagates the exception. Avoid `match=""`,
which warns because it matches every message; use `match="^$"` for an empty
message.

### Compare mixed and temporal values approximately

`pytest.approx` accepts mixed numeric and non-numeric collections. It also
supports `datetime.datetime` and `datetime.timedelta`. Use a `timedelta`
tolerance; datetime comparisons do not support relative tolerance.

## Reporting and diagnostics quick reference

- `--force-short-summary` retains the condensed summary at any verbosity.
- `truncation_limit_lines` and `truncation_limit_chars` control truncation.
- `console_output_style = times` prints each test's execution time.
- `assertion_text_diff_style` can show failed string equality as separate
  `Left:` and `Right:` blocks.
- Source highlighting is available by default; disable it with
  `--code-highlight=no`.
- Logging capture receives records from loggers with `propagate = False`.

For lifecycle-wide warning behavior and thread or unraisable diagnostics, read
[warnings-and-diagnostics.md](references/warnings-and-diagnostics.md).
