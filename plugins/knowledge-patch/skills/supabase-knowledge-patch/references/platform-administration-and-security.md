# Platform administration and security

## Access and organizations

### Organization and project role boundaries

Organization roles cover all present/future projects. Team/Enterprise can make project-scoped membership hide unrelated projects; Read-Only also requires those plans. Developers can read service keys, JWT secret, and Function secrets. Read-Only can read Function secrets and run `SELECT` as `supabase_read_only_user`, which has `pg_read_all_data`.

### AWS Marketplace-managed organizations

One AWS Marketplace subscription links exactly one organization and moves plans, payment, and tax to AWS while disabling Spend Cap. Each extra organization needs another subscription. Upgrades are immediate/prorated; downgrades wait for renewal; fixed and usage charges are separate invoices. Linking an existing organization resets its billing anchor and can produce a final direct-platform usage charge.

### Project transfer prerequisites

Transfers require source ownership and target membership. Remove GitHub integration, project-scoped memberships, and log drains. Vercel Marketplace targets are unsupported. Usage splits at transfer time; paid-to-Free can lose features and pause for 1–2 minutes. Region cannot change.

## Backups, restores, and migrations

### Physical backup and restore semantics

Postgres `15.8.1.079`+ uses physical backups. They omit Storage objects; downloadable daily backups omit custom login-role passwords. In-place restore makes a project unavailable and requires non-Realtime subscriptions and replication slots to be dropped/recreated.

### Point-in-Time Recovery lifecycle

PITR is a paid add-on needing Small compute or above. It replaces daily backups and archives WAL at worst about every two minutes; restore points exist only when activity creates WAL. Disabling PITR leaves physical points, not downloadable backups—make a logical dump for export.

### Restoring into a new project

A paid physical daily/PITR backup can create an independent project carrying database, Auth users, roles, extensions, compute/disk, SSL, network restrictions, and region. Reconfigure Storage objects/settings, Functions, Auth config/keys, Realtime, and replicas. A restored clone cannot itself be a clone source. Disable copied `pg_net`, `pg_cron`, and wrapper jobs before external actions repeat.

### Postgres migration modes

Use direct or Supavisor session port 5432 for dumps/restores/logical replication, never transaction mode. Portable dumps omit owners, privileges, subscriptions; recreate roles and RLS enablement. Logical replication additionally needs schema freeze and manual sequences, large objects, and cutover cleanup.

### Split CLI project backups

Dump roles, schema, and data separately, excluding vector-bucket internals; disable triggers while loading:

```sh
supabase db dump --db-url "$OLD_DB_URL" -f roles.sql --role-only
supabase db dump --db-url "$OLD_DB_URL" -f schema.sql
supabase db dump --db-url "$OLD_DB_URL" -f data.sql --use-copy --data-only \
  -x storage.buckets_vectors -x storage.vector_indexes
psql --single-transaction --variable ON_ERROR_STOP=1 \
  --file roles.sql --file schema.sql \
  --command 'SET session_replication_role = replica' --file data.sql \
  --dbname "$NEW_DB_URL"
```

Dump `supabase_migrations` and custom `auth`/`storage` changes separately, reset custom-role passwords, and copy the `pgsodium` root key via Management API before restoring encrypted columns. Downloaded Functions omit `deno.json` and legacy import maps.

## Compute, disk, and billing

### Provisioned disk performance

Default `gp3` provides 3,000 IOPS/125 MB/s. Large+ can provision more; `io2` provides higher IOPS with derived throughput. Effective performance is the lower compute/disk limit. Attribute changes start about six hours of cooldown; ordinary changes can grow, not shrink, disk.

### Disk autoscaling and read-only recovery

Paid disks at 90% expand 50%, capped at 200 GB per increase and once/six hours. Hitting 95% in cooldown makes DB read-only. A cleanup session can temporarily enable writes to delete/vacuum; later upgrade right-sizes to roughly `1.2 * database_size`, minimum 8 GB.

### Spend Cap and Fair Use scope

Pro Spend Cap covers disk/Storage size, egress, Function invocations, MAUs, Realtime, and transformations. It excludes compute, branches, replicas, domains, extra disk performance, IPv4, log drains, phone MFA, and PITR. Repeated capped/Free overage can pause the organization, make DB read-only, restrict transfers, or return 402. Exhausted grace does not reset when usage briefly falls; warnings clear only after multiple compliant cycles.

### Hourly and capacity metering

Compute/add-ons meter per resource-hour, rounding partial hours up. Database/object storage use GB-hours; disk performance uses IOPS-hours and MB/s-hours. Included quotas aggregate per organization. Monthly Compute Credits cover primary compute only, not branches/replicas.

### Invocation and Realtime package meters

Every Function response status counts, except CORS `OPTIONS`; overage rounds to million-invocation packages. A DB change counts per listening client; Broadcast counts the send plus each receiver. Project peak successful connections are summed then rounded to thousand-connection packages.

### Identity and image-transformation meters

Sign-in or refresh makes a user an MAU once/cycle. Native, SAML, and supported third-party Auth are separate usage items. Image transformations count distinct origin images, not variants, and overage rounds by 1,000 origins.

### Egress and log-drain accounting

Uncached service egress shares one organization quota; cached Storage egress has another. Supavisor output is Shared Pooler Egress, not duplicate DB egress. Each log drain bills configured hours, million-event packages, and egress; gzip can reduce egress.

### Log Drains on Pro

Pro projects can drain Postgres, Auth, Storage, Function, and Realtime logs to Datadog, Grafana Loki, Sentry, Axiom, S3, or a custom endpoint.

