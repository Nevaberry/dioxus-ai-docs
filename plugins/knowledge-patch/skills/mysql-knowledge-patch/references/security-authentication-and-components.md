# Security, Authentication, and Components

Use this reference for account DDL, password policy, role activation, access
control, connection throttling, key management, firewall migration, and masking.

## Privileges and account management

### Spatial reference systems have a dedicated privilege

In batch 9.2-9.3, `CREATE_SPATIAL_REFERENCE_SYSTEM` authorizes:

- `CREATE SPATIAL REFERENCE SYSTEM`;
- `CREATE OR REPLACE SPATIAL REFERENCE SYSTEM`; and
- `DROP SPATIAL REFERENCE SYSTEM`.

Relying on `SUPER` for these statements is deprecated. Grant the dedicated
privilege to the narrowest administrative role that needs it.

### Privilege flushing is deprecated

The following now warn and are deprecated:

- `FLUSH PRIVILEGES`;
- the `FLUSH_PRIVILEGES` privilege;
- `mysqladmin flush-privileges`;
- `mysqladmin reload`;
- privilege flushing through `SIGHUP` or `mysqladmin refresh`; and
- using `FLUSH PRIVILEGES` to clear the caching-SHA-2 cache.

Use account-management statements for grants and users, and use a purpose-built
administrative path for cache management.

### Authentication policy depends on the executor's privilege

For `CREATE USER`, an executor holding `AUTHENTICATION_POLICY_ADMIN` causes the
global `authentication_policy` to be ignored. Without that privilege, omitted
mandatory factors from the global policy are included automatically. Generate
account DDL with the executor's privileges in mind.

## Password and directory authentication

### Caching SHA-2 implementation changes

The caching-SHA-2 plugin moved to the event component API in batch 9.2-9.3,
removing the `sha2_cache_cleaner` audit plugin. Do not attempt to load or monitor
that former cleaner.

In batch 9.4-9.6, `caching_sha2_password_digest_rounds` defaults to `10000`.
Reassess authentication cost and configuration drift when an older deployment
set or assumed a different value.

In batch 9.7.0, `caching_sha2_password` supports a PBKDF2 storage format using
SHA-512. It applies to classic and X Protocol authentication. Administrators can
change or enforce the storage format without requiring client-side changes.

### SASL LDAP defaults to stronger SCRAM

For SASL LDAP in batch 9.4-9.6, `SCRAM-SHA-1` and its variable value are
deprecated. `authentication_ldap_sasl_auth_method_name` defaults to
`SCRAM-SHA-256`.

## Roles and policy evaluation

### Mandatory roles activate by default

`activate_mandatory_roles` is enabled by default in batch 9.4-9.6:

- with `activate_all_roles_on_login=OFF`, mandatory roles activate in addition
  to an account's default roles;
- with `activate_all_roles_on_login=ON`, mandatory and granted roles activate
  regardless of `activate_mandatory_roles`.

Account for the resulting effective privilege set in connection tests.

### Column masking uses policy DDL

Enterprise Edition in batch 9.7.0 adds column-level masking policies on base
tables:

- `CREATE MASKING POLICY`;
- `DROP MASKING POLICY`;
- `SHOW CREATE MASKING POLICY`; and
- `CREATE TABLE` and relevant `ALTER TABLE` forms that attach or change a policy.

`CURRENT_ROLE_IN()` and `CURRENT_USER_IN()` accept comma-separated role or user
lists and can act as gatekeeper functions in policy decisions.

## Connection control

### Replace both Connection Control plugins

`component_connection_control` replaces the two deprecated Connection Control
plugins, their variables, and the deprecated
`INFORMATION_SCHEMA.CONNECTION_CONTROL_FAILED_LOGIN_ATTEMPTS` table. Read failure
records from:

```text
performance_schema.connection_control_failed_login_attempts
```

### Exempt unknown-user health probes when appropriate

In batch 9.4-9.6,
`component_connection_control.exempt_unknown_users` can exempt failed
connections with no valid user credentials from delay penalties. This is useful
for load-balancer probes but changes brute-force throttling behavior.

`component_connection_control_exempted_unknown_users` counts the exemptions.
Monitor that counter when the exemption is enabled.

## Key management components

### HashiCorp Vault

`component_keyring_hashicorp` replaces the deprecated HashiCorp Vault keyring
plugin and its variables in batch 9.2-9.3. The component retains Vault AppRole
authentication. Translate plugin variables to component configuration rather
than copying their old names.

### KMIP key managers

`component_keyring_kmip` replaces the deprecated `keyring_okv` plugin in batch
9.4-9.6 and connects to KMIP 1.1-compatible key managers. Both implementations
support `SECRET` key types when the backing key vault is compatible.

## Enterprise Firewall migration

The Enterprise Firewall component replaces the deprecated firewall plugin in
batch 9.4-9.6. The component does not support the plugin's account profiles.
Convert account profiles to group profiles before migrating.

MySQL Configurator can enable the component or upgrade an existing firewall
plugin installation. Validate the converted group profiles before removing the
plugin.
