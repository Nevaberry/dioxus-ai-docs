# Runtime and Web-Platform Behavior

Use this reference when a compatibility-date change affects request handling,
fetch or cache behavior, JavaScript and stream semantics, runtime structures,
Access, tracing, email, or Dynamic Workers.

Relevant source batches: `2025`, `2026`, and
`2026-07-30-2026-08-14`.

## Incoming request cancellation

`enable_request_signal` exposes incoming-request cancellation through
`Request.signal` from compatibility date `2025-05-22`.
`request_signal_passthrough` propagates that signal when forwarding the request
with `fetch()` from compatibility date `2025-05-05`.

Enable both behaviors when a forwarded subrequest should stop after its client
disconnects.

## Cache API and `fetch()` cache controls

From `2025-05-19`, a Request's `cf` settings passed to the Cache API override
Cache Rules for user-owned or grey-clouded sites.

From `2025-08-07`, `fetch(url, { cache: "no-cache" })` is accepted. For
subrequests to origins outside the platform, it forces revalidation with a
conditional origin request even when the cache entry is fresh. It also adds
`Pragma: no-cache` and `Cache-Control: no-cache`.

## Per-request variation with `cf.vary`

Workers subrequests accept `cf.vary` to control caching of one origin response
that carries a `Vary` header. Rules can bypass unconfigured headers and
normalize configured values:

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

## Cross-origin redirect authorization

From compatibility date `2025-09-01`, `fetch()` strips `Authorization` when it
follows a redirect to a different origin. Set
`retain_authorization_on_cross_origin_redirect` only when credentials are
intended for the redirected origin.

## Web-platform conformance gates

- `2025-05-01` selects the standards-compliant `URLPattern`; use
  `urlpattern_original` for rollback.
- `2025-06-16` makes unknown import attributes throw.
- `2025-08-01` binds an `EventTarget` listener's `this` to its target.
- The undated `pedantic_wpt` flag initially applies stricter behavior to
  `Event` and `EventTarget`.
- The undated `enable_navigator_language` flag exposes `navigator.language`,
  whose value is always `en`.

## Weak references and finalizers

From `2025-05-05`, `enable_weak_ref` exposes `WeakRef` and
`FinalizationRegistry`. Finalizers are nondeterministic and may never run. A
finalizer can run after its handler completes, has no associated async context,
and cannot perform I/O or emit tail events. Never use a finalizer for required
cleanup or externally visible work.

## JavaScript and messaging APIs

Workers added explicit resource management and `Float16Array` in May, global
`MessageChannel` and `MessagePort` in August, and `Uint8Array` base64 and hex
operations with the V8 14.0 rollout. The global messaging constructors can be
enabled explicitly with `expose_global_message_channel`.

## Fresh execution contexts

Every event-handler invocation receives a fresh `ctx`, including for earlier
compatibility dates. `nonclass_entrypoint_reuses_ctx_across_invocations`
restores the previous reuse behavior.

From `2025-06-16`, `AsyncLocalStorage` snapshots and bound functions belong to
the request that created them. Invoking one from another request throws. Do not
store request-scoped ALS helpers for reuse across invocations.

## Startup evaluation

From compatibility date `2025-06-01`, `eval()` and `new Function()` are allowed
during Worker startup. `disallow_eval_during_startup` restores startup errors.
This gate does not imply that arbitrary dynamic evaluation is suitable for
request handling.

## Optional runtime fields

From `2025-12-03`, an optimized runtime struct representation installs optional
properties explicitly with value `undefined` rather than omitting them. Test:

```js
if (obj.key !== undefined) {
  // use obj.key
}
```

Do not infer a usable value from `"key" in obj` or
`Object.hasOwn(obj, "key")`.

## Forwardable email headers

From compatibility date `2025-08-01`,
`set_forwardable_email_full_headers` lets email Workers receive every value for
headers such as `To` and `Cc`, rather than one truncated value.

## Text decoding

- From `2026-01-13`, stream `readAllText()` strips a leading UTF-8 BOM. Use
  `do_not_strip_bom_in_read_all_text` to retain it.
- The `2026-02-24` gate replaces lone UTF-16LE surrogates with U+FFFD.
- The `2026-03-03` gate selects standards-oriented CJK and Big5 decoding.

Treat decoded-text fixtures as compatibility-date dependent when changing any
of these gates.

## Iterable fetch bodies

From `2026-02-19`, synchronous and asynchronous iterables supplied as
`Request` or `Response` bodies are consumed as streaming content instead of
being stringified or treated as ordinary objects. Arrays therefore no longer
become strings such as `"1,2,3"`.

A synchronous iterable that defines its own `toString` or `Symbol.toPrimitive`
remains on the string-coercion path.

```js
const body = (async function* () {
  yield new TextEncoder().encode("hello");
})();
return new Response(body);
```

## Unhandled rejection timing

From `2026-03-03`, `unhandledrejection` processing waits for the current
microtask checkpoint. A handler attached later in the same multi-microtask
promise chain can prevent the event rather than racing an early report.

## Encoding-stream backpressure and writers

From `2026-03-24`, `TextEncoderStream` and `TextDecoderStream` use readable
high-water mark 0. A write waits until a reader pulls instead of clearing
backpressure during startup. The same compatibility date selects
standards-compliant `WritableStream` writer locking and release behavior.

Audit code that writes before establishing a reader, or that relies on earlier
writer-lock release behavior.

## Structured error serialization

From `2026-04-21`, `structuredClone()` and V8 serialization preserve more error
types and an error object's own properties. Deserialization does not preserve
the original stack by default. `legacy_error_serialization` retains the earlier
basic-error behavior.

## Dynamic Workers

Dynamic Worker creation accepts a null name. The runtime update of `2026-04-17`
also allows custom limits to be passed when creating Dynamic Workers.

## Automatic tracing and tail visibility

From compatibility date `2025-11-05`, this setting enables automatic Workers
tracing as well as observability:

```jsonc
{
  "observability": { "enabled": true }
}
```

With older dates, opt in explicitly using
`"observability": { "traces": { "enabled": true } }`. Preview warnings that
were formerly available only in DevTools are also delivered to an attached
tail Worker.

## Worker-level Access and identity

An Access policy can attach to a Worker instead of to each hostname. It then
covers the Worker's routes, custom domains, `workers.dev` URL, and preview URLs
as they change. An account default can protect current and future Workers, with
per-Worker bypasses and separate preview-only or preview-and-production scope.

Authenticated requests expose `ctx.access.aud` and
`await ctx.access.getIdentity()` for identity attributes such as email, name,
and groups:

```js
export default {
  async fetch(request, env, ctx) {
    if (!ctx.access) return new Response("Unauthorized", { status: 401 });
    const identity = await ctx.access.getIdentity();
    return Response.json({ aud: ctx.access.aud, email: identity?.email });
  },
};
```

For local `wrangler dev`, inject an identity with `access.dev`:

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

Remove that block to simulate an unauthenticated local request.
