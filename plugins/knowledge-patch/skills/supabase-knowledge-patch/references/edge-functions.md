# Edge Functions

## Authoring and deployment

### Dashboard-managed Edge Functions and Deno 2.1

The Dashboard can create, test, edit, and deploy Functions without CLI or Docker, using templates for Storage uploads, AI proxying, and payment webhooks. The runtime moved to Deno 2.1.

### Function-local dependencies and entrypoints

Give every function its own `deno.json`; a shared file under `supabase/functions` can work locally but is discouraged for deployment. `deno.json` wins over legacy `import_map.json`. Put private-package `.npmrc` per function, or set `NPM_CONFIG_REGISTRY` at deployment.

Custom entrypoints need CLI 1.215.0+ and are relative to `supabase/config.toml`; `.ts`, `.js`, `.tsx`, `.jsx`, `.mjs` are accepted.

```toml
[functions.legacy-processor]
entrypoint = "./functions/legacy-processor/index.js"
```

### SDK-synchronized CORS headers

Since `@supabase/supabase-js` 2.95.0, use `corsHeaders` from `@supabase/supabase-js/cors` for both preflight and actual responses so new client headers remain synchronized.

```ts
import { corsHeaders } from '@supabase/supabase-js/cors'

Deno.serve((req) => req.method === 'OPTIONS'
  ? new Response('ok', { headers: corsHeaders })
  : Response.json({ ok: true }, { headers: corsHeaders }))
```

### Edge Function bundle portability and legacy Node deployment

Complete bundles can be uploaded as zip files, CLI can download deployed Functions without Docker, and legacy Node.js applications can be deployed as Functions.

### Multi-runtime server SDK

`@supabase/server` handles authentication, client creation, CORS, and context injection for Functions, Vercel Functions, Deno, Bun, and Cloudflare Workers.

### Built-in AI session backends

The runtime exposes `Supabase.ai.Session` without a package. `gte-small` produces English embeddings and truncates inputs to 512 tokens. `AI_INFERENCE_API_HOST` points at a self-managed inference server; default mode is `ollama`, while `openaicompatible` targets an API-compatible server. Pass `stream: false` for a non-streaming response.

Hosted LLM inference is not generally available; production needs a separately deployed server and a production `AI_INFERENCE_API_HOST` secret.

## Filesystems and asynchronous work

### S3-backed filesystem mounts

Set `S3FS_ENDPOINT_URL`, `S3FS_REGION`, `S3FS_ACCESS_KEY_ID`, and `S3FS_SECRET_ACCESS_KEY` as secrets to mount any S3-compatible service. Buckets appear under `/s3/<bucket>` with no platform count limit.

```ts
await Deno.writeTextFile('/s3/reports/latest.txt', 'complete')
const report = await Deno.readTextFile('/s3/reports/latest.txt')
```

### Invocation-scoped temporary storage

`/tmp` resets per invocation and offers 256 MB Free/512 MB paid. Async Deno/Node filesystem calls work in handlers/background tasks. Sync filesystem APIs are allowed only in initial module evaluation, not handlers, timers, or callbacks.

### Background work and local worker lifetime

`EdgeRuntime.waitUntil(promise)` keeps work alive after the response within worker limits. `beforeunload` receives shutdown reason; `unhandledrejection` observes background failures. Locally, enable worker reuse for post-response work:

```toml
[edge_runtime]
policy = "per_worker"
```

### Direct-database TLS in local functions

Hosted raw Postgres clients use SSL through injected `SUPABASE_DB_URL`. Locally, download the DB certificate and set these before serving with verification:

```dotenv
SSL_CERT_FILE=/path/to/cert.crt
DENO_TLS_CA_STORE=mozilla,system
```

## Environment, limits, and routing

### Injected environment and secret lifecycle

Default variables are `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_URL`. New publishable/secret keys are not injected; add them under `SB_` because user secrets cannot use reserved `SUPABASE_`.

