---
name: hashicorp-vault-knowledge-patch
description: HashiCorp Vault
version: 2.0
license: MIT
metadata:
  author: Nevaberry
---


# HashiCorp Vault Knowledge Patch

Load this skill when configuring, upgrading, integrating, or troubleshooting
Vault. It emphasizes changed defaults, removals, request and response schema
changes, edition-specific behavior, and operational hazards.

## How to use this skill

1. Determine the exact server, CLI, SDK, plugin, and provider versions in use.
2. Distinguish Community and Enterprise features before proposing a design.
3. Read the topic reference for every subsystem touched by the change.
4. Apply breaking-change and upgrade-safety guidance before new-feature advice.
5. Validate paths, response fields, listener settings, and policy semantics
   against the deployed release rather than assuming old behavior persists.
6. For clustered changes, test standby, secondary, seal, snapshot, and event
   behavior as applicable—not just an active-node happy path.
7. For secrets and identity changes, plan rollback around externally created
   credentials, synchronized copies, and ownership boundaries.

## Reference index

| Reference | Topics |
| --- | --- |
| [operations-and-upgrades.md](references/operations-and-upgrades.md) | Server configuration, containers, Raft, snapshots, storage, recovery, cluster health, upgrade issues |
| [authentication-and-policy.md](references/authentication-and-policy.md) | Auth methods, identities, SCIM, OAuth resource servers, ACLs, policy templates |
| [pki-and-cryptography.md](references/pki-and-cryptography.md) | Transit, PKI, ACME, SCEP, KMIP, managed keys, FIPS, TLS |
| [secrets-and-rotation.md](references/secrets-and-rotation.md) | Secrets engines, static and root rotation, Secret Sync, databases, secret delivery |
| [audit-events-and-telemetry.md](references/audit-events-and-telemetry.md) | Audit schemas, events, utilization, billing, logs, metrics |
| [plugins-ui-and-clients.md](references/plugins-ui-and-clients.md) | Plugin packaging, registration APIs, SDKs, listener limits, GUI routes |

## Breaking changes and removals

### Reject duplicate HCL

Duplicate server-configuration and policy attributes are parsing errors. Do not
rely on the former warning-only compatibility switch; it is gone. Search and
deduplicate keys before deployment. See
[operations and upgrades](references/operations-and-upgrades.md).

### Remove Snowflake password authentication

Snowflake database connections must no longer use password authentication.
Plan a key-pair migration and account for the separate key-pair refresh issue
on affected older release lines. See
[secrets and rotation](references/secrets-and-rotation.md).

### Migrate retired integrations

The Active Directory secrets plugin is retired, and Centrify authentication is
no longer officially supported. Replace both before an upgrade depends on
their continued availability. See
[secrets and rotation](references/secrets-and-rotation.md) and
[authentication and policy](references/authentication-and-policy.md).

### Use per-element list-policy matching

Exact-match comparison for list-valued `allowed_parameters` and
`denied_parameters` is retired. Write constraints for per-element contains-all
matching, and remember that policy names are lowercased before constraint
evaluation. See [authentication and policy](references/authentication-and-policy.md).

### Stop using the token-counter endpoint

`/sys/internal/counters/tokens` returns an unsupported-path 403. Replace it with
supported activity, utilization, or billing interfaces. See
[operations and upgrades](references/operations-and-upgrades.md) and
[audit and telemetry](references/audit-events-and-telemetry.md).

### Set integrated-storage memory locking explicitly

An integrated-storage server will not start if `disable_mlock` is omitted.
Containers cannot call `mlock()` in the current image behavior, so set
`disable_mlock = true` there and prevent swapping outside Vault. See
[operations and upgrades](references/operations-and-upgrades.md).

### Supply removed UBI utilities yourself

Do not assume `gnupg`, `openssl`, or `procps` exists inside a UBI image. Add a
separate tool image or package layer for scripts and diagnostics that need
them. See [operations and upgrades](references/operations-and-upgrades.md).

### Replace the Agent API proxy

Built-in API proxying in Vault Agent is deprecated and pending removal. Move
proxy workloads to Vault Proxy. See
[plugins, UI, and clients](references/plugins-ui-and-clients.md).

### Enforce Azure auth bindings and stored precedence

Azure auth requires a bound group or service-principal ID. Stored plugin
configuration wins over `AZURE_*` environment variables, so move intended
values into `auth/azure/config`. See
[authentication and policy](references/authentication-and-policy.md).

### Respect token-header limits

Listeners cap Vault token and bearer-authorization headers at 8 KB by default.
Reduce oversized tokens or explicitly configure the listener; use `-1` only
after assessing the operational tradeoff. See
[plugins, UI, and clients](references/plugins-ui-and-clients.md).

