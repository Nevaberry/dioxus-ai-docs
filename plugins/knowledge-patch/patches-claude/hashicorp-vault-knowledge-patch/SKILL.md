---
name: hashicorp-vault-knowledge-patch
description: HashiCorp Vault
version: "2.0"
license: MIT
metadata:
  author: Nevaberry
---


# HashiCorp Vault Knowledge Patch

Use this skill when planning, implementing, reviewing, or troubleshooting modern
Vault deployments, clients, plugins, policies, authentication, secrets engines,
PKI, integrated storage, or upgrades. Prefer the repository's manifests,
configuration, running-server behavior, and tests when they disagree with this
guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Audit, events, billing, and UI](references/audit-events-billing-and-ui.md) | Audit records, event delivery, quotas, billing and utilization, telemetry, and UI behavior |
| [Authentication, identity, and policy](references/auth-identity-and-policy.md) | Auth methods, identity and SCIM, OAuth, MFA, ACLs, namespaces, and proxy certificate handling |
| [Migration and known issues](references/migration-and-known-issues.md) | Breaking changes, retirements, upgrade blockers, compatibility switches, and workarounds |
| [PKI, Transit, and managed keys](references/pki-transit-and-managed-keys.md) | PKI issuance, ACME/SCEP, Transit algorithms, KMIP, managed keys, and cryptographic modes |
| [Plugins, agents, and delivery](references/plugins-agents-and-delivery.md) | Plugin registration, containers, Vault Agent and Proxy, SDK helpers, Terraform, and VSO delivery |
| [Secrets, rotation, and synchronization](references/secrets-rotation-and-sync.md) | Cloud and database engines, Rotation Manager, static roles, Secret Sync, imports, and recovery |
| [Server, cluster, and storage](references/server-cluster-and-storage.md) | Listeners, Raft, seals, storage backends, diagnostics, limits, and cluster health |

## Upgrade blockers first

### Remove duplicate HCL attributes

Duplicate attributes in server configuration and policy HCL are hard parse
errors. The temporary compatibility environment variable is gone. Find and
remove duplicates before starting an upgraded server.

### Set integrated-storage memory locking explicitly

When using integrated storage, configure `disable_mlock` explicitly as `true`
or `false`; omission prevents startup. Current containers cannot call
`mlock()`, so container deployments normally set it to `true` and prevent swap
at the host or runtime layer.

### Migrate retired authentication and credential modes

- The Active Directory secrets plugin is retired; migrate its workloads.
- Snowflake password authentication is retired; use key-pair authentication.
- Centrify authentication is no longer officially supported.
- Exact-match list policy comparison is retired; use per-element matching.
- The Vault Agent API proxy is deprecated; use Vault Proxy.
- Remove the obsolete LDAP `deny_null_bind` setting.

### Check plugin signing compatibility

Enterprise releases 1.19.17, 1.20.11, 1.21.6, and 2.0.1 cannot verify the
renewed signing key used by Enterprise plugins released on or after April 21,
2026. Upgrade to the patched release in the same line before registering such
plugins.

### Account for changed API schemas and statuses

- Managed-key usage values are names such as `encrypt` and `sign`, not integers.
- Activity exports use `token_creation_time` instead of `timestamp`.
- Utilization bundles use `snapshot_records` and `decoded_snapshot`.
- Invalid cross-cluster consistency tokens may return HTTP 403 instead of 412.
- External-CA `pem_bundle` certificate fields can include a private key.
- AWS credential consumers should read `session_token`, not `security_token`.

See [Migration and known issues](references/migration-and-known-issues.md) for
the complete upgrade checklist and unresolved release-line issues.

## Authentication, identity, and ACL quick reference

### Harden privileged and forwarded authentication

- Root generation, DR operation-token generation, and rekey endpoints
  authenticate callers by default. Opt into legacy unauthenticated access only
  with `enable_unauthenticated_access`.
- Vault strips Vault tokens from forwarded `Authorization` headers unless the
  header is explicitly configured for passthrough.
- Certificate auth accepts RFC 9440 forwarded certificate headers and can work
  behind a TLS-terminating proxy even when listener TLS is disabled.
- Validate and constrain trusted proxy headers; `X-Forwarded-For` values must be
  valid IP addresses.

### Update identity and policy controls

- Entity merges require `sudo`; merges involving SCIM-managed entities are
  rejected.
- Enable `force_identity_deduplication` only when intentionally resolving
  duplicate entities and groups by rename.
- `allowed_parameters` and `denied_parameters` use per-element list matching.
  Policy names are lowercased before constraint evaluation.
- Set `deny_slash_in_templated_path = true` when rendered identity values must
  never create additional path segments.
- Wildcards in rendered identity templates are rejected, and `resultant-acl`
  includes segment-wildcard paths in `glob_paths`.

### Adopt workload identity features deliberately

