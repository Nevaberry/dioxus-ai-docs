# Platform administration and security

## Organization roles and project scoping

Administrators have broad access but cannot update organization settings, transfer projects out, or add owners; Developers cannot change project settings, and Read-Only members have no write access. Read-Only and project-scoped roles require Team or Enterprise, and a project-scoped member cannot even see unassigned projects, while an organization-scoped role covers all current and future projects.

## Role names do not imply secret isolation

Developers can read service and anonymous API keys, the JWT secret, S3 access keys, and Function secrets; Read-Only members can also view Function secrets and run `SELECT` snippets as `supabase_read_only_user`, which has `pg_read_all_data`.

## Spend Cap boundaries

On Pro, an enabled Spend Cap blocks further covered usage after an organization exceeds its quota rather than charging overage. It covers variable items such as disk, egress, Functions, active users, Realtime, and Storage, but not opted-in resources such as compute, replicas, branching, domains, provisioned I/O, IPv4, log drains, phone MFA, or PITR, and it cannot set per-item budgets or alerts.

## AWS Marketplace-managed billing

One AWS Marketplace subscription links to exactly one organization, moves plan changes, payment and tax details to AWS, and disables the Spend Cap; linking an existing organization also resets its billing-cycle anchor and may produce a final direct-platform usage charge. Fixed subscription fees are invoiced in advance on that anchor date, while usage arrives on a separate calendar-month invoice, and plan downgrades wait for renewal.

## Capacity and add-on meters

Primary compute is billed in whole hours, with a partial hour rounded up; monthly Compute Credits apply only to primary-project compute, not branch or replica compute. Database and Storage capacity use GB-hours, while extra disk performance uses IOPS-hours and MB/s-hours, and every configured log drain separately accrues hours, whole one-million-event packages, and egress.

## Invocation and Realtime package meters

Every Function invocation counts regardless of response status except CORS `OPTIONS`, and billable overage rounds up to whole one-million-invocation packages. A database change counts once per listening Realtime client, Broadcast counts the send plus each receiver, and peak connections sum each project's successful cycle maximum before rounding to one-thousand-connection packages.

## Identity, image, and egress meters

A user counts once per cycle when signing in or refreshing a token, with native, SAML SSO, and supported third-party users tracked separately; image transformations count distinct origin images rather than variants. Uncached egress shares one organization-wide quota across services, cached Storage egress has a separate quota, and Supavisor output is classified as Shared Pooler Egress rather than double-counted as database egress.

## Physical backups and PITR

Projects on Postgres `15.8.1.079` or newer use physical backups, which omit custom-role passwords and Storage API objects; restoring takes the project offline and requires non-Realtime subscriptions and replication slots to be dropped and recreated. PITR requires at least Small compute, replaces daily backups while enabled, and has a worst-case recovery-point objective of two minutes; disabling it leaves physical restore points that cannot be downloaded, so create a logical dump when an export is required.

## Restore-to-new-project scope

A restore to a new project copies the database, roles, Auth users, enabled extensions, compute and disk attributes, SSL enforcement, and network restrictions into the source region, but Functions, Storage objects and settings, Auth/API and Realtime settings, database settings, and replicas still need manual setup. A restored project cannot itself be a clone source, and extensions that perform external work, such as `pg_net`, `pg_cron`, or wrappers, should be disabled immediately after the copy when duplicate actions would be unsafe.

## Provisioned disk constraints

Effective IOPS and throughput are the lower of the compute limit and provisioned disk limit; the default gp3 disk supplies 3,000 IOPS and 125 MB/s, and additional provisioning requires Large compute or above. Any disk-attribute change starts an approximately six-hour cooldown, and disk size can be increased but not manually decreased.

## Disk autoscaling and read-only recovery

Paid disks expand at 90% utilization by 50%, capped at 200 GB per expansion; reaching 95% during the six-hour cooldown puts the project into read-only mode, as does exceeding 500 MB on Free. A cleanup session can temporarily regain writes, and normal access resumes below 95%; an infrastructure upgrade can right-size the disk to 1.2 times database size with an 8 GB minimum.

```sql
set session characteristics as transaction read write;
vacuum;
set default_transaction_read_only = 'off';
```

