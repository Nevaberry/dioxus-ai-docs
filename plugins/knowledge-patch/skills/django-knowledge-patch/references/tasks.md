# Tasks

Batch attribution: `6.0-guide`.

## Contents

- [Declare and enqueue tasks](#declare-and-enqueue-tasks)
- [Configure execution backends](#configure-execution-backends)
- [Select execution options](#select-execution-options)
- [Serialize arguments and coordinate transactions](#serialize-arguments-and-coordinate-transactions)
- [Use task context](#use-task-context)
- [Inspect and retrieve results](#inspect-and-retrieve-results)

## Declare and enqueue tasks

Decorate a function with `@django.tasks.task`. The decorator returns an immutable `Task` object;
enqueue work through that object rather than invoking the decorated function as a normal callable.

```python
from django.tasks import task

@task(priority=2, queue_name="emails")
def email_users(user_ids):
    ...

result = email_users.enqueue([1, 2])
```

Use `enqueue()` from synchronous code and `aenqueue()` from asynchronous code.

## Configure execution backends

Configure aliases in `TASKS`:

```python
TASKS = {
    "default": {
        "BACKEND": "path.to.backend",
    },
}
```

Retrieve a configured alias from `task_backends[alias]`; use `default_task_backend` for the
default alias.

The built-in backends do not provide a production worker system:

- `ImmediateBackend` runs the task synchronously in the enqueueing process.
- `DummyBackend` records enqueue operations but does not execute them.

Use a third-party backend and its worker for production execution. Check backend capabilities
before requiring delayed scheduling, priorities, persistent results, or cross-process lookup.

## Select execution options

`Task.using()` returns a modified immutable copy. It can choose:

- `priority`
- `backend`
- `queue_name`
- `run_after`

The original task is unchanged. Deferred execution through `run_after` and priority ordering work
only when the selected backend supports them.

## Serialize arguments and coordinate transactions

Task arguments and return values must survive a JSON encode/decode round trip. Pass stable scalar
data and identifiers. Do not pass model instances, datetimes, or tuples without explicitly
converting them to a JSON-safe representation.

If a task needs a row written in the current transaction, enqueue only after commit so a worker
cannot start before the data becomes visible:

```python
from functools import partial
from django.db import transaction

transaction.on_commit(
    partial(process_thing.enqueue, thing_id=thing.pk)
)
```

Also account for rollback: an `on_commit()` callback is discarded when its transaction rolls back,
which prevents work from being queued for data that never committed.

## Use task context

Set `takes_context=True` when the implementation needs execution metadata:

```python
@task(takes_context=True)
def process(context, object_id):
    attempt = context.attempt
    current_result = context.task_result
```

The immutable `TaskContext` is supplied as the first argument. It exposes the current `attempt`
and `task_result`.

## Inspect and retrieve results

Enqueueing returns a snapshot-like `TaskResult`. It does not continuously update in memory.

- Call `refresh()` or `arefresh()` to load the latest state.
- Inspect `status` and `errors` to handle pending, failed, and successful execution.
- Read `return_value` only after the result reports success.
- Use `Task.get_result(id)` for later or cross-request lookup.
- Alternatively use the selected backend's `get_result(id)` when that backend implements result
  retrieval.

Do not assume every backend persists results or supports lookup by ID; branch on documented
backend capabilities.
