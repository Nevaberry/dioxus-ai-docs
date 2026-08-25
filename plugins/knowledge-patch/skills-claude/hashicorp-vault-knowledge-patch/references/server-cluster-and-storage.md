# Server, Cluster, and Storage

## Cluster health and removed nodes

### Health and seal-status fields

`sys/health` reports whether the node was removed and whether a standby can
heartbeat the active node. Default failure codes are 530 for removed and 474
for unhealthy HA, configurable through `removedcode` and `haunhealthycode`.
`sys/seal-status` and `vault status` include `removed_from_cluster`; seal status
also includes `migration_done_at_epoch`. (`1.19-changelog`)

### Removed Raft data

`sys/storage/raft/join` rejects a removed node that still has integrated-storage
data. A removed node stops serving requests and is shut down and sealed. Do not
reuse its data directory to rejoin it. (`1.19-changelog`)

## Listener and request limits

### JSON body limits

HTTP handling accepts `max_json_depth`, `max_json_string_value_length`,
`max_json_object_entry_count`, and `max_json_array_element_count`. Rate-limit
quotas run before these JSON limits. (`1.19-changelog`)

### Token header size

Listeners bound `X-Vault-Token` and `Authorization: Bearer` contents using
`max_token_header_size`, which defaults to 8 KB. Set `-1` only when an unlimited
header is intentional. (`2.0-changelog`)

```hcl
max_token_header_size = -1
```

### Response headers

Mount tuning can unset `allowed_response_headers`. (`1.21-changelog`)

## Memory locking and containers

Integrated storage has no default for `disable_mlock`; set it explicitly to
`true` or `false`, or Vault refuses to start. (`1.20-changelog`)

Containers run as `vault` and no longer carry `cap_ipc_lock`, so they cannot
call `mlock()`. Use `disable_mlock = true` and control swapping on the host or
container runtime. (`1.19-changelog`)

## Raft snapshots and recovery

### Recovery contents

Enterprise can load an integrated-storage snapshot and read, list, and recover
KV v1 and cubbyhole secrets. Later 1.20 releases add database static roles and
credentials and the SSH plugin CA. (`1.20-changelog`)

KV v2 recovery can restore in place or copy from a different source path within
the same mount and namespace. (`2.0.4`)

### Request format and alternate destinations

Move the snapshot ID from deprecated `recover_snapshot_id` to the
`X-Vault-Recover-Snapshot-Id` header. `RECOVER` is accepted alongside `POST` and
`PUT`. `vault recover -from` restores an item to a different live path.
(`1.21-changelog`)

### Loading, unloading, and delegated permission

Raft automated snapshots accept `autoload_enabled`; generated snapshots are
loaded automatically when enabled. Snapshot-management and recovery permissions
are separate, allowing recovery delegation without snapshot-administration
access. (`1.21-changelog`)

Clear a stuck loaded snapshot with
`vault operator raft snapshot unload -force` or:
(`1.21-changelog`)

```text
DELETE sys/storage/raft/snapshot-load/{snapshot_id}?force=true
```

## Seal HA and seal wrap

Seal HA refuses to persist the barrier keyring unless every seal is healthy.
Later 1.19 patches let new nodes join Seal-HA clusters. `detect_deadlocks`
accepts `sealwrap`; AppRole secrets are seal-wrapped when seal wrap is active.
Selected sensitive seal-wrap and managed-key values can come from environment
variables or files. (`1.19-changelog`)

Enterprise 1.19 has an unresolved duplicate unseal or seal-wrap HSM-key issue
requiring the documented workaround. (`1.19`)

Enterprise 1.19.18 has an unresolved condition in which seal wrapping can cause
Raft quorum failure, with no workaround listed. (`1.19`)

## Raft and storage configuration

### Live reload and validation

SIGHUP reloads additional Raft settings, and `/sys/config/state/sanitized`
reports them. (`1.19-changelog`)

Integrated storage rejects `performance_multiplier` values less than or equal
to zero. (`2.0-changelog`)

### Network discovery and canonical addresses

Agent, Proxy, server, and other configuration displays canonicalize IPv6 using
RFC 5952. Raft auto-join can force IPv4 on dual-stack networks.
(`1.19-changelog`)

### Cloud storage credentials and billing

The DynamoDB storage backend can modify its table to use per-request billing.
(`1.19-changelog`)

The PostgreSQL physical storage backend can authenticate with AWS IAM, Azure
MSI, or GCP IAM identities. (`1.20-changelog`)

The MySQL physical storage backend can read `VAULT_MYSQL_USERNAME` and
`VAULT_MYSQL_PASSWORD`. (`1.20-changelog`)

## Diagnostics and state capture

`pprof-dump-dir` writes startup profile dumps. `enable_post_unseal_trace` and
`post_unseal_trace_directory` enable and place post-unseal Go traces.
(`1.19-changelog`)

The sudo-protected `sys/reporting/scan` endpoint writes state-report files to
`reporting_scan_directory`. Protect the output directory. (`1.21-changelog`)

## Configuration parsing

Duplicate attributes in server and policy HCL were deprecated, then became
errors. The temporary `VAULT_ALLOW_PENDING_REMOVAL_DUPLICATE_HCL_ATTRIBUTES`
warning mode is removed, so duplicate attributes always fail parsing.
(`1.19-changelog`, `1.21-changelog`, `2.0.4`)

## Licensing and security modes

Vault Enterprise accepts IBM PAO license keys. This license type requires a
`license_entitlement` stanza in server configuration. (`2.0-changelog`)

Enterprise `common_criteria_mode` restricts listener TLS cipher suites. It also
tightens PKI chain, validation-time, `NotBefore`, key-usage, and uploaded-chain
validation. (`2.0-changelog`)

## Consistency and memory-sensitive operations

Invalid cross-cluster Server-Side Consistent Tokens sent to an active
performance secondary prefer HTTP 403 instead of HTTP 412. Update clients that
classify the failure by status. (`2.0.4`)

Core and Transit random-byte APIs permit larger outputs and pseudorandom output
seeded from random sources. Large requests consume proportionally more memory.
(`2.0-changelog`)
