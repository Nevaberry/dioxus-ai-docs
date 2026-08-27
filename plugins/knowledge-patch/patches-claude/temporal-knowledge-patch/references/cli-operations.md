# Temporal CLI Operations

## Route Cloud commands to the right plane

`temporal cloud login` authenticates the CLI, but ordinary service commands
still need the Cloud gRPC address and fully qualified Namespace:

```bash
temporal workflow list \
  --address <namespace>.<account>.tmprl.cloud:7233 \
  --namespace <namespace>.<account>
```

Use the Temporal Cloud extension's `temporal cloud namespace` commands for
Cloud Namespace administration. `temporal operator namespace` is for the
connected Temporal Service, not the Cloud control plane.

## Pause and resume Schedules

Both Schedule operations use `schedule toggle` and may record a reason:

```bash
temporal schedule toggle \
  --schedule-id hourly-job --pause --reason "maintenance"
temporal schedule toggle \
  --schedule-id hourly-job --unpause --reason "maintenance complete"
```

## Administer remote Clusters

`temporal operator cluster list` lists remote Clusters registered with the
connected Service. Use:

- `describe --detail` for shard and version details;
- `system --frontend-address` to query a remote Server directly;
- `upsert` to register or update a remote Cluster;
- `remove --name` to unregister it.

```bash
temporal operator cluster upsert \
  --frontend-address remote.example:7233 \
  --enable-connection true \
  --enable-replication true
temporal operator cluster remove --name remote-cluster
```

## Configure Namespace replication and archival

Create a replicated Namespace with `--global`, repeatable `--cluster`, and
`--active-cluster`:

```bash
temporal operator namespace create \
  --namespace payments \
  --global \
  --cluster east --cluster west \
  --active-cluster east \
  --retention 5d
```

Promote an existing Namespace with `--promote-global`.
`--replication-state` accepts `normal` or `handover`.

History and Visibility archival each have independent state and URI flags. An
archival URI cannot be changed after that archival mode has been enabled.

## Manage Nexus Endpoints

A Nexus Endpoint has one of two target forms:

- a Worker target, which requires both `--target-namespace` and
  `--target-task-queue`;
- an external URL through the experimental `--target-url`.

`endpoint update` is a partial update: it changes only fields supplied in the
command. Descriptions accept inline Markdown or a Markdown file and can be
cleared with `--unset-description`.

```bash
temporal operator nexus endpoint create \
  --name payments \
  --target-namespace payments \
  --target-task-queue nexus-handlers \
  --description-file DESCRIPTION.md
temporal operator nexus endpoint update \
  --name payments --target-task-queue nexus-v2
```

## Distinguish profiles from environments

The CLI maintains separate configuration selectors:

| Source | File format | Selector | Default location |
| --- | --- | --- | --- |
| `--config-file` | TOML | `--profile` | platform config directory at `temporalio/temporal.toml` |
| `--env-file` | YAML | `--env` (default `default`) | platform config directory at `temporalio/temporal.yaml` |

`--disable-config-file` disables config-file loading.
`--disable-config-env` disables environment-variable loading.

## Configure TLS, metadata, and Codecs

Supplying `--api-key` or any TLS option automatically enables TLS. Use
`--tls=false` only for an explicit plaintext override.

Add gRPC request metadata with repeated `--grpc-meta KEY=VALUE` flags or
`TEMPORAL_GRPC_META_[name]` variables. Configure a remote Codec Server with
`--codec-endpoint`, `--codec-auth`, and repeatable `--codec-header`.

## Produce scriptable output

Global `--output` formats are `text`, `json`, `jsonl`, and `none`.
`--time-format` accepts `relative`, `iso`, and `raw`.

When using JSON output, add `--no-json-shorthand-payloads` to keep raw Payload
representations instead of JSON shorthand.
