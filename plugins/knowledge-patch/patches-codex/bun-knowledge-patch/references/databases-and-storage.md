# Databases and storage

Use this reference for SQL adapters, SQLite, Redis, S3, archives, and credential storage.

## `Bun.SQL` error hierarchy

*Batch: `1.2.21`.*

Database errors are exposed as `Bun.SQL.PostgresError`, `SQLiteError`, and `MySQLError`, all extending `Bun.SQL.SQLError`, enabling adapter-specific or common `instanceof` checks.

```ts
try {
  await Bun.sql`SELECT invalid`;
} catch (error) {
  if (error instanceof Bun.SQL.SQLError) console.error(error);
}
```

## Binary Redis reads

*Batch: `1.2.13`.*

`RedisClient.getBuffer()` retrieves a Redis value without text decoding and resolves to `Uint8Array | null`.

```ts
import { redis } from "bun";
const bytes = await redis.getBuffer("asset");
```

## Built-in Postgres client

*Batch: `1.2-guide`.*

`Bun.sql` is a pooled Postgres tagged-template client that parameterizes interpolated values and automatically uses prepared statements. `sql(rows)` expands object arrays for bulk values, and `postgres({...})` from `bun` creates explicitly configured clients compatible with the `postgres.js` style.

```ts
import { sql } from "bun";
await sql`INSERT INTO users (name, age) VALUES ${sql([{ name: "Ada", age: 37 }])}`;
const users = await sql`SELECT * FROM users WHERE age >= ${18}`;
```

## Built-in Redis client

*Batch: `1.2.9`.*

The experimental `redis` singleton is a built-in Redis/Valkey client configured by `REDIS_URL`, while `RedisClient` creates explicitly configured connections. It wraps 66 commands, and unsupported commands can fall back to `redis.send(command, args)`.

```ts
import { redis, RedisClient } from "bun";

await redis.set("session", "active", "EX", 10);
const value = await redis.get("session");
const local = new RedisClient("redis://localhost:6379");
```

## Built-in S3 client

*Batch: `1.2-guide`.*

`Bun.s3` is a default `S3Client` configured by the usual AWS credential environment variables; custom clients can supply `endpoint`, `region`, and `bucket` for S3-compatible services. Its lazy, Blob-like files support reads, writes, multipart writers, and presigned URLs, while `Bun.file()` and `fetch()` accept `s3://` URLs.

```ts
import { s3 } from "bun";
const object = s3.file("folder/report.json");
await object.write(JSON.stringify({ ok: true }));
const data = await object.json();
const uploadURL = s3.presign("folder/upload.bin", { expiresIn: 3600 });
```

Passing an S3 file to `new Response()` produces a redirect to its presigned URL instead of proxying the object through the server.

## Configurable SQLite deserialization

*Batch: `1.2.6`.*

`Database.deserialize()` now accepts database options, allowing a deserialized database to opt into settings such as `readonly`, `strict`, and `safeIntegers` immediately.

```ts
import { Database } from "bun:sqlite";

const db = Database.deserialize(serializedData, {
  readonly: true,
  strict: true,
  safeIntegers: true,
});
```

## Dynamic `Bun.sql` columns and value lists

*Batch: `1.2.5`.*

Calling `sql(object, ...columns)` inside a query expands selected object keys for inserts and updates; omitting the column names in an update uses every key. For an `IN` clause, `sql(array)` expands scalar values and `sql(arrayOfObjects, "column")` selects one key from each object.

```ts
await sql`INSERT INTO users ${sql(user, "name", "email")}`;
await sql`UPDATE users SET ${sql(user)} WHERE id = ${user.id}`;
await sql`SELECT * FROM users WHERE id IN ${sql([1, 2, 3])}`;
```

## MySQL and MariaDB through `Bun.SQL`

*Batch: `1.2.21`.*

`SQL` now has a built-in MySQL/MariaDB adapter, selected by a `mysql://` URL or `adapter: "mysql"` connection options; it uses the same tagged-query interface as the PostgreSQL client.

```ts
import { SQL } from "bun";
const sql = new SQL("mysql://user:password@127.0.0.1:3306/app");
const users = await sql`SELECT * FROM users`;
```

## MySQL result metadata and value decoding

