# OpenAPI

## Contents

- [Generate a static document](#generate-a-static-document)
- [Operation mapping and coverage](#operation-mapping-and-coverage)
- [Router and schema support](#router-and-schema-support)
- [Document quality and server URLs](#document-quality-and-server-urls)
- [Generate a tRPC-aware Hey API client](#generate-a-trpc-aware-hey-api-client)

## Generate a static document

The alpha `@trpc/openapi` package statically analyzes the type of an exported
router. It does not execute the application and does not require route
annotations or `.output()` schemas.

Generate from the command line:

```sh
pnpm exec trpc-openapi ./src/server/router.ts \
  --output openapi.json --title "My API" --version 1.0.0
```

Or call the generator:

```ts
import { generateOpenAPIDocument } from '@trpc/openapi';

const document = generateOpenAPIDocument('./src/server/router.ts', {
  exportName: 'AppRouter',
  title: 'My API',
  version: '1.0.0',
});
```

OpenAPI JSON generation accepts any tRPC application router (since 11.13.2),
rather than requiring a special router construction.

## Operation mapping and coverage

The generator emits:

- a query as `GET /procedure.path`;
- a mutation as `POST /procedure.path`;
- Zod and application JSDoc descriptions in the resulting document.

Subscriptions are currently omitted. Do not advertise a subscription endpoint
from the generated document without defining its separate transport contract.

## Router and schema support

The 11.16.0-alpha OpenAPI package removes the previous type-depth limit of 20.
It supports recursive and cyclic types during both type inference and Zod
schema processing. A `z.lazy` schema is handled through a Standard Schema
fallback.

Keep recursive schemas in their natural form instead of manually flattening
them merely to satisfy generation.

## Document quality and server URLs

Generated output at 11.16.0:

- omits symbol keys such as `__@asyncIterator@5456`;
- uses more complete official OpenAPI document types;
- avoids deriving schema descriptions from JSDoc comments on types in
  `node_modules`.

The last behavior does not remove descriptions authored for the application's
own schemas. It prevents dependency-internal comments from leaking into schema
documentation.

Add hosted endpoint URLs to the generated OpenAPI document through server URL
support (since 11.18.0). Use this when the document must describe one or more
deployment endpoints rather than leaving server selection implicit.

## Generate a tRPC-aware Hey API client

A generic generated client does not know two tRPC wire conventions:

1. Query input is encoded as `?input=<JSON>`.
2. Responses and errors use tRPC envelopes and transformer semantics.

For Hey API, install the tRPC type resolvers in the generation configuration.

```ts
import { createClient } from '@hey-api/openapi-ts';
import { createTRPCHeyApiTypeResolvers } from '@trpc/openapi/heyapi';

await createClient({
  input: './openapi.json',
  output: './generated',
  plugins: [
    {
      name: '@hey-api/typescript',
      '~resolvers': createTRPCHeyApiTypeResolvers(),
    },
    { name: '@hey-api/sdk', operations: { strategy: 'single' } },
  ],
});
```

Then configure the generated runtime client with tRPC response handling.

```ts
import { configureTRPCHeyApiClient } from '@trpc/openapi/heyapi';
import superjson from 'superjson';
import { client } from './generated/client.gen';

configureTRPCHeyApiClient(client, {
  baseUrl: 'http://localhost:3000',
  transformer: superjson,
});
```

Pass the same transformer used by the server. Omitting it can silently turn
rich values such as dates into the wrong runtime representation.
