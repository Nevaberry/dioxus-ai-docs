# Operations and Upgrades

Use this reference for server configuration, integrated storage, containers,
cluster lifecycle, recovery, and upgrade hazards.

## Cluster state, Raft, and recovery

### Cluster health and removal signals (`1.19-changelog`)

`sys/health` reports whether a node was removed and whether a standby can
heartbeat the active node. Default failure codes are 530 and 474; override them
with `removedcode` and `haunhealthycode`. `sys/seal-status` and `vault status`
include `removed_from_cluster`; seal status later also includes
`migration_done_at_epoch`.

### Removed Raft nodes (`1.19-changelog`)

`sys/storage/raft/join` rejects a removed node that still has Raft data.
Removed nodes stop serving requests and are shut down and sealed.

### Seal HA and seal-wrap controls (`1.19-changelog`)

Seal HA persists the barrier keyring only when every seal is healthy; later
patches allow new nodes to join Seal-HA clusters. `detect_deadlocks` accepts
`sealwrap`, AppRole secrets are seal-wrapped when seal wrap is enabled, and
selected sensitive seal-wrap and managed-key values may come from environment
variables or files.

### Seal-wrapped Raft quorum (`1.19`)

Enterprise 1.19.18 has an unresolved issue in which seal wrapping can cause
Raft quorum failure. The release notes list no workaround.

### Recovery from integrated-storage snapshots (`1.20-changelog`)

Enterprise can load a snapshot and read, list, and recover KV v1 and cubbyhole
secrets. Later 1.20 releases add database static roles and credentials and the
SSH plugin CA.

### Snapshot recovery request changes (`1.21-changelog`)

Send the snapshot ID in `X-Vault-Recover-Snapshot-Id`, not the deprecated
`recover_snapshot_id` query parameter. Recovery accepts `RECOVER`, `POST`, and
`PUT`. `vault recover -from` restores an item to a different live path. Unload a
stuck snapshot with `vault operator raft snapshot unload -force` or
`DELETE sys/storage/raft/snapshot-load/{snapshot_id}?force=true`.

### Automatic snapshot loading (`1.21-changelog`)

Set `autoload_enabled` on an Enterprise Raft automated-snapshot configuration
to load generated snapshots automatically for recovery. Snapshot-management
and recovery permissions are separate, so recovery can be delegated alone.

### KV v2 snapshot recovery (`2.0.4`)

Enterprise recovery can read and recover KV v2 secrets from a loaded snapshot,
either in place or by copying another path in the same mount and namespace.

### Raft multiplier validation (`2.0-changelog`)

Integrated storage rejects `performance_multiplier` values less than or equal
to zero.

### Cross-cluster SSCT error status (`2.0.4`)

An invalid cross-cluster Server-Side Consistent Token sent to an active
performance secondary now prefers HTTP 403 over 412. Treat it as an
authorization failure when classifying API errors.

## Server configuration and runtime

### Container execution and memory locking (`1.19-changelog`)

Containers run as `vault` by default from 1.19.16. The 1.19.17 image required
runtime `IPC_LOCK`, but 1.19.18 removed built-in `cap_ipc_lock`; containers can
no longer call `mlock()`. Set `disable_mlock = true` and prevent swapping at the
runtime or host level.

### Integrated-storage memory locking (`1.20-changelog`)

With integrated storage, `disable_mlock` has no default. Set it explicitly to
`true` or `false`, or Vault refuses to start.

### Container image format (`1.19-changelog`)

Vault container images are compressed OCI image layouts. UBI images use UBI 10
minimal.

### Docker image startup (`1.19`)

The 1.19.16 image has an unresolved `setfcap` startup failure. Apply the
workaround from that release line when pinned to this image.

### UBI container package removal (`2.0.4`)

UBI images no longer contain `gnupg`, `openssl`, or `procps`. Supply any of
those tools needed by setup, health checks, or debugging separately.

### HCL duplicate attributes (`1.19-changelog`)

Duplicate attributes in server HCL and policy definitions are deprecated.

### Duplicate HCL attributes (`1.21-changelog`)

Duplicate attributes are errors. The temporary
`VAULT_ALLOW_PENDING_REMOVAL_DUPLICATE_HCL_ATTRIBUTES` setting downgrades them
to warnings only on releases that still support the switch.

### Duplicate HCL compatibility switch removed (`2.0.4`)

