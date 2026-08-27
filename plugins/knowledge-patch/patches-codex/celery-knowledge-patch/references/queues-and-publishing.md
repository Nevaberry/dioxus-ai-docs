# Queues and Publishing

## RabbitMQ quorum queues and delayed delivery

Quorum queues support ETA tasks in the `5.5-guide` line. When a worker detects
quorum queues, it enables native delayed delivery automatically.

The ordinary default task queue remains `classic`. Native delayed delivery
defaults to `quorum`, and worker detection is enabled. Configure the queue
type explicitly when the application should use quorum for its default task
queue:

```python
task_default_queue_type = "quorum"
broker_native_delayed_delivery_queue_type = "quorum"
worker_detect_quorum_queues = True
```

These settings control distinct decisions. Do not assume that the delayed
delivery default also changes the default task queue.

## Auto-created queue and exchange types

`task_create_missing_queue_type` selects the queue type Celery uses when it
creates a missing queue (`5.6-guide`). For example:

```python
task_create_missing_queue_type = "quorum"
```

`task_create_missing_queue_exchange_type` independently selects the exchange
type for that auto-created queue. Specify both where topology policy requires
a consistent queue and exchange declaration; otherwise verify the effective
broker topology after startup.

## ETA task memory cap

`worker_eta_task_limit` caps the number of ETA or countdown tasks retained in
a worker's memory (`5.6-guide`):

```python
worker_eta_task_limit = 1000
```

Its default is `None`, which means unlimited. Choose a finite cap when a large
scheduled backlog could exhaust worker memory. Observe publisher pressure and
task admission when testing the cap rather than treating it as a broker-side
queue limit.

## Publisher timeout forwarding

Task publishing forwards `timeout` and `confirm_timeout` to
`Producer.publish()` (`5.5.0`). Callers can bound broker I/O and the wait for
publisher confirms:

```python
task.apply_async(timeout=10, confirm_timeout=5)
```

The two values serve different waits. Select them using the broker's expected
latency and the application's retry or failure-handling policy.

