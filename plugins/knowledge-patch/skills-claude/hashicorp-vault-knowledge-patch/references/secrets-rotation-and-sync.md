# Secrets, Rotation, and Synchronization

## Rotation Manager and static roles

### Automated root rotation

Rotation Manager schedules root-credential rotation by schedule or TTL/period,
with Enterprise integrations for AWS auth and secrets, database secrets, and
GCP auth and secrets. Snowflake supports key-pair root rotation. Schedules are
interpreted in UTC. (`1.19-changelog`)

Enterprise also supports scheduled root rotation for Azure and LDAP auth and
secrets integrations. (`1.19`)

### Static-role initialization and statements

Enterprise database imports can skip the initial automatic rotation of static
roles. PostgreSQL `rotation_statements` accepts multiline statements.
(`1.19-changelog`)

Self-managed database static roles honor their configured `escaping` or
`disable_escaping` state. (`1.21-changelog`)

### Retry, visibility, and attestation

Enterprise Rotation Manager has configurable retry limits and can orphan a
rotation entry after it exhausts the allowed attempts. (`2.0-changelog`)

Rotation Manager exposes the time remaining until a scheduled rotation.
(`1.21-changelog`)

Server logs record details for successful and failed automated root, database
static-role, and LDAP static-role rotations. (`1.21`)

The LDAP secrets engine emits rotation-success and rotation-failure events.
(`1.21`)

### Mount migrations

Vault 1.19.19 fixes incorrect routing of local mount entries under namespaces,
but Rotation Manager can still lose track of entries after a mount migration.
(`1.19`)

## LDAP and Active Directory secrets

### Root and static-role rotation

Enterprise Active Directory root-password rotation accepts `schema`, defaulting
to `openldap` for compatibility. The LDAP secrets engine supports IBM RACF
static-role password phrases. (`1.19-changelog`)

Enterprise LDAP static roles can be self-managed and rotate with their own
password rather than `bindpass`. They support scheduled rotation and retry
policies. Existing roles migrate from the plugin queue to Rotation Manager, with
progress controlled through `static-migration`. (`2.0-changelog`)

In Enterprise 2.0+, a manual LDAP static-role rotation does not reset its
automated TTL. Toggle `disable_automated_rotation` to `true` and back to `false`
to calculate a new `next_vault_rotation`. (`upgrade-safety`)

Self-managed roles do not work when the LDAP engine is enabled through the
`openldap` built-in alias. Enable type `ldap`, then self-management.
(`upgrade-safety`)

```shell
vault secrets enable -path=<mount_path> ldap
vault write <mount_path>/config self_managed=true
```

### Active Directory retirement

The Active Directory secrets plugin is retired in the 1.19 release line;
migrate before upgrading. (`1.19`)

## AWS secrets

AWS secrets-engine writes persist omitted fields, enabling partial updates. To
clear a stored field, send its zero value explicitly. Enterprise supports
cross-account management of static roles. STS configuration accepts fallback
endpoint and region settings, and root configuration accepts `sts_region`.
(`1.19-changelog`)

AssumeRole and FederationToken consumers should read `session_token`; the
legacy `security_token` response field is deprecated. (`upgrade-safety`)

## Azure secrets

### Static and dynamic roles

The Enterprise Azure secrets plugin supports static roles.
(`1.21-changelog`)

Azure role management includes role metadata, separates static-credential
import, and lowers the minimum static-role TTL to 30 days. (`2.0`)

Rapid Enterprise Azure static-role rotations in 1.21 and 2.0 can race Azure
propagation, fail to remove the previous credential, and require manual
cleanup. Wait several minutes between `static-rotate` calls.
(`upgrade-safety`)

Azure dynamic-role creation can intermittently fail while a service principal
propagates. Use 1.19.19, 1.20.13, 1.21.8, or 2.0.3 or later for the appropriate
release line. (`upgrade-safety`)

### Password policies

Azure secrets `password_policy` is deprecated and unusable because Microsoft
Graph generates and returns passwords instead of accepting a requested
password. Remove dependencies on Vault-generated passwords.
(`upgrade-safety`)

## Database secrets

### MSSQL revocation

MSSQL lease revocation needs only `VIEW ANY DEFINITION`, not `sysadmin`.
Custom revocation statements execute as a single batch rather than being split
at semicolons. (`1.19-changelog`)

### Snowflake authentication

Snowflake key-pair credential refresh can fail in 1.19.x; the issue remains open
and has a workaround. (`1.19`)

Snowflake password authentication is deprecated in 1.20 and retired in 1.21.x.
Migrate to key-pair authentication. (`1.20`, `1.21`)

### Private database connectivity

Database secrets supports Private Service Connect for GCP Cloud SQL MySQL and
PostgreSQL and Private IP for MySQL. (`1.21-changelog`)

## OS and Terraform Cloud secrets

The OS secrets engine can rotate Linux local-account credentials automatically.
(`2.0`)

The Terraform Cloud secrets engine can issue dynamic team tokens. (`1.20`)

## Secret Sync

### Destination safety

Enterprise GCP destinations support user-managed encryption keys. Destination
configuration accepts IP and port allowlists. `force_delete` defaults to
`false`; forcing deletion when associations cannot be unsynced leaves
provider-side secrets orphaned. If the latest KV v2 version is removed, sync
falls back to the highest active version instead of deleting the external
secret. (`1.19-changelog`)

GitHub destinations accept `enterprise_url` for self-hosted GitHub Enterprise
Server. (`1.21-changelog`)

Secret Sync supports workload identity federation, with UI configuration for
AWS, Azure, and GCP destinations. Disabling or deleting a secrets-engine mount
immediately unsyncs its external secrets. (`2.0-changelog`)

### GCP KMS persistence and errors

GCP Secret Manager destinations retain per-region KMS keys across Vault
restarts. Customer-controlled-encryption validation errors return HTTP 400
rather than HTTP 500. (`2.0.4`)

## Import, attribution, and recovery

Enterprise beta cloud import can bring KV-compatible secrets from AWS, Azure,
and GCP into Vault. (`1.20`)

Enterprise Terraform provider ephemeral resources and write-only attributes
support KV and database secrets workflows. (`1.20`)

KV v2 versions expose attribution metadata through the API and CLI.
(`1.21-changelog`)

Enterprise integrated-storage recovery can read, list, and recover KV v1 and
cubbyhole values; later 1.20 releases add database static roles and credentials
and the SSH plugin CA. (`1.20-changelog`)

KV v2 snapshot recovery supports in-place restoration and copying from another
path in the same mount and namespace. (`2.0.4`)
