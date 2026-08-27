---
name: celery-knowledge-patch
description: Celery
version: "5.6.0"
license: MIT
metadata:
  author: Nevaberry
---


# Celery Knowledge Patch

Use this skill when upgrading, configuring, operating, or testing Celery and
the work can depend on recent worker, queue, broker, backend, scheduling, or
task behavior.

## How to use this skill

1. Inspect the project's Celery version and its pinned Python, Kombu,
   Billiard, broker-client, web-framework, and backend dependencies.
2. Identify the affected surface: compatibility, brokers and backends, queues
   and publishing, scheduling and testing, tasks and workflows, or workers and
   shutdown.
3. Read the matching reference file before recommending configuration or code.
4. Prefer the project's manifest, lockfile, configuration, code, and observed
   behavior when they disagree with general guidance.
5. Treat settings that change delivery, acknowledgement, shutdown, or schema
   creation semantics as rollout decisions, not mechanical renames.
6. Verify the result with a representative worker and the actual broker or
   result backend when practical.

## Reference index

| Reference | Topics |
| --- | --- |
| [Compatibility and upgrade decisions](references/compatibility.md) | Runtime and dependency floors, support policy, SQS HTTP dependency, Django checks |
| [Brokers and result backends](references/brokers-and-backends.md) | Redis recovery and credentials, Google Cloud Pub/Sub, database tables, DynamoDB, Azure Blob, redaction |
| [Queues and publishing](references/queues-and-publishing.md) | Quorum queues, delayed delivery, auto-created queues, publisher timeouts, ETA memory limits |
| [Scheduling and testing](references/scheduling-and-testing.md) | Crontab parsing and test-worker hostnames |
| [Tasks and workflows](references/tasks-and-workflows.md) | Pydantic conversion and singleton-group unrolling |
| [Workers and shutdown](references/workers-and-shutdown.md) | Soft and cold shutdown, signal remapping, gevent termination, timeout rejection, Django pools |

## Upgrade decisions first

### Check runtime floors before changing behavior

Do not begin an upgrade by copying new settings into an older environment.
First check the Python implementation and version, then Kombu and Billiard.
Also check redis-py, Django, SQLAlchemy, and the SQS transport dependency when
those integrations are present.

The Python floor moves between the relevant release lines. A deployment that
runs on the oldest supported Python in one line may need a Python upgrade
before moving to the next. See
[Compatibility and upgrade decisions](references/compatibility.md) for the
exact matrices.

### Account for the SQS dependency reversal

The SQS transport's HTTP dependency changes direction across these release
lines. Rebuild images and dependency allowlists instead of assuming the prior
replacement remains valid. Confirm that the required native build packages
and runtime library are present before deploying SQS workers.

### Treat the support window as an operating constraint

Do not describe the 5.x line as LTS. Plan migration work with the documented
end of 5.x support in mind, and do not propose Celery 4.x as a supported
fallback.

### Review changed lifecycle semantics

Several settings alter when work is rejected, requeued, allowed to finish, or
cancelled. Before rollout, test hard time limits, cold shutdown, soft
shutdown, idle workers, and the signals sent by the deployment platform.

## High-value configuration

### Bound graceful termination

Use a positive `worker_soft_shutdown_timeout` to give active tasks a bounded
completion interval before cold shutdown. The feature is disabled when the
timeout is zero. If idle workers must also enter soft shutdown, enable
`worker_enable_soft_shutdown_on_idle` explicitly.

This is especially important with visibility-timeout brokers, where abrupt
termination can delay redelivery. Match the timeout to orchestrator grace
periods and task behavior. See
[Workers and shutdown](references/workers-and-shutdown.md).

### Align container signals with intended shutdown

If the runtime sends `SIGTERM` but the desired worker path is the `SIGQUIT`
path, set the supported `REMAP_SIGTERM` environment variable. Document this at
the container or service boundary because it changes the meaning of the
runtime's default stop signal.

### Cap in-memory ETA work when necessary

Set `worker_eta_task_limit` when a worker can receive a large number of ETA or
countdown tasks. The default is unlimited, so the setting only provides
protection after an explicit finite value is chosen. Pair the limit with
monitoring and publisher behavior; see
[Queues and publishing](references/queues-and-publishing.md).

