# Migrations and Deprecations

## Runtime Support

- pytest 8.4.0 dropped Python 3.8 and officially supports Python 3.14.
- pytest 9.0.0 dropped Python 3.9 and requires Python 3.10 or newer.
- pytest 9.1.0 officially supports Python 3.15.

Check the project's interpreter matrix before upgrading pytest, and update CI,
packaging metadata, and local development constraints together.

## Tests That No Longer Degrade Gracefully

Since 8.4.0, the following are errors rather than warnings or implicit skips:

- An async test without a suitable plugin fails. Install and configure the
  async plugin appropriate for the suite.
- A test that returns a non-`None` value fails. Assert the result or move it to
  a fixture instead of returning it.
- A test function containing `yield` produces an explicit error. Replace
  generator-test patterns with parametrization or ordinary loops.

## Async Fixture Resolution

Since 8.4.0, requesting an async fixture without a `pytest_fixture_setup` hook
that resolves it emits `DeprecationWarning`. A synchronous test requesting an
async fixture is the common case, but the requirement also applies to
`autouse` fixtures. Ensure an async plugin or custom hook resolves the value
before the next major release.

## Fixture Placement and Lifecycle

### Doctest collectors and autouse fixtures

In 9.1.0 with `--doctest-modules`, a module-, package-, or session-scoped
autouse fixture defined in a Python test module can run once for the normal
module collector and again for the doctest collector. Move it to `conftest.py`
to avoid duplicate execution. Doctests do not support parametrized fixtures,
including parametrized autouse fixtures.

### Class-scoped methods

Since 9.1.0, a class-scoped fixture defined as an instance method warns because
fixture attributes are set on a different instance from the test methods. Add
`@classmethod`; the instance-method form is scheduled to become an error in
pytest 10.

### Teardown dependencies

Since 9.1.0, calling `request.getfixturevalue()` during teardown for a fixture
that was not requested earlier is deprecated and is scheduled to become an
error in pytest 10. Establish the dependency during setup.

### `usefixtures` placement

Since 8.4.0, an empty `pytest.mark.usefixtures()` warns. Applying
`pytest.mark.usefixtures` to `pytest.param` errors because that placement never
had an effect.

## Reusable Parametrization Inputs

Since 9.1.0, generators, iterators, and other non-`Collection` iterables used
as `argvalues` in `pytest.mark.parametrize` or `Metafunc.parametrize` are
deprecated. Repeated collection can exhaust one-shot inputs and silently skip
tests. Materialize them first:

```python
values = list(generate_values())

@pytest.mark.parametrize("value", values)
def test_value(value):
    ...
```

## Plugin Hook Declaration

Configuring hook implementations through markers is scheduled for removal in
pytest 10. The marker form has been deprecated since pytest 7.2. In 9.1.0,
plugin hooks should use the supported hook implementation decorators.

## Removed and Externalized Interfaces

### Removal warnings

In 9.0.0, `PytestRemovedIn9Warning` fails the run by default. A temporary
9.0.x-only escape hatch is available, but the affected deprecated features are
effectively removed in 9.1.0:

```ini
[pytest]
filterwarnings =
    ignore::pytest.PytestRemovedIn9Warning
```

Use the filter only while completing a migration.

### Pastebin integration

Since 9.1.0, the built-in `--pastebin` option is deprecated. Install and use
the external `pytest-pastebin` plugin when that workflow is required.

### Programmatic entry point

Since 9.1.0, `pytest.console_main()` is deprecated and is scheduled for removal
in pytest 10. Call `pytest.main()` from code that invokes pytest.

## Namespace Package Migration

Since 9.0.0, `monkeypatch.syspath_prepend()` warns when the inserted path
contains a namespace package implemented with
`pkg_resources.declare_namespace()`. Migrate the package to a PEP 420 native
namespace.

