---
name: prisma-knowledge-patch
description: "Prisma changes since training cutoff (latest: 7.3) — v7 ESM rewrite, prisma-client generator, driver adapters, prisma.config.ts, TypedSQL, SQL comments. Load before working with Prisma."
license: MIT
version: "7.3"
metadata:
  author: Nevaberry
---

# Prisma 5.19+ / 7.x Knowledge Patch

Claude's baseline knowledge covers Prisma through 5.18. This skill provides changes from 5.19.0 onwards, with major focus on the Prisma 7 rewrite.

## Prisma 7 Breaking Changes Quick Reference

| What Changed | Old (v6) | New (v7+) |
|--------------|----------|-----------|
| Generator | `prisma-client-js` | `prisma-client` (required) |
| Output | Auto in `node_modules` | `output` field required |
| Import | `from "@prisma/client"` | `from "./generated/prisma/client"` |
| DB connection | Connection string in schema | Driver adapter required |
| Config | `schema.prisma` datasource | `prisma.config.ts` at project root |
| Module format | CJS | ESM only (`"type": "module"`) |
| Env vars | Auto-loaded `.env` | Manual load (use `dotenv`) |
| Middleware | `$use()` | Client Extensions `$extends()` |
| Seeding | Auto after `migrate dev` | Manual `prisma db seed` |
| Generate | Auto after `migrate dev` | Manual `prisma generate` |
| SSL certs | Ignored invalid certs | Validated by `node-pg` |

## Prisma 7 Setup

```prisma
// schema.prisma
generator client {
  provider = "prisma-client"
  output   = "../src/generated/prisma"
}
```

```ts
// prisma.config.ts (project root)
import "dotenv/config"
import { defineConfig, env } from "prisma/config"

export default defineConfig({
  schema: "prisma/schema.prisma",
  migrations: { path: "prisma/migrations", seed: "tsx prisma/seed.ts" },
  datasource: { url: env("DATABASE_URL") },
})
```

```ts
// app.ts — PostgreSQL
import { PrismaClient } from "./generated/prisma/client"
import { PrismaPg } from "@prisma/adapter-pg"

const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL })
export const prisma = new PrismaClient({ adapter })
```

```ts
// app.ts — SQLite
import { PrismaClient } from "./generated/prisma/client"
import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3"

const adapter = new PrismaBetterSqlite3({ url: "file:./dev.db" })
export const prisma = new PrismaClient({ adapter })
```

```ts
// app.ts — Prisma Accelerate (no adapter)
import { PrismaClient } from "./generated/prisma/client"
import { withAccelerate } from "@prisma/extension-accelerate"

export const prisma = new PrismaClient({
  accelerateUrl: process.env.DATABASE_URL,
}).$extends(withAccelerate())
```

See [references/prisma7-migration.md](references/prisma7-migration.md) for full upgrade guide.

## TypedSQL (5.19.0+)

Write `.sql` files in `prisma/sql/`, generate typed functions:

```sql
-- prisma/sql/getUsersByAge.sql
SELECT * FROM "User" WHERE "age" > $1
```

```ts
import { getUsersByAge } from "@prisma/client/sql"  // v6
// or from "./generated/prisma/sql" in v7
const users = await prisma.$queryRawTyped(getUsersByAge(18))
```

## SQL Comments / Observability (7.1.0+)

```ts
import { queryTags, withQueryTags } from '@prisma/sqlcommenter-query-tags'
import { traceContext } from '@prisma/sqlcommenter-trace-context'

const prisma = new PrismaClient({
  adapter,
  comments: [queryTags(), traceContext()],
})

// Per-request tags
const users = await withQueryTags(
  { route: '/api/users', requestId: 'abc-123' },
  () => prisma.user.findMany(),
)
// SQL: SELECT ... FROM "User" /*requestId='abc-123',route='/api/users'*/
```

Custom plugins implement `SqlCommenterPlugin` from `@prisma/sqlcommenter`.

## Other New Features

- **6.3.0**: `limit` on `updateMany()` and `deleteMany()`
- **6.3.0**: `NOT EXISTS` replaces `NOT IN` for PostgreSQL relation filters (better perf)
- **7.0.0**: MongoDB not yet supported in v7 (continue using v6)
- **7.0.0**: `prisma migrate diff` options renamed: `--from-url` → `--from-config-datasource`
- **7.3.0**: `compilerBuild` option (`"fast"` | `"small"`) in generator block
- **7.3.0**: Raw queries (`$executeRaw`/`$queryRaw`) bypass query compiler with driver adapters

## Prerequisites (v7)

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Node.js | 20.19.0 | 22.x |
| TypeScript | 5.4.0 | 5.9.x |
