---
name: nomad-knowledge-patch
description: HashiCorp Nomad
version: "2.0.0"
license: MIT
metadata:
  author: Nevaberry
---


# HashiCorp Nomad Knowledge Patch

Use this skill when planning upgrades, editing jobs or agent configuration,
operating servers, integrating APIs, or maintaining plugins. Read the topic
reference that matches the task before proposing a change.

## Reference index

| Reference | Read for |
| --- | --- |
| [CLI, API, and observability](references/cli-api-and-observability.md) | CLI flags, API responses, event streams, metrics, and evaluation diagnostics |
| [Drivers, plugins, and platforms](references/drivers-plugins-and-platforms.md) | External plugins, task drivers, QEMU, execution failures, and platform support |
| [Jobs, scheduling, and deployments](references/jobs-scheduling-and-deployments.md) | Jobspec validation, deployments, services, templates, secrets, and scheduler behavior |
| [Security, identity, and governance](references/security-identity-and-governance.md) | ACLs, OIDC, workload identity, Sentinel, quotas, and licensing |
| [Storage and volumes](references/storage-and-volumes.md) | Dynamic host volumes, CSI visibility, disk accounting, and storage quota schemas |
| [Upgrading and server operations](references/upgrading-and-server-operations.md) | Upgrade order, server joins, Raft migration, health checks, and downgrade constraints |

## Breaking changes and required migrations

### Remove unsupported job and task constructs

- Remove `reschedule` blocks from `system` and `sysbatch` jobs before submitting
  them to Nomad 1.11.0 or later; submission now fails instead of ignoring the
  blocks.
- Rename any task named `alloc`; that name is reserved because it breaks
  inter-task filesystem isolation.
- Replace deprecated task-group disconnect fields with the `disconnect` block.
  The old fields have no effect.
- Do not depend on task-driver remote tasks. That interface has been removed.
- Update custom drivers that reference `DriverNetwork.Hash` before building
  against Nomad 2.0.5; the method is no longer in `plugin/drivers`.

### Migrate allocation authentication

The deprecated token-based allocation authentication workflows for Consul and
Vault have been removed. A task with a `template` block no longer receives an
implicit Consul identity, so jobs must not depend on that side effect. Use the
documented identity and secret mechanisms in
[Security, identity, and governance](references/security-identity-and-governance.md)
and [Jobs, scheduling, and deployments](references/jobs-scheduling-and-deployments.md).

### Update server join configuration

Migrate `server.retry_join`, `server.retry_interval`, `server.retry_max`, and
`server.start_join` to `server.server_join` before Nomad 2.1.0. Unauthenticated
`nomad server join` and Join Agent API use is deprecated in 2.0.4; Nomad 2.1.0
requires a token with `agent:write`.

Run a join against the region leader when adding a node, or against the
authoritative region when federating a region. For a new cluster, prefer
`server_join` with gossip encryption and mTLS.

### Migrate Raft log storage deliberately

Replace the deprecated `raft_boltdb` server parameter with `raft_logstore`.
The following command migrates BoltDB to WAL:

```shell
nomad operator raft migrate-backend
```

The migration cannot be reversed in place. Returning to BoltDB requires a
snapshot taken before migration. Read
[Upgrading and server operations](references/upgrading-and-server-operations.md)
before changing the backend.

### Update API and metrics consumers

- Replace Go API uses of `Node.Resources` and `Node.Reserved`, which are never
  populated, with `Node.NodeResources` and `Node.ReservedResources`.
- Expect `/v1/acl/token/self` to return `200` with an ACL-disabled body when
  ACLs are off and `403` when ACLs are on without a valid token.
- Expect client allocation endpoints to return `404`, rather than `500`, when
  an allocation's node cannot be found.
- Update eval-broker queries: dispatch and periodic job labels now contain the
  parent job ID, and `nomad.nomad.broker.eval_waiting` no longer has `eval_id`.
- Generated check IDs and service rendezvous hashes can change because
  Nomad-native checks, Consul checks, and rendezvous hashing use SHA-256.

## High-value configuration

### Bound server startup work

Nomad 1.10.1 adds `server.start_timeout`, defaulting to `30s`, for setup and
startup work such as keyring decryption. A server logs errors and exits when
the work does not finish in time.

```hcl
server {
  start_timeout = "1m"
}
```

### Opt in to allocation metrics

Starting in 1.10.2, clients do not collect or publish allocation metrics when
`telemetry.publish_allocation_metrics` is unset or false. Enable it explicitly
on clients that must export those metrics.

```hcl
telemetry {
  publish_allocation_metrics = true
}
```

### Limit submitted job size

The `job_max_count` server option defaults to `50000` and limits the sum of a
job's task-group `count` values at submission or scaling time. Changing it does
not affect existing jobs.

```hcl
server {
  job_max_count = 100000
}
```

### Enable more outstanding plan writes

Use the `plan_apply_pipeline` configuration when the leader should have more
outstanding Raft writes while evaluating plans.

## Common new workflows

### Create and use dynamic host volumes

Create host volumes through the CLI or API without restarting clients, then
consume them in stateful deployments with `volume` and `volume_mount` blocks.

```shell
nomad volume create ./internal-plugin.volume.hcl
```

The scheduler tracks availability, but Nomad does not interpret the underlying
storage; a volume may use local or highly available network storage. Read
[Storage and volumes](references/storage-and-volumes.md) for governance and
visibility details.

### Introduce clients with constrained tokens

Create a signed JWT introduction token, pass it to the joining client, and
inspect or renew the identity issued after registration:

```shell
nomad node intro create
nomad agent -client-intro-token <token>
nomad node identity get
nomad node identity renew
```

Introduction tokens can constrain node names, node pools, and TTLs. Servers
enforce the configured introduction policy and issue and rotate a client
identity for RPC authentication alongside mTLS.

### Fetch jobspec secrets

Use a `secret` block to fetch from Nomad, Vault, or a custom secret-provider
plugin, and interpolate a fetched value as `${secret.secret_name.key}`. Task
secrets can also interpolate into service check `Header` and `Args` fields and
service `Tags`.

### Roll out system jobs

`system` jobs support deployments controlled by the job's `update`
configuration, including blue/green and canary strategies. Inspect deployment
status in the web UI or with `nomad deployment` commands.

### Inspect placement decisions

Use `nomad eval status` for related evaluations, placed allocations, plan
annotations, failed placements, and preemptions. Use
`nomad alloc status -verbose` for evaluated and rejected node counts and node
scores. The Go API's `Evaluations.Info` populates `RelatedEvals`.

### Generate structured plans

`nomad job plan` accepts `-json-output` and `-t` for structured output.

```shell
nomad job plan -json-output ./job.nomad
```

## Upgrade execution guardrails

- Upgrade servers one at a time, then clients. Do not use new features until
  every relevant node is upgraded.
- If a client restart exceeds the default `heartbeat_grace` of `10s`, all
  allocations on that node may be rescheduled. Drain old clients when replacing
  them.
- Nomad does not support downgrades. A client downgrade requires draining its
  allocations and removing its data directory; a safe server downgrade
  requires reprovisioning the cluster.
- After each server joins, compare `nomad agent-info` `last_log_index`, check
  `nomad server members`, and proceed only after replication is current.

Read [Upgrading and server operations](references/upgrading-and-server-operations.md)
for federated deployments, leave behavior, Raft protocol 3, license validation,
and single-server recovery details.
