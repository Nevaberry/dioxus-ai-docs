# Tooling, Testing, and Serialization

Batch attribution: `5.1`, `5.2-guide`, `5.2`, `6.0-guide`, `6.0`.

## Contents

- [Automatic shell imports](#automatic-shell-imports)
- [Management-command extension hooks](#management-command-extension-hooks)
- [Test request query parameters](#test-request-query-parameters)
- [Test isolation and debugging](#test-isolation-and-debugging)
- [Fixture timing and parallel tests](#fixture-timing-and-parallel-tests)
- [Asynchronous pagination](#asynchronous-pagination)
- [Serialization](#serialization)
- [Project scaffolding and static files](#project-scaffolding-and-static-files)

## Automatic shell imports

The `shell` command automatically imports models from every installed application (since
`5.2-guide`). Use verbosity 2 to list successful automatic imports, and pass `--no-imports` to
start without them:

```console
python manage.py shell -v 2
python manage.py shell --no-imports
```

A custom `shell` command can extend the set by overriding `get_auto_imports()` and returning fully
qualified import paths:

```python
from django.core.management.commands import shell

class Command(shell.Command):
    def get_auto_imports(self):
        return [*super().get_auto_imports(), "django.conf.settings"]
```

In addition to application models, Django 6.0 automatically imports `settings`, `connection`,
`models`, `reset_queries`, `functions`, and `timezone` (since `6.0-guide`). Account for name
collisions in project models and custom auto-import lists. Use `--no-imports` when validating that
an example contains all of its required imports.

## Management-command extension hooks

- A `makemigrations` or `migrate` subclass can replace `Command.autodetector` (since `5.2`).
- A custom command can override `BaseCommand.get_check_kwargs()` to control the arguments passed
  into system checks (since `5.2`).
- `runserver` warns that it is not a production server (since `5.2`). Set
  `DJANGO_RUNSERVER_HIDE_WARNING=true` only to suppress that warning in a deliberate development
  environment; it does not make the server production-safe.
- A custom migration operation can set `Operation.category`, which lets `makemigrations` display
  a meaningful operation symbol (since `5.1`).

## Test request query parameters

`RequestFactory`, `AsyncRequestFactory`, `Client`, and `AsyncClient` accept `query_params` on every
HTTP method (since `5.1`):

```python
self.client.post(
    "/items/1",
    query_params={"action": "delete"},
)
```

Use this parameter for the URL query string and the existing request-data parameter for the body;
do not manually concatenate an unescaped query string.

## Test isolation and debugging

`SimpleTestCase` rejects database connections used from threads (since `5.1`). If a threaded test
needs database access, inherit from an appropriate database-enabled test case and configure its
database access rather than bypassing the isolation guard.

Django's custom assertion helpers hide their internal stack frames (since `5.2-guide`). Assertion
failures point to the calling test, and `test --pdb` enters the failing test method rather than an
assertion helper. Debug local variables in that test frame first.

## Fixture timing and parallel tests

Data from `TransactionTestCase.fixtures` and from migrations using `serialized_rollback=True` is
available during `TransactionTestCase.setUpClass()` (since `5.2`). Class-level setup may query that
data, but still clean up any other class-scoped resources correctly.

`DiscoverRunner` supports parallel tests when Python multiprocessing uses the `forkserver` start
method (since `6.0`). Do not disable parallelism solely because the runtime selects `forkserver`;
instead test that workers can import and initialize the suite.

## Asynchronous pagination

`AsyncPaginator` and `AsyncPage` are asynchronous counterparts to `Paginator` and `Page` (since
`6.0`). Use their async interfaces when the object count or page data comes from async-capable
query work. Passing `orphans >= per_page` is deprecated for both paginator families and becomes
unsupported in Django 7.0.

## Serialization

Each registered serialization format exposes a `Deserializer` class rather than a function (since
`5.2`). Subclass it when a custom format needs to extend deserialization behavior.

The JSON serializer always ends its output with a newline, even when `indent` is omitted (since
`6.0`). Include that terminal newline in byte-for-byte snapshots and stream consumers.

Migration serialization supports `zoneinfo.ZoneInfo` and deconstructible-object keyword names that
are not valid Python identifiers (since `6.0`). See
[orm-and-databases.md](orm-and-databases.md) for migration state and re-squashing details.

## Project scaffolding and static files

`startproject` and `startapp` create a missing custom target directory (since `6.0`). A caller no
longer needs to pre-create that destination, but should still reject an unintended path before
running the command.

Static-file manifests have deterministic path ordering (since `6.0`), improving reproducible
output. At `collectstatic --verbosity 1`, Django summarizes skipped files and files deleted by
`--clear`; use verbosity 2 when per-file output is required.
