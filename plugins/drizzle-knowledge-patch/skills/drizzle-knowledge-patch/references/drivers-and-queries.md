# Drivers and Query APIs

## `node-sqlite` driver

*Since 1.0.0-beta.17 (2025-03-11)*

Drizzle supports Node.js's built-in `node:sqlite` module via `drizzle-orm/node-sqlite`.

```ts
import { drizzle } from 'drizzle-orm/node-sqlite';

// Simple usage (Drizzle creates the connection)
const db = drizzle("sqlite.db");

// With existing DatabaseSync instance
import { DatabaseSync } from 'node:sqlite';
const sqlite = new DatabaseSync('sqlite.db');
const db = drizzle({ client: sqlite });
```

---

## `.comment()` for query tagging (sqlcommenter)

*Since 1.0.0-beta.19 (2025-03-23)*

Chain `.comment()` on any query to append SQL comments with metadata tags. Works with PostgreSQL and MySQL.

```ts
// String form
db.select().from(users).comment("my_tag");

// Key-value object form (recommended)
db.select().from(users).comment({ priority: 'high', category: 'analytics' });
// → select ... from "users" /*priority='high',category='analytics'*/
```

Note: `.comment()` cannot be used with prepared statements.
