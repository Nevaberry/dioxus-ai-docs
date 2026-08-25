# Tasks

Load this reference when declaring tasks, selecting execution backends, enqueueing
work, or inspecting results.

## Declare and enqueue work (`6.0-guide`)

`@django.tasks.task` returns an immutable `Task`. Calling the decorated object
does not enqueue work; use `enqueue()` or `aenqueue()`.

```python
from django.tasks import task

@task(priority=2, queue_name="emails")
def email_users(user_ids):
    ...

result = email_users.enqueue([1, 2])
```

Configure aliases with `TASKS`. Retrieve a configured backend with
`task_backends[alias]` or use `default_task_backend`.

```python
TASKS = {
    "default": {
        "BACKEND": "path.to.backend",
    },
}
```

## Choose a real execution backend (`6.0-guide`)

`ImmediateBackend` executes synchronously. `DummyBackend` records enqueue
operations without executing them. Both are intended for development and tests;
production needs a third-party backend and worker.

Backend capabilities vary. Delayed execution, priorities, and result lookup must
not be assumed unless the selected backend advertises them.

## Override task options immutably (`6.0-guide`)

`Task.using()` returns a modified copy. It can choose `priority`, `backend`,
`queue_name`, or `run_after` without mutating the declared task.

## Serialize arguments and results safely (`6.0-guide`)

Arguments and return values must survive a JSON encode/decode round trip. Pass
identifiers and simple JSON values rather than model instances, datetimes, or
tuples.

If a worker needs rows changed in the current transaction, enqueue only after
commit so it cannot observe uncommitted state:

```python
from functools import partial
from django.db import transaction

transaction.on_commit(partial(process_thing.enqueue, thing_id=thing.pk))
```

## Read context and results (`6.0-guide`)

With `@task(takes_context=True)`, the first function argument is an immutable
`TaskContext` exposing `attempt` and `task_result`.

Enqueueing returns a snapshot-like `TaskResult`. Call `refresh()` or
`arefresh()` before reading current state, inspect `status` and `errors`, and
read `return_value` only after successful completion.

For cross-request lookup, use `Task.get_result(id)` or the backend's
`get_result(id)` when supported.
