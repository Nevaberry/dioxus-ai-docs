# Advanced Features

## Lazy routers

Dynamically load routers to reduce cold starts. Use `lazy()` from `@trpc/server`:

```ts
import { lazy } from '@trpc/server';
import { router } from '../trpc';

const appRouter = router({
  // Short-hand: module has exactly 1 exported router
  greeting: lazy(() => import('./greeting.js')),
  // Named export
  user: lazy(() => import('./user.js').then((m) => m.userRouter)),
});
```

## localLink (unstable)

Call tRPC procedures directly without HTTP. Import as `unstable_localLink`:

```ts
import { createTRPCClient, unstable_localLink } from '@trpc/client';

const client = createTRPCClient<AppRouter>({
  links: [
    unstable_localLink({
      router: appRouter,
      createContext: async () => ({}),
      onError: (opts) => console.error(opts.error),
    }),
  ],
});
```

## Shorthand router definitions

Plain objects work as inline sub-routers (no `router()` wrapper needed):

```ts
const appRouter = router({
  nested: {
    proc: publicProcedure.query(() => '...'),
  },
});
```

## Non-JSON content types (FormData, File, Blob)

```ts
import { octetInputParser } from '@trpc/server/http';
import { z } from 'zod';

const appRouter = router({
  formData: publicProcedure
    .input(z.instanceof(FormData))
    .mutation(({ input }) => { /* input: FormData */ }),
  file: publicProcedure
    .input(octetInputParser)
    .mutation(({ input }) => { /* input: ReadableStream */ }),
});
```

`httpBatchLink` doesn't support FormData/File. Use `splitLink` + `isNonJsonSerializable`:

```ts
import { splitLink, httpBatchLink, httpLink, isNonJsonSerializable } from '@trpc/client';

createTRPCClient<AppRouter>({
  links: [
    splitLink({
      condition: (op) => isNonJsonSerializable(op.input),
      true: httpLink({ url }),       // handles FormData/File
      false: httpBatchLink({ url }), // handles JSON
    }),
  ],
});
```

## @trpc/openapi (alpha)

Generates OpenAPI 3.1 spec from your tRPC router via static analysis (never executes code). No `.output()` schemas required — types are inferred.

```bash
pnpm add @trpc/openapi
# CLI:
pnpm exec trpc-openapi ./src/server/router.ts -o api.json --title "My API" --version 1.0.0
```

```ts
// Programmatic:
import { generateOpenAPIDocument } from '@trpc/openapi';
const doc = generateOpenAPIDocument('./src/server/router.ts', {
  exportName: 'AppRouter',
  title: 'My API',
  version: '1.0.0',
});
```

Use with Hey API for typed client generation. If using transformers (superjson), configure `configureTRPCHeyApiClient` with matching transformer:

```ts
import { configureTRPCHeyApiClient } from '@trpc/openapi/heyapi';
import superjson from 'superjson';
import { client } from './generated/client.gen';

configureTRPCHeyApiClient(client, {
  baseUrl: 'http://localhost:3000',
  transformer: superjson, // must match server transformer
});
```

## Standalone adapter: HTTP/2 support

New `createHTTP2Handler` for HTTP/2 servers:

```ts
import http2 from 'http2';
import { createHTTP2Handler } from '@trpc/server/adapters/standalone';

const handler = createHTTP2Handler({ router: appRouter, createContext });
http2.createSecureServer({ key, cert }, handler).listen(3001);
// Context type: CreateHTTP2ContextOptions (has Http2ServerRequest/Response)
```
