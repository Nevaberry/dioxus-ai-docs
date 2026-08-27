# Runtime compatibility

Use the Worker's compatibility date and flags as the source of truth. The
date-gated runtime guidance here includes batch `2025` and batch `2026`.

## Requests, Fetch, and Cache

### Incoming cancellation

`enable_request_signal` exposes client cancellation through the incoming
`Request.signal` from compatibility date `2025-05-22`.
`request_signal_passthrough` propagates that signal when forwarding the request
with `fetch()` from `2025-05-05`. Enable both behaviors when cancellation must
reach a downstream origin or service.

### Cache precedence and revalidation

From `2025-05-19`, a request's `cf` settings passed to the Cache API override
Cache Rules for user-owned or grey-clouded sites.

From `2025-08-07`, `fetch(url, { cache: "no-cache" })` is accepted. For
subrequests to origins outside the platform, it forces conditional origin
revalidation even when the cached response is fresh and adds
`Pragma: no-cache` and `Cache-Control: no-cache`.

### Per-request variation with `cf.vary`

Subrequests can use `cf.vary` to control how one origin response carrying a
`Vary` header is cached. Rules can bypass headers without explicit handling and
normalize selected values:

```ts
return fetch(request, {
  cf: {
    vary: {
      default: { action: "bypass" },
      headers: {
        accept: {
          action: "normalize",
          media_types: ["text/html", "application/json"],
        },
      },
    },
  },
});
```

### Cross-origin redirects

From `2025-09-01`, `fetch()` strips `Authorization` while following a redirect
to another origin. Use `retain_authorization_on_cross_origin_redirect` only
when retaining credentials across that boundary is intentional.

### Iterable bodies

From `2026-02-19`, synchronous and asynchronous iterables used as `Request` or
`Response` bodies are streamed rather than stringified or treated as ordinary
objects. Arrays no longer become strings such as `"1,2,3"`. A synchronous
iterable that defines its own `toString` or `Symbol.toPrimitive` remains on the
string-coercion path.

```js
const body = (async function* () {
  yield new TextEncoder().encode("hello");
})();
return new Response(body);
```

## Web-platform behavior

### URLPattern, import attributes, and EventTarget

- `2025-05-01` selects the standards-compliant `URLPattern`; use
  `urlpattern_original` only as a rollback.
- `2025-06-16` makes unknown import attributes throw.
- `2025-08-01` binds an `EventTarget` listener's `this` to its target.
- The undated `pedantic_wpt` flag initially tightens `Event` and `EventTarget`
  behavior.
- `enable_navigator_language` exposes `navigator.language`, whose value is
  always `en`.

### Weak references and finalizers

From `2025-05-05`, `enable_weak_ref` exposes `WeakRef` and
`FinalizationRegistry`. Finalizers are nondeterministic and may never run. A
finalizer may execute after the handler completes, has no associated async
context, and cannot perform I/O or emit tail events. Never use it for required
cleanup.

### Added JavaScript and messaging APIs

The runtime added explicit resource management and `Float16Array` in May,
global `MessageChannel` and `MessagePort` in August, and `Uint8Array` base64 and
hex operations with the V8 14.0 rollout. The global messaging constructors can
also be enabled explicitly with `expose_global_message_channel`.

### Fresh event contexts and AsyncLocalStorage isolation

Each event-handler invocation now receives a fresh `ctx`, retroactively across
compatibility dates. `nonclass_entrypoint_reuses_ctx_across_invocations`
restores the former reuse behavior.

From `2025-06-16`, AsyncLocalStorage snapshots and bound functions belong to
the request that created them and throw when invoked from another request.

### Startup evaluation

From `2025-06-01`, `eval()` and `new Function()` are allowed during startup.
`disallow_eval_during_startup` restores the earlier startup error behavior.

### Optional runtime fields

From `2025-12-03`, optimized runtime structs explicitly install optional
properties with the value `undefined` rather than omitting the properties.
Test values rather than property presence:

```js
if (obj.key !== undefined) {
  // The optional value is available.
}
```

Do not rely on `"key" in obj` or `Object.hasOwn(obj, "key")` to distinguish an
absent optional value.

### Unhandled rejection timing

From `2026-03-03`, `unhandledrejection` processing waits for the current
microtask checkpoint. A rejection handler added later in the same
multi-microtask promise chain can prevent the event.

## Text, streams, and serialization

### Text decoding

From `2026-01-13`, stream `readAllText()` strips a leading UTF-8 BOM;
`do_not_strip_bom_in_read_all_text` restores the old result. The `2026-02-24`
and `2026-03-03` gates replace lone UTF-16LE surrogates with U+FFFD and select
standards-oriented CJK and Big5 decoding.

### Encoding-stream backpressure

From `2026-03-24`, `TextEncoderStream` and `TextDecoderStream` use a readable
high-water mark of 0. Writes therefore wait for a reader to pull instead of
clearing backpressure during startup. The same date selects standards-compliant
`WritableStream` writer-lock and release behavior.

### Structured error serialization

From `2026-04-21`, `structuredClone()` and V8 serialization preserve more
error types and an error object's own properties. Deserialization does not
preserve the original stack by default. `legacy_error_serialization` restores
the older basic-error behavior.

## Execution, email, and observability

### Automatic tracing and tail warnings

From `2025-11-05`, `"observability": { "enabled": true }` also enables
automatic Workers tracing. With an older compatibility date, opt in through:

```jsonc
{
  "observability": { "traces": { "enabled": true } }
}
```

Preview warnings that were formerly visible only in DevTools are also sent to
an attached tail Worker.

### Forwardable email headers

From `2025-08-01`, `set_forwardable_email_full_headers` makes email Workers
receive all values for headers such as `To` and `Cc`, rather than one truncated
value.

### Dynamic Workers

Dynamic Worker creation accepts a null name. The runtime update of
`2026-04-17` also permits custom limits when creating a Dynamic Worker.

## Worker-level Access

The Access and local-identity guidance in this section comes from batch
`2026-07-30-2026-08-14`.

An Access policy can attach to the Worker itself and automatically protect its
routes, custom domains, `workers.dev` URL, and preview URLs as they change. An
account-wide default can cover existing and future Workers, with per-Worker
bypasses and separate preview-only or preview-and-production scopes.

Authenticated requests expose `ctx.access.aud` and
`await ctx.access.getIdentity()`. Test locally by injecting an identity with
`access.dev`; removing the block simulates an unauthenticated request.

```jsonc
{
  "access": {
    "dev": {
      "aud": "my-app",
      "identity": { "email": "admin@example.com" }
    }
  }
}
```

```js
export default {
  async fetch(request, env, ctx) {
    if (!ctx.access) return new Response("Unauthorized", { status: 401 });
    const identity = await ctx.access.getIdentity();
    return Response.json({ aud: ctx.access.aud, email: identity?.email });
  },
};
```
