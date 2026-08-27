# Brokers, Queues, and Publishing

## RabbitMQ quorum queues and delayed delivery

The default task queue remains a `classic` queue. To opt the default task
queue into quorum semantics:

```python
task_default_queue_type = "quorum"
```

Quorum queues support ETA tasks. Workers detect quorum queues by default and
automatically enable native delayed delivery. Native delayed delivery itself
defaults to quorum queues:

```python
broker_native_delayed_delivery_queue_type = "quorum"
worker_detect_quorum_queues = True
```

These settings are part of the `5.5-guide` behavior. Keep queue declarations,
broker policies, and worker settings aligned.

## Auto-created queue and exchange types

Choose the type Celery uses when it creates a missing queue:

```python
task_create_missing_queue_type = "quorum"
```

Supported choices include `quorum` and `classic`. Configure
`task_create_missing_queue_exchange_type` when auto-created queues need a
specific exchange type as well.

## ETA task memory limits

`worker_eta_task_limit` caps how many ETA or countdown tasks a worker holds in
memory:

```python
worker_eta_task_limit = 1000
```

The default is `None`, meaning unlimited. Select a finite value when producers
can deliver large backlogs of future tasks.

## Redis broker recovery

Kombu 5.5 resolves long-standing Redis broker disconnections.

## Google Cloud Pub/Sub

Install the Google Cloud Pub/Sub transport through the `gcpubsub` extra:

```console
pip install "celery[gcpubsub]"
```

Configure the project in the broker URL:

```python
broker_url = "gcpubsub://projects/project-id"
```

## SQS dependency reversal

Celery 5.5 moved from `pycurl` to `urllib3`. In the `5.6-guide`, the SQS
transport reverses that migration and uses `pycurl` again. Celery 5.6 SQS
deployments must therefore provide the restored `pycurl` dependency.

## Publisher timeouts

Task publishing forwards `timeout` and `confirm_timeout` to
`Producer.publish()`. Bound both broker I/O and publisher-confirm waiting when
required:

```python
task.apply_async(timeout=10, confirm_timeout=5)
```

This behavior was fixed in `5.5.0`; do not assume either option is only a task
execution timeout.

## Broker URL redaction

The delayed-delivery mechanism sanitizes passwords in broker URLs in all log
output rather than exposing them in plaintext.