## Domains and networking

### Custom-domain activation

One project can have one CNAME custom subdomain or one experimental `supabase.co` vanity subdomain. The original URL remains, but Auth advertises the new host immediately; add both OAuth callbacks and update SAML metadata before activation.

```sh
supabase domains create --project-ref "$PROJECT_REF" --custom-hostname api.example.com
supabase domains reverify --project-ref "$PROJECT_REF"
supabase domains activate --project-ref "$PROJECT_REF"
```

### Dedicated IPv4 behavior

IPv4 add-on gives static database ingress only, not outbound. Supavisor is already IPv4-compatible. Toggling briefly disrupts direct DNS, pausing/toggling can replace the address, and each replica gets/bills one.

### Database network restrictions

Restrictions cover direct DB and all poolers, not HTTPS APIs. IPv6-capable direct clients normally need both IPv4/IPv6 CIDRs. Updates replace the whole allowlist. Functions cannot connect directly to a restricted database; use SDK/API.

```sh
supabase network-restrictions --project-ref "$PROJECT_REF" update \
  --db-allow-cidr 203.0.113.0/24 --db-allow-cidr 2001:db8::/64 \
  --experimental
```

### AWS PrivateLink

Team/Enterprise beta uses organization-level AWS VPC Lattice sharing for same-region VPC access to direct DB and pgBouncer; replica access needs support. Auth, Storage, Realtime, and APIs stay public. Support can disable public DB only after every client/tool uses private endpoints.

### Postgres SSL enforcement

Postgres/Supavisor may allow plaintext unless DB SSL enforcement is enabled; HTTPS always uses TLS. Changing it briefly reboots DB. Install project CA and use `sslmode=verify-full` for identity verification.

```sh
supabase ssl-enforcement --project-ref "$PROJECT_REF" update \
  --enable-db-ssl-enforcement --experimental
```

### Database login abuse protection

Every hosted database uses fail2ban to block IPs after failed logins, independently of database allowlists.

## Read replicas

### Read-replica eligibility and scale

Replicas require AWS hosting, Postgres 15+, Small+, and physical backups; they match primary compute. Below XL: two replicas; XL+: five. Each disk is 1.25× primary size plus matching optional IOPS/throughput/IPv4.

### Read-replica API semantics

A dedicated replica Data API permits only GET. RPCs opt in with `{ get: true }`; replica endpoints cannot serve Auth, Storage, or Realtime. The load-balancer routes writes to primary and fronts other services, but custom domains bypass it. Removing the last replica removes that endpoint—move clients first.

```ts
await supabase.rpc('report_totals', {}, { get: true })
```

### Read-replica lifecycle operations

Remove all replicas before project upgrade/restore, then redeploy. Restart/compute changes restart primary while replicas remain readable, then all replicas together. Monitor `physical_replication_lag_physical_replica_lag_seconds`; long transactions, exclusive locks, or resource saturation cause staleness.

## Upgrades and ownership

### Platform schema ownership

Keep `storage` objects owned by `supabase_storage_admin` and `auth` by `supabase_auth_admin`; later platform migrations depend on those privileges.

### In-place Postgres upgrades

Prefer `pg_upgrade`; failed attempts restore the original DB, and above 1 GB it is usually faster than pause/restore. Plan DB and dependent-service downtime. Replication slots are lost; oversized `cron.job_run_details` may exhaust duplicated disk; old TimescaleDB/`plv8` can block; reset MD5 custom-role passwords to SCRAM-SHA-256.

### Paused-project and Postgres 17 upgrade constraints

Free paused projects have a 90-day one-click restore window, then only downloadable DB/Storage backups. A later organization upgrade can re-enable restore that still fails compatibility. For Postgres 17 disable `plcoffee`, `plls`, `plv8`, `pgjwt`; upgrade right-sizes oversized disks from live DB size.

## Security posture and compliance

### RLS-secure table creation and alerts

Dashboard tables start with RLS. An event-trigger setup can enforce RLS for external/migration-created tables. Table Editor marks disabled RLS, and owners receive email/Dashboard alerts.

### Security Advisor checks and delivery

Security Advisors use Splinter to find missing RLS, permissive policies, and exposed sensitive columns. Dashboard provides fixes, owners receive weekly summaries, and the official MCP server can run/fix findings in development.

### High Compliance projects

After BAA plus HIPAA add-on, mark individual projects High Compliance for continuous advisor checks. Baseline requires PITR, Small+, SSL enforcement, and DB restrictions.

### Platform audit-log boundary

Team/Enterprise records Dashboard/Platform API member actions with actor IP/email/token type, metadata/status, and target. Logs are visible in organization Dashboard but cannot be exported or drained; retention varies by plan.

### HIPAA boundary for self-hosting

Hosted HIPAA controls are not supplied automatically for self-hosting. Establish separate legal agreements, operational controls, policies, and audited configuration.

### SOC 2 report and compliance boundary

Team/Enterprise Legal Documents provides the SOC 2 Type 2 report covering a rolling March–February period. Scope is data within Supabase, not external customer systems; customers choose compliant primary/replica regions.

### Customer penetration-testing policy

Customers may test their own Auth, DB, Functions, Storage, Realtime, and endpoints without approval. Stay within the project; no DoS/DDoS/flooding/cross-tenant tests. Report product vulnerabilities within 24 hours after testing.

### Expanded Terraform coverage

Terraform Provider 1.9.0 adds Edge Function and Function-secret resources plus a network-bans data source.
