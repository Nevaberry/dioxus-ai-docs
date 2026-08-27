---
name: pytest-knowledge-patch
description: pytest
version: "9.1.0"
license: MIT
metadata:
  author: Nevaberry
---


# pytest Compatibility and Modern Usage

Use this skill when maintaining a pytest suite, plugin, configuration, or
programmatic integration whose behavior may depend on recent pytest changes.

## Start With Project Reality

1. Determine the pytest version from the project manifest. Use a lockfile or
   the installed environment only when the manifest does not pin it.
2. Inspect the active configuration file and command-line options. Do not
   assume that every discovered configuration file contributes settings.
3. Identify installed async, collection, and reporting plugins before changing
   tests that depend on their hooks.
4. Apply guidance only when the project's version includes the described
   behavior. Prefer observed code, tests, and current runtime behavior if they
   disagree with this patch.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Migrations and deprecations](references/migrations-and-deprecations.md) | Python support, newly failing tests, async and fixture migrations, removals |
| [Configuration and execution](references/configuration-and-execution.md) | TOML, strictness, collection, warnings, output, progress, logging |
| [Assertions and parametrization](references/assertions-and-parametrization.md) | exception groups, `raises` predicates, subtests, IDs, `approx` |
| [Plugin and fixture APIs](references/plugin-and-fixture-apis.md) | typed and aliased ini options, public APIs, registration, override precedence |

## Breaking-Change Triage

When a previously passing suite begins failing after an upgrade, check these
cases before weakening assertions or warning policy:

- An async test without a suitable async plugin is an error. Confirm that the
  plugin is installed, enabled, and configured for the test.
- A test must return `None`; move computed values into assertions or fixtures.
- A test function containing `yield` is invalid. Replace legacy generator-test
  patterns with parametrization.
- A synchronous test that receives an unresolved async fixture is on a removal
  path. Ensure an async plugin or hook resolves the fixture, including when it
  is `autouse`.
- Removal warnings can fail the run. Migrate the affected feature instead of
  treating a warning-filter workaround as a durable fix.
- New fixture lookup during teardown is deprecated. Declare or request the
  dependency during setup so it already exists at teardown time.
- Parametrization inputs must be reusable collections. Materialize generators
  and iterators before passing them as `argvalues`.

See [Migrations and deprecations](references/migrations-and-deprecations.md)
for class-scoped fixture methods, doctest interactions, marker-configured
hooks, legacy namespace packages, and programmatic entry-point migrations.

## Fixture Migration Checklist

For fixture-related failures or warnings:

1. Move module-, package-, or session-scoped inline autouse fixtures into
   `conftest.py` when normal collection and doctest collection both see them.
2. Add `@classmethod` to a class-scoped fixture declared on a test class.
3. Establish all dependencies before fixture teardown begins.
4. Move parametrized autouse fixtures away from doctest-dependent designs;
   doctests do not support parametrized fixtures.
5. Keep `pytest.mark.usefixtures()` non-empty and place it on supported test
   objects, never on `pytest.param`.
6. For plugins that cannot expose a declarative fixture during collection,
   consider imperative registration; keep `@pytest.fixture` as the normal
   interface.

## Configuration Selection

Prefer native TOML when a project already uses `pyproject.toml` and benefits
from arrays or other typed values:

```toml
[tool.pytest]
addopts = ["-ra", "-q"]
testpaths = ["tests", "integration"]
```

Do not combine `[tool.pytest]` with `[tool.pytest.ini_options]`. If more than
one candidate configuration file contains pytest configuration, pytest uses
one and warns about the others. Remove or consolidate stale configuration
rather than assuming the settings merge.

To opt into all current strictness checks, use:

```toml
[tool.pytest]
strict = true
```

Global strict mode includes configuration, marker, parametrization-ID, and
xfail strictness. An explicitly configured individual option overrides the
global value. Expect future strictness checks to join the global switch.