Vault can authenticate SPIFFE JWTs and X.509 identities and can issue JWT-SVIDs.
Its OAuth resource server can authorize registered agents with JWTs and apply
Rich Authorization Request constraints. Enterprise SCIM manages entities,
aliases, and groups but preserves a strict ownership boundary around managed
entities.

See [Authentication, identity, and policy](references/auth-identity-and-policy.md)
for exact fields, endpoints, and auth-method behavior.

## Server and storage quick reference

### Detect removed or unhealthy nodes

Use `sys/health`, `sys/seal-status`, and `vault status` to distinguish a removed
node from an unhealthy standby. Do not reuse Raft data from a removed node:
join rejects it, and removed nodes stop serving requests and seal.

### Bound requests and queues

- Configure JSON nesting, string, object-entry, and array-element limits.
- Configure `max_token_header_size`; it defaults to 8 KB and `-1` disables it.
- Event subscriber queues are unbuffered by default. A positive
  `VAULT_EVENT_NOTIFICATIONS_BOUNDED_QUEUE_SIZE` enables a bounded buffer up to
  1000 but can trade backpressure for missed events.
- Large random-byte responses use correspondingly more memory.

### Operate snapshots and seals safely

Enterprise snapshot loading supports delegated recovery and recovery into a
different path. Automated snapshots can be autoloaded, and a forced unload can
clear a stuck snapshot. Seal HA requires every seal to be healthy before
persisting the barrier keyring.

See [Server, cluster, and storage](references/server-cluster-and-storage.md) for
health codes, listener settings, Raft details, storage credentials, and
diagnostics.

## Secrets and rotation quick reference

### Treat partial updates and rotations explicitly

- AWS secrets configuration writes preserve omitted fields; send a zero value
  to clear an existing field.
- Rotation Manager schedules are UTC. Configure retries and monitor orphaned
  entries after exhausted attempts.
- Manually rotating an LDAP static role does not reset its automated TTL.
  Toggle `disable_automated_rotation` to start a new cadence.
- Space Azure static-role rotations by several minutes to avoid propagation
  races and orphaned credentials.

### Protect synchronization and recovery

Secret Sync destinations support workload identity, network allowlists, and GCP
customer-managed encryption keys. `force_delete` can leave provider-side
secrets orphaned, while disabling or deleting a source mount unsyncs secrets
immediately. Snapshot recovery supports KV v1, KV v2, cubbyhole, database
static-role, and SSH CA recovery where applicable.

See [Secrets, rotation, and synchronization](references/secrets-rotation-and-sync.md)
for engine-specific migration and operational details.

## PKI and cryptography quick reference

### Enforce issuance constraints

PKI enforces issuer extensions, name constraints, chain validation, path length,
and configured maximum TTLs. Use `leaf_not_after_behavior =
"always_enforce_err"` when overlong leaf lifetimes must fail even for CA and
ACME issuance. Bound CRL growth with `max_crl_entries`.

### Handle modern algorithms and managed keys

Transit supports post-quantum signatures, RSA PKCS#1 v1.5 encryption, AES-CBC,
envelope encryption, and managed-key operations according to edition and
feature maturity. PKCS#11 `slot` and `token_label` are mutually exclusive; clear
the old selector while setting the new one.

### Treat certificate bundles as secrets

External CA responses requested as `pem_bundle` can place the private key in the
`certificate` field. Protect logs, caches, and parsers that handle that field.

See [PKI, Transit, and managed keys](references/pki-transit-and-managed-keys.md)
for algorithms, protocols, constraints, and managed-key endpoint support.

## Plugins, agents, delivery, and UI

### Register plugins from the intended artifact

External plugin registration expects an extracted artifact in the plugin
directory. Official-plugin automatic downloads are beta, and Enterprise can
override pinned versions when mounting or tuning supported backends. Prefer the
detailed registration client APIs; the older `RegisterPlugin` variants are
deprecated.

### Prepare minimal containers

Containers run as the `vault` user, lack built-in `IPC_LOCK`, and UBI images no
longer include `gnupg`, `openssl`, or `procps`. Supply required operational tools
separately rather than assuming they exist in the image.

### Update UI links and automation

Secrets-engine UI routes use `/secrets-engines`, and the list no longer supports
bulk deletion. Pagination has a known issue when page size changes away from
page 1. Root-token GUI access under an EGP can fail for the UI mounts endpoint;
use CLI/API access or explicitly permit that endpoint.

See [Plugins, agents, and delivery](references/plugins-agents-and-delivery.md)
and [Audit, events, billing, and UI](references/audit-events-billing-and-ui.md)
for delivery mechanisms, UI capabilities, reporting, and event semantics.

## Review workflow

1. Identify the exact Vault edition, release, enabled plugins, and storage type.
2. Read the migration reference before changing binaries or container tags.
3. Validate listener, seal, storage, and policy configuration in a non-production
   environment.
4. Exercise authentication, rotation, lease, event, and recovery workflows that
   the deployment actually uses.
5. Update clients for changed fields, endpoints, status codes, and retry rules.
6. Inspect audit, billing, utilization, and rotation evidence after rollout.
