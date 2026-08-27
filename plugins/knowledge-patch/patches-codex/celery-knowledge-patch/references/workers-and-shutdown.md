# Workers and Shutdown

## Soft shutdown before cold shutdown

A worker can enter soft shutdown before cold shutdown, giving active tasks a
bounded interval to finish before cancellation (`5.5-guide`). Configure the
interval in seconds:

```python
worker_soft_shutdown_timeout = 30.0
worker_enable_soft_shutdown_on_idle = True
```

`worker_soft_shutdown_timeout` defaults to `0.0`, so soft shutdown is disabled
until a positive timeout is configured. Idle-worker soft shutdown defaults to
`False`; enable it explicitly with
`worker_enable_soft_shutdown_on_idle`.

This is particularly useful with visibility-timeout brokers such as Redis and
SQS. Coordinate the value with the service manager or container runtime's
termination grace period.

## Remapping SIGTERM

Set the supported `REMAP_SIGTERM` environment variable to make `SIGTERM`
follow the `SIGQUIT` shutdown path (`5.5-guide`):

```bash
export REMAP_SIGTERM="SIGQUIT"
```

This is useful when a container runtime sends TERM by default but the worker
must take the QUIT path. Test the complete stop sequence because the remapping
changes operational signal semantics.

## Gevent task termination

The gevent concurrency pool implements request and job termination (`5.5.0`).
A revoke with `terminate=True` can stop a running gevent task:

```python
result = slow_task.delay()
result.revoke(terminate=True)
```

Forced termination can bypass task cleanup, so reserve it for cases where the
task is safe to interrupt.

## Hard-timeout rejection

When a task exceeds its hard time limit while
`task_acks_on_failure_or_timeout` is `False`, the worker rejects the task
(`5.5.0`):

```python
task_acks_on_failure_or_timeout = False
```

Verify broker redelivery, dead-lettering, and idempotency before relying on
this behavior in production.

## Fork-safe Django connection pools

Celery closes Django psycopg3 connection pools before worker forks
(`5.6-guide`). This prevents inherited pools from causing
`psycopg_pool.PoolTimeout` errors. Application-created pools should follow the
same lifecycle principle: close or avoid them before fork, then initialize
usable connections in the child process.

## Cold-shutdown timeout handling

Workers skip timeout-failure handling during cold shutdown (`5.6-guide`).
Tasks therefore no longer fail with a spurious timeout merely because cold
shutdown is in progress; they can finish or be requeued as appropriate.
Operational tooling should distinguish shutdown interruption from a genuine
task time-limit failure.

