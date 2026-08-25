# TanStack Query and Next.js

## Contents

- [Prefer the TanStack-native integration](#prefer-the-tanstack-native-integration)
- [Prefix cache keys and mutation options](#prefix-cache-keys-and-mutation-options)
- [Use skipToken with suspense infinite queries](#use-skiptoken-with-suspense-infinite-queries)
- [Prefetch in React Server Components](#prefetch-in-react-server-components)
- [Create callable App Router Server Actions](#create-callable-app-router-server-actions)

## Prefer the TanStack-native integration

Use `@trpc/tanstack-react-query` for new React integration work. The classic
hook-wrapping integration remains maintained and can coexist with it during an
incremental migration, but significant new functionality is expected on the
TanStack-native integration.

The classic wrapper is difficult to lint correctly under the Rules of Hooks.
It also encourages patterns such as passing hooks through props, which can
break under React Compiler. Migrate by feature or router rather than requiring
an all-at-once replacement.

## Prefix cache keys and mutation options

Apply a caller-chosen common prefix to every generated query and mutation key
when tRPC cache entries must share a namespace. Use the same prefix for reads,
writes, invalidation, hydration, and inspection; a mismatched prefix addresses
a different cache entry.

Mutation options support procedure-path prefixes (since 11.18.0). Define
options for a router prefix when matching mutations should inherit common
behavior, and override them at a narrower procedure path only when needed.

Keep these two concepts distinct:

- a cache-key prefix namespaces all generated query and mutation keys;
- a procedure-path prefix scopes mutation option defaults to matching router
  procedures.

## Use skipToken with suspense infinite queries

`useSuspenseInfiniteQuery` accepts `skipToken` without a type error when
`getNextPageParam` is omitted (since 11.12.0). Do not add a meaningless
`getNextPageParam` callback only to satisfy older typing behavior.

```tsx
import { skipToken } from '@tanstack/react-query';

const result = trpc.posts.list.useSuspenseInfiniteQuery(
  paused ? skipToken : { limit: 20 },
  {},
);
```

## Prefetch in React Server Components

Use the React Server Component helpers to start a procedure during server
rendering. The client can adopt the pending promise and automatically hydrate
the React Query cache.

This permits server prefetching without waiting for the server component to
finish and then issuing a second server-to-client request. Keep the server and
client query keys, transformer, and cache prefix identical so hydration finds
the pending entry.

## Create callable App Router Server Actions

Combine the experimental `experimental_caller` procedure API with
`experimental_nextAppDirCaller` to turn a procedure into a directly callable
Next.js App Router Server Action.

```ts
// server/trpc.ts
import { initTRPC } from '@trpc/server';
import { experimental_nextAppDirCaller } from '@trpc/server/adapters/next-app-dir';
import { currentUser } from './auth';

interface Meta {
  span: string;
}

const t = initTRPC.meta<Meta>().create();

export const serverActionProcedure = t.procedure
  .experimental_caller(
    experimental_nextAppDirCaller({
      pathExtractor: ({ meta }) => (meta as Meta)?.span ?? '',
    }),
  )
  .use(async (opts) =>
    opts.next({ ctx: { user: await currentUser() } }),
  );
```

Build and export the action from a server-only module:

```ts
// app/_actions.ts
'use server';

import { z } from 'zod';
import { serverActionProcedure } from '../server/trpc';

export const createPost = serverActionProcedure
  .meta({ span: 'create-post' })
  .input(z.object({ title: z.string() }))
  .mutation(({ ctx, input }) => ({
    author: ctx.user,
    title: input.title,
  }));
```

These calls bypass an HTTP adapter. Inject per-call state such as the current
user through middleware rather than expecting adapter context.

The direct call also has no router path. Put an observability identifier in
procedure metadata and derive it with `pathExtractor` for logs or tracing.