### Choose queue types deliberately

The default task queue remains classic unless configured otherwise. Native
delayed delivery uses quorum queues by default, and workers can detect quorum
queues automatically. Decide separately:

- the default task queue type;
- the delayed-delivery queue type;
- whether worker quorum detection is enabled; and
- the queue and exchange types used for auto-created missing queues.

Read [Queues and publishing](references/queues-and-publishing.md) before
mixing classic, quorum, and auto-created queues.

### Make backend table ownership explicit

The database result backend eagerly creates its tables during setup by
default. Disable `create_tables_at_setup` when migrations or another schema
owner must control table creation. See
[Brokers and result backends](references/brokers-and-backends.md).

## Task authoring quick reference

### Pydantic-aware tasks

Set `pydantic=True` on a task to validate and convert annotated Pydantic input
before invocation and serialize an annotated Pydantic result. Use the
additional task options to select strict validation, provide validation
context, or customize model dumping.

Type annotations remain part of the contract. Account for optional values and
generic annotations rather than inserting manual conversion that duplicates
the task wrapper. Full examples are in
[Tasks and workflows](references/tasks-and-workflows.md).

### Single-item groups in chains

A single-item `group` chained into another signature unrolls to the contained
signature. The next task receives the scalar task result, not a one-element
list. Audit downstream tasks that normalize or index a list solely for this
case.

### Parse standard crontab text directly

Use `crontab.from_string()` for a standard five-field expression. Month names
can be supplied to `crontab` where that improves configuration readability.
Keep validation at configuration boundaries; details are in
[Scheduling and testing](references/scheduling-and-testing.md).

## Broker and backend quick reference

### Redis resilience and identity

Temporary Redis result-backend failures can be classified as safe to retry,
and the broker stack includes improved disconnection recovery. Configure
retry policy deliberately; resilience does not make every exception safe.

For managed Redis authentication, use
`redis_backend_credential_provider`. Use `redis_client_name` to label backend
connections for monitoring. Avoid embedding credentials in diagnostic output
even though delayed-delivery broker URL logging sanitizes passwords.

### Bound publisher I/O

Pass `timeout` and `confirm_timeout` through `apply_async()` when callers need
bounds on broker I/O and publisher-confirm waits. Choose values with broker
latency and retry behavior in mind.

### Select the correct backend connection form

The Google Cloud Pub/Sub broker uses the `gcpubsub` extra and a project URL.
The DynamoDB result backend accepts a remote local-service host rather than
requiring `localhost`. Azure Blob result storage can use managed credentials.
Use the focused examples in
[Brokers and result backends](references/brokers-and-backends.md).

## Worker behavior quick reference

### Terminate gevent tasks intentionally

The gevent pool can terminate running requests and jobs, so a revoke with
`terminate=True` can now stop active work. Treat forced termination as a
last-resort operation because task code may not complete cleanup.

### Validate hard-timeout acknowledgement policy

When `task_acks_on_failure_or_timeout` is false, a task that exceeds its hard
time limit is rejected. Test redelivery and dead-letter behavior with the
actual broker before changing this setting.

### Avoid inherited Django connection pools

Django psycopg3 pools are closed before worker forks to prevent inherited
pools from timing out. If pool errors persist, verify that connection setup
occurs in the correct post-fork lifecycle and inspect application-specific
pool creation.

### Do not infer cold-shutdown timeout failures

Cold shutdown skips timeout-failure handling. During shutdown incidents,
distinguish tasks that complete, are requeued, or are actually timed out; do
not classify every interrupted task as a timeout failure.

## Verification checklist

- Confirm runtime and dependency floors from the deployed environment, not
  only from a developer lockfile.
- Inspect the effective queue declaration and exchange type on the broker.
- Publish a task with the configured timeout and confirm policy.
- Exercise ETA or countdown tasks under the configured memory cap.
- Test soft, cold, and signal-remapped shutdown with active and idle workers.
- Verify hard-timeout rejection and broker redelivery behavior.
- Start workers against each configured result backend and authentication
  mode.
- Run a Pydantic task with valid, invalid, optional, and returned model data.
- Exercise chained groups with both one item and multiple items.
- Run scheduling and worker-hostname tests through the project's actual test
  fixtures.
