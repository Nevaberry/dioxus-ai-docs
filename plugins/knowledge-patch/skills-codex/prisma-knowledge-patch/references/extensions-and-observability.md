# Client Extensions and observability

## Event listeners and extensions

`$on()` returns the modified client and can be chained as of 6.5.0. Extended
clients do not expose `$on()`, so register event listeners before `$extends()`:

```ts
const prisma = new PrismaClient({
  adapter,
  log: [{ emit: 'event', level: 'query' }],
})
  .$on('query', (event) => console.log(event.query))
  .$extends(extension)
```

## Extension composition

Separately derived clients isolate their added behavior from one another and
from the standard client, while sharing the standard client's connection pool.
An extension that creates a separate `PrismaClient` receives its own query
engine and pool (client-extensions).

Use these composition rules:

- If chained extensions define the same member, the last extension wins.
- Query extensions begin in declaration order, like first-in-first-out
  middleware.
- A client-level method may be absent from an extended client; check it before
  calling it.
- A `query` extension cannot intercept nested reads or nested writes.

```ts
const prisma = new PrismaClient()
  .$extends({ client: { source() { return 'first' } } })
  .$extends({ client: { source() { return 'second' } } })

prisma.source() // 'second'
```

Prisma 7 projects can use the latest `@prisma/extension-read-replicas`, while
Prisma 6 projects must pin `0.4.1` (7.1.0).

## OpenTelemetry tracing

Tracing became GA in 6.1.0, so remove the `tracing` preview flag. Update span
filters and dashboards for these names:

- `prisma:engine:query` replaced `prisma:engine`.
- `prisma:engine:response_json_serialization` was added.

Install `@opentelemetry/api` explicitly because it is a peer dependency.
`registerInstrumentations` is re-exported by `@prisma/instrumentation`, so an
application that needed `@opentelemetry/instrumentation` only for that helper
can import it from Prisma:

```ts
import {
  PrismaInstrumentation,
  registerInstrumentations,
} from '@prisma/instrumentation'
```

`PrismaInstrumentation` can filter unwanted spans since 6.5.0. Prisma's
instrumentation package accepts `@opentelemetry/instrumentation` versions
`>=0.52.0 <1` as of 6.17.0.

## SQL commenter plugins

Prisma Client accepts a `comments` array of sqlcommenter plugins (7.1.0):

- Query tags propagate arbitrary metadata through async context.
- Trace context adds `traceparent` only for an active sampled span and requires
  configured `@prisma/instrumentation`.
- Custom plugins derive tags from the query context.

```ts
import type { SqlCommenterPlugin } from '@prisma/sqlcommenter'
import { queryTags, withQueryTags } from '@prisma/sqlcommenter-query-tags'
import { traceContext } from '@prisma/sqlcommenter-trace-context'

const applicationTags: SqlCommenterPlugin = (context) => ({
  application: 'my-service',
  action: context.query.action,
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

## Metrics and query diagnosis

The deprecated `metrics` preview API was removed in 7.0.0. Collect equivalent
information from the underlying adapter or driver, such as PostgreSQL pool
metrics. Prisma Console provides database-level egress, average response size,
average query duration, and query-cache guidance (6.18.0), while its broader
dashboard shows estimated invoices, storage, database counts, cumulative
operations, and daily operations (6.17.0).

Query Insights is embedded in Prisma Studio, allowing slow-query investigation
alongside data browsing (product-updates). Studio's Prisma Streams browser also
shows live aggregations, diagnostics, routing keys, WAL-history handoff,
event-log summaries, and OpenTelemetry signals (7.9.0).

## Driver errors

Unmapped database-driver errors are surfaced as catchable `P2039` errors
instead of crashing the client (product-updates). Keep application error
handling broad enough to log the underlying driver context without treating an
unmapped failure as an uncatchable process error.
