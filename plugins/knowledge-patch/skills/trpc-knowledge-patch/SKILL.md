---
name: trpc-knowledge-patch
description: tRPC
license: MIT
version: 11.18.0
metadata:
  author: Nevaberry
---

# tRPC Knowledge Patch

Use this skill to choose current tRPC APIs and transport patterns. Read the
reference that matches the task before changing an integration; transport,
subscription, and cache behavior often depend on one another.

## Reference index

| Reference | Topics |
| --- | --- |
| [migration-and-core.md](references/migration-and-core.md) | Removed compatibility APIs, nested and lazy routers, in-process calls, runtime fixes |
| [non-json-and-http.md](references/non-json-and-http.md) | `FormData`, binary bodies, link routing, transformers, server batch limits |
| [openapi.md](references/openapi.md) | Static OpenAPI generation, recursive schemas, document cleanup, generated clients |
| [streaming-and-retry.md](references/streaming-and-retry.md) | Async generators, batch streaming, headers, runtimes, keepalives, retry policies |
| [subscriptions.md](references/subscriptions.md) | SSE and WebSocket recovery, credentials, liveness, React state, mobile support, types |
| [tanstack-and-nextjs.md](references/tanstack-and-nextjs.md) | TanStack-native keys and options, RSC hydration, Server Actions |

## Working method

1. Identify whether the operation is a request/response call, an incremental
   result, or an ongoing subscription.
2. Choose the terminating link from the input and response semantics. Do not
   send non-JSON bodies through either batching link.
3. Configure authentication at connection creation time and decide whether a
   reconnect must refresh it.
4. Keep router types as the source of truth for client, subscription, and
   OpenAPI types.
5. Check runtime stream support before selecting a streaming link.
6. Preserve cache-key prefixes across query, mutation, invalidation, and
   mutation-option helpers.

## Breaking changes and deprecations

### Remove `.interop()`

The temporary compatibility mode no longer exists. Finish the builder-API
migration before upgrading code that still calls `.interop()`; do not try to
shim it in a current router.

### Pause subscriptions with `skipToken`

Pass TanStack Query's `skipToken` as the subscription input. Treat the older
`enabled` option as deprecated.

```tsx
import { skipToken } from '@tanstack/react-query';

const result = trpc.postFeed.useSubscription(
  paused ? skipToken : undefined,
  { onData: handlePost },
);
```

### Route non-JSON inputs away from batching

Use `httpLink` for `FormData`, `Blob`, `File`, `Uint8Array`, and octet-stream
inputs. `httpBatchLink` and `httpBatchStreamLink` do not carry these inputs.

```ts
splitLink({
  condition: (op) => isNonJsonSerializable(op.input),
  true: httpLink({ url }),
  false: httpBatchLink({ url }),
});
```

### Choose non-streaming responses for result-dependent headers

`httpBatchStreamLink` commits headers before procedure results exist.
Procedures cannot set result-dependent headers or cookies after streaming
starts, and streamed `responseMeta` receives no `data` property. Use
`httpBatchLink` when headers depend on returned data.

## Native inputs

Validate `FormData` normally. Parse an octet-stream request with
`octetInputParser`; its procedure input is a `ReadableStream`.

```ts
import { octetInputParser } from '@trpc/server/http';
import { z } from 'zod';

const appRouter = router({
  uploadForm: publicProcedure
    .input(z.instanceof(FormData))
    .mutation(({ input }) => consumeForm(input)),
  uploadBytes: publicProcedure
    .input(octetInputParser)
    .mutation(({ input }) => consumeStream(input)),
});
```

When a transformer is configured, keep the request serializer as identity on
the non-JSON branch while retaining the transformer's response deserializer.
See [non-json-and-http.md](references/non-json-and-http.md) for the complete
split-link configuration.

## Streaming query and mutation results

Return an async generator from a query or mutation and use
`httpBatchStreamLink`. The resolved client result is an `AsyncIterable`.

```ts
const numbers = publicProcedure.query(async function* () {
  yield 1;
  yield 2;
});

const values = await client.numbers.query();
for await (const value of values) process(value);
```

Keep this distinct from subscriptions: an incremental procedure result ends
with that call, while a subscription represents an ongoing event source.
Configure runtime stream primitives, JSONL keepalives, and retry policy using
[streaming-and-retry.md](references/streaming-and-retry.md).

## Resumable subscriptions

Prefer SSE as the first subscription transport unless bidirectional WebSocket
behavior is required. Implement a generator and yield `tracked(id, data)` so
SSE and WebSocket links can resume from `lastEventId`.

```ts
const feed = publicProcedure
  .input(z.object({ lastEventId: z.string().nullish() }).optional())
  .subscription(async function* (opts) {
    const live = on(events, 'post', { signal: opts.signal });
    yield* replayAfter(opts.input?.lastEventId);
    for await (const [post] of live) yield tracked(post.id, post);
  });
```

Attach the live listener before querying missed records, or an event can fall
between replay and listening. Expect thrown server errors in the 5xx class to
reconnect and resume; let other errors stop and reach the client callback.

Use a ponyfill for arbitrary request headers. Place `retryLink` before
`httpSubscriptionLink` when a reconnect must rerun URL or credential callbacks.
Read [subscriptions.md](references/subscriptions.md) before implementing auth,
liveness, completion state, or React Native support.

## TanStack-native integration

Prefer `@trpc/tanstack-react-query` for new React work and migrate incrementally
from classic hook wrappers. Apply a common prefix consistently to generated
query and mutation keys. Router-prefix mutation options can supply defaults to
all matching procedures.

Use the RSC helpers to start a procedure on the server and let the client adopt
the pending promise while hydrating the query cache. This avoids adding a
server-to-client request waterfall.

For a suspense infinite query, `skipToken` is valid even when
`getNextPageParam` is omitted.

## Next.js App Router actions

Use `experimental_caller` with `experimental_nextAppDirCaller` to expose a
procedure as a directly callable Server Action. Because the call bypasses HTTP:

- inject request-specific context in middleware;
- derive an observability path with `pathExtractor` and procedure metadata;
- do not assume an adapter-provided router path exists.

```ts
const actionProcedure = t.procedure
  .experimental_caller(
    experimental_nextAppDirCaller({
      pathExtractor: ({ meta }) => meta?.span ?? '',
    }),
  )
  .use(async (opts) => opts.next({ ctx: await createActionContext() }));
```

Keep action construction and RSC/TanStack setup aligned with
[tanstack-and-nextjs.md](references/tanstack-and-nextjs.md).

## OpenAPI generation

Use the alpha `@trpc/openapi` generator for a static OpenAPI 3.1 document. It
analyzes an exported router type without running the application or requiring
route annotations and output schemas. It maps queries to `GET`, mutations to
`POST`, and omits subscriptions.

Generated clients need tRPC-aware query-input encoding plus response and error
decoding. For Hey API, install the tRPC type resolvers during generation and
configure the runtime client with the same transformer used by the server.
Read [openapi.md](references/openapi.md) for recursive schemas and server URLs.

## Final checks

- Verify every non-JSON input takes the direct HTTP branch.
- Verify stream-capable `fetch` and stream primitives in non-browser runtimes.
- Verify subscription replay attaches its live listener before reading history.
- Verify refreshed credentials recreate the subscription connection.
- Verify cache prefixes match across all TanStack helpers.
- Verify streamed procedures do not depend on late response headers.
- Verify generated API clients use tRPC-aware encoding and the server transformer.