*Batch: `1.2.22`.*

MySQL query results now expose `affectedRows` and `lastInsertRowid`. Safe `INT`, `TINYINT`, and `MEDIUMINT` values decode as numbers, `BIT(1)` as a boolean, and binary-protocol `BIT(N)` values where N is greater than one as numbers.

```ts
const result = await Bun.sql`INSERT INTO users (name) VALUES ('Ada')`;
console.log(result.affectedRows, result.lastInsertRowid);
```

## MySQL TLS and native-password authentication

*Batch: `1.2.22`.*

`Bun.SQL` accepts `tls` for encrypted MySQL connections and now handles `mysql_native_password` plus authentication switching.

```ts
import { SQL } from "bun";
const db = new SQL("mysql://user:password@db.example/app", { tls: true });
```

## Native operating-system credential storage

*Batch: `1.2.21`.*

`Bun.secrets` asynchronously stores, retrieves, and deletes credentials in the platform credential manager using a service/name pair.

```ts
import { secrets } from "bun";
await secrets.set({ service: "my-cli", name: "token", value: "secret" });
const token = await secrets.get({ service: "my-cli", name: "token" });
```

## Node-compatible SQLite

*Batch: `1.4-3`.*

`node:sqlite` is now implemented using Bun's bundled SQLite, including `DatabaseSync`, `StatementSync`, backups, sessions and changesets, scalar/aggregate/window functions, authorizers, and `process.versions.sqlite`.

## Postgres protocol controls

*Batch: `1.2.3`.*

Appending `.simple()` uses PostgreSQL's simple-query protocol for multi-statement queries, but it cannot contain interpolated parameters. Set `prepare: false` on a `Bun.SQL` client when prepared statements are unsuitable, such as with PgBouncer transaction mode.

```ts
await Bun.sql`SELECT 1; SELECT 2;`.simple();
const sql = new Bun.SQL({ url: databaseURL, prepare: false });
```

## Postgres result decoding

*Batch: `1.2.3`.*

PostgreSQL arrays of integers, text, dates, timestamps, and other supported types now decode to JavaScript arrays, preserving database `NULL` elements as `null`. PostgreSQL `numeric` values received in binary format are returned as strings to avoid precision loss.

## PostgreSQL binary and custom-type decoding

*Batch: `1.2.4`.*

The built-in PostgreSQL client now correctly detects binary-format values and handles custom type OIDs, so binary and custom-type columns can be selected through normal tagged queries.

```ts
const rows = await Bun.sql`SELECT bytea_column, custom_type_column FROM records`;
```

## PostgreSQL connection flushing

*Batch: `1.2.11`.*

The built-in PostgreSQL client's `flush()` method is now implemented instead of being `undefined`.

```ts
import { sql } from "bun";

await sql`SELECT * FROM users`;
sql.flush();
```

## PostgreSQL startup preconnection

*Batch: `1.2.19`.*

`bun --sql-preconnect app.ts` opens the connection from `DATABASE_URL` before application code runs. A failed warm-up is non-fatal; the first query attempts to connect normally.

## PostgreSQL Unix sockets and startup parameters

*Batch: `1.2.6`.*

`Bun.SQL` accepts `path` as either a full PostgreSQL Unix-socket path or a directory, in which case it appends `/.s.PGSQL.{port}`. Runtime settings such as `search_path` can also be supplied through URL query parameters or the `connection` options object.

```ts
import { SQL } from "bun";

await using local = new SQL({ path: "/tmp", user: "postgres", database: "mydb" });
await using scoped = new SQL(databaseURL, {
  connection: { search_path: "information_schema" },
});
```

## Redis connection lifecycle

*Batch: `1.4-3`.*

`RedisClient.idleTimeout` now starts at connection and resets on incoming data instead of acting like a connection timeout. Failed or explicitly closed clients cancel retries and release their sockets, while `duplicate()` of a closed client starts as a fresh reconnectable client.

## Redis connections stay open when idle

*Batch: `1.2.10`.*

The built-in Redis client's default idle timeout changed from 30 seconds to `0`, meaning no idle timeout. Connections now remain active indefinitely by default.

## Redis database selection

*Batch: `1.2.22`.*

