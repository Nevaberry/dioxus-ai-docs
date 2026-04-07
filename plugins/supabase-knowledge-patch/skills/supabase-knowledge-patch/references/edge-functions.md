# Edge Functions

## Background Tasks (`EdgeRuntime.waitUntil`)

Edge Functions can now run background tasks outside the request handler. Respond immediately while processing continues asynchronously.

```ts
Deno.serve(async (req) => {
  // Process in background — does NOT block the response
  EdgeRuntime.waitUntil(asyncLongRunningTask())

  return new Response('accepted')
})
```

`EdgeRuntime.waitUntil(promise)` can be called at top level or inside the request handler. The function instance stays alive until all `waitUntil` promises resolve.

Listen for shutdown with `beforeunload`:

```ts
addEventListener('beforeunload', (ev) => {
  console.log('Shutting down:', ev.detail?.reason)
})
```

For local testing, background tasks require `per_worker` policy (default `oneshot` terminates after each request):

```toml
[edge_runtime]
policy = "per_worker"
```

## S3 Mounts (Persistent Storage)

Mount any S3-compatible bucket (including Supabase Storage) as a filesystem path. Read/write files using standard Deno file APIs — no SDK needed.

Set these secrets:
- `S3FS_ENDPOINT_URL`
- `S3FS_REGION`
- `S3FS_ACCESS_KEY_ID`
- `S3FS_SECRET_ACCESS_KEY`

Access files at `/s3/BUCKET-NAME/path`:

```ts
// Read from S3
const data = await Deno.readFile('/s3/my-bucket/results.csv')

// Write to S3
await Deno.writeTextFile('/s3/my-bucket/demo.txt', 'hello world')

// Create directories
await Deno.mkdir('/s3/my-bucket/sub-dir')
```

No size limits on S3 mounts.

## Ephemeral Storage (`/tmp`)

Write temporary files to `/tmp` during a single invocation. Resets between invocations.

Limits: 256MB (free), 512MB (paid).

Synchronous file APIs (`Deno.readFileSync`, `Deno.writeFileSync`, `Deno.statSync`, etc.) are **only available during initial script evaluation** — they throw errors inside `Deno.serve()` callbacks or `setTimeout`:

```ts
Deno.statSync('/tmp/file')  // ✅ works at top level

Deno.serve(() => {
  Deno.statSync('/tmp/file')  // ❌ ERROR: blocklisted in this context
})
```

## New Auth Pattern: `getClaims()` + Publishable Keys

The legacy `verify_jwt` flag is being replaced. Instead, verify JWTs manually inside your function using asymmetric keys:

```ts
const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SB_PUBLISHABLE_KEY')!
)

Deno.serve(async (req) => {
  const token = req.headers.get('Authorization')!.replace('Bearer ', '')
  const { data, error } = await supabase.auth.getClaims(token)

  if (!data?.claims?.email || error) {
    return Response.json({ msg: 'Invalid JWT' }, { status: 401 })
  }

  return Response.json({ message: `hello ${data.claims.email}` })
})
```

New API keys use `SB_PUBLISHABLE_KEY` (replaces `SUPABASE_ANON_KEY`). Not yet auto-exposed in Edge Functions — set manually as secrets with `SB_` prefix.

## Updated Limits

| Limit | Value |
|-------|-------|
| Memory | 256MB |
| Wall clock (free) | 150s |
| Wall clock (paid) | 400s |
| CPU time per request | 2s |
| Bundle size | 20MB |
| Functions per project | 100 (free) / 500 (pro) / 1000 (team) |
| Secrets per project | 100 (max 48 KiB each) |

HTML content restriction: `GET` requests returning `text/html` are rewritten to `text/plain` unless you use a custom domain. Web Workers and Node `vm` API are not available.
