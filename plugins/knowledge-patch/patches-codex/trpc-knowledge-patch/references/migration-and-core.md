# Migration and Core APIs

## Contents

- [Removed interop mode](#removed-interop-mode)
- [Router composition](#router-composition)
- [Runtime error and proxy compatibility](#runtime-error-and-proxy-compatibility)
- [Direct in-process calls](#direct-in-process-calls)
- [Lazy-loaded routers](#lazy-loaded-routers)

## Removed interop mode

The temporary `.interop()` compatibility layer has been removed. If an
application still uses it, first complete the older procedure migration to the
router/procedure/middleware builder API, then upgrade. Do not recreate the
compatibility layer locally.

## Router composition

### Inline sub-router shorthand

A nested object in a router definition is a sub-router. Use an extra `router()`
call only when it adds useful composition behavior.

```ts
import { publicProcedure, router } from './trpc';

export const appRouter = router({
  account: {
    profile: publicProcedure.query(() => ({ name: 'Ada' })),
  },
});
```

The procedure remains available at `account.profile` and participates in type
inference as if the nested value had been wrapped in `router()`.

## Runtime error and proxy compatibility

### Cross-context errors

Errors created inside a Node `vm` context are recognized correctly after they
cross into the main context (since 11.15.0). Do not rely on `instanceof`-only
application workarounds to make tRPC classify these errors.

### React proxy coercion

The server proxy created through `createInnerProxy` tolerates React 19 coercion
(since 11.17.0). React can inspect or coerce a proxy without making the tRPC
server proxy unusable.

## Direct in-process calls

`unstable_localLink` is a terminating client link that runs queries, mutations,
and subscriptions directly against a router. Use it when client semantics are
useful but an HTTP hop is not.

```ts
import { createTRPCClient, unstable_localLink } from '@trpc/client';
import { appRouter, type AppRouter } from './server';

const client = createTRPCClient<AppRouter>({
  links: [
    unstable_localLink({
      router: appRouter,
      createContext: async () => ({ requestId: crypto.randomUUID() }),
      onError: ({ error, path }) => console.error(path, error),
    }),
  ],
});
```

Create context for every operation. The link retains ordinary client behavior,
including abort signals, transformers, and `onError` handling; do not treat it
as a raw direct function call.

## Lazy-loaded routers

Wrap a dynamic import with `lazy()` to defer loading a child router. This can
reduce cold-start work without changing the procedure path or call syntax.

```ts
import { lazy } from '@trpc/server';
import { router } from '../trpc';

export const appRouter = router({
  greeting: lazy(() => import('./greeting.js')),
  user: lazy(() => import('./user.js').then((mod) => mod.userRouter)),
});
```

Import a module directly when it has exactly one router export. When the module
has multiple exports, resolve the promise to the intended router explicitly.
