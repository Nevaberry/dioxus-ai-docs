---
name: supabase-knowledge-patch
description: "Supabase changes since training cutoff — OAuth 2.1 server, Web3 auth, Edge Function background tasks/S3 mounts, Realtime authorization, vector/analytics buckets, pgmq queues, MCP server, new API key model. Load before working with Supabase."
version: "2026.03"
license: MIT
metadata:
  author: Nevaberry
---

# Supabase Knowledge Patch

Claude's baseline knowledge covers Supabase through mid-2025. This skill provides features and breaking changes from late 2025 onwards.

## Index

- [references/auth.md](references/auth.md) — OAuth 2.1 server, custom/Web3 providers, JWT signing keys, before-user-created hook
- [references/edge-functions.md](references/edge-functions.md) — Background tasks (`waitUntil`), S3 mounts, ephemeral storage, `getClaims()` auth pattern, limits
- [references/realtime.md](references/realtime.md) — Private channels with RLS, broadcast from database, broadcast replay
- [references/storage.md](references/storage.md) — Vector buckets (similarity search), analytics buckets (Iceberg)
- [references/api-postgrest.md](references/api-postgrest.md) — Publishable/secret API keys, `overrideTypes<>()`, JSON field inference, Python type gen
- [references/js-client.md](references/js-client.md) — Node 20+ required, new filters, auth throw mode, `skipAutoInitialize`, CORS headers export
- [references/queues-cron.md](references/queues-cron.md) — Sub-minute pg_cron, `pgmq_public` queues via PostgREST
- [references/local-dev.md](references/local-dev.md) — Declarative schemas, storage bucket seeding, seed splitting, local backup restore
- [references/self-hosting.md](references/self-hosting.md) — Asymmetric keys, Supavisor pooler, reverse proxy overlays, migration guide
- [references/deployment.md](references/deployment.md) — Branch config, secret management (`env()`/`encrypted:`), deployment DAG, CLI commands
- [references/mcp-server.md](references/mcp-server.md) — Remote hosted MCP, feature groups, AI SDK integration, PostgREST MCP
- [references/breaking-changes.md](references/breaking-changes.md) — OpenAPI spec restricted, pg_graphql disabled, Edge Functions rate limits

## Quick Reference: New API Key Model

| Type | Format | Replaces | Notes |
|------|--------|----------|-------|
| Publishable | `sb_publishable_...` | `anon` JWT | Safe for client-side |
| Secret | `sb_secret_...` | `service_role` JWT | Browser-blocked (401) |

Both old and new keys work simultaneously. Not JWTs — gateway mints short-lived JWT internally. Platform-only (not CLI/self-hosted).

```typescript
// Client-side
const supabase = createClient(SUPABASE_URL, 'sb_publishable_...')
// Server-side
const supabase = createClient(SUPABASE_URL, 'sb_secret_...', {
  auth: { persistSession: false },
})
```

## Quick Reference: Auth

| Feature | API |
|---------|-----|
| OAuth 2.1 server | `supabase.auth.oauth.approveAuthorization(id)` |
| Custom OAuth/OIDC | `supabase.auth.admin.customProviders.createProvider({...})` |
| Web3 (Ethereum/Solana) | `supabase.auth.signInWithWeb3({ chain: 'ethereum' })` |
| JWT claims in Edge Fn | `supabase.auth.getClaims(token)` |
| Throw on error | `createClient(url, key, { auth: { throwOnError: true } })` |
| Skip auto-init (SSR) | `createClient(url, key, { auth: { skipAutoInitialize: true } })` |
| Before user hook | SQL function returning `{ "error": {...} }` to reject signup |

OAuth tokens include `client_id` claim — use in RLS to restrict OAuth client access:

```sql
CREATE POLICY "No OAuth access" ON sensitive_table FOR ALL USING (
  auth.uid () = user_id
  AND (auth.jwt () ->> 'client_id') IS NULL
);
```

## Quick Reference: Edge Functions

| Feature | Usage |
|---------|-------|
| Background tasks | `EdgeRuntime.waitUntil(promise)` |
| S3 mount read/write | `Deno.readFile('/s3/BUCKET/path')` |
| Ephemeral `/tmp` | 256MB free, 512MB paid; sync APIs only at top level |
| Wall clock | 150s free / 400s paid |
| CPU per request | 2s |
| Bundle size | 20MB |
| Functions/project | 100 free / 500 pro / 1000 team |

## Quick Reference: Realtime

Private channels require RLS on `realtime.messages` + `private: true`:

