# v11 Migration & Breaking Changes

## Transformers moved to links

Transformers (e.g. superjson) are no longer set on client init. Add them to each HTTP link instead:

```ts
import { httpBatchLink } from '@trpc/client';
import superjson from 'superjson';

httpBatchLink({
  url: '/api/trpc',
  transformer: superjson, // was on createTRPCClient before
});
```

Server-side `initTRPC.create({ transformer: superjson })` stays the same.

## React Query v5 required

`@trpc/react-query@^11` requires `@tanstack/react-query@^5`. Main change: `isLoading` is replaced by `isPending`.

## Rename: createTRPCProxyClient → createTRPCClient

`createTRPCProxyClient` is deprecated. Use `createTRPCClient` (same API, just renamed).

## Requirements

- TypeScript >=5.7.2
- Node.js 18+
- React >=18.2.0
