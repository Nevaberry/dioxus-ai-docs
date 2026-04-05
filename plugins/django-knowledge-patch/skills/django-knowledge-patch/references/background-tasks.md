# Background Tasks Framework

*Since 6.0 (December 2025)*

Built-in framework for defining and enqueueing background tasks. Django handles definition, validation, queuing, and result tracking — actual execution requires external infrastructure (third-party backend + worker).

## Basic Usage

```python
# tasks.py
from django.tasks import task

@task
def send_welcome_email(user_id):
    user = User.objects.get(pk=user_id)
    send_mail("Welcome!", "...", None, [user.email])

# Enqueue
result = send_welcome_email.enqueue(user_id=42)
result.id       # unique ID
result.status   # TaskResultStatus.READY / RUNNING / SUCCESSFUL / FAILED
```

## Configuration

```python
# settings.py
TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.immediate.ImmediateBackend",  # dev/test only
    }
}
```

Built-in backends (dev/test only): `ImmediateBackend` (runs synchronously), `DummyBackend` (no-op, stores results for inspection). Production requires a third-party backend.

## Full API

```python
from django.tasks import task, default_task_backend

# Decorator options
@task(priority=2, queue_name="emails", backend="default", takes_context=True)
def my_task(context, arg1):
    print(f"Attempt {context.attempt}, result ID: {context.task_result.id}")

# Modify before enqueueing (immutable — returns new Task)
my_task.using(priority=10, run_after=timedelta(minutes=5)).enqueue(arg1="hello")

# Retrieve results
result = my_task.get_result(result_id)
result.refresh()            # Update status
result.return_value         # Get return value (raises ValueError if not SUCCESSFUL)
result.errors[0].traceback  # Traceback string on FAILED

# Async variants: aenqueue(), aget_result(), result.arefresh()
```

## Important Notes

- All arguments and return values must be JSON-serializable and survive a `json.dumps()`/`json.loads()` round-trip
- Use `transaction.on_commit()` when enqueueing inside transactions
