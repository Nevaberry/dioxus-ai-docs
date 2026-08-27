# Security, Authentication, and Components

## Privileges and account-management behavior

### Spatial reference systems (9.2-9.3)

`CREATE_SPATIAL_REFERENCE_SYSTEM` authorizes `CREATE`, `CREATE OR REPLACE`, and
`DROP SPATIAL REFERENCE SYSTEM`. Depending on `SUPER` for those statements is
deprecated.

### Privilege-cache flushing (9.2-9.3)

`FLUSH PRIVILEGES`, the `FLUSH_PRIVILEGES` privilege, `mysqladmin
flush-privileges`, and `mysqladmin reload` are deprecated and warn. Privilege
flushing through SIGHUP or `mysqladmin refresh` is also deprecated, as is using
`FLUSH PRIVILEGES` to clear the caching-SHA-2 cache. Use account-management
statements, which update privileges directly.

### Authentication policy enforcement (9.2-9.3)

For `CREATE USER`, an actor holding `AUTHENTICATION_POLICY_ADMIN` bypasses the
global `authentication_policy`. Without that privilege, omitted mandatory factors
from the global policy are added automatically.

## Password storage and authentication defaults

### System-account migration and cache cleanup (9.2-9.3)

An upgrade from 5.7 changes the server-created `mysql.sys` and `mysql.session`
accounts from `mysql_native_password` to `caching_sha2_password`. The
caching-SHA-2 implementation moved to the event component API, so the
`sha2_cache_cleaner` audit plugin was removed.

### Digest rounds and LDAP SASL (9.4-9.6)

`caching_sha2_password_digest_rounds` defaults to `10000`. For SASL LDAP,
`SCRAM-SHA-1` and its variable value are deprecated, while
`authentication_ldap_sasl_auth_method_name` defaults to `SCRAM-SHA-256`.

### PBKDF2 credential storage (9.7.0)

`caching_sha2_password` supports PBKDF2 with SHA-512, including X Protocol
authentication. Administrators can switch or enforce the server-side storage
format without requiring client changes.

## Roles and login controls

### Mandatory roles (9.4-9.6)

`activate_mandatory_roles` defaults to enabled. If
`activate_all_roles_on_login=OFF`, mandatory roles supplement the account's
default roles. If it is `ON`, mandatory and granted roles activate regardless of
the value of `activate_mandatory_roles`.

### Unknown-user connection-control exemption (9.4-9.6)

Set `component_connection_control.exempt_unknown_users` when invalid-user
connections, such as load-balancer probes, should not incur delay penalties.
`component_connection_control_exempted_unknown_users` counts exemptions.

## Component migrations

### Connection Control and HashiCorp keyring (9.2-9.3)

`component_connection_control` replaces both Connection Control plugins, their
variables, and the deprecated
`INFORMATION_SCHEMA.CONNECTION_CONTROL_FAILED_LOGIN_ATTEMPTS` table. Read failures
from `performance_schema.connection_control_failed_login_attempts`.

`component_keyring_hashicorp` replaces the HashiCorp Vault keyring plugin and its
variables while retaining Vault AppRole authentication.

### Enterprise Firewall (9.4-9.6)

The Enterprise Firewall component replaces the firewall plugin, but it does not
support account profiles. Convert account profiles to group profiles first.
MySQL Configurator can enable the component or upgrade a plugin installation.

### KMIP keyring (9.4-9.6)

`component_keyring_kmip` replaces the deprecated `keyring_okv` plugin for KMIP
1.1-compatible key managers. Both forms support `SECRET` key types when the key
vault is compatible.

### Additional Community components (9.7.0)

Community Edition includes Replication Applier Metrics, Group Replication Flow
Control Statistics, Group Replication Resource Manager, Group Replication Primary
Election, and Telemetry components.

## Enterprise masking policies

### Column-level dynamic masking (9.7.0)

Enterprise Edition can define base-table column policies with `CREATE MASKING
POLICY`, remove them with `DROP MASKING POLICY`, and inspect them with `SHOW
CREATE MASKING POLICY`. `CREATE TABLE` and applicable `ALTER TABLE` forms attach
or change policies. `CURRENT_ROLE_IN()` and `CURRENT_USER_IN()` accept
comma-separated role or user lists and can act as policy gatekeepers.
