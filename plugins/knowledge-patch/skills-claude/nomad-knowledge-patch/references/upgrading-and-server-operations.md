# Upgrading and Server Operations

## Upgrade planning

### Version skew and feature use

Nomad aims to remain backward compatible across at least two point releases,
such as 1.7.x with 1.5.x. Do not use new features until every relevant node is
upgraded.

Nomad versions before 1.10.0 are no longer supported.

### No supported downgrade path

Nomad does not support downgrades. Downgrading a client requires draining its
allocations and removing its data directory. Safely downgrading servers
requires reprovisioning the cluster.

### Upgrade order and restart window

Upgrade servers one at a time before clients. If a client restart exceeds
`heartbeat_grace`, which defaults to `10s`, all allocations on that node may be
rescheduled. Drain old clients when replacing them instead of upgrading them in
place.

In a federated deployment, new features are not guaranteed until every agent in
the region and the authoritative region's servers are upgraded.

## Server restart and health checks

### Startup timeout

In the `1.10-upgrade` guidance, Nomad 1.10.1 adds `server.start_timeout`, which
defaults to `30s`, for setup and startup work such as keyring decryption. If the
work does not finish in time, the server logs errors and exits.

```hcl
server {
  start_timeout = "1m"
}
```

### Leave behavior

For an in-place upgrade, choose a shutdown signal that does not trigger the
configured `leave_on_terminate` or `leave_on_interrupt`. For example, with
`leave_on_terminate` enabled, use `SIGINT` rather than `SIGTERM`.

After each server joins, compare its `nomad agent-info` `last_log_index` with
the other servers, check membership with `nomad server members`, and proceed
only when replication is current.

When replacing a server, stop it and confirm it is `left`, or remove it with:

```shell
nomad server force-leave <server-id>
```

## Server joins

### Authenticated joins

In the `2.0-upgrade` guidance, unauthenticated `nomad server join` and Join
Agent API use is deprecated in 2.0.4. Nomad 2.1.0 requires a token with
`agent:write`.

Run the command against the region leader when adding a node, or against the
authoritative region when federating a region. For a new cluster, prefer
`server_join` with gossip encryption and mTLS.

### Legacy join parameters

The deprecated `server.retry_join`, `server.retry_interval`,
`server.retry_max`, and `server.start_join` parameters will be removed in
Nomad 2.1.0. Migrate them to `server.server_join` before upgrading.

## Raft log store

### Configuration and migration

Nomad 2.0.0 deprecates `raft_boltdb`; use `raft_logstore` instead. The
`nomad operator raft migrate-backend` command migrates the Raft log store from
BoltDB to WAL.

```shell
nomad operator raft migrate-backend
```

The migration cannot be reversed in place. Returning to BoltDB requires
restoring a snapshot taken before migration.

The `/v1/agent/self` response includes Raft log store details, and the WAL
backend exposes Raft log store metrics.

## Raft protocol 3

### Multi-server production migration

Raft protocol 3 requires Nomad 0.8.0 or later on every server. Once every
server uses protocol 3, servers using an older protocol cannot join because
quorum membership identifies servers by node ID rather than IP address. The
outage-recovery `peers.json` format also changes.

For a cluster with at least three servers, stop and force-leave one server at a
time, restart it with protocol 3, then verify `RaftProtocol` with
`nomad operator raft list-peers` and replication through `nomad agent-info`.
Leave the leader until last.

Set `raft_protocol = 3` explicitly only when upgrading to a Nomad version
earlier than 1.3.0.

```hcl
server {
  raft_protocol = 3
}
```

### Single-server migration

A single server cannot elect itself after an in-place protocol 3 restart unless
a new-format `server/raft/peers.json` is written before restarting. Build it
from the configured data directory, current leader address, and server node ID:

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

## Enterprise upgrade checks

Before upgrading servers to Nomad Enterprise 1.6.0 or later, validate the
Enterprise license with `nomad license inspect` from the target Nomad binary.