### Treat SCIM-managed identities as externally owned

Entity merge cannot move aliases, policies, or memberships across the
SCIM-managed ownership boundary, even for privileged callers. Reconcile those
changes through the managing SCIM client. See
[authentication and policy](references/authentication-and-policy.md).

### Treat External CA PEM bundles as secret material

An External CA `pem_bundle` certificate response includes the private key in
the `certificate` field. Protect logs, caches, and parsers that handle it. See
[PKI and cryptography](references/pki-and-cryptography.md).

### Reclassify invalid cross-cluster tokens

Invalid cross-cluster consistency tokens at an active performance secondary
prefer HTTP 403 rather than 412. Update retry and authorization-error logic.
See [operations and upgrades](references/operations-and-upgrades.md).

## Upgrade-safety checklist

- Remove duplicate HCL attributes and deprecated configuration fields.
- Confirm Azure auth values are stored where precedence rules will read them.
- Space Azure static-role rotations to allow cloud propagation.
- Upgrade away from plugin-signing-key verification failures before registering
  newly released Enterprise plugins.
- Preserve rekey nonces for cancellation automation.
- Verify container startup, memory locking, and required diagnostic utilities.
- Exercise snapshot load, delegated recovery, unload, and destination-path
  restore before relying on disaster recovery.
- Test policy paths containing wildcards, trailing slashes, and rendered
  identity values under the stricter rules.
- Check GUI workarounds independently from CLI/API access.
- Verify event consumers tolerate bounded-queue loss and status-code changes.

The detailed version-specific fixes and known issues are in
[operations and upgrades](references/operations-and-upgrades.md) and the
subsystem references.

## High-value feature guidance

### Snapshot recovery

Enterprise recovery can load snapshots, delegate recovery separately from
snapshot management, restore to another live path, and recover KV v1, KV v2,
cubbyhole data, selected static credentials, and an SSH CA. See
[operations and upgrades](references/operations-and-upgrades.md).

### OAuth resource-server authorization

Vault can authorize requests from OAuth JWTs and apply RAR parameter controls
with identity-template expressions. Validate accepted `typ` values and treat an
empty optional authorization-details array as absent. See
[authentication and policy](references/authentication-and-policy.md).

### SCIM provisioning

Enterprise SCIM manages identities, aliases, and groups, supports multi-change
PATCH operations, offers explicit filtering, and exposes direct memberships.
Unsupported filters return 400. See
[authentication and policy](references/authentication-and-policy.md).

### LDAP self-managed rotation

Mount the engine as `ldap`, enable `self_managed`, and account for Rotation
Manager migration, retry/orphan policy, and manual-rotation cadence. See
[secrets and rotation](references/secrets-and-rotation.md).

### Transit and managed keys

Transit supports newer signature schemes, AES-CBC, derived-DEK context,
envelope encryption, managed-key rewrap, and managed-key certificate
operations. Parse managed-key usages as names rather than integers. See
[PKI and cryptography](references/pki-and-cryptography.md).

### PKI protocol services

PKI includes SCEP, richer ACME administration, External CA workflows, managed
key issuers, chain constraints, and delta-CRL advertisement. Apply the private
key handling rule for External CA PEM bundles. See
[PKI and cryptography](references/pki-and-cryptography.md).

### Secret Sync safeguards

Use destination allowlists, workload identity federation, and customer-managed
GCP keys. Understand `force_delete` orphaning, mount-triggered unsync, and KV v2
fallback behavior before deleting either side. See
[secrets and rotation](references/secrets-and-rotation.md).

### Event and billing consumers

Events can include consistency indexes and lease or LDAP rotation signals;
billing and utilization schemas add and rename fields. Treat schema changes as
API migrations rather than display-only additions. See
[audit, events, and telemetry](references/audit-events-and-telemetry.md).

### External plugins

Place extracted artifacts before registration, use detailed registration APIs,
and validate pinned-version overrides and SHA-256 data. Confirm the server line
can verify the current Enterprise plugin signing key. See
[plugins, UI, and clients](references/plugins-ui-and-clients.md).

## Task routing

For a server upgrade, begin with operations, then read every reference matching
an enabled auth method, secrets engine, audit device, plugin, or UI workflow.

For policy or identity work, combine authentication guidance with the target
auth or secrets-engine reference; identity templates affect both ACL paths and
OAuth authorization details.

For certificate workflows, read PKI guidance plus authentication guidance when
certificates are used for login, and audit guidance when OCSP or failed-login
metadata enters audit records.

For rotation automation, combine secrets guidance with audit/event guidance so
the schedule, retry policy, and compliance signals agree.
