---
name: drizzle-knowledge-patch
description: "Drizzle ORM v1.0 beta changes since training cutoff (latest: 1.0.0-beta.19) — new relational query builder v2 with defineRelations, object-based where/orderBy, node-sqlite driver, validator consolidation, Effect Postgres. Load before writing Drizzle ORM code."
license: MIT
metadata:
  author: Nevaberry
  version: "1.0.0-beta.19"
---

# Drizzle ORM v1.0 Knowledge Patch

Claude's baseline knowledge covers Drizzle ORM through 0.30.x. This skill provides features from v1.0 beta (2024–2025).

## Quick Reference

### Relational Query Builder v2 (completely redesigned in v1)

| Old API | New API |
|---------|---------|
| `relations()` | `defineRelations(schema, callback)` |
| `drizzle({ schema })` | `drizzle({ relations })` |
| `where: (fields, ops) => ops.eq(...)` | `where: { id: 1 }` (object syntax) |
| `orderBy: (fields, ops) => ops.asc(...)` | `orderBy: { id: 'asc' }` |

```ts
const relations = defineRelations(schema, (r) => ({
  users: {
    posts: r.many.posts(),
    profile: r.one.profiles({ from: r.users.id, to: r.profiles.userId }),
  },
}));
const db = drizzle({ relations });
```

**Object-based `where` operators:** `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `notIn`, `like`, `ilike`, `notLike`, `notIlike`, `isNull`, `isNotNull`, `arrayOverlaps`, `arrayContained`, `arrayContains`.

**Many-to-many** uses `.through()`:

```ts
groups: r.many.groups({
  from: r.users.id.through(r.usersToGroups.userId),
  to: r.groups.id.through(r.usersToGroups.groupId),
}),
```

**Filter by relations** (find users who have matching posts):

```ts
db.query.users.findMany({
  where: { posts: { content: { like: 'M%' } } },
});
```

**Nested `with` now supports `offset`:**

```ts
db.query.posts.findMany({
  with: { comments: { limit: 3, offset: 5 } },
});
```

See `references/relational-queries.md` for full defineRelations API, OR/AND/NOT combinators, nested orderBy.

### Drivers & Integrations

| Feature | Import / Usage |
|---------|---------------|
| Node.js built-in SQLite | `drizzle-orm/node-sqlite` — pass file path or `DatabaseSync` |
| Effect Postgres | `drizzle-orm/effect-postgres` — `PgDrizzle.make(opts)` |
| Zod schemas | `drizzle-orm/zod` (replaces `drizzle-zod`) |
| Valibot schemas | `drizzle-orm/valibot` (replaces `drizzle-valibot`) |
| TypeBox schemas | `drizzle-orm/typebox` (replaces `drizzle-typebox`) |
| ArkType schemas | `drizzle-orm/arktype` (replaces `drizzle-arktype`) |
| Effect Schema | `drizzle-orm/effect-schema` (new) |

**Node.js built-in SQLite:**

```ts
import { drizzle } from 'drizzle-orm/node-sqlite';
const db = drizzle("sqlite.db");  // or pass DatabaseSync instance via { client }
```

**Validator migration** — just change the import path (no breaking changes):

```ts
// Before: import { createInsertSchema } from 'drizzle-zod';
import { createInsertSchema } from 'drizzle-orm/zod';
```

See `references/drivers-validators.md` for Effect Postgres API, TypeBox legacy vs modern, full migration table.

### Schema, Migrations & Query Features

| Feature | Details |
|---------|---------|
| `.generatedAlwaysAs()` | Now requires `` sql`...` `` — raw strings removed (breaking) |
| `drizzle-kit check` | Detects conflicting migrations across branches (PG, MySQL) |
| `.comment()` | Adds SQL comments (sqlcommenter) for query metadata |

**`.generatedAlwaysAs()` now requires `sql` template:**

```ts
// Old (broken): generatedAlwaysAs("col1 + col2")
generatedAlwaysAs(sql`col1 + col2`)
generatedAlwaysAs(() => sql`${table.col1} + ${table.col2}`)
```

**`.comment()` for query metadata (sqlcommenter):**

```ts
db.select().from(users).comment({ priority: 'high', category: 'analytics' });
// → select "id", "name" from "users" /*priority='high',category='analytics'*/
```

See `references/schema-migrations-queries.md` for drizzle-kit check details, comment string form.

## Reference Files

| File | Contents |
|------|----------|
| `relational-queries.md` | defineRelations, many-to-many, object where/orderBy, nested offset |
| `drivers-validators.md` | node-sqlite, Effect Postgres, validator package consolidation |
| `schema-migrations-queries.md` | generatedAlwaysAs breaking change, drizzle-kit check, .comment() |

## Critical Examples

### Full Relational Query

```ts
import { defineRelations } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/node-postgres';
import * as schema from './schema';

const relations = defineRelations(schema, (r) => ({
  users: {
    posts: r.many.posts(),
    profile: r.one.profiles({ from: r.users.id, to: r.profiles.userId }),
  },
  posts: {
    author: r.one.users({ from: r.posts.authorId, to: r.users.id }),
    comments: r.many.comments(),
  },
}));

const db = drizzle({ relations });

const results = await db.query.users.findMany({
  where: {
    OR: [{ age: { gt: 18 } }, { name: { like: 'A%' } }],
    NOT: { id: { in: [1, 2, 3] } },
  },
  orderBy: { id: 'asc' },
  with: {
    posts: {
      orderBy: { id: 'desc' },
      limit: 10,
      offset: 5,
    },
  },
});
```

### Effect Postgres

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
