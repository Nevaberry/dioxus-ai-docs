# Runtime and Worker Lifecycle

## Runtime and dependency requirements

The `5.5-guide` runtime matrix supports CPython 3.8 through 3.13 and PyPy
3.10+. Its dependency minimums are:

- Kombu 5.5
- redis-py 4.5.2
- Billiard 4.2.1
- Django 2.2.28

Celery 5.5 supports both SQLAlchemy 1.4 and 2.0. Django integrations can pass
`--skip-checks` to bypass Django core checks.

Celery 5.5 replaces the `pycurl` dependency with `urllib3`. This does not
describe the later SQS-specific reversal; see
[brokers-and-queues.md](brokers-and-queues.md).

The `5.6-guide` runtime matrix supports CPython 3.9 through 3.13 and PyPy 3.11.
Its new minimums are Kombu 5.6 and Billiard 4.2.4.

Celery 4.x is no longer supported. Celery 5.x is not an LTS release and is
supported only until Celery 6.x.

## Soft shutdown

A worker can enter soft shutdown before cold shutdown. This gives active tasks
a bounded interval to finish before cancellation. Configure the interval with:

```python
worker_soft_shutdown_timeout = 30.0
```

The default is `0.0`, which disables soft shutdown. Soft shutdown on an idle
worker is separately controlled by:

```python
worker_enable_soft_shutdown_on_idle = True
```

Its default is `False`. Enabling it is particularly useful with
visibility-timeout brokers such as Redis and SQS.

## Cold shutdown

During cold shutdown, workers skip timeout-failure handling. A task is no
longer failed with a spurious timeout during this path and can instead
complete or be requeued correctly.

## Signal remapping

`REMAP_SIGTERM` can make `SIGTERM` follow the `SIGQUIT` shutdown path:

```bash
export REMAP_SIGTERM="SIGQUIT"
```

Use this when the desired shutdown behavior is tied to `SIGQUIT` but an
orchestrator or container runtime sends `SIGTERM`.

## Fork-safe Django pools

Before worker forks, Celery closes Django psycopg3 connection pools. This
prevents child processes from inheriting pools and later producing
`psycopg_pool.PoolTimeout` errors.

## Test-worker identity

Workers started by `celery.contrib.pytest` or
`celery.contrib.testing.worker` accept a custom hostname. With the pytest
integration:

```python
@pytest.fixture
def celery_worker_parameters():
    return {"hostname": "test-worker@localhost"}
```
