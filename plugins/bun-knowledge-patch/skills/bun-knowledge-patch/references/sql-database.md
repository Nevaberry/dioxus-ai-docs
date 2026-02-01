# SQL & Database

## PostgreSQL (`Bun.sql`)

Tagged template literals with auto-escaping:

```ts
import { sql } from "bun";

const users = await sql`SELECT * FROM users WHERE age >= ${minAge}`;

// Bulk insert
await sql`INSERT INTO users (name, age) VALUES ${sql([
  { name: "Alice", age: 25 },
  { name: "Bob", age: 30 },
])}`;

// Results are arrays of objects
console.log(users); // [{ name: "Alice", age: 25 }, ...]
```

### Dynamic Columns

```ts
// Insert/update specific columns
await sql`INSERT INTO users ${sql(user, "name", "email")}`;
await sql`UPDATE users SET ${sql(user, "name", "email")} WHERE id = ${user.id}`;

// WHERE IN
await sql`SELECT * FROM users WHERE id IN ${sql([1, 2, 3])}`;
await sql`SELECT * FROM users WHERE id IN ${sql(users, "id")}`;
```

### Multi-Statement Queries

```ts
await sql`
  CREATE TABLE users (id SERIAL PRIMARY KEY);
  INSERT INTO users DEFAULT VALUES;
  SELECT * FROM users;
`.simple();
```

Note: Simple queries cannot use parameters.

### PostgreSQL Array Types

```ts
await sql`INSERT INTO users (roles) VALUES (${sql.array(["admin", "user"], "TEXT")})`;
await sql`SELECT ${sql.array([1, 2, 3], "INTEGER")} as nums`;
```

Supports: `TEXT`, `INTEGER`, `BIGINT`, `BOOLEAN`, `JSON`, `JSONB`, `TIMESTAMP`, `UUID`.

### Unix Socket Connection

```ts
import { SQL } from "bun";

const sql = new SQL({
  path: "/tmp/.s.PGSQL.5432",
  user: "postgres",
  database: "mydb",
});
```

### Preconnect at Startup

```sh
bun --sql-preconnect index.js  # Uses $DATABASE_URL
```

## Unified SQL Client (`Bun.SQL`)

Same API for PostgreSQL, MySQL/MariaDB, and SQLite:

```ts
import { SQL } from "bun";

// MySQL/MariaDB
const mysql = new SQL("mysql://user:pass@localhost:3306/mydb");

// SQLite
const sqlite = new SQL(":memory:");
// or: new SQL("sqlite://path/to/db.sqlite")

// Same tagged template API
await sqlite`CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)`;
await sqlite`INSERT INTO users (name) VALUES ${SQL.values([["Alice"], ["Bob"]])}`;
```

Error classes: `Bun.SQL.PostgresError`, `Bun.SQL.MySQLError`, `Bun.SQL.SQLiteError` (extend `Bun.SQL.SQLError`).

### MySQL Specifics

```ts
const result = await sql`INSERT INTO users (name) VALUES ('John')`;
result.lastInsertRowid; // e.g., 1
result.affectedRows;    // 1

// TLS connection
const sql = new SQL({ adapter: "mysql", tls: true, ... });
```

## SQLite (`bun:sqlite`)

```ts
import { Database } from "bun:sqlite";

// Map results to class instances
class User { id: number; name: string; }
const users = db.query("SELECT * FROM users").as(User).all();

// Iterate without loading all into memory
for (const row of db.query("SELECT * FROM users").iterate()) { }

// Track changes
const { changes, lastInsertRowid } = db.run("INSERT INTO ...");

// BigInt support
const db = new Database(":memory:", { safeIntegers: true });

// Strict parameter mode (no $ prefix needed)
const db = new Database(":memory:", { strict: true });
db.query("SELECT $name").all({ name: "Alice" });
```

### Column Type Introspection

```ts
const stmt = db.query("SELECT id, name, id + 1 AS computed FROM users");
stmt.get();

stmt.declaredTypes; // ["INTEGER", "TEXT", null] - from schema
stmt.columnTypes;   // ["INTEGER", "TEXT", "INTEGER"] - from values
```

## Redis (`Bun.redis`)

```ts
import { redis, RedisClient } from "bun";

// Uses $REDIS_URL by default
await redis.set("foo", "bar");
const value = await redis.get("foo"); // "bar"

// With TTL
await redis.set("foo", "bar", "EX", 10);
await redis.ttl("foo"); // 10

// Custom client
const client = new RedisClient("redis://localhost:6379/2"); // DB #2
await client.set("key", "value");

// Binary data
const buffer = await redis.getBuffer("binary-key"); // Uint8Array | null

// Hash fields
const value = await redis.hget("my-hash", "field");

// Unsupported commands
await redis.send("PING", []); // "PONG"
```

### Redis Pub/Sub

```ts
// Subscriber
const sub = new RedisClient("redis://localhost:6379");
await sub.connect();
await sub.subscribe("my-channel", (message, channel) => {
  console.log(`${channel}: ${message}`);
});

// Publisher
const pub = new RedisClient("redis://localhost:6379");
await pub.connect();
pub.publish("my-channel", "Hello!");
```