## Custom-domain activation changes Auth

A project supports one CNAME-based custom domain or experimental vanity subdomain, while its original project domain remains usable; activation immediately changes OAuth callback URLs and the SAML entity ID, so providers must be prepared first. Custom domains also bypass the read-replica API load balancer.

```sh
supabase domains create --project-ref <ref> --custom-hostname api.example.com
supabase domains reverify --project-ref <ref>
supabase domains activate --project-ref <ref>
```

## Database ingress addressing and restrictions

Direct database endpoints use IPv6 by default, while both Supavisor modes use IPv4; the IPv4 add-on guarantees a static ingress address only, can briefly interrupt direct connections when toggled, and may assign a new address after toggling or pausing. Network restrictions replace the entire allowlist and cover direct and pooled database routes, usually requiring both IPv4 and IPv6 CIDRs, but do not cover HTTPS APIs and always block direct database access from Edge Functions.

## PrivateLink scope

PrivateLink is a Team/Enterprise beta that shares an AWS VPC Lattice resource configuration with a VPC in the project's region. It carries only direct Postgres and PgBouncer traffic—API, Auth, Storage, and Realtime remain public—and disabling the public database endpoint requires support.

## Organization MFA enforcement

Only an owner who already uses MFA can enable organization enforcement; members without an MFA-backed session immediately lose resource access but retain membership and recover their original permissions after enrollment. Personal access tokens are not subject to this enforcement boundary.

## Organization SSO lockout behavior

Organization SAML SSO can auto-join matching email domains with a chosen default role, and organization invitations from SSO accounts are restricted to the same identity provider. Disabling the provider immediately prevents all SSO users from signing in, so retain a non-SSO owner before doing so.

## Managed schema ownership

Hosted services require every object in `storage` to remain owned by `supabase_storage_admin` and every object in `auth` by `supabase_auth_admin`; violating this may surface only when a later service migration fails.

## Project-transfer prerequisites

A transfer requires ownership of the source organization and membership in the target, with no active GitHub integration, project-scoped role, or log drain; Vercel Marketplace-managed targets are unsupported. Transfers do not change region, may reduce access or features under the target plan, and can incur brief downtime when moving to Free.

## Read-replica lifecycle

Replicas require AWS, Postgres 15+, physical backups, and at least Small compute; sizes below XL allow two, XL and above allow five, and every replica inherits the primary's compute size. Their dedicated Data API accepts only `GET` requests, read-only RPCs need `{ get: true }`, and all replicas must be removed before project upgrades or restores; removing the final replica also removes the load-balancer endpoint.

```ts
await supabase.rpc('report', {}, { get: true })
```

## SSL enforcement restarts the database

SSL enforcement applies to Postgres and Supavisor only because all HTTPS APIs already require TLS, and changing it triggers a database reboot with downtime. Clients needing certificate identity verification should use `sslmode=verify-full` with the project CA certificate, not merely rely on server-side enforcement.

## Project-to-project dump contract

CLI backup and restore use separate role, schema, and data dumps, with Vector bucket system tables excluded from the data dump; restore them through a direct or session-mode port 5432 connection in one `psql` transaction with triggers disabled. Custom `auth`/`storage` changes, migration history, login-role passwords, Storage objects, and function dependency files such as `deno.json` or import maps require separate handling.

```sh
supabase db dump --db-url "$OLD_DB_URL" -f roles.sql --role-only
supabase db dump --db-url "$OLD_DB_URL" -f schema.sql
supabase db dump --db-url "$OLD_DB_URL" -f data.sql --use-copy --data-only \
  -x "storage.buckets_vectors" -x "storage.vector_indexes"
```

## External Postgres migration omissions

Use the session pooler on port 5432 for dump/restore and logical-replication migrations; portable dumps should use `--no-owner --no-privileges --no-subscriptions`, after which users, roles, privileges, and RLS enablement must be recreated. Logical replication supports low-downtime migrations from Postgres 10+, but it does not carry DDL, sequences, or large objects, so freeze schema and synchronize sequences before cutover.

## Auth0 password-hash imports

