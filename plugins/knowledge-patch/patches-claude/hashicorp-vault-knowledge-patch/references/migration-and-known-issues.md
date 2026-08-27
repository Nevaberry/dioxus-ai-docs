# Migration and Known Issues

Use this as an upgrade gate. Match each item to the exact edition, storage type,
plugins, and release line in the deployment.

## Mandatory configuration and packaging changes

### Integrated storage and `mlock`

Integrated-storage deployments must set `disable_mlock` explicitly to `true` or
`false`; there is no default, and startup fails when it is omitted.
(`1.20-changelog`)

Containers run as the `vault` user from 1.19.16. The 1.19.17 image required
runtime `IPC_LOCK`; 1.19.18 removed the built-in `cap_ipc_lock`. Current
containers cannot call `mlock()`, so use `disable_mlock = true` and prevent swap
at the runtime or host. (`1.19-changelog`)

### Minimal UBI images

UBI container images no longer contain `gnupg`, `openssl`, or `procps`. Supply
those utilities separately for setup, health checks, or debugging that needs
them. (`2.0.4`)

Vault container images are distributed as compressed OCI image layouts, and
UBI images use UBI 10 minimal. (`1.19-changelog`)

### HCL duplicate attributes

Duplicate attributes in server HCL and policy definitions were deprecated.
(`1.19-changelog`)

They became errors in 1.21; the temporary
`VAULT_ALLOW_PENDING_REMOVAL_DUPLICATE_HCL_ATTRIBUTES` switch downgraded them to
warnings. (`1.21-changelog`)

The switch is removed, and duplicates now always fail parsing. Remove all
duplicates before upgrade. (`2.0.4`)

### File audit-device permissions

An executable file audit device became an unseal blocker in 1.19.7. From
1.19.16, unseal warns about and clears existing executable bits; creation of a
new file audit device still rejects executable permissions.
(`1.19-changelog`)

## Retirements and replacements

### Secrets and authentication

- The Active Directory secrets plugin is retired in the 1.19 line; migrate
  before upgrading. (`1.19`)
- Snowflake database password authentication is deprecated in 1.20.
  (`1.20`)
- Snowflake password authentication is retired in 1.21.x and no longer works;
  use key-pair authentication. (`1.21`)
- Centrify authentication is no longer officially supported; choose another
  auth method. (`upgrade-safety`)
- LDAP `deny_null_bind` is deprecated and ineffective because empty-password
  login is always denied; remove it. (`upgrade-safety`)

### Policy, API, and agent behavior

- Exact-match list comparison for `allowed_parameters` and
  `denied_parameters` is retired in 1.21.x; use per-element matching. (`1.21`)
- `/sys/internal/counters/tokens` is deprecated and now returns HTTP 403
  `unsupported path`; remove callers. (`1.20-changelog`)
- Vault Agent's built-in API proxy is deprecated and pending removal; migrate
  proxy workloads to Vault Proxy. (`upgrade-safety`)
- PKI role `allow_token_displayname` is deprecated and targeted for removal in
  April 2027. Replace it with `allowed_domains`, `allow_bare_domains`,
  `allow_subdomains`, or `allow_glob_domains`. (`upgrade-safety`)
- AWS AssumeRole and FederationToken consumers should use `session_token`; the
  `security_token` response is deprecated. (`upgrade-safety`)
- Azure secrets `password_policy` is deprecated and unusable because Microsoft
  Graph generates and returns the password. Remove dependencies on a
  Vault-generated Azure password policy. (`upgrade-safety`)

## Client and API migrations

### Managed keys, activity, and utilization

`GET sys/managed-keys/:type/:name` returns usage names—`encrypt`, `decrypt`,
`sign`, `verify`, `wrap`, `unwrap`, `generate_random`, and `mac`—rather than
numeric IDs. Update typed decoders. (`2.0-changelog`)

Activity exports rename `timestamp` to `token_creation_time` and add the
client's first-use timestamp for the requested interval. (`1.21-changelog`)

