# Tooling, Testing, and Serialization

Load this reference for the interactive shell, management commands, test
isolation, fixtures, pagination, serializers, scaffolding, static files, and
protocol output.

## Control automatic shell imports

The `shell` command imports models from every installed application.
`--verbosity 2` lists the imports and `--no-imports` disables them. A custom
shell command can extend the defaults by overriding `get_auto_imports()` with
fully qualified paths. (`5.2-guide`)

```python
from django.core.management.commands import shell

class Command(shell.Command):
    def get_auto_imports(self):
        return [*super().get_auto_imports(), "django.conf.settings"]
```

In addition to app models, the shell imports `settings`, `connection`, `models`,
`reset_queries`, `functions`, and `timezone` by default. (`6.0-guide`)

## Construct test requests

`RequestFactory`, `AsyncRequestFactory`, `Client`, and `AsyncClient` accept a
`query_params` mapping for every HTTP method. (`5.1`)

```python
self.client.post("/items/1", query_params={"action": "delete"})
```

## Select the right test case

Database connections used from threads are rejected in `SimpleTestCase`. Use an
appropriate database-enabled test class for threaded database tests. (`5.1`)

Django's custom assertions hide internal stack frames, so failures point at the
calling test. `test --pdb` therefore opens in the failing test method rather
than an assertion helper. (`5.2-guide`)

`TransactionTestCase.fixtures` data and migrations using
`serialized_rollback=True` are available during
`TransactionTestCase.setUpClass()`. (`5.2`)

`DiscoverRunner` supports parallel execution when multiprocessing uses the
`forkserver` start method. (`6.0`)

## Extend management commands

`makemigrations` and `migrate` command subclasses can replace
`Command.autodetector`. Custom commands can override
`BaseCommand.get_check_kwargs()` to control system checks. (`5.2`)

`runserver` warns that it is unsuitable for production. Set
`DJANGO_RUNSERVER_HIDE_WARNING=true` to suppress only that warning. (`5.2`)

`startproject` and `startapp` create a missing custom target directory.
(`6.0`)

## Interpret static-file command output (`6.0`)

Static manifests have deterministic path ordering. At verbosity 1,
`collectstatic` summarizes skipped and `--clear`-deleted files; use verbosity 2
for per-file output.

## Extend deserialization (`5.2`)

Every serialization format exposes a `Deserializer` class rather than a function.
Custom formats can subclass it to extend deserialization behavior.

The JSON serializer always terminates output with a newline, even when `indent`
is not specified. (`6.0`)

Migration serialization supports `zoneinfo.ZoneInfo` and deconstructible-object
keyword names that are not valid Python identifiers. A squashed migration can be
squashed again before it becomes a normal migration. (`6.0`)

## Paginate asynchronously

`AsyncPaginator` and `AsyncPage` provide async counterparts to `Paginator` and
`Page`. (`6.0`)

Passing `orphans >= per_page` to either paginator is deprecated and becomes
unsupported at the Django 7.0 boundary. (`6.0`, `deprecation-roadmap`)

## Account for protocol behavior (`6.0`)

ASGI accepts multiple `Cookie` headers in HTTP/2 requests. If protocol tests or
custom request adapters previously collapsed these headers, add a multi-header
case.
