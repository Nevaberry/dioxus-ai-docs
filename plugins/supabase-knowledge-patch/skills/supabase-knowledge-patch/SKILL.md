---
name: supabase-knowledge-patch
description: "Supabase platform changes since training cutoff — new API keys (sb_publishable/sb_secret), OAuth 2.1 server, Web3 auth, Realtime authorization, Vector/Analytics buckets, Edge Function S3 mounts, Queues (pgmq), MCP server, Branching. Load before working with Supabase."
license: MIT
metadata:
  author: Nevaberry
  version: "2025.04"
---

# Supabase Knowledge Patch

## New API Key Model (sb_publishable / sb_secret)

Supabase is replacing JWT-based `anon` and `service_role` keys with opaque API keys. Both old and new keys work simultaneously.

| Type | Format | Replaces |
|------|--------|----------|
| Publishable key | `sb_publishable_...` | `anon` JWT key |
| Secret key | `sb_secret_...` | `service_role` JWT key |

Key differences: independently rotatable, secret keys blocked in browsers (401 on browser User-Agent), multiple secret keys per project, gateway-minted short-lived JWTs.

```typescript
import { createClient } from '@supabase/supabase-js'
const supabase = createClient('https://your-ref.supabase.co', 'sb_publishable_...')
```

**Limitations**: Edge Functions only support JWT verification with old keys (use `--no-verify-jwt` with new keys + manual `apikey`-header auth). Not available in CLI/self-hosting. Cannot be sent as `Authorization: Bearer` (not JWTs). Public Realtime limited to 24h without user auth.

## Realtime Authorization (Quick Reference)

Broadcast and Presence now support RLS via `realtime.messages` table. Channels must use `private: true`.

```sql
CREATE POLICY "users can read broadcasts" ON "realtime"."messages" FOR
SELECT
  TO authenticated USING (
    EXISTS (
      SELECT
        1
      FROM
        public.rooms_users
      WHERE
        room_topic = (
          SELECT
            realtime.topic ()
        )
        AND user_id = auth.uid ()
    )
  );
```

```javascript
await supabase.realtime.setAuth();
const channel = supabase
  .channel('room:123', { config: { private: true } })
  .on('broadcast', { event: 'message' }, (payload) => console.log(payload))
  .subscribe();
```

**Broadcast from Database** is now the recommended approach over Postgres Changes — use `realtime.send()` and `realtime.broadcast_changes()` from triggers. See `references/realtime.md`.

## Edge Function Limits

| Limit | Value |
|-------|-------|
| Memory | 256 MB |
| Wall clock (free / paid) | 150s / 400s |
| CPU time per request | 2s |
| Bundle size | 20 MB |
| Max functions (free/pro/team) | 100 / 500 / 1000 |
| Max secrets | 100 (48 KiB each) |
| Recursive call rate limit | 5,000 req/min per chain |

Key patterns: `EdgeRuntime.waitUntil(promise)` for background tasks, S3 mounts at `/s3/<bucket>`, `/tmp` for ephemeral storage (256/512 MB). See `references/edge-functions.md`.

## Edge Function Auth: `getClaims()` Pattern

The `verify_jwt` flag is being replaced by explicit verification inside functions:

```typescript
const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SB_PUBLISHABLE_KEY')!, // New API key format
);
Deno.serve(async (req) => {
  const token = req.headers.get('Authorization')!.replace('Bearer ', '');
  const { data, error } = await supabase.auth.getClaims(token);
  if (!data?.claims?.email || error) {
    return Response.json({ msg: 'Invalid JWT' }, { status: 401 });
  }
  return Response.json({ message: `hello ${data.claims.email}` });
});
```

## Queues (pgmq) — Quick Reference

Supabase wraps `pgmq` with `pgmq_public` schema for Data API + RLS access. Client uses `supabase.schema('pgmq_public').rpc(...)`:

```typescript
// Send
await supabase.schema('pgmq_public').rpc('send', {
  queue_name: 'tasks',
  message: { type: 'process', id: 123 },
  sleep_seconds: 0,
});
// Read (with 30s visibility timeout)
const { data } = await supabase.schema('pgmq_public').rpc('read', {
  queue_name: 'tasks',
  sleep_seconds: 30,
  n: 5,
});
// Pop (read + delete atomically)
await supabase.schema('pgmq_public').rpc('pop', { queue_name: 'tasks' });
```

Expose locally: add `pgmq_public` to `[api] schemas` in `config.toml`. See `references/database-and-queues.md`.

## JS Client Breaking Changes

