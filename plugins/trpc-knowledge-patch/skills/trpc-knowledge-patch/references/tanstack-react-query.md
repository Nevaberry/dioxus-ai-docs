# TanStack React Query Integration

## New package: @trpc/tanstack-react-query

Replaces `@trpc/react-query` with a TanStack Query-native API. Instead of tRPC-wrapped hooks, use native `useQuery`/`useMutation` with tRPC option factories:

```tsx
// Setup: createTRPCContext (with React context) or createTRPCOptionsProxy (singleton)
import { createTRPCContext } from '@trpc/tanstack-react-query';
export const { TRPCProvider, useTRPC } = createTRPCContext<AppRouter>();

// Usage in components:
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTRPC } from './trpc';

function MyComponent() {
  const trpc = useTRPC();
  // Queries: .queryOptions(input) instead of .useQuery(input)
  const greeting = useQuery(trpc.greeting.queryOptions({ name: 'Jerry' }));
  // Mutations: .mutationOptions() instead of .useMutation()
  const create = useMutation(trpc.createUser.mutationOptions());
  // Invalidation: .queryFilter(input) with native queryClient
  const qc = useQueryClient();
  await qc.invalidateQueries(trpc.greeting.queryFilter({ name: 'Jerry' }));
}
```

## createTRPCOptionsProxy for server components / singletons

For RSC prefetching or SPA singletons without React context:

```ts
import { createTRPCOptionsProxy } from '@trpc/tanstack-react-query';
// Server-side (RSC): pass router + context directly (no HTTP round-trip)
const trpc = createTRPCOptionsProxy({ ctx: createTRPCContext, router: appRouter, queryClient: getQueryClient });
// SPA singleton: pass a tRPC client
const trpc = createTRPCOptionsProxy<AppRouter>({ client: trpcClient, queryClient });
// Then use with prefetchQuery/fetchQuery:
void queryClient.prefetchQuery(trpc.hello.queryOptions({ text: 'world' }));
```

## Migration from @trpc/react-query

Both clients coexist (same query keys). Codemod available: `npx @trpc/upgrade` (select "Migrate Hooks to xxxOptions API").