Hosted invocations also get `SB_REGION`, per-instance `SB_EXECUTION_ID`, and `DENO_DEPLOYMENT_ID` formatted `<project-ref>_<function-id>_<version>`. Hosted secret changes apply immediately without redeployment.

### JWKs in local Edge Function environments

Locally served Functions receive configured JWKs as a non-internal environment value for code that needs local key material.

### Hosted runtime and project limits

Workers: 256 MB; 150s Free/400s paid wall lifetime; 2s CPU/request excluding async I/O; response must begin within 150s idle timeout. Bundle cap: 20 MB. Functions per project: Free 100, Pro 500, Team 1,000, Enterprise unlimited. Logs: 100 events/10s/function, 10,000 chars/message. Secrets: 100/project, names 256 chars, values 24,576 chars.

### Hosted runtime restrictions

Outbound SMTP 25/587 is blocked. Without a custom domain, GET `text/html` becomes `text/plain`. Web Workers, Node `vm`, and multithreading-dependent Node libraries are unsupported. Static files cannot deploy through the API path; use CLI Docker bundling.

### Nested invocation throttling

Function-to-function calls in one project share at least 5,000/minute per request chain; recursion, chains, cycles, and fan-out count, while inbound/external calls do not. Exhaustion throws `Deno.errors.RateLimitError`; use `retryAfterMs`.

```ts
try {
  return await fetch(otherFunctionUrl, options)
} catch (error) {
  if (error instanceof Deno.errors.RateLimitError) {
    return new Response('retry later', {
      status: 429,
      headers: { 'Retry-After': String(Math.ceil(error.retryAfterMs / 1000)) },
    })
  }
  throw error
}
```

### Region selection and introspection

Default placement is near the caller. Pin DB-heavy calls through the client `region` option, `x-region`, or `forceFunctionRegion` query parameter. Response `x-sb-edge-region` and function `SB_REGION` reveal selection. Explicit regions do not fail over; callers must switch during outages.

### Runtime failure status codes

Uncaught execution: `500 WORKER_ERROR`; startup/dependency: `503 BOOT_ERROR`; idle response timeout: `504`; CPU/memory/resource: custom `546 WORKER_LIMIT`, with resource in logs.

## WebSockets and alternate runtimes

### WebSocket servers and relays

Functions support inbound/outbound WebSockets. Return the response paired by `Deno.upgradeWebSocket()`:

```ts
Deno.serve((req) => {
  if (req.headers.get('upgrade')?.toLowerCase() !== 'websocket') {
    return new Response('WebSocket upgrade required', { status: 400 })
  }
  const { socket, response } = Deno.upgradeWebSocket(req)
  socket.onmessage = (event) => socket.send(event.data)
  return response
})
```

Browser sockets cannot attach normal authorization headers. Disable platform JWT verification and validate a query token or custom subprotocol before upgrade; query tokens may enter logs. Local sockets require `per_worker` (and lose edit auto-reload). Hosted sockets end at normal worker limits.

### Dart Edge maintenance status

Dart Edge can compile experimental Dart Functions, but recurring Dart/Wasm changes have left it unmaintained. Do not depend on it as a stable production route.

### Hono starter bootstrap

Bootstrap a Hono starter preconfigured with `@supabase/supabase-js` and `@supabase/ssr`; enable anonymous sign-ins for its flow.

```sh
npx supabase@latest bootstrap hono
```

### Unauthenticated MCP servers on Edge Functions

Host a server with `McpServer`, `WebStandardStreamableHTTPServerTransport`, and an Edge router such as Hono. The documented deployment has no authentication, so disable JWT verification locally and hosted:

```sh
supabase functions new mcp
supabase functions serve --no-verify-jwt mcp
supabase functions deploy --no-verify-jwt mcp
```

Endpoints are local `/functions/v1/mcp` and hosted `https://<project-ref>.supabase.co/functions/v1/mcp`. Match Hono `basePath` to another function name. Streamable HTTP must accept `application/json` and `text/event-stream`.
