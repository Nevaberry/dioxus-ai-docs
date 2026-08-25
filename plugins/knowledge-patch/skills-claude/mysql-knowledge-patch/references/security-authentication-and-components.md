# Security, Authentication, and Components

Use this reference when changing accounts, privileges, authentication,
connection throttling, key storage, firewalling, or data masking.

## Privileges and account management

### Grant the spatial-reference-system privilege

`CREATE_SPATIAL_REFERENCE_SYSTEM` authorizes `CREATE`, `CREATE OR REPLACE`, and
`DROP SPATIAL REFERENCE SYSTEM`. Depending on `SUPER` for these statements is
deprecated.

### Stop flushing privilege caches

The following are deprecated and warn:

- `FLUSH PRIVILEGES` and the `FLUSH_PRIVILEGES` privilege
- `mysqladmin flush-privileges` and `mysqladmin reload`
- privilege flushing through `SIGHUP` or `mysqladmin refresh`
- using `FLUSH PRIVILEGES` to clear the caching-SHA-2 cache

Use account-management statements, which apply privilege changes directly.

### Apply authentication policy with privilege awareness

For `CREATE USER`, an actor holding `AUTHENTICATION_POLICY_ADMIN` causes the
global `authentication_policy` to be ignored. Without that privilege, omitted
mandatory factors from the global policy are added automatically.

### Account for mandatory-role activation

`activate_mandatory_roles` defaults to enabled. If
`activate_all_roles_on_login` is off, mandatory roles activate in addition to
an account's default roles. If it is on, mandatory and granted roles activate
regardless of `activate_mandatory_roles`.

## Password storage and authentication

### Use PBKDF2 storage without client changes

`caching_sha2_password` supports PBKDF2 with SHA-512, including for X Protocol
authentication. Administrators can change or enforce this server-side storage
format without requiring client-side changes.

### Prepare upgraded system accounts

An upgrade from MySQL 5.7 to a later series changes the server-created
`mysql.sys` and `mysql.session` accounts from `mysql_native_password` to
`caching_sha2_password`. The caching-SHA-2 plugin also moved to the event
component API, removing the `sha2_cache_cleaner` audit plugin.

### Recheck hashing and LDAP defaults

`caching_sha2_password_digest_rounds` defaults to `10000`. For SASL LDAP,
`SCRAM-SHA-1` and its variable value are deprecated, while
`authentication_ldap_sasl_auth_method_name` defaults to `SCRAM-SHA-256`.

`MD5()` and `SHA1()` were deprecated in 9.4 and moved out of the server in 9.6.
Install the `classic_hashing` component only for applications that still need
those functions.

## Component migrations

### Replace Connection Control plugins

`component_connection_control` replaces both deprecated Connection Control
plugins and their variables. It also replaces
`INFORMATION_SCHEMA.CONNECTION_CONTROL_FAILED_LOGIN_ATTEMPTS` with
`performance_schema.connection_control_failed_login_attempts`.

`component_connection_control.exempt_unknown_users` can exempt failed
connections with no valid user credentials from delay penalties, which is
useful for load-balancer probes. Monitor the
`component_connection_control_exempted_unknown_users` counter.

### Replace keyring plugins

- `component_keyring_hashicorp` replaces the deprecated HashiCorp Vault
  keyring plugin and its variables while retaining Vault AppRole
  authentication.
- `component_keyring_kmip` replaces the deprecated `keyring_okv` plugin for
  KMIP 1.1-compatible key managers.
- Both KMIP implementations support `SECRET` keys when the key vault does.

### Migrate Enterprise Firewall profiles

The Enterprise Firewall component replaces the deprecated firewall plugin, but
does not support its account profiles. Convert account profiles to group
profiles before migrating. MySQL Configurator can enable the component or
upgrade an existing plugin installation.

### Remove Version Tokens

MySQL 9.2 deprecated the Version Tokens plugin, its `version_tokens_*()`
functions, `VERSION_TOKEN_ADMIN`, and `version_tokens_session` variables. MySQL
9.3 removes the plugin. Remove all dependencies before upgrading.

## Dynamic data masking

Enterprise Edition supports column-level masking policies on base tables with
`CREATE MASKING POLICY`, `DROP MASKING POLICY`, and
`SHOW CREATE MASKING POLICY`. `CREATE TABLE` and relevant `ALTER TABLE` forms
can attach or change a policy.

`CURRENT_ROLE_IN()` and `CURRENT_USER_IN()` accept comma-separated role or user
lists and can act as masking-policy gatekeepers.
