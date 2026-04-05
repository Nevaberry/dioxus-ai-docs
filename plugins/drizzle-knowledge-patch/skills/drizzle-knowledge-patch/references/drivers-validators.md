# Drivers & Validator Packages

## `node-sqlite` Driver (beta.17)

Drizzle now supports Node.js's built-in `node:sqlite` module (`DatabaseSync`).

```ts
import { drizzle } from 'drizzle-orm/node-sqlite';

// Simple — pass a file path
const db = drizzle("sqlite.db");

// Or pass an existing DatabaseSync instance
import { DatabaseSync } from 'node:sqlite';
const sqlite = new DatabaseSync('sqlite.db');
const db = drizzle({ client: sqlite });
```

## Effect Postgres Driver (beta.13)

The `drizzle-orm/effect-postgres` driver was redesigned for Effect-native usage.

- `PgDrizzle.make(opts)` / `PgDrizzle.makeWithDefaults()` replace manual `drizzle(client)` construction
- `PgDrizzle.DefaultServices` provides no-op logger + no cache by default
- `EffectLogger.layer` enables Effect-native query logging; `EffectLogger.layerFromDrizzle(logger)` wraps Drizzle loggers
- `EffectCache.layerFromDrizzle(cache)` wraps Drizzle cache for Effect

```ts
import * as PgDrizzle from 'drizzle-orm/effect-postgres';
import { EffectLogger } from 'drizzle-orm/effect-postgres';

const program = Effect.gen(function*() {
  const db = yield* PgDrizzle.make({ relations }).pipe(
    Effect.provide(EffectLogger.layer),
    Effect.provide(PgDrizzle.DefaultServices),
  );
  const users = yield* db.select().from(usersTable);
});
Effect.runPromise(program.pipe(Effect.provide(PgClientLive)));
```

## Validator Packages Consolidated into `drizzle-orm` (beta.15)

Separate validator packages are now available as `drizzle-orm` subpath imports. Old packages still work but new imports are recommended. No breaking changes — just change the import path.

| Old Package | New Import |
|-------------|------------|
| `drizzle-zod` | `drizzle-orm/zod` |
| `drizzle-valibot` | `drizzle-orm/valibot` |
| `drizzle-typebox` | `drizzle-orm/typebox` (using `typebox`) or `drizzle-orm/typebox-legacy` (using `@sinclair/typebox`) |
| `drizzle-arktype` | `drizzle-orm/arktype` |
| (new) | `drizzle-orm/effect-schema` for Effect Schema validation |

```ts
// Before
import { createInsertSchema } from 'drizzle-zod';
// After
import { createInsertSchema } from 'drizzle-orm/zod';
```