Admin user creation accepts existing bcrypt or Argon2 hashes through `password_hash`, plus a custom UUID and confirmation flags, so password users can be migrated without forcing a reset. OAuth users sign in through their provider instead of being pre-created, Auth0 organizations have no direct migration, and exported TOTP factors may need reenrollment.

```ts
await supabase.auth.admin.createUser({
  id: oldUserId,
  email,
  password_hash: exportedHash,
  email_confirm: true,
})
```

## Project-upgrade lifecycle

In-place `pg_upgrade` is the preferred path and brings the original database back online if it fails, while pause-and-restore upgrades are Free-only and paused projects have a 90-day one-click restore window. Logical replication slots are not preserved, custom-role passwords are absent from restore backups, and custom roles still using MD5 passwords must be reset to migrate them to SCRAM-SHA-256.

## High Compliance projects

Organizations handling protected health information need a signed BAA and the HIPAA add-on before marking a project High Compliance. That setting runs continuous Security Advisor checks and requires PITR with at least Small compute, SSL enforcement, and network restrictions.

## Automatic revocation of leaked secret keys

Supabase automatically revokes new-format secret keys detected in public GitHub repositories and notifies the project owner with rotation instructions. This applies to secret keys, not publishable keys.

## RLS-secure table creation and alerts

Tables created through the dashboard have RLS enabled by default; for tables created by migrations or external tools, the dashboard can install a Postgres event trigger that enables RLS automatically. The Table Editor labels tables without RLS, and project owners receive both dashboard and email alerts when such tables are created.

## Security Advisor checks and remediation surfaces

Security Advisor uses Splinter to detect issues such as tables without RLS, policies that could be more restrictive, and exposed sensitive columns; findings appear in the dashboard and in weekly emails to organization owners. The dashboard Assistant can generate and apply RLS policy SQL, while the hosted MCP server can scan and fix Advisor findings from a development environment.

## Restricted OpenAPI schema visibility

With new publishable keys, the OpenAPI specification requires elevated permissions instead of exposing the complete table-and-column schema as legacy anonymous keys did. Applications or tooling that relied on anonymous schema discovery must use an appropriately privileged path.

## Automatic database login blocking

Hosted Supabase databases run fail2ban and automatically block source IP addresses after failed database login attempts, independently of optional network restrictions.

## Platform audit-log boundary

Team and Enterprise organizations automatically log member actions performed through the dashboard or Platform API, including the actor's IP, email and token type, action metadata, and target. Platform Audit Logs are distinct from project Auth logs; dashboard export and log drains are unavailable, and retention depends on the plan.

## Hosted HIPAA boundary

The hosted platform supplies the controls needed for HIPAA environments, but self-hosted Supabase does not provide those controls out of the box because compliance also depends on BAAs, operating controls, and policies. Security Advisor warnings identify weakened required controls, but remediation remains the customer's responsibility.

## SOC 2 report and compliance boundary

Supabase is assessed annually for SOC 2 Type 2, and Team or Enterprise customers can download the report from the organization's Legal Documents page. The attestation covers data inside the hosted Supabase product boundary; it does not make a customer's application or external environment SOC 2 compliant.

## Customer penetration-testing policy

Customers may test their own hosted Auth, Database, Edge Functions, Storage, Realtime, and project endpoints without prior approval. DoS or DDoS testing, request flooding, and cross-tenant testing are prohibited, and product vulnerabilities found during testing must be reported to Supabase Security within 24 hours after testing is completed.

## Log Drains on Pro

Pro projects can send Postgres, Auth, Storage, Edge Functions, and Realtime logs to Datadog, Grafana Loki, Sentry, Axiom, S3, or a custom endpoint.

## Terraform coverage for Functions and network bans

Terraform Provider 1.9.0 adds resources for Edge Functions and their secrets plus a data source for network bans.

## Unified Logs open beta (1.26.08)

Unified Logs provides one searchable view across all Supabase services, with live tailing, filtering, and a timeline.

## One-click Grafana Cloud observability (1.26.08)

Every plan, including Free, can connect a project to Grafana Cloud in one click for a pre-built dashboard, alerts, and metrics.

## Searchable field-level encryption with CipherStash (1.26.08)

The CipherStash integration adds field-level encryption with queryable ciphertext and zero-knowledge key management, without requiring schema changes.
