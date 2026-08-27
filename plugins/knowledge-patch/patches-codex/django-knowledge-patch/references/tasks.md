# Tasks

## Declare and enqueue tasks

The Tasks API introduced in the 6.0-guide turns a decorated function into an immutable `Task`.
Queue it with `enqueue()` or `aenqueue()`; do not call the decorated object as though it were the
original function.

```python
from django.tasks import task

@task(priority=2, queue_name="emails")
def email_users(user_ids):
    ...

result = email_users.enqueue([1, 2])
```

Configure aliases in `TASKS`, retrieve one through `task_backends[alias]`, and use
`default_task_backend` for the default alias.

```python
TASKS = {
    "default": {"BACKEND": "path.to.backend"},
}
```

## Select an execution backend

- `ImmediateBackend` executes a task synchronously.
- `DummyBackend` records the enqueue operation without executing the task.
- Both built-ins are development and testing facilities. Production execution requires a
  third-party backend and worker.

Backend capabilities vary. Delayed execution, priorities, queues, and stored-result lookup work
only when the selected backend supports them.

## Override task options immutably

`Task.using()` returns a modified copy rather than mutating the task. It can override `priority`,
`backend`, `queue_name`, or `run_after` for an enqueue operation.

Use `aenqueue()` in async code. Preserve the same serialization and transaction rules as for a
synchronous enqueue.

## Pass JSON-round-trippable data

Arguments and return values must survive JSON encoding and decoding. Pass identifiers and simple
data structures rather than model instances, datetimes, or tuples. Reconstruct richer objects
inside the task.

When task work depends on rows changed by the current transaction, defer the enqueue until commit
so a worker cannot race uncommitted state:

```python
from functools import partial
from django.db import transaction

transaction.on_commit(partial(process_thing.enqueue, thing_id=thing.pk))
```

## Use task context

Set `takes_context=True` when the function needs execution metadata. Django passes an immutable
`TaskContext` as the first argument. It exposes the current `attempt` and `task_result`.

```python
@task(takes_context=True)
def process_batch(context, batch_id):
    attempt = context.attempt
    ...
```

Do not attempt to mutate the context or treat it as application payload.

## Observe results

Enqueueing returns a snapshot-like `TaskResult`. Call `refresh()` or `arefresh()` before relying on
later state, inspect `status` and `errors`, and read `return_value` only after successful
completion.

For lookup outside the enqueueing request, call `Task.get_result(id)` or the backend's
`get_result(id)`. Stored lookup is capability-dependent; code must not assume every backend keeps
results.

## Test task code

- Use `ImmediateBackend` when a test needs the task body to run in-process.
- Use `DummyBackend` when asserting enqueue arguments and options independently of execution.
- Test enqueueing inside `transaction.on_commit()` with a transaction-aware test strategy.
- Exercise both sync and async enqueue paths when application code supports both.
- Validate payloads through an actual JSON round trip, including return values.
- Test delayed execution, priority ordering, and result retrieval against the production backend,
  because the core API does not guarantee those capabilities.
