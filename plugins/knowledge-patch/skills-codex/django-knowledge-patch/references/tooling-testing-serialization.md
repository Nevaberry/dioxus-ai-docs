# Tooling, Testing, and Serialization

## Control automatic shell imports

The `shell` command automatically imports models from every installed application (5.2-guide).
Use verbosity 2 to list imported names and `--no-imports` to disable automatic imports. A custom
command can extend the defaults by overriding `get_auto_imports()` with fully qualified paths.

```python
from django.core.management.commands import shell

class Command(shell.Command):
    def get_auto_imports(self):
        return [
            *super().get_auto_imports(),
            "django.conf.settings",
        ]
```

The 6.0-guide expands the defaults beyond application models to include `settings`, `connection`,
`models`, `reset_queries`, `functions`, and `timezone`. Prefer `--no-imports` when validating that
a script declares its own dependencies.

## Extend management commands

Subclasses of `makemigrations` and `migrate` can replace `Command.autodetector` (since 5.2).
Custom commands can override `BaseCommand.get_check_kwargs()` to control system-check arguments.

`runserver` warns that it is not for production use. Set
`DJANGO_RUNSERVER_HIDE_WARNING=true` only to suppress that message in a known development
workflow; it does not make the development server production-ready.

## Keep tests isolated correctly

Database connections opened from threads are not allowed in `SimpleTestCase` (since 5.1). Use a
database-enabled test class for any threaded database access.

Django's custom assertions hide internal stack frames, so failures point to the calling test and
`test --pdb` opens in that test method (5.2-guide). Do not write debugger automation that expects
to start inside an assertion helper.

Data from `TransactionTestCase.fixtures` and migrations using `serialized_rollback=True` is
available during `TransactionTestCase.setUpClass()` (since 5.2). Account for the earlier data
availability in class-level setup and cleanup.

`DiscoverRunner` supports parallel execution under the multiprocessing `forkserver` start method
(since 6.0). Verify that custom test-runner state is serializable and does not depend on `fork`
inheritance.

## Pass query parameters in test clients

`RequestFactory`, `AsyncRequestFactory`, `Client`, and `AsyncClient` accept `query_params` for any
HTTP method (since 5.1). Keep the URL query separate from POST or other body data:

```python
self.client.post(
    "/items/1",
    data={"confirm": True},
    query_params={"action": "delete"},
)
```

## Extend deserialization

Every serialization format exposes a `Deserializer` class rather than a function (since 5.2).
Subclass that class when implementing a compatible custom format instead of wrapping an assumed
function-only API.

The JSON serializer always terminates output with a newline, even when `indent` is not supplied
(since 6.0). Include the final newline in exact-output tests and stream concatenation logic.

## Serialize migrations safely

Migration serialization handles `zoneinfo.ZoneInfo` and deconstructible-object keyword names that
are not valid Python identifiers (since 6.0). A squashed migration can also be re-squashed before
it becomes a normal migration. Inspect dependencies and replacements after re-squashing rather
than assuming only original migrations are squash inputs.

## Use scaffolding and static-file commands

`startproject` and `startapp` create a missing custom target directory (since 6.0). Validate the
resolved target path before running scaffolding in automation, because absence no longer causes
the command to stop at that point.

Static manifests order paths deterministically. At verbosity 1, `collectstatic` summarizes skipped
files and files deleted by `--clear`; use verbosity 2 when automation or diagnosis needs per-file
output.

## Update generated project expectations

New project settings no longer include the `debug()` context processor by default (since 5.2).
Do not assume a newly scaffolded project exposes its debug context values unless the processor is
configured explicitly.

`BigAutoField` is the actual default for `DEFAULT_AUTO_FIELD` and
`AppConfig.default_auto_field`, not only a line emitted into generated templates (since 6.0).
Projects already choosing it explicitly may remove redundant boilerplate after confirming
migration state does not change.

## Handle protocol inputs

ASGI accepts multiple physical `Cookie` headers in an HTTP/2 request (since 6.0). Custom request
test fixtures, middleware, and protocol adapters should cover repeated cookie headers instead of
normalizing test input prematurely.