See [Configuration and execution](references/configuration-and-execution.md)
for native TOML filenames and sections, collection boundaries, warning limits,
terminal behavior, duplicate paths, stepwise state, and logging capture.

## Exception Assertions

Use structured matchers when the exception group's members or nesting are part
of the contract:

```python
with pytest.RaisesGroup(ValueError, TypeError):
    raise ExceptionGroup("errors", [ValueError(), TypeError()])
```

`pytest.RaisesExc` describes one exception and can be nested inside
`pytest.RaisesGroup`. Both matcher objects can be supplied to
`pytest.mark.xfail(raises=...)`.

Use `check=` when type and message matching are insufficient:

```python
with pytest.raises(OSError, check=lambda exc: exc.errno == 13):
    operation()
```

The predicate runs after type and message checks. If it returns false, the
exception is not accepted and propagates. Avoid `match=""`, which matches every
message and warns; use `match="^$"` to require an empty message.

See [Assertions and parametrization](references/assertions-and-parametrization.md)
for precise exception-group typing, regex mismatch diffs, hidden parameter
IDs, tuple unpacking, mixed-value approximation, and datetime tolerances.

## Built-In Subtests

Use the `subtests` fixture for cases discovered dynamically when each case
should be reported independently:

```python
def test_values(subtests: pytest.Subtests):
    for value in [1, 2, 3]:
        with subtests.test(value=value):
            assert value > 0
```

Core support also handles `unittest.TestCase.subTest`. Prefer ordinary
parametrization when cases are known at collection time and need independent
node IDs, selection, or fixture parametrization.

## Collection Controls

Set `collect_imported_tests = false` when imported production objects happen
to look like tests and should not be collected from a test module:

```ini
[pytest]
collect_imported_tests = false
```

When `consider_namespace_packages` is enabled, `--pyargs` can discover tests
inside implicit namespace packages. Repeated and overlapping path arguments
are normally deduplicated or collapsed; use `--keep-duplicates` only when
preserving duplicate execution is intentional.

If `testpaths` points outside `rootdir`, rely on directory ancestry for nested
`conftest.py` visibility. Fixtures from one nested directory do not apply to a
sibling merely because both are outside the root.

## Reproducible Plugin Loading

Disable automatic third-party plugin discovery when isolation matters:

```ini
[pytest]
addopts = --disable-plugin-autoload
```

This is the command-line counterpart of `PYTEST_DISABLE_PLUGIN_AUTOLOAD`.
Explicit `-p` plugins can still be selected. The `pythonpath` setting is
applied early enough to affect plugins loaded with `-p`.

Plugin authors should use supported hook implementation decorators instead of
markers, use `pytest.main()` for programmatic execution, and use public types
such as `pytest.TerminalReporter` and `pytest.ScopeName` in annotations where
appropriate. See [Plugin and fixture APIs](references/plugin-and-fixture-apis.md).

## Warning Budgets and Diagnostics

`--max-warnings` or `max_warnings` can turn warning volume into an explicit
suite limit. Warning filters now cover more of the lifecycle, including late
warnings and multiple unraisable or unhandled-thread exceptions in a test
phase, so investigate where a warning originates before suppressing it.

An invalid warning-filter class now produces a diagnostic instead of aborting
the entire run. File-descriptor warnings from the lsof plugin use
`pytest.PytestFDWarning`.

## Output and Debugging

Useful controls include:

- `--force-short-summary` to retain the condensed failure summary at any
  verbosity.
- `truncation_limit_lines` and `truncation_limit_chars` to control snippets.
- `console_output_style = times` to show each test's duration.
- `assertion_text_diff_style` to select separate `Left:` and `Right:` blocks
  for string equality failures.
- `faulthandler_exit_on_timeout = true` when a timeout should interrupt a
  deadlocked run, rather than only dump tracebacks.
- `--code-highlight=no` when highlighted source output is undesirable.

