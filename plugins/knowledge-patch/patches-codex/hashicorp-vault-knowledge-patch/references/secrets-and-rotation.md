# Secrets Engines, Sync, and Rotation

Use this reference for secrets-engine behavior, credential rotation, Secret
Sync, database integrations, and secret delivery.

## Root and static credential rotation

### AWS secrets configuration updates (`1.19-changelog`)

AWS secrets-engine writes persist fields and support partial updates. Clear a
field by writing its zero value. Enterprise supports cross-account static-role
management. STS configuration has fallback endpoint/region fields, and root
configuration has `sts_region`.

### Automated root rotation (`1.19-changelog`)

Rotation Manager schedules root rotation by schedule or TTL/period; schedules
use UTC. Enterprise integrations include AWS auth and secrets, database
secrets, and GCP auth and secrets. Snowflake later supports key-pair root
rotation.

### Static-role rotation behavior (`1.19-changelog`)

Enterprise database imports can skip the first automatic static-role rotation.
PostgreSQL `rotation_statements` accepts multiline statements.

### LDAP, Active Directory, and RACF rotation (`1.19-changelog`)

Enterprise Active Directory root-password rotation supports `schema`, which
defaults to `openldap` for compatibility. LDAP secrets static roles support IBM
RACF password phrases.

### Additional automated root-rotation targets (`1.19`)

Enterprise Rotation Manager schedules root rotation for the Azure and LDAP auth
method and secrets-engine integrations.

### Rotation scheduling visibility (`1.21-changelog`)

Enterprise Rotation Manager reports the time remaining until a scheduled
rotation.

### Enterprise LDAP static roles (`2.0-changelog`)

Enterprise LDAP self-managed static roles can rotate using their own password
without `bindpass`; they support schedules and retry policies. Existing static
roles migrate from the plugin queue to Rotation Manager, with progress exposed
at `static-migration`.

### Rotation retry policies (`2.0-changelog`)

Enterprise Rotation Manager supports retry limits and can orphan entries after
they exhaust the allowed attempts.

### Linux local-account rotation (`2.0`)

The OS secrets engine can automatically rotate credentials for Linux local
accounts.

### LDAP manual-rotation cadence (`upgrade-safety`)

In Enterprise 2.0+, manual LDAP static-role rotation no longer resets its
automated TTL; the original schedule remains. To restart the cadence, set
`disable_automated_rotation=true` and then `false`, recalculating
`next_vault_rotation`.

### LDAP self-managed static-role mount type (`upgrade-safety`)

Enterprise 2.0 self-managed roles do not work when the LDAP engine is mounted
via the `openldap` alias. Mount type `ldap` and enable self-management:

```shell
vault secrets enable -path=<mount_path> ldap
vault write <mount_path>/config self_managed=true
```

### Azure static-credential rotation spacing (`upgrade-safety`)

In Enterprise 1.21 and 2.0, rapid consecutive Azure `static-rotate` calls can
race propagation, fail to remove the previous credential, and require manual
cleanup. Wait several minutes between calls.

### Azure dynamic-role provisioning fixes (`upgrade-safety`)

New service-principal propagation can intermittently break dynamic credential
creation. Use 1.19.19, 1.20.13, 1.21.8, or 2.0.3 or later in the corresponding
release line.

## Database and cloud secrets engines

### Active Directory secrets-engine retirement (`1.19`)

The Active Directory plugin is retired in the 1.19 line. Migrate before
upgrading.

### Snowflake key-pair credential refresh (`1.19`)

Snowflake credential refresh can fail with key-pair authentication. The issue
is unresolved in 1.19.x; use the release-line workaround.

### MSSQL revocation (`1.19-changelog`)

MSSQL revocation requires only `VIEW ANY DEFINITION`, not `sysadmin`. Custom
revocation statements execute as one batch rather than splitting at
semicolons.

### Snowflake password authentication deprecation (`1.20`)

Snowflake password authentication is deprecated; migrate away from password
credentials.

### Azure static roles (`1.21-changelog`)

The Enterprise Azure secrets plugin supports static roles.

### Private database connectivity (`1.21-changelog`)

Database secrets support Private Service Connect for GCP Cloud SQL MySQL and
PostgreSQL, plus Private IP for MySQL.

### Database static-role escaping (`1.21-changelog`)

Self-managed database static roles honor their configured `escaping` or
`disable_escaping` setting.

### Snowflake password authentication retirement (`1.21`)

Snowflake password authentication is retired and unavailable in 1.21.x.

### Azure role management (`2.0`)

The Azure secrets engine adds role metadata, separates static-credential
import, and lowers the static-role minimum TTL to 30 days.

### AWS session-token response field (`upgrade-safety`)

AWS AssumeRole and FederationToken consumers must read `session_token`;
`security_token` is deprecated.

### Azure secrets password policies (`upgrade-safety`)

Azure `password_policy` is deprecated and unusable because Microsoft Graph
generates passwords instead of accepting requested ones. Remove dependencies on
Vault-generated Azure passwords.

## Secret Sync and delivery

### Secret Sync safety controls (`1.19-changelog`)

Enterprise GCP destinations support user-managed encryption keys; destination
configuration supports IP and port allowlists. `force_delete` defaults false
and can delete an unsyncable destination while leaving provider-side secrets
orphaned. If the latest KV v2 version is removed, sync falls back to the highest
active version rather than deleting the external secret.

### Cloud secrets import (`1.20`)

Enterprise beta imports KV-compatible secrets from AWS, Azure, and GCP into
Vault.

### KV v2 version attribution (`1.21-changelog`)

KV v2 versions carry attribution metadata visible through CLI and API.

### GitHub Enterprise Secret Sync (`1.21-changelog`)

Secret Sync destinations accept `enterprise_url` for self-hosted GitHub
Enterprise Server.

### Protected secrets through the Vault Secrets Operator (`1.21`)

Vault Secrets Operator can mount secrets directly into application pods as CSI
shared volumes, avoiding native Kubernetes Secret objects.

### Secret Sync workload identity (`2.0-changelog`)

Secret Sync supports workload identity federation and GUI configuration for
AWS, Azure, and GCP. Disabling or deleting a secrets-engine mount immediately
unsyncs its external secrets.

### GCP Secret Sync KMS persistence (`2.0.4`)

GCP Secret Manager destinations retain their per-region KMS key across Vault
restarts. Customer-controlled-encryption validation failures return HTTP 400,
not 500.

## Client and infrastructure integrations

### Terraform ephemeral values (`1.20`)

The Enterprise Vault provider supports ephemeral resources and write-only
attributes for KV and database secrets engines.

### Terraform Cloud dynamic team tokens (`1.20`)

The Terraform Cloud secrets engine generates dynamic team tokens.
