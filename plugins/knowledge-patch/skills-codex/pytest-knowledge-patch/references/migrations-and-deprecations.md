# Migrations and deprecations

## Runtime support

pytest 8.4.0 dropped Python 3.8 and officially supported Python 3.14. pytest
9.0.0 dropped Python 3.9 and requires Python 3.10 or newer. pytest 9.1.0
officially supports Python 3.15.

## Invalid and unsupported tests

Since 8.4.0, invalid test shapes fail instead of being tolerated:

- An async test without a suitable plugin fails instead of warning and being
  skipped.
- A test returning a value other than `None` fails.
- A test function containing `yield` produces an explicit error.

Install and configure an async plugin for async tests, keep normal test return
values implicit, and replace yield tests with supported parametrization or
fixtures.

## Async fixture resolution

Since 8.4.0, requesting an async fixture without a `pytest_fixture_setup` hook
that resolves it emits `DeprecationWarning`. A synchronous test requesting an
async fixture is the common case, but the rule also matters for `autouse`
fixtures.

Ensure that an async plugin or custom hook resolves every async fixture before
the next major release.

## Fixture and parametrization migrations

The following patterns are deprecated in 9.1.0 and are planned to become
errors:

- A class-scoped fixture defined as an instance method warns because fixture
  attributes are assigned on a different instance from the test methods. Add
  `@classmethod` before pytest 10.
- Calling `request.getfixturevalue()` during teardown for a fixture that was
  not requested earlier is deprecated. Establish the dependency during setup
  before pytest 10.
- Passing a generator, iterator, or other non-`Collection` iterable as
  parametrization `argvalues` is deprecated because repeated collection can
  exhaust it and silently skip tests. Materialize it, for example with
  `list(generate_values())`.

## Plugin hook migration

Configuring hook implementations through markers is scheduled for removal in
pytest 10. This mechanism had already been deprecated since pytest 7.2.
Declare plugin hooks with the supported hook implementation decorators.

## Programmatic and command-line replacements

In 9.1.0:

- The built-in `--pastebin` option is deprecated. Install and use the external
  `pytest-pastebin` plugin.
- `pytest.console_main()` is deprecated and will be removed in pytest 10. Use
  `pytest.main()` for programmatic execution.

## Namespace package migration

Since 9.0.0, `monkeypatch.syspath_prepend()` warns when the inserted path
contains a namespace package based on `pkg_resources.declare_namespace()`.
Migrate these packages to PEP 420 native namespaces.

## Removal warnings

Since 9.0.0, `PytestRemovedIn9Warning` fails the run by default. It can be
temporarily suppressed during the 9.0.x series:

```ini
[pytest]
filterwarnings =
    ignore::pytest.PytestRemovedIn9Warning
```

Affected deprecated features are effectively removed in 9.1.0, so suppression
is only a short migration bridge.
