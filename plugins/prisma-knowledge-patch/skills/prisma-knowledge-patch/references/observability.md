# Observability — SQL Comments (7.1)

Prisma 7.1 adds sqlcommenter support to append metadata to SQL queries as comments, useful for observability and distributed tracing.

## Setup

```ts
import { PrismaClient } from './generated/prisma/client'
import { PrismaPg } from '@prisma/adapter-pg'
import { queryTags, withQueryTags } from '@prisma/sqlcommenter-query-tags'
import { traceContext } from '@prisma/sqlcommenter-trace-context'

const prisma = new PrismaClient({
  adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL }),
  comments: [queryTags(), traceContext()],
})
```

## Per-Request Tags

Use `withQueryTags` to add context-specific metadata via async context:

```ts
const users = await withQueryTags(
  { route: '/api/users', requestId: 'abc-123' },
  () => prisma.user.findMany(),
)
// SQL: SELECT ... FROM "User" /*requestId='abc-123',route='/api/users'*/
```

## Custom Plugins

Create custom sqlcommenter plugins to add application-specific tags:

```ts
import type { SqlCommenterPlugin } from '@prisma/sqlcommenter'

const appTags: SqlCommenterPlugin = (context) => ({
  application: 'my-service',
  operation: context.query.action,
  model: context.query.modelName,
})

const prisma = new PrismaClient({
  adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL }),
  comments: [appTags],
})
```