Duplicate attributes always fail parsing; the temporary compatibility switch
has been removed.

### Canonical paths and trailing slashes (`1.19-changelog`)

Non-canonical paths began failing in 1.19.16; 1.19.19 redirects `/./`, `/../`,
and `//` forms to cleaned paths. A mount tuneable can trim trailing slashes on
POST. A trailing-slash LIST now applies the more-specific deny rule rather than
falling through to a broader allow.

### JSON request limits (`1.19-changelog`)

HTTP listeners support `max_json_depth`, `max_json_string_value_length`,
`max_json_object_entry_count`, and `max_json_array_element_count`. Rate-limit
quotas run before these limits.

### Operator diagnostics and reloads (`1.19-changelog`)

Use `pprof-dump-dir` for startup profile dumps and
`enable_post_unseal_trace`/`post_unseal_trace_directory` for post-unseal Go
traces. SIGHUP reloads additional Raft settings, which also appear at
`/sys/config/state/sanitized`.

### Network and storage configuration (`1.19-changelog`)

Agent, Proxy, server, and other configuration displays canonicalize IPv6 under
RFC 5952. Raft auto-join can force IPv4 on dual-stack networks. DynamoDB
storage can modify its table to use per-request billing.

### Cloud identity for PostgreSQL storage (`1.20-changelog`)

PostgreSQL physical storage supports AWS IAM, Azure MSI, and GCP IAM identity
authentication.

### MySQL storage credentials from the environment (`1.20-changelog`)

The MySQL physical storage backend reads `VAULT_MYSQL_USERNAME` and
`VAULT_MYSQL_PASSWORD`.

### State reporting scan (`1.21-changelog`)

The sudo-protected `sys/reporting/scan` endpoint writes Vault-state report
files into `reporting_scan_directory`.

### IBM PAO licensing (`2.0-changelog`)

Enterprise accepts IBM PAO license keys only when server configuration includes
a `license_entitlement` stanza.

## Operator and client behavior

### Privileged system endpoints (`1.19-changelog`)

`sys/generate-root`, `sys/replication/dr/secondary/generate-operation-token`,
and `sys/rekey` authenticate callers by default. A root token generated on the
primary can authenticate to a DR secondary. Restore legacy unauthenticated
behavior only explicitly:

```hcl
enable_unauthenticated_access = ["generate-root", "generate-operation-token", "rekey"]
```

### Rekey cancellation nonce (`1.19`)

From 1.19.6, cancellation requires the rekey operation nonce. Automation must
retain and send it.

### Lease renewal and rate-limit retries (`1.19-changelog`)

`vault lease renew --fail-if-not-fulfilled` fails if the requested renewal
cannot be fulfilled. The default API client honors `Retry-After`, and quota
delays round up to whole seconds.

### Automatic irrevocable-lease removal (`1.20-changelog`)

Enterprise `remove_irrevocable_lease_after` deletes irrevocable leases after
that duration past expiry. A nonzero duration must be at least two days.

### Removed token-counter endpoint (`1.20-changelog`)

`/sys/internal/counters/tokens` is deprecated and returns HTTP 403 with
`unsupported path`; clients must not depend on it.

### Response-header tuning (`1.21-changelog`)

The mounts API can unset `allowed_response_headers`.

## Release-line and known-issue checks

### Enterprise LTS lifecycle (`1.19`)

Enterprise 1.19 is the current LTS line in this guidance; 1.16.x moved into
long-term support.

### Duplicate HSM keys (`1.19`)

Enterprise 1.19 has an unresolved duplicate unseal or seal-wrap HSM-key issue;
the release notes require a workaround.

### Local auth-mount configuration (`1.19`)

Writes to local LDAP, AWS, GCP, or Azure auth mounts can ignore the mount's
`local` flag in 1.19.x. No workaround is listed.

### Rotation Manager mount handling (`1.19`)

1.19.19 fixes routing of local mount entries under namespaces, but Rotation
Manager can still lose entries after a mount migration.

### Enterprise plugin signing-key compatibility (`upgrade-safety`)

Enterprise 1.19.17, 1.20.11, 1.21.6, and 2.0.1 cannot register Enterprise
plugins released on or after April 21, 2026 because the renewed signing key
fails verification. Existing registrations work. Upgrade respectively to
1.19.18, 1.20.12, 1.21.7, or 2.0.2 or later.
