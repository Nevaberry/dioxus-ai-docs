---
name: nomad-knowledge-patch
description: HashiCorp Nomad
version: 2.0.0
license: MIT
metadata:
  author: Nevaberry
---



# HashiCorp Nomad Knowledge Patch

Use this skill when creating, reviewing, upgrading, or troubleshooting Nomad
agents, jobs, plugins, integrations, API clients, or operational automation.
Check breaking changes first, then open the reference matching the task.

## Index

| Reference | Topics |
|---|---|
| [Identity and policy](references/identity-and-policy.md) | Client introduction, ACL responses, OIDC, workload identity, secrets, Sentinel, quotas, join authorization, licensing |
| [Jobs and scheduling](references/jobs-and-scheduling.md) | Validation, allocation limits, deployments, updates, plan output, evaluation diagnostics, templates, networking |
| [Operations and observability](references/operations-and-observability.md) | Startup timeout, telemetry, metric labels, CLI hints, node APIs, event streams, hashes, endpoint responses |
| [Storage, drivers, and plugins](references/storage-drivers-and-plugins.md) | Dynamic host volumes, disk capacity, plugin registration, task drivers, QEMU, driver APIs, architectures |
| [Upgrades and Raft](references/upgrades-and-raft.md) | Upgrade order, downgrade constraints, server cycling, WAL migration, Raft protocol, server joins |

## Breaking changes first

### Remove invalid or ignored job fields

- Remove `reschedule` blocks from `system` and `sysbatch` jobs; submission now
  fails instead of ignoring them.
- Rename tasks called `alloc`; that name is reserved for filesystem isolation.
- Replace deprecated task-group disconnect fields with the `disconnect` block.
- Never generate a negative `resources.cores` value.

### Migrate allocation authentication

Token-based Consul and Vault allocation authentication is removed. Declare
workload identities explicitly. Do not expect a task with a `template` block to
receive a Consul identity implicitly.

### Audit custom task drivers and plugins

- Remote task-driver support is removed.
- `DriverNetwork.Hash` is removed from `plugin/drivers`.
- An executable in `plugin_dir` is skipped unless a matching `plugin`
  configuration block exists.

### Update quota integrations

Replace `variables_limit` and `QuotaSpec.VariablesLimit` with
`region_limit.storage.variables` and
`QuotaSpec.RegionLimit.Storage.Variables`. Update Go code for the
`QuotaSpec.RegionLimit` type change from `Resources` to `QuotaResources`.

### Prepare authenticated joins

Unauthenticated `nomad server join` and Join Agent API use is deprecated in
2.0.4. Nomad 2.1.0 requires an `agent:write` token. Also migrate the legacy
`server.retry_join`, `server.retry_interval`, `server.retry_max`, and
`server.start_join` settings to `server.server_join`.

### Treat Raft WAL migration as one-way

Use `raft_logstore` instead of deprecated `raft_boltdb`. Before running the WAL
migration, take a snapshot that can restore BoltDB; the migration cannot be
reversed in place.

```shell
nomad operator raft migrate-backend
```

## Upgrade safety quick reference

### Order and compatibility

1. Upgrade servers one at a time.
2. Confirm replication after every server rejoins.
3. Upgrade clients only after servers are healthy.
4. Wait to use new features until every relevant node is upgraded.

Nomad does not support downgrades. A client downgrade requires draining its
allocations and removing its data directory; a safe server downgrade requires
reprovisioning the cluster.

### Validate each server

After a server rejoins, compare `last_log_index` in `nomad agent-info`, inspect
`nomad server members`, and continue only when replication is current. Upgrade a
Raft protocol 3 leader last.

Do not accidentally trigger `leave_on_terminate` or `leave_on_interrupt` during
an in-place upgrade. Choose the shutdown signal to match the agent configuration.

### Protect client allocations

A client restart exceeding `heartbeat_grace` can reschedule all allocations on
that node. The default grace is `10s`. Drain old clients when replacing them.

## Job and scheduling quick reference

### Limit job scale

