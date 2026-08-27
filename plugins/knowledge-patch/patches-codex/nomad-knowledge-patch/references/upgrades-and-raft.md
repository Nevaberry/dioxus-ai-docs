# Upgrades and Raft

## Upgrade invariants

Nomad aims for backward compatibility across at least two point releases, such as
1.7.x with 1.5.x, but does not support downgrades (upgrade-procedure). Do not use
new features until every relevant node is upgraded.

To downgrade a client, drain its allocations and remove its data directory.
Safely downgrading servers requires reprovisioning the cluster.

Versions before 1.10.0 are outside the support floor established in batch 1.10.0.

## Upgrade servers before clients

Upgrade servers one at a time, then upgrade clients. A client restart longer than
`heartbeat_grace`—`10s` by default—can cause every allocation on that node to be
rescheduled. When replacing old clients, drain them instead of upgrading in
place.

In a federated deployment, new features are not guaranteed until every agent in
the region and the authoritative region's servers are upgraded.

## Safely cycle servers

For an in-place server upgrade, use a shutdown signal that does not trigger the
configured `leave_on_terminate` or `leave_on_interrupt`. For example, with
`leave_on_terminate` enabled, use `SIGINT`, not `SIGTERM`.

After each server rejoins:

1. Compare its `nomad agent-info` `last_log_index` with the other servers.
2. Check membership with `nomad server members`.
3. Proceed only when replication is current.

When replacing a server, stop it and confirm it is `left`, or remove it with:

```shell
nomad server force-leave <server-id>
```

## Raft log store migration

The server `raft_boltdb` parameter is deprecated in 2.0.0; use `raft_logstore`
(batch 2.0-upgrade). Migrate from BoltDB to WAL with:

```shell
nomad operator raft migrate-backend
```

The migration is not reversible in place. Returning to BoltDB requires a snapshot
taken before migration. The `/v1/agent/self` response includes Raft log store
details, and the WAL backend exposes Raft log store metrics.

## Raft protocol 3 on a cluster

Raft protocol 3 requires Nomad 0.8.0 or later on every server. After all servers
use it, an older-protocol server cannot join because quorum membership identifies
servers by node ID rather than IP address. The outage-recovery `peers.json` format
also changes.

For a cluster with at least three servers, stop and force-leave one server at a
time, restart it with protocol 3, and verify `RaftProtocol` with
`nomad operator raft list-peers` plus replication with `nomad agent-info`. Upgrade
the leader last. Set `raft_protocol = 3` explicitly only when upgrading to a
version earlier than 1.3.0.

```hcl
server {
  raft_protocol = 3
}
```

## Raft protocol 3 on one server

A single server cannot elect itself after an in-place protocol 3 restart unless a
new-format `server/raft/peers.json` is written before the restart. Derive the data
directory, leader address, and node ID, then write:

```shell
NOMAD_DATA_DIR=$(nomad agent-info -json | jq -r '.config.DataDir')
NOMAD_ADDR=$(nomad agent-info -json | jq -r '.stats.nomad.leader_addr')
NODE_ID=$(cat "$NOMAD_DATA_DIR/server/node-id")

cat >"$NOMAD_DATA_DIR/server/raft/peers.json" <<EOF
[
  {
    "id": "$NODE_ID",
    "address": "$NOMAD_ADDR",
    "non_voter": false
  }
]
EOF
```

## Server join configuration migration

The deprecated `server.retry_join`, `server.retry_interval`,
`server.retry_max`, and `server.start_join` parameters are removed in 2.1.0.
Migrate them to `server.server_join` before that upgrade (batch 2.0-upgrade).

Unauthenticated CLI and API server joins are also deprecated in 2.0.4 and require
an `agent:write` token in 2.1.0. See the identity and policy reference for leader,
federation, and new-cluster guidance.

## Removed and ignored job behavior

Deprecated task-group disconnect fields have no effect in 1.10.0. Replace them
with the `disconnect` block introduced in 1.8.

Token-based Consul and Vault allocation authentication and the remote task-driver
interface are removed in 1.10.0. Migrate identities and custom drivers before the
upgrade. Quota variable fields and related Go API types also require the migration
documented in the identity and policy reference.
