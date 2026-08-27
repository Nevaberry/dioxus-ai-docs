# Tasks and Workflows

## Pydantic task conversion

Set `pydantic=True` on a task to convert type-hinted Pydantic arguments before
the task function is invoked and to dump a returned Pydantic model to a
dictionary (`5.5-guide`):

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

Related task options refine conversion behavior:

- `pydantic_strict` enables strict validation;
- `pydantic_context` supplies validation context; and
- `pydantic_dump_kwargs` customizes result serialization.

Keep the function annotations aligned with the actual accepted and returned
models because they drive conversion.

## Optional and generic annotations

Pydantic task type-hint handling recognizes `Optional[...]` and accepts
generic annotations (`5.5.0`). Optional models can pass through as either a
validated model or `None`:

```python
from typing import Optional
from pydantic import BaseModel

class Payload(BaseModel):
    value: int

@app.task(pydantic=True)
def echo(arg: Optional[Payload]) -> Optional[Payload]:
    return arg
```

Do not add manual conversion solely to work around optional or generic type
annotations when the task wrapper can perform it.

## Singleton group unrolling

A one-item `group` chained with `|` unrolls to its contained signature
(`5.5.0`). The downstream task receives the single result rather than a
one-element list:

```python
workflow = group(add.s(1, 1)) | consume.s()  # consume receives 2
```

Downstream tasks should accept the scalar result for the one-item case. Test
both singleton and multi-item groups if workflow cardinality varies at
runtime.

