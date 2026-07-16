# Client Extensions and observability

Use this reference when composing extended clients, registering events, instrumenting queries, adding SQL comments, configuring replicas, or handling low-level driver failures.

## Contents

- [Register events before extensions](#register-events-before-extensions)
- [Understand extension isolation and precedence](#understand-extension-isolation-and-precedence)
- [Compose query extensions](#compose-query-extensions)
- [Configure tracing](#configure-tracing)
- [Annotate SQL](#annotate-sql)
- [Select the Read Replicas extension](#select-the-read-replicas-extension)
- [Replace removed metrics and handle driver errors](#replace-removed-metrics-and-handle-driver-errors)

## Register events before extensions

`$on()` returns the modified client and can be chained as of 6.5.0. Extended clients do not expose `$on()`, so attach listeners first:

```ts
const prisma = new PrismaClient({
  adapter,
  log: [{ emit: 'event', level: 'query' }],
})
  .$on('query', (event) => console.log(event.query))
  .$extends({
    client: {
      ping() {
        return 'pong'
      },
    },
  })
```

Do not rewrite this as `new PrismaClient(...).$extends(...).$on(...)`; the listener method is unavailable after extension.

## Understand extension isolation and precedence

Clients derived separately from the same standard client with `$extends()` keep their added behavior isolated. An extension on one derived client does not leak into another derived client or the standard client. They still share the standard client's query engine connection pool.

An extension that constructs a separate `PrismaClient` creates a separate query engine and pool. Avoid that pattern when the extension only needs behavior layered onto an existing connection.

When multiple extensions on one chain define the same member, the later extension wins:

```ts
const extended = prisma
  .$extends({
    client: {
      source() {
        return 'first'
      },
    },
  })
  .$extends({
    client: {
      source() {
        return 'second'
      },
    },
  })

extended.source() // 'second'
```

Do not assume every standard-client method remains available on an extended client. Test for an optional client-level method before calling it:

```ts
if (extended.$connect) {
  await extended.$connect()
}
```

These isolation, precedence, and availability rules are part of the `client-extensions` batch.

## Compose query extensions

Chained `query` components behave like middleware and begin in declaration order: the first declared extension runs before the next one. Use that ordering deliberately for logging, policy enforcement, rewriting, and timing.

The `query` component cannot intercept nested reads or writes. For example, an extension around a top-level `user.update()` cannot customize a nested relation operation inside that update. Choose a schema, application-service, or database mechanism when nested behavior must be controlled.

These query-composition constraints are also covered by the `client-extensions` batch.

## Configure tracing

Tracing became generally available in 6.1.0; remove the old `tracing` Preview flag. That release also changed the emitted span set:

- Replace filters or dashboards looking for `prisma:engine` with `prisma:engine:query`.
- Account for the added `prisma:engine:response_json_serialization` span.

`@opentelemetry/api` is a peer dependency and must be installed explicitly:

```sh
npm install @opentelemetry/api
```

`registerInstrumentations` is re-exported by `@prisma/instrumentation`, so an application that used another instrumentation package only for that helper can import it from Prisma:

```ts
import {
  PrismaInstrumentation,
  registerInstrumentations,
} from '@prisma/instrumentation'
```

`PrismaInstrumentation` can filter unwanted spans as of 6.5.0. Apply filtering close to instrumentation setup so exporters and dashboards do not process spans the application has intentionally excluded.

Compatibility with `@opentelemetry/instrumentation` was widened in 6.17.0 to versions `>=0.52.0 <1`, reducing dependency conflicts across the 0.x line.

## Annotate SQL

`PrismaClient` accepts a `comments` array of sqlcommenter plugins as of 7.1.0. Comments can carry request metadata, sampled trace context, or custom values into generated SQL.

```ts
import type { SqlCommenterPlugin } from '@prisma/sqlcommenter'
import { queryTags, withQueryTags } from '@prisma/sqlcommenter-query-tags'
import { traceContext } from '@prisma/sqlcommenter-trace-context'
import { PrismaClient } from './generated/prisma/client'

const applicationTags: SqlCommenterPlugin = (context) => ({
  application: 'billing-service',
  operation: context.query.action,
  model: context.query.modelName,
})

const prisma = new PrismaClient({
  adapter,
  comments: [queryTags(), traceContext(), applicationTags],
})

const users = await withQueryTags(
  { route: '/api/users', requestId: 'req-123' },
  () => prisma.user.findMany(),
)
```

Plugin behavior:

- Query tags propagate arbitrary metadata through asynchronous context.
- Trace context adds `traceparent` only when a sampled span is active and `@prisma/instrumentation` is configured.
- Custom plugins derive tags from query context.

## Select the Read Replicas extension

Extension versions differ by Prisma major (7.1.0):

```sh
# Prisma 7
npm install @prisma/extension-read-replicas@latest

# Prisma 6 compatibility
npm install @prisma/extension-read-replicas@0.4.1
```

Do not install the latest extension into a Prisma 6 project without checking compatibility.

## Replace removed metrics and handle driver errors

The deprecated `metrics` Preview API was removed in 7.0.0. Obtain pool and transport metrics from the underlying adapter or database driver; for PostgreSQL, use the `pg` pool's metrics. Prisma Postgres Console metrics and Query Insights are separate product surfaces, not replacements exposed through `PrismaClient`.

Unmapped database-driver failures surface as catchable `P2039` errors in the `product-updates` batch. Treat them as application-visible failures instead of assuming an unknown adapter error will crash the client:

```ts
try {
  await prisma.user.findMany()
} catch (error) {
  if (
    typeof error === 'object' &&
    error !== null &&
    'code' in error &&
    error.code === 'P2039'
  ) {
    // Log adapter details and apply the application's failure policy.
  }
  throw error
}
```
