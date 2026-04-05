# Prisma v7 Migration Guide

Prisma 7.0 is a ground-up rewrite. The Rust query engine is replaced by a pure TypeScript/ESM client. This reference covers all breaking changes.

## New Generator

The `prisma-client-js` generator is replaced by `prisma-client`:

```prisma
generator client {
  provider = "prisma-client"              // was "prisma-client-js"
  output   = "../src/generated/prisma"    // output is now REQUIRED
}
```

Import from the generated output path, not `@prisma/client`:

```ts
import { PrismaClient } from './generated/prisma/client'
```

## Driver Adapters Required

You can no longer call `new PrismaClient()` with no arguments or just a URL. A driver adapter must be passed:

```ts
import { PrismaClient } from './generated/prisma/client'
import { PrismaPg } from '@prisma/adapter-pg'

const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_URL,
})
const prisma = new PrismaClient({ adapter })
```

### Available Adapters

| Database | Package | Class |
|----------|---------|-------|
| PostgreSQL | `@prisma/adapter-pg` | `PrismaPg` |
| SQLite | `@prisma/adapter-better-sqlite3` | `PrismaBetterSqlite3` |
| MariaDB | `@prisma/adapter-mariadb` | `PrismaMariaDb` |
| Neon (HTTP) | `@prisma/adapter-neon` | `PrismaNeonHttp` |
| Turso/LibSQL | `@prisma/adapter-libsql` | `PrismaLibSql` |
| Cloudflare D1 | `@prisma/adapter-d1` | `PrismaD1Http` |

Removed constructor options: `datasources`, `datasourceUrl`, and the empty `new PrismaClient()`.

### Prisma Accelerate

```ts
const prisma = new PrismaClient({
  accelerateUrl: process.env.DATABASE_URL,
}).$extends(withAccelerate())
```

## `prisma.config.ts` Required

For introspection and migration, a TypeScript config file is required. The `datasource.url` moves from the schema to the config:

```ts
// prisma.config.ts
import 'dotenv/config'
import { defineConfig } from 'prisma/config'

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: {
    seed: 'tsx prisma/seed.ts',
  },
  datasource: {
    url: process.env.DATABASE_URL,
  },
})
```

The schema `datasource` block no longer contains `url`, `directUrl`, or `shadowDatabaseUrl`.

## No Automatic Env Loading

Prisma CLI no longer auto-loads `.env` files. Use `dotenv` explicitly in `prisma.config.ts` (as shown above with `import 'dotenv/config'`).

## No Implicit Generate or Seed

- Post-install hook no longer runs `prisma generate`. Run it explicitly.
- `prisma migrate` no longer runs `generate` or `seed` afterward. Run them explicitly.

## `prisma` Block in `package.json` Removed

Use `prisma.config.ts` instead for schema path and seed script configuration.

## MongoDB Not Supported

MongoDB users must stay on Prisma v6. Support is planned for a future release.

## Removed Features

- `metrics` preview feature — use driver adapter pool metrics instead
- Client engines (LibraryEngine, BinaryEngine, DataProxyEngine) — all removed
- `prisma generate` flags: `--data-proxy`, `--accelerate`, `--no-engine`, `--allow-no-models`
- `prisma introspect` command — use `prisma db pull` instead
