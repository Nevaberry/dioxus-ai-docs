# Edge Functions

## Background Tasks with `EdgeRuntime.waitUntil()`

Edge Functions can now run background tasks outside the request handler using the Supabase-specific `EdgeRuntime.waitUntil(promise)` API. The function instance stays alive until the promise resolves.

```typescript
Deno.serve(async (req) => {
  // Won't block the response — runs in background
  EdgeRuntime.waitUntil(asyncLongRunningTask());
  return new Response('Accepted', { status: 202 });
});

// Listen for shutdown to save state
addEventListener('beforeunload', (ev) => {
  console.log('Shutting down:', ev.detail?.reason);
});
```

For local testing, background tasks require `per_worker` policy (default terminates instances after each request):

```toml
[edge_runtime]
policy = "per_worker"
```

## S3 Persistent Storage Mounts

Edge Functions can mount any S3-compatible bucket (including Supabase Storage) as a POSIX filesystem at `/s3/<bucket-name>`. Set these secrets: `S3FS_ENDPOINT_URL`, `S3FS_REGION`, `S3FS_ACCESS_KEY_ID`, `S3FS_SECRET_ACCESS_KEY`.

```typescript
// Read/write S3 as local files
const data = await Deno.readFile('/s3/my-bucket/results.csv');
await Deno.writeTextFile('/s3/my-bucket/output.txt', 'hello world');
await Deno.mkdir('/s3/my-bucket/sub-dir');
```

No size limits on S3 mounts. Combine with `EdgeRuntime.waitUntil()` for large file processing workflows.

## Ephemeral Storage (`/tmp`)

Write temporary files to `/tmp` during a single invocation. Resets between invocations. Limits: 256MB (free), 512MB (paid).

```typescript
// Write uploaded file to temp, process in background
await Deno.writeFile(`/tmp/${uploadId}.zip`, req.body);
EdgeRuntime.waitUntil(processZipFile(uploadId, `/tmp/${uploadId}.zip`));
```

**Important**: Synchronous file APIs (`Deno.statSync`, `Deno.readFileSync`, etc.) only work during initial script evaluation — they throw errors inside `Deno.serve()` handlers or `setTimeout` callbacks.

## Auth: `getClaims()` Replaces Implicit JWT Verification

The `verify_jwt` flag is being replaced by explicit JWT verification inside the function. New pattern uses `supabase.auth.getClaims(token)`:

```typescript
const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SB_PUBLISHABLE_KEY')!, // New API key format (sb_ prefix)
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

New API keys use `SB_PUBLISHABLE_KEY` (replacing `SUPABASE_ANON_KEY`). Must be manually set as secrets with the `SB_` prefix for now.

## Runtime Limits

| Limit | Value |
|-------|-------|
| Memory | 256MB |
| Wall clock (free) | 150s |
| Wall clock (paid) | 400s |
| CPU time per request | 2s |
| Request idle timeout | 150s |
| Bundle size | 20MB |
| Max functions (free/pro/team) | 100 / 500 / 1000 |
| Max secrets | 100 (48 KiB each, no `SUPABASE_` prefix) |

HTML serving requires custom domains — `GET` requests returning `text/html` are rewritten to `text/plain` otherwise. Outgoing ports 25/587 blocked. No Web Worker or Node `vm` API.

## Edge Runtime Config: Deno 2 and Worker Policy

Configure the edge runtime in `config.toml`:

```toml
[edge_runtime]
enabled = true
policy = "per_worker"    # Keep instance alive across requests (needed for background tasks)
deno_version = 2         # Use Deno 2 runtime
```

## MCP Server on Edge Functions (mcp-lite)

Build and deploy MCP (Model Context Protocol) servers on Edge Functions using `mcp-lite` — a zero-dependency TypeScript framework:

```bash
npm create mcp-lite@latest  # Select "Supabase Edge Functions" template
```

Uses Hono for routing with a two-app pattern (outer app for function-name routing, inner app for MCP endpoints):

```typescript
import { McpServer, StreamableHttpTransport } from 'mcp-lite';
import { Hono } from 'hono';
import { z } from 'zod';

const mcp = new McpServer({
  name: 'my-mcp-server',
  version: '1.0.0',
  schemaAdapter: (schema) => z.toJSONSchema(schema as z.ZodType),
});

mcp.tool('sum', {
  description: 'Adds two numbers',
  inputSchema: z.object({ a: z.number(), b: z.number() }),
  handler: (args) => ({
    content: [{ type: 'text', text: String(args.a + args.b) }],
  }),
});

const transport = new StreamableHttpTransport();
const httpHandler = transport.bind(mcp);

const mcpApp = new Hono();
mcpApp.all('/mcp', async (c) => httpHandler(c.req.raw));

const app = new Hono();
app.route('/mcp-server', mcpApp); // Mount at /<function-name>

Deno.serve(app.fetch);
```

Deploy with `supabase functions deploy --no-verify-jwt mcp-server`. Server available at `https://<ref>.supabase.co/functions/v1/mcp-server/mcp`.

## Recursive/Nested Call Rate Limit

Outbound `fetch()` calls from one Edge Function to another Edge Function within the same project are rate-limited to a minimum of 5,000 requests per minute per request chain. This applies to direct recursion, function chaining, circular calls, and fan-out patterns.

Inbound requests and calls to external APIs (Stripe, OpenAI, etc.) are **not** subject to this limit. Only function-to-function calls are counted.

To avoid rate limits in recursive patterns: batch work in a single function invocation, use queues (pgmq) instead of chaining, or reduce fan-out concurrency.
