---
name: prisma-knowledge-patch
description: >
  Prisma 6.2–7.3 features: v7 migration (new generator, driver adapters required,
  prisma.config.ts), ULID support, updateManyAndReturn, batch limits, mapped enums,
  SQLite json/enum, sqlcommenter observability, compilerBuild option.
  Load before writing Prisma 6.2+ code.
license: MIT
metadata:
  author: Nevaberry
  version: "7.3"
---

# Prisma 6.2+ Knowledge Patch

Claude's baseline knowledge covers Prisma through 6.1. This skill provides features from 6.2 onwards, including the major v7 rewrite.

## Reference Index

- [v7 Migration Guide](references/v7-migration.md) — New generator, driver adapters required, `prisma.config.ts`, env loading changes, removed features, MongoDB dropped
- [Schema Features](references/schema-features.md) — ULID `@default(ulid())`, mapped enums with `@map`, SQLite `Json` and `enum` support
- [Query API](references/query-api.md) — `updateManyAndReturn`, `limit` on `updateMany`/`deleteMany`
- [Observability](references/observability.md) — SQL comments via `@prisma/sqlcommenter`, query tags, trace context, custom plugins

## Quick Reference — v7 Migration Essentials

Prisma 7.0 is a major rewrite. The three critical changes:

### 1. New Generator (Required)

```prisma
generator client {
  provider = "prisma-client"              // was "prisma-client-js"
  output   = "../src/generated/prisma"    // output is now REQUIRED
}
```

```ts
// Import from generated path, NOT @prisma/client
import { PrismaClient } from './generated/prisma/client'
```

### 2. Driver Adapters (Required)

Empty `new PrismaClient()` no longer works. You must pass a driver adapter:

```ts
import { PrismaClient } from './generated/prisma/client'
import { PrismaPg } from '@prisma/adapter-pg'

const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL })
const prisma = new PrismaClient({ adapter })
```

| Database | Adapter Package | Class |
|----------|----------------|-------|
| PostgreSQL | `@prisma/adapter-pg` | `PrismaPg` |
| SQLite | `@prisma/adapter-better-sqlite3` | `PrismaBetterSqlite3` |
| MariaDB | `@prisma/adapter-mariadb` | `PrismaMariaDb` |
| Neon (HTTP) | `@prisma/adapter-neon` | `PrismaNeonHttp` |
| Turso/LibSQL | `@prisma/adapter-libsql` | `PrismaLibSql` |
| Cloudflare D1 | `@prisma/adapter-d1` | `PrismaD1Http` |

Removed options: `datasources`, `datasourceUrl`, empty constructor.

### 3. `prisma.config.ts` (Required)

```ts
import 'dotenv/config'
import { defineConfig } from 'prisma/config'

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: { seed: 'tsx prisma/seed.ts' },
  datasource: { url: process.env.DATABASE_URL },
})
```

The schema `datasource` block no longer contains `url`, `directUrl`, or `shadowDatabaseUrl`. Prisma CLI no longer auto-loads `.env` files — use `dotenv` in config.

### Other v7 Breaking Changes

| Change | Details |
|--------|---------|
| No implicit `generate`/`seed` | Post-install hook removed; `prisma migrate` no longer runs them |
| `prisma` in `package.json` removed | Use `prisma.config.ts` for schema path and seed |
| MongoDB not supported | Stay on v6; support planned for future release |
| Client engines removed | No more LibraryEngine, BinaryEngine, DataProxyEngine |
| `prisma introspect` removed | Use `prisma db pull` |
| `metrics` preview removed | Use driver adapter pool metrics |

## Quick Reference — New Features (6.2+)

| Feature | Since | Notes |
|---------|-------|-------|
| `@default(ulid())` | 6.2 | Auto-generated ULID for `String` fields |
| `updateManyAndReturn` | 6.2 | PostgreSQL, CockroachDB, SQLite only |
| SQLite `Json` and `enum` | 6.2 | Native support in schema |
| `limit` on `updateMany`/`deleteMany` | 6.3 | Batch operation limiting |
| Enum `@map` | 7.0 | Map enum members to DB values |
| SQL comments (`sqlcommenter`) | 7.1 | Observability via query tags |
| `compilerBuild` option | 7.3 | `"fast"` (default) or `"small"` |

### ULID Support (6.2)

```prisma
model User {
  id String @id @default(ulid())
}
```

### `updateManyAndReturn` (6.2)

Returns actual rows (not just count). PostgreSQL, CockroachDB, SQLite only:

```ts
const users = await prisma.user.updateManyAndReturn({
  where: { email: { contains: 'prisma.io' } },
  data: { role: 'ADMIN' },
})
```

### `limit` on Batch Mutations (6.3)

```ts
await prisma.user.deleteMany({
  where: { inactive: true },
  limit: 100,
})
```

### SQLite `Json` and `enum` (6.2)

```prisma
model User {
  id   Int    @id @default(autoincrement())
  role Role
  data Json
}

enum Role {
  Customer
  Admin
}
```

### SQL Comments / Observability (7.1)

```ts
import { queryTags, withQueryTags } from '@prisma/sqlcommenter-query-tags'
import { traceContext } from '@prisma/sqlcommenter-trace-context'

const prisma = new PrismaClient({
  adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL }),
  comments: [queryTags(), traceContext()],
})

// Per-request tags via async context
const users = await withQueryTags(
  { route: '/api/users', requestId: 'abc-123' },
  () => prisma.user.findMany(),
)
// SQL: SELECT ... FROM "User" /*requestId='abc-123',route='/api/users'*/
```

### Prisma Accelerate (v7)

```ts
const prisma = new PrismaClient({
  accelerateUrl: process.env.DATABASE_URL,
}).$extends(withAccelerate())
```

### Mapped Enums

```prisma
enum PaymentProvider {
  MixplatSMS    @map("mixplat/sms")
  InternalToken @map("internal/token")
  Offline       @map("offline")
  @@map("payment_provider")
}
```

```ts
// Use Prisma-side names in TS (NOT @map values)
PaymentProvider.MixplatSMS // === "MixplatSMS"
```

### `compilerBuild` Option (7.3)

```prisma
generator client {
  provider      = "prisma-client"
  output        = "../src/generated/prisma"
  compilerBuild = "fast"  // "fast" (default) | "small"
}
```
