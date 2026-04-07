---
name: drizzle-knowledge-patch
description: "Drizzle ORM changes since training cutoff (latest: 1.0.0-beta.19) — consolidated validator imports, Effect Schema support, node-sqlite driver, .comment() query tagging. Load before working with Drizzle."
version: "1.0.0-beta.19"
license: MIT
metadata:
  author: Nevaberry
---

# Drizzle ORM Knowledge Patch

Claude Opus 4.6 knows Drizzle ORM through 0.30.x. This skill provides features from 1.0.0-beta.15 (2025-02-05) onwards.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Schema validation | [references/schema-validation.md](references/schema-validation.md) | Validator packages consolidated into `drizzle-orm`, Effect Schema support |
| Drivers and queries | [references/drivers-and-queries.md](references/drivers-and-queries.md) | `node-sqlite` driver, `.comment()` query tagging |

---

## Quick Reference

### Validator imports (consolidated)

Old standalone packages are now available as `drizzle-orm` subpath imports:

| Library | New import path |
|---|---|
| Zod | `drizzle-orm/zod` |
| Valibot | `drizzle-orm/valibot` |
| TypeBox | `drizzle-orm/typebox` |
| TypeBox (legacy) | `drizzle-orm/typebox-legacy` |
| ArkType | `drizzle-orm/arktype` |
| Effect Schema | `drizzle-orm/effect-schema` |

```ts
// Old (still works)
import { createInsertSchema } from 'drizzle-zod';
// New (recommended)
import { createInsertSchema } from 'drizzle-orm/zod';
```

See [references/schema-validation.md](references/schema-validation.md) for all import paths.

---

### `node-sqlite` driver

Use Node.js's built-in `node:sqlite` module:

```ts
import { drizzle } from 'drizzle-orm/node-sqlite';
const db = drizzle("sqlite.db");

// Or with existing DatabaseSync instance
import { DatabaseSync } from 'node:sqlite';
const sqlite = new DatabaseSync('sqlite.db');
const db = drizzle({ client: sqlite });
```

---

### `.comment()` query tagging

Append SQL comments to queries (PostgreSQL and MySQL):

```ts
db.select().from(users).comment("my_tag");
db.select().from(users).comment({ priority: 'high', category: 'analytics' });
// → select ... from "users" /*priority='high',category='analytics'*/
```

Note: Cannot be used with prepared statements.

See [references/drivers-and-queries.md](references/drivers-and-queries.md) for full details.

---

## Reference Files

| File | Contents |
|---|---|
| [schema-validation.md](references/schema-validation.md) | Validator packages consolidated into `drizzle-orm`, supported libraries, Effect Schema integration |
| [drivers-and-queries.md](references/drivers-and-queries.md) | `node-sqlite` driver setup, `.comment()` query tagging with sqlcommenter |