`RedisClient` accepts a database number in the standard Redis URL path, avoiding a separate `SELECT` command.

```ts
import { RedisClient } from "bun";
const db2 = new RedisClient("redis://localhost:6379/2");
```

## Redis Pub/Sub and TLS

*Batch: `1.2.23`.*

`RedisClient.subscribe()` registers a channel callback receiving the message and channel, while `publish()` sends messages; Redis TLS connections through `rediss://` or `tls: true` now work as well.

```ts
import { RedisClient } from "bun";
const subscriber = new RedisClient("redis://localhost:6379");
await subscriber.connect();
await subscriber.subscribe("events", (message, channel) => console.log(channel, message));

const publisher = new RedisClient("redis://localhost:6379");
await publisher.connect();
await publisher.publish("events", "ready");
```

## Response metadata in S3 presigned URLs

*Batch: `1.3.7`.*

`S3File.presign()` now applies `contentDisposition` and `type` as the `response-content-disposition` and `response-content-type` query parameters.

```ts
const url = file.presign({
  contentDisposition: 'attachment; filename="report.pdf"',
  type: "application/octet-stream",
});
```

## S3 content encoding

*Batch: `1.3.7`.*

S3 uploads accept `contentEncoding` through file `.write()`, file `.writer()`, and bucket `.write()`, allowing pre-compressed objects to carry the correct `Content-Encoding` metadata.

```ts
await s3.file("data.json.gz").write(compressedData, { contentEncoding: "gzip" });
```

## S3 object listing

*Batch: `1.2.9`.*

`S3Client.list()` performs `ListObjectsV2` requests with prefix filtering, result limits, and continuation-token pagination. Results expose objects through `contents` and the next page token through `nextContinuationToken`.

```ts
const page = await client.list({
  bucket: "my-bucket",
  prefix: "uploads/",
  maxKeys: 100,
});
const next = await client.list({
  bucket: "my-bucket",
  prefix: "uploads/",
  continuationToken: page.nextContinuationToken,
});
```

## S3 Requester Pays buckets

*Batch: `1.3.6`.*

S3 operations accept `requestPayer: true` for buckets that charge request and transfer costs to the requester. The option applies to reads, writes, stat calls, and multipart uploads.

```ts
import { s3 } from "bun";

const file = s3.file("data.csv", {
  bucket: "requester-pays-bucket",
  requestPayer: true,
});
const data = await file.text();
```

## S3 storage classes

*Batch: `1.2.1`.*

S3 presigned requests now accept a `storageClass` option, allowing the upload's storage class to be included in the signed request.

```ts
import { s3 } from "bun";

const s3file = s3.file("archive.tar");
const uploadURL = s3file.presign({
  expiresIn: 10,
  storageClass: "GLACIER_IR",
});
```

## S3 upload content disposition

*Batch: `1.3.5`.*

The built-in S3 client accepts `contentDisposition` when creating an S3 file or writing an object. It applies to simple, multipart, and streaming uploads, allowing a later browser download to select inline display or an attachment filename.

```ts
import { s3 } from "bun";

await s3.write("report.pdf", Bun.file("./report.pdf"), {
  contentDisposition: 'attachment; filename="quarterly-report.pdf"',
});
```

## Safe SQL composition

*Batch: `1.2.3`.*

Executing a query as `sql("SELECT ...")` now throws `ERR_POSTGRES_NOT_TAGGED_CALL`; use a tagged template or explicitly opt into raw text with `sql.unsafe(query)`. Nested tagged-template fragments and their parameters can be interpolated into another query, and the client also gains `sql.array` and `sql.file` helpers.

```ts
const orderBy = (field: string) => sql`ORDER BY ${sql(field)} DESC`;
const posts = await sql`SELECT * FROM posts ${orderBy("created_at")}`;
const raw = await sql.unsafe(queryText);
```

## SQL decoding and TLS configuration

*Batch: `1.4-2`.*

MySQL `DATETIME`/`TIMESTAMP` values decode as UTC, and MariaDB 10.5+ JSON columns decode to JavaScript values instead of strings. PostgreSQL connections honor `PGSSLMODE` unless a URL option overrides it, and infinite date/timestamp values decode as numeric `Infinity` or `-Infinity` rather than invalid dates.

