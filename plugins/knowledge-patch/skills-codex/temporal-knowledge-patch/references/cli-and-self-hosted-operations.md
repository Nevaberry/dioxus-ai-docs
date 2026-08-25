# CLI and Self-Hosted Operations

## Cloud login and service routing

`temporal cloud login` authenticates the CLI, but service commands must still
target the Cloud gRPC address and fully qualified Namespace:

```bash
temporal workflow list \
  --address <namespace>.<account>.tmprl.cloud:7233 \
  --namespace <namespace>.<account>
```

Use the Temporal Cloud extension's `temporal cloud namespace` commands for
Cloud Namespace administration. `temporal operator namespace` is for service
operator workflows, not Cloud Namespace administration.

## Pause and resume Schedules

Use `schedule toggle` for both operations. Record an operational reason when
useful:

```bash
temporal schedule toggle \
  --schedule-id hourly-job --pause --reason "maintenance"

temporal schedule toggle \
  --schedule-id hourly-job --unpause --reason "maintenance complete"
```

## Administer remote Clusters

`temporal operator cluster list` shows remote Clusters registered with the
connected Service.

- `describe --detail` shows shard and version details.
- `system --frontend-address` queries a remote Server directly.
- `upsert` registers or updates a remote Cluster.
- `remove` unregisters a remote Cluster by name.

```bash
temporal operator cluster upsert \
  --frontend-address remote.example:7233 \
  --enable-connection true \
  --enable-replication true

temporal operator cluster remove --name remote-cluster
```

## Replicated Namespaces

Create a replicated Namespace with `--global`, one or more repeatable
`--cluster` flags, and `--active-cluster`:

```bash
temporal operator namespace create \
  --namespace payments \
  --global \
  --cluster east \
  --cluster west \
  --active-cluster east \
  --retention 5d
```

Promote an existing Namespace with `--promote-global`.
`--replication-state` accepts `normal` or `handover`.

History archival and Visibility archival each have independent state and URI
flags. Once an archival mode has been enabled, its archival URI cannot be
changed.

## Nexus Endpoint targets

A Nexus Endpoint targets either:

- a Worker, which requires both `--target-namespace` and
  `--target-task-queue`; or
- an external URL through the experimental `--target-url`.

Descriptions accept inline Markdown or a Markdown file and can be cleared with
`--unset-description`.

```bash
temporal operator nexus endpoint create \
  --name payments \
  --target-namespace payments \
  --target-task-queue nexus-handlers \
  --description-file DESCRIPTION.md

temporal operator nexus endpoint update \
  --name payments \
  --target-task-queue nexus-v2
```

`endpoint update` patches only fields supplied in the command; it does not
replace the whole Endpoint.

## Configuration files, environments, and profiles

The CLI has two distinct selectors:

| Settings source | File format | File flag | Selector |
| --- | --- | --- | --- |
| Configuration profiles | TOML | `--config-file` | `--profile` |
| Environment settings | YAML | `--env-file` | `--env` |

The default profile environment is `default`. Default files are:

```text
<platform-config-directory>/temporalio/temporal.toml
<platform-config-directory>/temporalio/temporal.yaml
```

Use `--disable-config-file` to disable config-file loading and
`--disable-config-env` to disable environment-variable loading.

## TLS and request metadata

Supplying `--api-key` or any TLS option automatically enables TLS. Use
`--tls=false` only for an intentional plaintext override.

Add gRPC request metadata with repeatable:

```text
--grpc-meta KEY=VALUE
```

or environment variables named:

```text
TEMPORAL_GRPC_META_[name]
```

Configure a remote Codec Server with `--codec-endpoint`, `--codec-auth`, and
repeatable `--codec-header` flags.

## Scriptable output

The global `--output` formats are:

- `text`
- `json`
- `jsonl`
- `none`

`--time-format` accepts `relative`, `iso`, or `raw`. With JSON output,
`--no-json-shorthand-payloads` retains raw Payload representations rather than
using JSON shorthand.