- **Node.js 20+ required** (v2.79.0+) — `@supabase/node-fetch` removed, native `fetch()` required
- **Monorepo restructure** (v2.74.0+) — all packages in `github.com/supabase/supabase-js`, single version number
- **New filter methods** (v2.84.0+): `.isDistinct()`, `.match(col, '~', regex)`, `.notin()` (v2.88.0)
- **`overrideTypes<>()`** — override inferred return types on any query
- **`throwOnError` for Auth** (v2.79.0) — `auth: { throwOnError: true }` in client options
- **`skipAutoInitialize`** (v2.97.0) — prevent auto session fetch on construction
- **`detectSessionInUrl` predicate** (v2.88.0) — function instead of boolean
- **`corsHeaders` export** (v2.95.3) — convenience CORS headers for Edge Functions
- **`FunctionsFetchError`** (v2.81.0) — normalized abort/timeout errors with `signal: AbortSignal.timeout(ms)`
- **`DatabaseWithoutInternals<>`** (v2.89.0) — strips internal schemas from Database type
- **Computed function inference** (v2.75.0) — PostgREST computed fields type-inferred in `.select()`
- **URL length validation** (v2.94.0) — catches oversized query URLs early

See `references/js-client.md` for full API details and examples.

## Platform Breaking Changes

- **OpenAPI spec requires secret key** — `/rest/v1/` schema endpoint no longer accepts `anon` key. Use `service_role` or `sb_secret_`. Normal data queries unaffected.
- **pg_graphql disabled by default** — new projects must `CREATE EXTENSION pg_graphql` manually
- **Python type generation** — `supabase gen types --lang python --linked > database_types.py`

## MCP Server

Hosted at `https://mcp.supabase.com/mcp` (HTTP transport, OAuth 2.1 login). Configure with URL params:

```json
{
  "mcpServers": {
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp?project_ref=abcdefghijkl&read_only=true&features=database,docs"
    }
  }
}
```

Feature groups: `account`, `docs`, `database`, `debugging`, `development`, `functions`, `storage`, `branching`. Local CLI MCP at `http://localhost:54321/mcp`. See `references/mcp-server.md`.

## Branching (Preview & Persistent)

Branching creates isolated environments (DB, API, Auth, Storage, Realtime). Preview branches are ephemeral (per-PR), persistent branches are long-lived:

```bash
supabase --experimental branches create --persistent
supabase --experimental branches list
```

Configure per-environment in `config.toml` with `[remotes.<name>]` blocks. See `references/cli-and-deployment.md`.

## Storage: Vector Buckets (Alpha)

Store and query embeddings via `supabase.storage.vectors`:

```typescript
const index = supabase.storage.vectors.from('embeddings').index('docs-openai')
await index.putVectors({ vectors: [{ key: 'doc-1', data: { float32: embedding }, metadata: { title: 'Doc' } }] })
const { data } = await index.queryVectors({
  queryVector: { float32: query }, topK: 10,
  filter: { category: 'electronics', price: { $lte: 500 } },
  returnDistance: true, returnMetadata: true,
})
```

SQL access via `<===>` operator and `embd_distance()`. See `references/storage.md`.

## Reference Files

| File | Contents |
|------|----------|
| [auth.md](references/auth.md) | OAuth 2.1 server, custom OAuth/OIDC providers, Web3 auth (Ethereum/Solana), auth hooks via HTTP, OAuth token security with RLS |
| [realtime.md](references/realtime.md) | Private channel authorization, broadcast from database, broadcast replay, realtime limits |
| [edge-functions.md](references/edge-functions.md) | Background tasks (waitUntil), S3 mounts, ephemeral storage, getClaims auth, MCP on Edge Functions, runtime config |
| [storage.md](references/storage.md) | Vector buckets API + SQL access, analytics buckets (Iceberg) |
| [database-and-queues.md](references/database-and-queues.md) | OrioleDB, CLI postgres config, replication pipelines (ETL), Wasm FDWs, queues (pgmq/pgmq_public), cron + queues pattern |
| [js-client.md](references/js-client.md) | Monorepo restructure, Node 20 requirement, new filters, overrideTypes, throwOnError, JSON type inference, computed functions, skipAutoInitialize, detectSessionInUrl, corsHeaders, FunctionsFetchError |
| [cli-and-deployment.md](references/cli-and-deployment.md) | Declarative schemas, storage bucket seeding, multiple seeds, backup restore, branching config, encrypted secrets, deployment DAG, webhooks, CI credentials, config push, pgdelta, db lint, inspect, edge function debugging |
| [self-hosting.md](references/self-hosting.md) | Supavisor connection pooler, new API keys (ES256), self-hosted edge functions, MCP server access, platform-to-self-hosted restore, HTTPS overlays, custom email templates |
| [mcp-server.md](references/mcp-server.md) | Hosted MCP server config, feature groups and tools, local CLI MCP, AI SDK integration (createToolSchemas), PostgREST MCP server |