```js
await supabase.realtime.setAuth()
const channel = supabase.channel('room:123', { config: { private: true } })
```

Server-side broadcast: `SELECT realtime.send(payload, event, topic, private)`.

Broadcast replay (alpha, private channels only):

```js
const channel = supabase.channel('room:main', {
  config: { private: true, broadcast: { replay: { since: timestamp, limit: 10 } } },
})
```

## Quick Reference: Vector Buckets (Alpha)

```typescript
const bucket = supabase.storage.vectors.from('embeddings');
await bucket.createIndex({
  indexName: 'docs',
  dataType: 'float32',
  dimension: 1536,
  distanceMetric: 'cosine',
});

const index = bucket.index('docs');
await index.putVectors({
  vectors: [
    { key: 'doc-1', data: { float32: embedding }, metadata: { title: 'Doc' } },
  ],
});
const { data } = await index.queryVectors({
  queryVector: { float32: query },
  topK: 10,
  filter: { category: 'guide' },
});
```

SQL access via FDW: `WHERE data <==> '[...]'::embd ORDER BY embd_distance(data)`. Limits: 10 buckets, 10 indexes/bucket, 4096 dims.

## Quick Reference: Declarative Schemas

Place desired-state SQL in `supabase/schemas/`, then diff to generate migrations:

```bash
supabase db diff -f create_employees_table
```

```toml
[db.migrations]
schema_paths = ["./schemas/employees.sql", "./schemas/*.sql"]
```

## Quick Reference: Secret Management

```toml
# env() — reference env vars in any config field
[auth.external.github]
client_id = "env(GITHUB_CLIENT_ID)"
secret = "env(GITHUB_SECRET)"
```

```bash
supabase secrets set --env-file ./supabase/.env
```

## Quick Reference: Queues (pgmq_public)

```typescript
// Send
await supabase.schema('pgmq_public').rpc('send', {
  queue_name: 'my_queue',
  message: { hello: 'world' },
  sleep_seconds: 0,
});
// Read (with visibility timeout)
await supabase.schema('pgmq_public').rpc('read', {
  queue_name: 'my_queue',
  sleep_seconds: 30,
  n: 5,
});
// Pop (read + delete)
await supabase.schema('pgmq_public').rpc('pop', { queue_name: 'my_queue' });
```

Requires: enable `pgmq` extension, toggle "Expose Queues via PostgREST", enable RLS on `pgmq.q_<name>`.

## Quick Reference: JS Client (v2.74–v2.101)

| Change | Version | Details |
|--------|---------|---------|
| Node.js 20+ required | v2.79.0+ | `@supabase/node-fetch` removed; pin v2.78.0 for Node 18 |
| `notin()` filter | — | `.notin('id', [1,2,3])` |
| `isdistinct()` filter | — | `.isdistinct('deleted_at', null)` — NULL-safe |
| `overrideTypes<>()` | v2.48.0+ | Override query result types |
| Auth throw mode | v2.79.0+ | `{ auth: { throwOnError: true } }` |
| `detectSessionInUrl` fn | v2.88.0+ | Accepts predicate function |
| Functions timeout | v2.81.0+ | `signal: AbortSignal.timeout(30000)` |
| CORS headers | v2.95.0+ | `import { corsHeaders } from '@supabase/supabase-js/cors'` |
| `DatabaseWithoutInternals` | v2.89.0+ | Strips internal schemas from Database type |

## Quick Reference: MCP Server

Remote: `https://mcp.supabase.com/mcp` (HTTP transport, OAuth 2.1 auth).
Local CLI: `http://localhost:54321/mcp` (no OAuth).

Config via URL params: `?project_ref=...&read_only=true&features=database,docs`

Feature groups: `account`, `docs`, `database`, `debugging`, `development`, `functions`, `storage`, `branching`. All enabled by default except `storage`.

## Quick Reference: Sub-Minute Cron

```sql
SELECT cron.schedule('fast-poll', '30 seconds', 'SELECT process_pending()');
```

Valid: 1–59 seconds. Requires Postgres 15.1.1.61+.

## Breaking Changes (2025–2026)

- **OpenAPI spec via anon key removed** (Mar 2026) — use `service_role` or `sb_secret_` key
- **pg_graphql disabled by default** on new projects — `CREATE EXTENSION pg_graphql` to re-enable
- **PostgREST v14 JWT cache** — enabled by default (~20% more RPS); disable: `ALTER ROLE authenticator SET pgrst.jwt_cache_max_entries TO 0`
- **Edge Functions recursive call rate limit** (Mar 2026) — 5,000 req/min budget for function-to-function calls within a project
