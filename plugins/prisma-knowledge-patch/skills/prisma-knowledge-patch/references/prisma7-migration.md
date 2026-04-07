# Prisma 7 Migration Guide

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Node.js | 20.19.0 | 22.x |
| TypeScript | 5.4.0 | 5.9.x |

## Step 1: Update Packages

```bash
npm install @prisma/client@7
npm install -D prisma@7
```

## Step 2: ESM Configuration

```json
// package.json
{
  "type": "module"
}
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "module": "ESNext",
    "moduleResolution": "bundler",
    "target": "ES2023",
    "strict": true,
    "esModuleInterop": true
  }
}
```

## Step 3: Update Schema

```prisma
// schema.prisma
generator client {
  provider = "prisma-client"          // was "prisma-client-js"
  output   = "../src/generated/prisma" // REQUIRED — no longer in node_modules
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")       // still works but CLI config moves to prisma.config.ts
}
```

## Step 4: Create prisma.config.ts

```ts
// prisma.config.ts (project root, next to package.json)
import "dotenv/config"
import { defineConfig, env } from "prisma/config"

export default defineConfig({
  schema: "prisma/schema.prisma",
  migrations: {
    path: "prisma/migrations",
    seed: "tsx prisma/seed.ts",
  },
  datasource: {
    url: env("DATABASE_URL"),
    // shadowDatabaseUrl: env("SHADOW_DATABASE_URL"),  // optional
  },
})
```

Install dotenv (Bun users skip this):
```bash
npm install dotenv
```

## Step 5: Install Driver Adapter

### PostgreSQL
```bash
npm install @prisma/adapter-pg pg
```

```ts
import { PrismaClient } from "./generated/prisma/client"
import { PrismaPg } from "@prisma/adapter-pg"

const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_URL,
})
export const prisma = new PrismaClient({ adapter })
```

### SQLite
```bash
npm install @prisma/adapter-better-sqlite3
```

```ts
import { PrismaClient } from "./generated/prisma/client"
import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3"

const adapter = new PrismaBetterSqlite3({
  url: process.env.DATABASE_URL || "file:./dev.db",
})
export const prisma = new PrismaClient({ adapter })
```

### MySQL
```bash
npm install @prisma/adapter-mysql2 mysql2
```

### Prisma Accelerate / Prisma Postgres
Do NOT pass `prisma://` or `prisma+postgres://` URLs to a driver adapter. Use the Accelerate extension:

```ts
import { PrismaClient } from "./generated/prisma/client"
import { withAccelerate } from "@prisma/extension-accelerate"

export const prisma = new PrismaClient({
  accelerateUrl: process.env.DATABASE_URL,
}).$extends(withAccelerate())
```

## Step 6: Update Imports

```ts
// Before
import { PrismaClient } from "@prisma/client"
// After
import { PrismaClient } from "./generated/prisma/client"
```

Adjust path based on your `output` config and importing file location.

## Step 7: Replace Middleware with Extensions

```ts
// Before (removed)
prisma.$use(async (params, next) => {
  console.log(params.model, params.action)
  return next(params)
})

// After
const prisma = new PrismaClient({ adapter }).$extends({
  query: {
    $allModels: {
      async $allOperations({ model, operation, args, query }) {
        console.log(model, operation)
        return query(args)
      },
    },
  },
})
```

## Step 8: Update CLI Workflows

```bash
# Generate is no longer automatic
npx prisma generate

# Then run migrations
npx prisma migrate dev

# Seeding is no longer automatic
npx prisma db seed
```

## Step 9: SSL Certificate Handling

If you get `P1010: User was denied access`, configure SSL:

```ts
const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },  // or configure proper certs
})
```

Or use `NODE_EXTRA_CA_CERTS` environment variable.

## Connection Pool Notes

Driver adapters use the underlying driver's pool settings, which may differ from v6:
- `pg` driver: no connection timeout by default (v6 used 5s)
- Configure pool settings on the adapter, not via Prisma connection string parameters

## Removed CLI Flags

| Command | Removed Flag | Alternative |
|---------|-------------|-------------|
| `prisma generate` | `--data-proxy`, `--accelerate`, `--no-engine`, `--allow-no-models` | (not needed) |
| `prisma migrate dev` | `--skip-generate`, `--skip-seed` | (not needed — no longer auto) |
| `prisma db push` | `--skip-generate` | (not needed) |
| `prisma db execute` | `--schema`, `--url` | Configure in `prisma.config.ts` |
| `prisma migrate diff` | `--from-url`, `--to-url`, `--from-schema-datasource`, `--to-schema-datasource` | `--from-config-datasource`, `--to-config-datasource` |

## Removed Environment Variables

`PRISMA_CLI_QUERY_ENGINE_TYPE`, `PRISMA_CLIENT_ENGINE_TYPE`, `PRISMA_QUERY_ENGINE_BINARY`, `PRISMA_QUERY_ENGINE_LIBRARY`, `PRISMA_GENERATE_SKIP_AUTOINSTALL`, `PRISMA_SKIP_POSTINSTALL_GENERATE`, `PRISMA_GENERATE_IN_POSTINSTALL`, `PRISMA_GENERATE_DATAPROXY`, `PRISMA_GENERATE_NO_ENGINE`, `PRISMA_CLIENT_NO_RETRY`, `PRISMA_MIGRATE_SKIP_GENERATE`, `PRISMA_MIGRATE_SKIP_SEED`

## MongoDB

Prisma 7 does **not yet support MongoDB**. Continue using Prisma 6 for MongoDB projects.
