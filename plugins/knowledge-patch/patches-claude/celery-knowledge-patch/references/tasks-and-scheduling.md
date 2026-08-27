# Tasks, Workflows, and Scheduling

## Pydantic argument and result conversion

Set `pydantic=True` on a task to convert type-hinted Pydantic arguments before
invocation. If the task returns a type-hinted Pydantic model, Celery dumps it
to a dictionary:

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

Tune conversion with:

- `pydantic_strict` for strict validation.
- `pydantic_context` to provide validation context.
- `pydantic_dump_kwargs` to customize result serialization.

The `5.5.0` handling also recognizes `Optional[...]` and accepts generic
annotations:

```python
from typing import Optional
from pydantic import BaseModel

class Payload(BaseModel):
    value: int

@app.task(pydantic=True)
def echo(arg: Optional[Payload]) -> Optional[Payload]:
    return arg
```

## Named months and crontab parsing

`celery.schedules.crontab` accepts month names:

```python
from celery.schedules import crontab

january_mornings = crontab(month_of_year="jan", hour=9, minute=0)
```

Use `crontab.from_string()` to parse a standard five-field crontab expression:

```python
daily_mornings = crontab.from_string("0 9 * * *")
```

## Singleton group unrolling

When a single-item `group` is chained with `|`, it unrolls to the contained
signature:

```python
workflow = group(add.s(1, 1)) | consume.s()
```

`consume` receives the scalar result `2`, not `[2]`. Design the downstream
task for the unrolled value, especially when a dynamically constructed group
can contain exactly one signature.

## Gevent termination

The gevent concurrency pool implements request and job termination. Revoking
with `terminate=True` can stop a running gevent task:

```python
result = slow_task.delay()
result.revoke(terminate=True)
```

## Hard-timeout rejection

When a task exceeds its hard time limit and
`task_acks_on_failure_or_timeout` is `False`, the worker rejects the task:

```python
task_acks_on_failure_or_timeout = False
```
