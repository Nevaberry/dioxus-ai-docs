# Client Extensions and observability

## Register event listeners before extensions

`$on()` returns the modified client as of 6.5.0, so event listeners can be
registered in a chain before `$extends()`. Extended clients do not expose
`$on()`, making this order significant.

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

## Predict extension-chain behavior

Separately derived extended clients isolate their added behavior from one
another and from the standard client, while sharing the standard client's
connection pool. An extension that constructs another `PrismaClient` creates
a separate query engine and pool. (client-extensions)

When several extensions define a member with the same name, the last extension
in the chain wins. Query extensions compose like middleware and begin in
declaration order, so the first declared extension starts first.
(client-extensions)

```ts
const prisma = new PrismaClient()
  .$extends({ client: { source() { return 'first' } } })
  .$extends({ client: { source() { return 'second' } } })

prisma.source() // 'second'
```

Client-level methods are not guaranteed to exist on an extended client. Test
for availability before use. The `query` extension component cannot intercept
nested reads or nested writes. (client-extensions)

```ts
if (prisma.$connect) {
  await prisma.$connect()
}
```

## Update tracing configuration

Tracing became GA in 6.1.0, so remove the `tracing` preview feature. Update
span filters and dashboards for these span-set changes:

- `prisma:engine:query` replaces `prisma:engine`.
- `prisma:engine:response_json_serialization` records response JSON
  serialization.

`@opentelemetry/api` is a peer dependency and must be installed explicitly.
`registerInstrumentations` is re-exported by `@prisma/instrumentation`, so an
application that needed `@opentelemetry/instrumentation` only for that helper
can import it from Prisma's package instead. (6.1.0)

```sh
npm install @opentelemetry/api
```

```ts
import {
  PrismaInstrumentation,
  registerInstrumentations,
} from '@prisma/instrumentation'
```

`PrismaInstrumentation` can filter unwanted spans as of 6.5.0. Prisma also
supports `@opentelemetry/instrumentation` versions `>=0.52.0 <1` as of 6.17.0,
reducing peer-version conflicts.

## Attach SQL commenter metadata

Since 7.1.0, the client accepts a `comments` array of sqlcommenter plugins:

- Query tags propagate arbitrary metadata through async context.
- Trace context adds `traceparent` only for an active sampled span with
  `@prisma/instrumentation` configured.
- Custom plugins can derive tags from the query context.

```ts
import type { SqlCommenterPlugin } from '@prisma/sqlcommenter'
import { queryTags, withQueryTags } from '@prisma/sqlcommenter-query-tags'
import { traceContext } from '@prisma/sqlcommenter-trace-context'

const applicationTags: SqlCommenterPlugin = (context) => ({
  application: 'my-service',
  operation: context.query.action,
  model: context.query.modelName,
})

const prisma = new PrismaClient({
  adapter,
  comments: [queryTags(), traceContext(), applicationTags],
})

const users = await withQueryTags(
  { route: '/api/users', requestId: 'abc-123' },
  () => prisma.user.findMany(),
)
```

## Replace removed metrics and handle driver failures

Prisma 7 removed the deprecated `metrics` preview API (7.0.0). Obtain pool and
driver metrics from the underlying adapter or driver; for PostgreSQL, use the
pool's metrics rather than expecting Prisma Client's former metrics surface.

Unmapped database-driver errors are surfaced as catchable `P2039` errors
instead of crashing the client (product-updates). Treat `P2039` as the wrapper
for a failure Prisma does not map to a more specific client error and inspect
its attached driver details.

Query Insights is embedded in Prisma Studio for slow-query investigation next
to the affected data (product-updates). Prisma Postgres Console metrics and
Studio workflows are documented in the product and tooling references.

## Select a Read Replicas extension version

The current `@prisma/extension-read-replicas` supports Prisma 7. Prisma 6
projects must pin `0.4.1` instead (7.1.0).

```sh
# Prisma 7
npm install @prisma/extension-read-replicas@latest

# Prisma 6
npm install @prisma/extension-read-replicas@0.4.1
```
