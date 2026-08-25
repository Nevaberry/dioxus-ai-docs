---
name: celery-knowledge-patch
description: Celery
version: 5.6.0
license: MIT
metadata:
  author: Nevaberry
---


# Celery Knowledge Patch

Load this skill when maintaining Celery applications, workers, brokers, result
backends, schedules, or task workflows. Start with the quick reference, then
open the topic file that matches the work at hand.

## Reference index

| Reference | Topics |
| --- | --- |
| [runtime-and-lifecycle.md](references/runtime-and-lifecycle.md) | Runtime and dependency requirements, support policy, worker shutdown, signals, pools, and testing |
| [brokers-and-queues.md](references/brokers-and-queues.md) | RabbitMQ quorum queues, Redis, SQS, Google Cloud Pub/Sub, publishing, ETA limits, and queue creation |
| [tasks-and-scheduling.md](references/tasks-and-scheduling.md) | Pydantic tasks, crontab parsing, canvas behavior, timeouts, and gevent revocation |
| [result-backends.md](references/result-backends.md) | Database, Redis, DynamoDB, and Azure Blob Storage result backends |

## Check compatibility before upgrading

### Runtime requirements changed

- For 5.5, use CPython 3.8–3.13 or PyPy 3.10+, Kombu 5.5 or newer,
  redis-py 4.5.2 or newer, Billiard 4.2.1 or newer, and Django 2.2.28
  or newer.
- For 5.6, use CPython 3.9–3.13 or PyPy 3.11, Kombu 5.6 or newer,
  and Billiard 4.2.4 or newer.
- SQLAlchemy 1.4 and 2.0 are supported.
- Celery 4.x is unsupported. Celery 5.x is not an LTS line and is supported
  only until Celery 6.x.

See [runtime-and-lifecycle.md](references/runtime-and-lifecycle.md) before
changing Python, framework, or transport dependencies.

### SQS uses `pycurl` again

Celery 5.5 replaced the `pycurl` dependency with `urllib3`, but the 5.6 SQS
transport reverses that change and uses `pycurl` again. Ensure 5.6 SQS worker
images and deployment environments provide the restored dependency.

### Singleton groups unroll

A one-item `group` chained with `|` unrolls to its contained signature. The
downstream task receives the item result, not a one-element list:

```python
workflow = group(add.s(1, 1)) | consume.s()
```

Here, `consume` receives `2`. Audit downstream tasks that assumed a list.

### Hard timeouts can reject tasks

If a task exceeds its hard time limit while
`task_acks_on_failure_or_timeout` is `False`, the worker rejects it:

```python
task_acks_on_failure_or_timeout = False
```

## Configure queues and delayed tasks

### Use quorum queues deliberately

The default task queue type remains `classic`. To make the default task queue
a quorum queue, configure:

```python
task_default_queue_type = "quorum"
```

Quorum queues support ETA tasks. Workers detect them by default and
automatically enable native delayed delivery. The delayed-delivery queue type
defaults to `quorum`:

```python
broker_native_delayed_delivery_queue_type = "quorum"
worker_detect_quorum_queues = True
```

For queues Celery creates on demand, choose their queue type separately:

```python
task_create_missing_queue_type = "quorum"
```

Use `task_create_missing_queue_exchange_type` when the auto-created queue also
needs an explicit exchange type.

### Cap in-memory ETA tasks

Workers otherwise hold an unlimited number of ETA and countdown tasks in
memory. Set a cap for workloads that can accumulate many scheduled messages:

```python
worker_eta_task_limit = 1000
```

See [brokers-and-queues.md](references/brokers-and-queues.md) for transport,
publishing, and credential details.

## Make shutdown behavior explicit

### Allow a soft-shutdown interval

Soft shutdown gives active tasks a bounded interval to finish before cold
shutdown cancels them. It is disabled by default because its timeout is `0.0`:

```python
worker_soft_shutdown_timeout = 30.0
worker_enable_soft_shutdown_on_idle = True
```

Idle-worker soft shutdown defaults to `False`. Enabling both settings is
especially useful with visibility-timeout brokers such as Redis and SQS.

### Remap container termination

To make `SIGTERM` follow the `SIGQUIT` shutdown path, set:

```bash
export REMAP_SIGTERM="SIGQUIT"
```

This is useful when a container runtime sends `SIGTERM` by default. During
cold shutdown, workers skip timeout-failure handling so tasks are not marked
with spurious timeout failures and can complete or be requeued correctly.

## Use typed Pydantic tasks

Set `pydantic=True` on a task to convert type-hinted Pydantic arguments before
the task runs and dump a returned Pydantic model to a dictionary:

```python
from celery import Celery
from pydantic import BaseModel

app = Celery("tasks")

class Input(BaseModel):
    value: int

@app.task(pydantic=True)
def double(arg: Input) -> Input:
    return Input(value=arg.value * 2)
```

Optional and generic annotations are recognized. Use:

- `pydantic_strict` for strict validation.
- `pydantic_context` to pass validation context.
- `pydantic_dump_kwargs` to customize result serialization.

See [tasks-and-scheduling.md](references/tasks-and-scheduling.md) for optional
models, crontab parsing, publishing timeouts, and task termination.

## Choose backend initialization and credentials

The database result backend creates its tables during backend initialization
because `create_tables_at_setup` defaults to `True`. Set it to `False` to keep
lazy first-use creation when another system manages the schema.

Redis result backends support provider-based authentication through
`redis_backend_credential_provider`, including AWS ElastiCache IAM
authentication. Set `redis_client_name` to label backend connections for
Redis monitoring.

See [result-backends.md](references/result-backends.md) for Redis recovery,
remote local-DynamoDB endpoints, and Azure managed credentials.
