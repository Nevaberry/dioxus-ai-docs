# Non-JSON Inputs and HTTP Transport

## Contents

- [Native procedure inputs](#native-procedure-inputs)
- [Octet-stream bodies](#octet-stream-bodies)
- [Choose links by input type](#choose-links-by-input-type)
- [Preserve transformer behavior](#preserve-transformer-behavior)
- [Limit server batch size](#limit-server-batch-size)

## Native procedure inputs

Procedures can receive `FormData` and binary values such as `Blob`, `File`, and
`Uint8Array`. Apply an ordinary input validator to `FormData`.

```ts
import { z } from 'zod';
import { publicProcedure, router } from './trpc';

export const appRouter = router({
  submit: publicProcedure
    .input(z.instanceof(FormData))
    .mutation(({ input }) => {
      const title = input.get('title');
      return { title };
    }),
});
```

## Octet-stream bodies

Use `octetInputParser` for an octet-stream request body. The parser exposes the
body to the resolver as a `ReadableStream`.

```ts
import { octetInputParser } from '@trpc/server/http';

const upload = publicProcedure
  .input(octetInputParser)
  .mutation(async ({ input }) => {
    for await (const chunk of input) {
      await writeChunk(chunk);
    }
  });
```

Treat the stream as the input value; do not wrap it in a JSON object before
sending it.

## Choose links by input type

`httpLink` carries non-JSON input directly. Neither `httpBatchLink` nor
`httpBatchStreamLink` supports those bodies. Route each operation with
`isNonJsonSerializable` and `splitLink`.

```ts
import {
  httpBatchLink,
  httpLink,
  isNonJsonSerializable,
  splitLink,
} from '@trpc/client';

const transport = splitLink({
  condition: (op) => isNonJsonSerializable(op.input),
  true: httpLink({ url: 'http://localhost:2022' }),
  false: httpBatchLink({ url: 'http://localhost:2022' }),
});
```

Apply this split before a non-JSON operation reaches a batching link. This rule
also applies when the normal JSON branch uses `httpBatchStreamLink`.

## Preserve transformer behavior

A transformer such as SuperJSON must not serialize the non-JSON request body.
Use an identity request serializer on the direct HTTP branch, but keep the
transformer's response deserializer so results still decode consistently.

```ts
import superjson from 'superjson';

splitLink({
  condition: (op) => isNonJsonSerializable(op.input),
  true: httpLink({
    url,
    transformer: {
      serialize: (value) => value,
      deserialize: (value) => superjson.deserialize(value),
    },
  }),
  false: httpBatchLink({ url, transformer: superjson }),
});
```

Use the same response semantics on both branches so dates and other rich
values do not change shape based on the input transport.

## Limit server batch size

Impose a server-side maximum number of operations per request when unbounded
batches would be unsafe (since 11.15.0). The server can reject an oversized
batch even if a client fails to constrain its own batch size; do not depend on
client configuration as the enforcement boundary.
