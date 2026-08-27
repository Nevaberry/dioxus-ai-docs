# Configuration and Execution

## Native TOML Configuration

Since 9.0.0, pytest accepts native TOML configuration in `[tool.pytest]` in
`pyproject.toml`, and in `[pytest]` in `pytest.toml` or `.pytest.toml`. Native
TOML values can use arrays and other TOML types:

```toml
[tool.pytest]
minversion = "9.0"
addopts = ["-ra", "-q"]
testpaths = ["tests", "integration"]
```

The compatibility section `[tool.pytest.ini_options]` remains supported, but
it cannot coexist with `[tool.pytest]`. If configuration occurs in more than
one candidate file, pytest 9.0.0 warns and uses only one file; it does not
merge all candidates.

## Strict Mode

Since 9.0.0, `strict = true` or `--strict` enables all of these checks:

- `strict_config`
- `strict_markers`
- `strict_parametrization_ids`
- `strict_xfail`

An explicitly set individual option overrides the global setting.
`strict_parametrization_ids` rejects duplicate IDs rather than suffixing them.
Future strictness options automatically join unified strict mode.

## Collection Boundaries

### Imported tests

Since 8.4.0, set `collect_imported_tests = false` to collect test-looking
classes and functions only when defined in the test file. This prevents
imported production objects from being collected accidentally.

### Namespace-package targets

Since 9.0.0, when `consider_namespace_packages` is true, `--pyargs` discovers
tests in PEP 420 implicit namespace packages. Previously the setting affected
imports but not `--pyargs` discovery.

### Duplicate and overlapping paths

Since 9.0.0, overlapping path arguments collapse to their common prefix
regardless of argument order, and repeating the same file does not run it
twice. `--keep-duplicates` restores the earlier duplicate-path behavior,
including the old overlap bug.

### External test paths and `conftest.py`

In 9.1.0, when `testpaths` points outside `rootdir`, a nested `conftest.py` is
scoped correctly and its fixtures no longer leak into sibling directories.

## Plugin Loading and Version Inspection

Since 8.4.0, `--disable-plugin-autoload` is the command-line equivalent of
`PYTEST_DISABLE_PLUGIN_AUTOLOAD`. It can be persisted in `addopts`:

```ini
[pytest]
addopts = --disable-plugin-autoload
```

Since 9.0.0, one command-line `--version` avoids loading plugins. Repeat the
flag (`pytest --version --version`) to include plugin information. This early
handling works only when the flag is supplied directly on the command line,
not through `PYTEST_ADDOPTS` or configured `addopts`.

## Stepwise State

Since 8.4.0, a run without `--stepwise` does not erase the last failed-test
state. A later stepwise run resumes there unless the suite-size check rejects
the state as stale. Use `--stepwise-reset` or `--sw-reset` to discard saved
state and start at the beginning.

## Warning Behavior and Limits

### Lifecycle coverage

Since 8.4.0, configured and command-line `filterwarnings` rules cover more of
the pytest lifecycle. Very late warnings plus unraisable or unhandled-thread
exceptions can therefore fail a suite. Multiple unraisable and thread
exceptions may be collected in each test phase. The lsof plugin's warning is
`pytest.PytestFDWarning`.

### Invalid filters

Since 9.0.0, a warning filter naming a class that pytest cannot import emits a
diagnostic message instead of aborting the run.

### Warning budgets

Since 9.1.0, `--max-warnings` and the `max_warnings` configuration option fail
a run after the warning count exceeds the configured threshold:

```ini
[pytest]
max_warnings = 10
```

## Terminal and Source Output

Since 8.4.0:

- `--force-short-summary` keeps the condensed failure summary at any
  verbosity.
- `truncation_limit_lines` and `truncation_limit_chars` control snippet
  truncation.
- `console_output_style = times` reports each test's execution time.
- `pygments` is a required dependency, so source is highlighted by default;
  use `--code-highlight=no` to disable it.

In 9.0.0, the internal terminal-progress plugin sends OSC 9;4 progress updates
automatically in a supported TTY. Disable it with
`pytest -p no:terminalprogress`, or persist `-p no:terminalprogress` in
`addopts`.

Since 9.1.0, `assertion_text_diff_style` can render failed string equality
assertions as separate `Left:` and `Right:` blocks instead of an `ndiff`.

## Timeouts and CI Detection

Since 9.0.0, `faulthandler_exit_on_timeout` can interrupt pytest when a
faulthandler timeout detects a deadlock. Its default is `false`, preserving
the traceback-dump-only behavior.

Also since 9.0.0, an empty `CI` or `BUILD_NUMBER` environment variable does not
activate CI mode. At least one of those signals must have a non-empty value.

## Logging Capture

Since 9.1.0, pytest logging capture, including `caplog`, receives records from
loggers whose `propagate` attribute is `False`. Records no longer need to
reach the root logger to be captured.