## SQL insert defaults and bulk columns

*Batch: `1.3.6`.*

The SQL object helper omits `undefined` properties from inserts so database defaults apply instead of receiving `NULL`. For bulk object inserts, columns are collected across every row rather than only from the first object, preventing later-row values from being dropped.

```ts
import { sql } from "bun";

await sql`INSERT INTO jobs ${sql({ name: "sync", created_at: undefined })}`;
await sql`INSERT INTO jobs ${sql([{ name: "a" }, { name: "b", priority: 1 }])}`;
```

## SQLite error codes

*Batch: `1.4-4`.*

Generic `bun:sqlite` failures such as syntax errors or unknown tables and columns now set `error.code` to `"SQLITE_ERROR"`, enabling the same error branching used with `better-sqlite3`.

## SQLite named parameters and shutdown

*Batch: `1.4-2`.*

The SQLite adapter's `sql.unsafe()` and `sql.file()` accept named-parameter objects for `:name`, `$name`, and `@name`; keys retain their prefix unless the connection uses `strict: true`. `db.close()` now finalizes statements created by `db.query()` but leaves `db.prepare()` statements usable, while `db.close(true)` finalizes both kinds.

## SQLite object and streaming queries

*Batch: `1.2-guide`.*

`Database.query(...).as(Class)` maps rows onto a class prototype without invoking constructors or supporting initializers/private fields. Queries also implement iteration directly, while `.iterate()` explicitly yields rows without loading the full result set.

```ts
const query = db.query("SELECT * FROM users").as(User);
for (const user of query.iterate()) console.log(user);
```

## SQLite result type metadata

*Batch: `1.2.17`.*

`bun:sqlite` statements expose `declaredTypes` from the table schema and `columnTypes` from the first result row's actual values. Execute the statement before reading them; schema types are `null` for computed columns.

```ts
import { Database } from "bun:sqlite";

const db = new Database(":memory:");
const stmt = db.query("SELECT 1 + 1 AS result");
stmt.get();
console.log(stmt.declaredTypes, stmt.columnTypes); // [null], ["INTEGER"]
```

## SQLite strictness and integer handling

*Batch: `1.2-guide`.*

`new Database(path, { strict: true })` allows unprefixed object keys for `$`, `@`, or `:` parameters and throws for missing parameters. `{ safeIntegers: true }` or `query.safeIntegers(true)` preserves 64-bit values as `bigint`; `db.run()` now returns `changes` and `lastInsertRowid`.

## SQLite through `Bun.SQL`

*Batch: `1.2.21`.*

The unified `SQL` API also accepts `":memory:"` or a `sqlite://` file URL, and `SQL.values()` expands row arrays for bulk values.

```ts
import { SQL } from "bun";
const db = new SQL(":memory:");
await db`CREATE TABLE users (name TEXT)`;
await db`INSERT INTO users VALUES ${SQL.values([["Ada"], ["Lin"]])}`;
```

## Tar archives with `Bun.Archive`

*Batch: `1.3.6`.*

`Bun.Archive` creates and reads tar archives from file maps, blobs, typed arrays, or array buffers. It can list entries with an optional glob, extract to disk, emit bytes or a blob, and gzip output at levels 1–12; an archive can be passed directly to `Bun.write()` for local or S3 output.

```ts
const archive = new Bun.Archive(
  { "hello.txt": "Hello" },
  { compress: "gzip", level: 6 },
);
await Bun.write("bundle.tar.gz", archive);
await new Bun.Archive(await Bun.file("input.tar.gz").bytes()).extract("./out");
```

## TypeScript 5.9 and SQLite transaction types

*Batch: `1.2.20`.*

`@types/bun` is now compatible with TypeScript 5.9 without the prior `ArrayBuffer` conflict that required `skipLibCheck`. The `bun:sqlite` types also infer a transaction callback's arguments and return value through `db.transaction()`.

## Virtual-hosted S3 endpoints

*Batch: `1.2.3`.*

`S3Client` accepts `virtualHostedStyle: true` for S3-compatible services whose bucket is part of the hostname rather than the URL path.

```ts
import { S3Client } from "bun";
const s3 = new S3Client({ bucket: "my-bucket", virtualHostedStyle: true });
```
