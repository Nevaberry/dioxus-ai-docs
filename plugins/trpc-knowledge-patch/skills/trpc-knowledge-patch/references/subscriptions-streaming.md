# Subscriptions & Streaming

## SSE subscriptions replace Observable pattern

Subscriptions now use async generators + SSE instead of Observables + WebSockets. Observable subscriptions are deprecated.

```ts
const appRouter = router({
  onEvent: publicProcedure.subscription(async function* (opts) {
    for await (const data of on(ee, 'event', { signal: opts.signal })) {
      yield data[0];
    }
  }),
});
```

SSE config in `initTRPC.create()`:

```ts
const t = initTRPC.create({
  sse: {
    ping: { enabled: true, intervalMs: 15_000 },
    client: { reconnectAfterInactivityMs: 20_000 },
  },
});
```

## tracked() for subscription reconnection

Wrap yielded events with `tracked(id, data)` so clients auto-reconnect and resume from the last received event:

```ts
import { tracked } from '@trpc/server';

t.procedure
  .input(z.object({ lastEventId: z.string().nullish() }).optional())
  .subscription(async function* (opts) {
    if (opts.input?.lastEventId) {
      // fetch and yield missed events since lastEventId
    }
    for await (const [data] of on(ee, 'add', { signal: opts.signal })) {
      yield tracked(data.id, data); // client tracks this id
    }
  });
```

## httpSubscriptionLink setup

Use `splitLink` to route subscriptions to SSE and other operations to batch HTTP:

```ts
import { splitLink, httpBatchLink, httpSubscriptionLink } from '@trpc/client';

const client = createTRPCClient<AppRouter>({
  links: [
    splitLink({
      condition: (op) => op.type === 'subscription',
      true: httpSubscriptionLink({
        url: '/api/trpc',
        // Auth via EventSource ponyfill:
        EventSource: EventSourcePolyfill,
        eventSourceOptions: async ({ op }) => ({
          headers: { authorization: `Bearer ${token}` },
        }),
        // Or via URL params (less secure):
        connectionParams: async () => ({ token: 'secret' }),
      }),
      false: httpBatchLink({ url: '/api/trpc' }),
    }),
  ],
});
```

## useSubscription return type

Returns a discriminated union on `status`: `'idle' | 'connecting' | 'pending' | 'error'`. Use `reset()` to reconnect:

```tsx
const sub = trpc.onEvent.useSubscription(undefined, {
  onStarted: () => {},
  onData: (data) => {},
  onError: (err) => {},
  onComplete: () => {},  // server ended the subscription
});
// sub.status, sub.data, sub.error, sub.reset()
// Use skipToken from @tanstack/react-query to pause (replaces enabled)
```

## Streaming queries/mutations via async generators

With `httpBatchStreamLink`, resolvers can be async generators:

```ts
const appRouter = router({
  stream: publicProcedure.query(async function* () {
    for (let i = 0; i < 10; i++) {
      yield i;
      await new Promise((r) => setTimeout(r, 500));
    }
  }),
});
// Client: const iterable = await trpc.stream.query(); for await (const v of iterable) { ... }
```

## Embedded promises in streamed responses

With `httpBatchStreamLink`, return objects with promise values — they stream as they resolve:

```ts
publicProcedure.query(() => ({
  instant: 'ready',
  slow: slowAsyncFn(), // streams when resolved
}));
```
