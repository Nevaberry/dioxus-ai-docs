# Next.js Server Actions

## Server Actions via experimental_caller

Turn tRPC procedures into plain async functions usable as Next.js server actions. Use `experimental_caller` with the `experimental_nextAppDirCaller` adapter:

```ts
import { initTRPC, TRPCError } from '@trpc/server';
import { experimental_nextAppDirCaller } from '@trpc/server/adapters/next-app-dir';

interface Meta { span: string }
const t = initTRPC.meta<Meta>().create();

export const serverActionProcedure = t.procedure
  .experimental_caller(
    experimental_nextAppDirCaller({
      pathExtractor: ({ meta }) => (meta as Meta)?.span ?? '',
    }),
  )
  // Context via middleware (no HTTP adapter = no createContext)
  .use(async (opts) => {
    const user = await currentUser();
    return opts.next({ ctx: { user } });
  });

// Auth guard
export const protectedAction = serverActionProcedure.use((opts) => {
  if (!opts.ctx.user) throw new TRPCError({ code: 'UNAUTHORIZED' });
  return opts.next({ ctx: { ...opts.ctx, user: opts.ctx.user } });
});
```

## Defining actions

Define actions in a `"use server"` file — the procedure becomes a plain function:

```ts
'use server';
import { z } from 'zod';
import { protectedAction } from '../server/trpc';

export const createPost = protectedAction
  .meta({ span: 'create-post' }) // for observability (no router path)
  .input(z.object({ title: z.string() }))
  .mutation(async (opts) => { /* opts.ctx.user, opts.input.title */ });
// createPost is now: (input: { title: string }) => Promise<void>
```

Use in client components like any server action — works with form `action` (progressive enhancement) and programmatic calls.