Manual utilization bundles rename `snapshots` to `snapshot_records`; the old
human-readable snapshot is nested in `decoded_snapshot`. (`2.0-changelog`)

### Recovery and error handling

Recovery clients should move snapshot IDs from the deprecated
`recover_snapshot_id` query parameter to `X-Vault-Recover-Snapshot-Id`.
`RECOVER` joins `POST` and `PUT` as an accepted recovery method.
(`1.21-changelog`)

Invalid cross-cluster Server-Side Consistent Tokens sent to an active
performance secondary prefer HTTP 403 over HTTP 412. Treat the new response as
an authorization failure. (`2.0.4`)

External CA responses using `certificate_format=pem_bundle` include the private
key in the `certificate` field. Update parsers and protect this value as secret
material. (`2.0.4`)

### UI route changes

Secrets-engine routes moved from `/secrets` to `/secrets-engines`, and the
secrets-engine list no longer permits bulk deletion. Update bookmarks, tests,
and UI automation. (`2.0-changelog`)

## Release-line upgrade blockers

### Enterprise plugin signing key

Vault Enterprise 1.19.17, 1.20.11, 1.21.6, and 2.0.1 cannot register Enterprise
plugins released on or after April 21, 2026 because verification fails for the
renewed signing key. Existing registrations still work. Upgrade to 1.19.18,
1.20.12, 1.21.7, or 2.0.2 or later in the corresponding line.
(`upgrade-safety`)

### Azure provisioning and rotations

Azure dynamic-role creation can fail while a new service principal propagates.
Upgrade to 1.19.19, 1.20.13, 1.21.8, or 2.0.3 or later in the corresponding
line. (`upgrade-safety`)

In Enterprise 1.21 and 2.0, rapid Azure static-role rotations can race Azure
propagation, leave the old credential, and require manual cleanup. Wait several
minutes between `static-rotate` calls. (`upgrade-safety`)

### Azure authentication configuration precedence

From 2.0, stored `auth/azure/config` values override `AZURE_*` environment
variables. Persist intended settings in the auth configuration before upgrade.
(`upgrade-safety`)

### LDAP self-managed roles and schedules

Enterprise 2.0 self-managed LDAP static roles do not work when the engine is
mounted with the `openldap` built-in alias. Mount type `ldap`, then enable
self-management. (`upgrade-safety`)

```shell
vault secrets enable -path=<mount_path> ldap
vault write <mount_path>/config self_managed=true
```

Manually rotating an Enterprise LDAP static role no longer resets its automated
rotation TTL. To establish a new cadence, set `disable_automated_rotation` to
`true`, then back to `false`, which recalculates `next_vault_rotation`.
(`upgrade-safety`)

## Known operational issues

### Enterprise 1.19 issues

- Duplicate unseal or seal-wrap HSM keys remain unresolved and require the
  release-note workaround. (`1.19`)
- Snowflake key-pair credential refresh can fail and requires its documented
  workaround. (`1.19`)
- Writes to local LDAP, AWS, GCP, or Azure auth mounts can ignore `local`; no
  workaround is listed. (`1.19`)
- Multiple event clients can miss events; a workaround is available. (`1.19`)
- 1.19.19 corrects routing of local mount entries beneath namespaces, but
  Rotation Manager can still lose entries after mount migration. (`1.19`)
- The 1.19.16 Docker image can fail startup due to `setfcap`; use the available
  workaround. (`1.19`)
- Enterprise 1.19.18 seal wrapping can cause Raft quorum failure; no workaround
  is listed. (`1.19`)

Vault Enterprise 1.19 is the current LTS line in its release context, while
1.16.x moves into long-term support. (`1.19`)

### GUI issues

An Enterprise 2.0 Endpoint Governing Policy can block root-token GUI access to
a child namespace when the UI calls `sys/internal/ui/mounts`. CLI and API
access still work. Use those interfaces or explicitly permit the endpoint.
(`upgrade-safety`)

In 1.21 and 2.0, changing **Items per page** from any Secrets Engines results
page other than page 1 can produce an empty or incomplete table. Return to page
1 or refresh before changing page size. (`upgrade-safety`)
