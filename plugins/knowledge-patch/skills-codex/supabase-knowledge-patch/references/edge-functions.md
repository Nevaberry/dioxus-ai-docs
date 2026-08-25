# Edge Functions

## Canonical Edge Function CORS headers (supabase-js-2.101.0)

Supabase JS exports canonical CORS headers for Edge Functions.

## Function invocation handling (supabase-js-2.101.0)

Function calls support a configurable timeout, normalize abort and timeout failures as `FunctionsFetchError`, parse `application/pdf` responses, and stringify object bodies even when a custom `Content-Type` is supplied. Edge runtimes also expose `RateLimitError` in the `Deno.errors` namespace.

## Per-function dependency manifests

For deployment, each function should keep its own `deno.json` and, for private packages, its own `.npmrc`; global files under `supabase/functions` are supported locally but are not recommended for deployed isolation. Import maps are legacy, and a colocated `deno.json` takes precedence when both exist.

```json
{ "imports": { "supabase": "npm:@supabase/supabase-js@2" } }
```

## Publishable keys are not injected automatically

The new publishable keys are not yet default Edge Function environment variables. Add one explicitly as a secret using an `SB_` name—the `SUPABASE_` prefix is reserved—then read that name when constructing the client.

```sh
supabase secrets set SB_PUBLISHABLE_KEY=<key>
```

## S3 buckets as mounted filesystems

An Edge Function can mount any S3-compatible bucket and use normal filesystem APIs beneath `/s3/<bucket>`; configure `S3FS_ENDPOINT_URL`, `S3FS_REGION`, `S3FS_ACCESS_KEY_ID`, and `S3FS_SECRET_ACCESS_KEY`. The platform does not limit the number of persistent buckets mounted this way.

```ts
await Deno.writeTextFile('/s3/my-bucket/results.txt', 'done')
```

## Ephemeral filesystem boundaries

`/tmp` is reset for every invocation and is limited to 256 MB on Free or 512 MB on paid projects. Synchronous Deno and Node filesystem calls work only during initial module evaluation and are blocklisted in request handlers, timers, and other callbacks; use asynchronous calls there.

## Static files in function bundles

CLI 2.7.0 or later can bundle assets declared with `static_files`. Such functions must use the CLI's Docker-based bundling path and cannot deploy through the `--use-api` path.

```toml
[functions.wasm-add]
static_files = ["./functions/wasm-add/add-wasm/pkg/*"]
```

## Long-lived local workers

The local CLI normally terminates an instance after its request, which cuts off background work and WebSockets. Use the per-worker policy to keep it alive; this also disables automatic reload after edits.

```toml
[edge_runtime]
policy = "per_worker"
```

## Nested-call rate-limit scope

Outbound calls from one Edge Function to another in the same project share a per-request-chain budget of at least 5,000 calls per minute; inbound calls and calls to external APIs do not consume it. On exhaustion, `Deno.errors.RateLimitError.retryAfterMs` gives the retry delay.

## Explicit regional invocation

Invocations normally run near the caller, but the SDK `region` option, `x-region` header, or `forceFunctionRegion` query parameter can pin execution; inspect `x-sb-edge-region` in the response or `SB_REGION` in the function. Explicitly pinned requests do not fail over to another region during an outage.

```sh
curl -H 'x-region: us-east-1' \
  https://<project-ref>.supabase.co/functions/v1/<function>
```

## Hosted execution ceilings

Hosted functions have 256 MB of memory, two seconds of CPU per request, a 150-second response-idle timeout, and worker wall-clock limits of 150 seconds on Free or 400 seconds on paid plans; bundled functions are capped at 20 MB. A worker stopped for exceeding resources returns the custom `546` status with `WORKER_LIMIT`.

## Log and secret quotas

A log message is capped at 10,000 characters and a function can emit 100 events per ten seconds. Projects can hold 100 secrets; names are capped at 256 characters, values at 48 KiB, and names cannot start with `SUPABASE_`.

## Runtime compatibility restrictions

Outbound SMTP connections on ports 25 and 587 are blocked, and without a custom domain a `GET` response labeled `text/html` is rewritten to `text/plain`. Web Workers, Node's `vm` API, and Node libraries that require multithreading are unsupported.

## WebSocket authentication and lifetime

Edge Functions support inbound and outbound WebSockets, but browser clients cannot attach the normal custom authorization header. Disable gateway JWT verification and validate a token inside the handler through a query parameter or custom subprotocol—bearing in mind that query strings may be logged—and design connections to end at the worker wall-clock limit.

## Edge Function dashboard outside the hosted platform

Self-hosted and CLI environments can use the dashboard to list, search, inspect, test, and download Edge Functions as ZIP files; these controls are no longer cloud-only.

## Portable and legacy Edge Function deployment

The dashboard accepts complete Function bundles as drag-and-drop ZIP files, while the CLI can download Functions without Docker. Edge Functions can also deploy legacy Node.js applications.

## Bulk Edge Function secret editing

The platform now supports bulk-pasting Function secrets and editing individual secrets, reducing the need to update them one at a time.

## Per-function Edge Function metrics (1.26.08)

The Edge Functions overview now shows each function's error rate, execution time, CPU use, and memory use.
