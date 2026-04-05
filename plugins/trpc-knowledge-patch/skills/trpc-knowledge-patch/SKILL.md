---
name: trpc-knowledge-patch
description: >
  tRPC v11 features: SSE subscriptions with tracked() reconnection, streaming
  queries/mutations, @trpc/tanstack-react-query options API, Next.js server
  actions via experimental_caller, lazy routers, @trpc/openapi, non-JSON
  content types, localLink, HTTP/2 adapter. Load before writing tRPC v11 code.
license: MIT
metadata:
  author: Nevaberry
  version: "11.0"
---

# tRPC v11 Knowledge Patch

Claude's baseline knowledge covers tRPC through v10. This skill provides features from v11 (December 2024) onwards.

## Reference Index

- [v11 Migration & Breaking Changes](references/v11-migration.md) — Transformers moved to links, React Query v5 required, `createTRPCProxyClient` renamed, TypeScript 5.7.2+ / Node 18+ requirements
- [Subscriptions & Streaming](references/subscriptions-streaming.md) — SSE subscriptions via async generators, `tracked()` reconnection, `httpSubscriptionLink`, `useSubscription` status union, streaming queries/mutations, embedded promises with `httpBatchStreamLink`
- [TanStack React Query Integration](references/tanstack-react-query.md) — New `@trpc/tanstack-react-query` package, `createTRPCContext`, `createTRPCOptionsProxy` for RSC/singletons, `.queryOptions()`/`.mutationOptions()` API, migration codemod
- [Next.js Server Actions](references/nextjs-server-actions.md) — `experimental_caller` with `experimental_nextAppDirCaller`, turning procedures into plain async functions, auth guards, progressive enhancement
- [Advanced Features](references/advanced-features.md) — Lazy routers, `localLink`, shorthand router definitions, non-JSON content types (FormData/File/Blob), `@trpc/openapi` (alpha), HTTP/2 standalone adapter

## Quick Reference — v11 Breaking Changes

| Change | v10 | v11 |
|--------|-----|-----|
| Transformer location | `createTRPCClient({ transformer })` | `httpBatchLink({ transformer })` |
| React Query version | v4 | v5 required (`isPending` replaces `isLoading`) |
| Client constructor | `createTRPCProxyClient` | `createTRPCClient` (same API) |
| Subscriptions | Observable + WebSocket | Async generator + SSE |
| Min TypeScript | — | >=5.7.2 |
| Min Node.js | — | 18+ |

## Quick Reference — Essential Patterns

### Transformer in link (v11)

```ts
import { httpBatchLink } from '@trpc/client';
import superjson from 'superjson';

httpBatchLink({
  url: '/api/trpc',
  transformer: superjson, // moved here from createTRPCClient
});
```

### SSE subscription (async generator)

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

### tracked() — subscription reconnection

```ts
import { tracked } from '@trpc/server';

t.procedure
  .input(z.object({ lastEventId: z.string().nullish() }).optional())
  .subscription(async function* (opts) {
    if (opts.input?.lastEventId) { /* fetch missed events */ }
    for await (const [data] of on(ee, 'add', { signal: opts.signal })) {
      yield tracked(data.id, data); // client tracks this id
    }
  });
```

### httpSubscriptionLink setup

```ts
import { splitLink, httpBatchLink, httpSubscriptionLink } from '@trpc/client';

const client = createTRPCClient<AppRouter>({
  links: [
    splitLink({
      condition: (op) => op.type === 'subscription',
      true: httpSubscriptionLink({
        url: '/api/trpc',
        eventSourceOptions: async ({ op }) => ({
          headers: { authorization: `Bearer ${token}` },
        }),
      }),
      false: httpBatchLink({ url: '/api/trpc' }),
    }),
  ],
});
```

### useSubscription return type

Returns discriminated union on `status`: `'idle' | 'connecting' | 'pending' | 'error'`.

```tsx
const sub = trpc.onEvent.useSubscription(undefined, {
  onData: (data) => {},
  onError: (err) => {},
});
// sub.status, sub.data, sub.error, sub.reset()
```

### Streaming query (httpBatchStreamLink)

```ts
const appRouter = router({
  stream: publicProcedure.query(async function* () {
    for (let i = 0; i < 10; i++) {
      yield i;
      await new Promise((r) => setTimeout(r, 500));
    }
  }),
});
// Client: for await (const v of await trpc.stream.query()) { ... }
```

### Embedded promises in streamed responses

```ts
publicProcedure.query(() => ({
  instant: 'ready',
  slow: slowAsyncFn(), // streams when resolved
}));
```

### TanStack React Query options API

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTRPC } from './trpc';

function MyComponent() {
  const trpc = useTRPC();
  const greeting = useQuery(trpc.greeting.queryOptions({ name: 'Jerry' }));
  const create = useMutation(trpc.createUser.mutationOptions());
  // Invalidation
  const qc = useQueryClient();
  await qc.invalidateQueries(trpc.greeting.queryFilter({ name: 'Jerry' }));
}
```

### createTRPCOptionsProxy (RSC / singletons)

```ts
import { createTRPCOptionsProxy } from '@trpc/tanstack-react-query';
// RSC: direct router call, no HTTP
const trpc = createTRPCOptionsProxy({ ctx: createTRPCContext, router: appRouter, queryClient: getQueryClient });
// SPA singleton:
const trpc = createTRPCOptionsProxy<AppRouter>({ client: trpcClient, queryClient });
void queryClient.prefetchQuery(trpc.hello.queryOptions({ text: 'world' }));
```

Migration codemod: `npx @trpc/upgrade` (select "Migrate Hooks to xxxOptions API").

### Next.js server action

```ts
'use server';
import { protectedAction } from '../server/trpc';
import { z } from 'zod';

export const createPost = protectedAction
  .meta({ span: 'create-post' })
  .input(z.object({ title: z.string() }))
  .mutation(async (opts) => { /* opts.ctx.user, opts.input.title */ });
// createPost is now: (input: { title: string }) => Promise<void>
```

### Lazy router

```ts
import { lazy } from '@trpc/server';

const appRouter = router({
  greeting: lazy(() => import('./greeting.js')),
  user: lazy(() => import('./user.js').then((m) => m.userRouter)),
});
```

### Non-JSON with batch link (splitLink)

```ts
import { splitLink, httpBatchLink, httpLink, isNonJsonSerializable } from '@trpc/client';

createTRPCClient<AppRouter>({
  links: [
    splitLink({
      condition: (op) => isNonJsonSerializable(op.input),
      true: httpLink({ url }),
      false: httpBatchLink({ url }),
    }),
  ],
});
```

### @trpc/openapi — generate OpenAPI spec

```bash
pnpm add @trpc/openapi
pnpm exec trpc-openapi ./src/server/router.ts -o api.json --title "My API" --version 1.0.0
```
