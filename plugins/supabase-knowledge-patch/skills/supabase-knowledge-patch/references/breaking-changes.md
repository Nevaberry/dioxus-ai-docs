# Breaking Changes & Platform Changelog

## OpenAPI Spec Access via Anon Key Removed

As of March 2026, the `/rest/v1/` schema endpoint (which returns the full OpenAPI spec including tables, columns, and types) is no longer accessible via the `anon` key. Only `service_role` or the new `sb_secret_` API keys can access it.

This does **not** affect normal Data API usage — accessing `/rest/v1/your_table` via client libraries works as before. Only the schema introspection endpoint is restricted.

If your app fetches the schema spec client-side, move that call server-side (e.g., Edge Functions) using a privileged key. A new Management API endpoint is also available for CLI and third-party integrations.

## pg_graphql Disabled by Default

New Supabase projects no longer have `pg_graphql` enabled automatically. Existing projects older than 30 days with zero GraphQL requests also have it disabled.

If your application uses GraphQL, manually enable the extension:

```sql
CREATE EXTENSION pg_graphql;
```

Or add it to your migrations to ensure it's always present.

## PostgREST v14 JWT Cache

PostgREST v14 (deployed Dec 2025) includes a JWT cache enabled by default, providing ~20% more RPS for GET requests. Disable if memory issues arise:

```sql
ALTER ROLE authenticator SET pgrst.jwt_cache_max_entries TO 0; -- default is 1000
```

Schema cache loading is also dramatically faster (7 minutes → 2 seconds on complex databases). No configuration needed.

## Edge Functions: Recursive Call Rate Limits

Edge Functions have a rate limit on function-to-function calls within a project (introduced Mar 2026). Each request chain has a minimum budget of **5,000 requests per minute**.

What's rate-limited:
- Direct recursion (function calling itself)
- Function chaining (A → B)
- Circular calls (A → B → A)
- Fan-out patterns (A calling multiple functions concurrently)

**Not** rate-limited: inbound requests to Edge Functions, requests to external APIs (Stripe, OpenAI, etc.).

## Platform Features

### Management API for Backups and Read Replicas

Programmatically manage backups and read replicas via the Management API at `api.supabase.com/v1`:

```bash
export SUPABASE_ACCESS_TOKEN="your-access-token"
export PROJECT_REF="your-project-ref"

# List all available backups
curl -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  "https://api.supabase.com/v1/projects/$PROJECT_REF/database/backups"

# Restore from a PITR backup (Unix timestamp)
curl -X POST "https://api.supabase.com/v1/projects/$PROJECT_REF/database/backups/restore-pitr" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "recovery_time_target_unix": "1735689600" }'

# Create a Read Replica in a specific region
curl -X POST "https://api.supabase.com/v1/projects/$PROJECT_REF/read-replicas/setup" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "region": "us-east-1" }'

# Delete a Read Replica
curl -X POST "https://api.supabase.com/v1/projects/$PROJECT_REF/read-replicas/remove" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "database_identifier": "replica-identifier" }'
```

Read Replica limits: up to 5 replicas on XL+ compute, up to 2 on smaller compute. All replicas inherit the Primary's compute size.

### Read Replica Load Balancer Geo-Routing

As of April 2025, the Read Replica load balancer uses **geo-routing** instead of round-robin. `GET` requests are automatically routed to the closest database (primary or replica). Non-`GET` requests always go to the Primary.

The load balancer also handles Auth, Edge Functions, Realtime, and Storage requests (Auth always routes to Primary). Custom domains bypass the load balancer — use dedicated endpoints instead.

Read-only Postgres functions called via REST API must use the `get: true` option to be routed to replicas:

```js
const { data } = await supabase.rpc('my_read_function', { param: 'value' }, { get: true })
```

### PrivateLink via AWS VPC Lattice (Beta)

Enterprise-grade private connectivity between AWS VPCs and Supabase databases using AWS VPC Lattice. Database and PgBouncer connections only — Auth, Storage, Realtime, and API continue over public internet.

Connection string changes from public to private endpoint:

```
# Public
postgresql://user:pass@db.PROJECT-REF.supabase.co:5432/postgres

# Private (VPC Lattice endpoint)
postgresql://user:pass@your-private-endpoint.vpce.amazonaws.com:5432/postgres
```

Setup: Add AWS account ID in Supabase dashboard → accept AWS Resource Share in RAM console → create VPC endpoint or attach to VPC Lattice service network. Available on Team and Enterprise plans.

### Disk Types: gp3 vs io2

Two disk types available for Supabase databases:

| | gp3 (default) | io2 |
|---|---|---|
| Max disk size | 16 TB | 60 TB |
| Max IOPS | 16,000 (at 32 GB) | 80,000 (at 80 GB) |
| Max throughput | 1,000 MB/s | Scales with IOPS |
| IOPS provisioning | 500 IOPS per GB | 1,000 IOPS per GB |

Additional IOPS/throughput provisioning requires Large compute or above. After any disk attribute change, there is a ~6 hour cooldown before further adjustments. Disk size can only be increased, never decreased.
