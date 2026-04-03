# Lambda Durable Functions (Dec 2025)

Checkpoint-and-replay execution for Lambda. **Must be enabled at function creation time** — cannot be added later. Open-source SDK.

Supports JS/TS (Node.js 22/24) and Python (3.13/3.14).

## Core API

```python
from aws_durable_execution_sdk_python import (
    DurableContext, StepContext, durable_execution, durable_step,
)
from aws_durable_execution_sdk_python.config import Duration, StepConfig, CallbackConfig
from aws_durable_execution_sdk_python.retries import RetryStrategyConfig, create_retry_strategy

@durable_step
def my_step(step_context: StepContext, data: str) -> dict:
    return {"result": data}

@durable_execution
def lambda_handler(event: dict, context: DurableContext) -> dict:
    result = context.step(my_step(event["data"]))
    return result
```

## Wait (Suspend Without Compute Charges)

```python
@durable_execution
def lambda_handler(event: dict, context: DurableContext) -> dict:
    result = context.step(my_step(event["data"]))
    context.wait(Duration.from_minutes(5))  # suspends — no compute charges
    return result
```

## Callbacks for External Approvals

```python
@durable_execution
def lambda_handler(event: dict, context: DurableContext) -> dict:
    callback = context.create_callback(
        name="approval", config=CallbackConfig(timeout=Duration.from_minutes(30))
    )
    approval = callback.result()  # suspends until callback received
    return {"approved": approval}
```

## Key Details

- Built-in idempotency via execution names
- Use Lambda versions for replay consistency