`job_max_count` defaults to `50000` and limits the sum of task-group counts at job
submission or scaling time. Changing it does not affect existing jobs.

```hcl
server {
  job_max_count = 100000
}
```

### Roll out system jobs

System jobs support controlled deployments through their `update` configuration,
including canary and blue/green strategies. Inspect them with the web UI or
`nomad deployment` commands.

For service and batch jobs, changing a task group to `count = 0` stops all of its
non-terminal allocations as if the group were removed.

### Preserve resources and inspect plans

Use `-preserve-resources` during a job update to retain the existing resource
block. Use structured plan output for automation:

```shell
nomad job plan -json-output ./job.nomad
```

`nomad job plan` also accepts `-t`. Allocation `exec`, `logs`, and `fs` commands
accept `-group` for explicit group targeting.

## Identity and secrets quick reference

### Introduce clients with constrained tokens

Generate a signed introduction token with `nomad node intro create`, pass it with
`nomad agent -client-intro-token`, and inspect or renew the resulting identity
with `nomad node identity get` or `nomad node identity renew`. Token constraints
can cover node names, node pools, and TTLs.

### Use private-key OIDC assertions

OIDC auth methods can use private-key JWT assertions instead of a client secret.
Enable PKCE with `OIDCEnablePKCE: true` and confirm the provider supports and, if
necessary, enables PKCE.

### Fetch jobspec secrets

Use a `secret` block to fetch from Nomad, Vault, or a custom provider, then
interpolate `${secret.secret_name.key}`. Secret values can also interpolate into
service check `Header` and `Args` fields and service `Tags`.

## Storage and driver quick reference

### Create dynamic host volumes

```shell
nomad volume create ./volume.hcl
```

Consume them with `volume` and `volume_mount` blocks. Nomad schedules around
availability but does not understand whether the underlying storage is local or
highly available. Match the storage design to the workload's failure model.

### Reserve host disk explicitly

Scheduling capacity is calculated as `totalBytes - client.reserved.disk`, not
from current free disk space. Reserve at least the space used by the host OS; do
not depend on the removed `unique.storage.bytesfree` attribute.

### Check QEMU jobs

QEMU supports `emulator` and `machine_type`, defaulting to
`qemu-system-x86_64` and `pc`. Filesystem environment variables expose host paths,
not paths such as `/alloc` or `/local`. A custom `-smp` flag takes precedence over
the value derived from `resources.cores`.

## Operations quick reference

### Make allocation telemetry explicit

Clients do not collect or publish allocation metrics unless
`telemetry.publish_allocation_metrics` is true.

```hcl
telemetry {
  publish_allocation_metrics = true
}
```

### Bound server startup

`server.start_timeout` defaults to `30s` and covers setup work such as keyring
decryption. A server logs errors and exits if that work misses the deadline.

```hcl
server {
  start_timeout = "1m"
}
```

### Update evaluation dashboards

Dispatch and periodic evaluation broker metrics use the parent job ID in their
`job` label. `nomad.nomad.broker.eval_waiting` no longer supplies `eval_id`.
Revise alerts and queries that depend on the former labels.

### Handle response changes

- `/v1/acl/token/self` returns `200` when ACLs are disabled and `403` when ACLs
  are enabled without a valid token; do not expect `404` for those cases.
- A client allocation endpoint returns `404`, not `500`, if the allocation's node
  is missing.
- Executor setup failures in `exec`, `raw_exec`, `java`, and `qemu` report exit
  code `-1`.

## Configuration and API checks

- Keep `num_schedulers` between zero and the machine's available CPU count.
- Use `Node.NodeResources` and `Node.ReservedResources`; deprecated
  `Node.Resources` and `Node.Reserved` are never populated.
- Correct duplicate or invalid ACL policy keys before writing a policy.
- Expect SHA-256-derived service check IDs and rendezvous hashes to differ after
  an upgrade.
- Treat the secrets plugin execution timeout as 60 seconds.

Open the relevant reference before changing production configuration, upgrade
automation, plugin code, observability rules, or stateful job behavior.
