# Databases and storage

## `Bun.SQL`

### Tagged templates and Postgres (`1.2-guide`)

`Bun.sql` began as a Postgres tagged-template client modeled on `postgres.js`.
Interpolated values are parameterized; `sql(arrayOfObjects)` expands a multi-row
`VALUES` list.

```ts
import { sql } from "bun";

await sql`INSERT INTO users (name, age) VALUES ${sql([{ name: "Alice", age: 25 }])}`;
const rows = await sql`SELECT * FROM users WHERE age >= ${65}`;
```

### Safe composition and query modes (`1.2.3`)

- Calling `sql("query")` as a plain function throws
  `ERR_POSTGRES_NOT_TAGGED_CALL`; use a tagged template or
  `sql.unsafe(query)`.
- `.simple()` uses the simple query protocol for multiple statements and does
  not allow parameters.
- `new SQL({ prepare: false })` disables prepared statements for PgBouncer
  transaction mode.
- Nested template fragments compose for conditional clauses.
- Postgres array columns decode to JavaScript arrays with `null` elements.
- Binary-format `numeric` always decodes as a string.

### Object and array helpers (`1.2.5`, `1.2.23`, `1.3-guide`)

`sql(obj, ...columns)` builds insert column lists or update `SET` clauses.
Passing an array builds `WHERE IN`; passing objects plus a column plucks that
field. `sql.array(values, type)` binds a typed Postgres array and composes inside
object notation.

```ts
await sql`INSERT INTO users ${sql(user, "name", "email")}`;
await sql`UPDATE users SET ${sql(user)} WHERE id = ${user.id}`;
await sql`SELECT * FROM users WHERE id IN ${sql([1, 2, 3])}`;
await sql`UPDATE users SET ${sql({ roles: sql.array(["mod"], "TEXT") })}`;
```

Keys whose value is `undefined` are omitted rather than inserted as `NULL`.
If every value is `undefined`, the helper throws `SyntaxError`.

### Connections and pipelining (`1.2.6`, `1.2.11`, `1.2.19`)

- `new SQL({ path })` accepts a Unix socket file or directory; a directory gets
  `/.s.PGSQL.{port}` appended.
- Postgres runtime settings can come from URL query parameters or a
  `connection` object.
- `sql.flush()` pushes pending pipelined queries.
- Pipelining is automatic. `.execute()` eagerly starts a query so several can
  be awaited together.
- `--sql-preconnect` reads `DATABASE_URL` and opens during startup. Failure is
  non-fatal and is retried on the first query.

### MySQL/MariaDB and SQLite adapters (`1.2.21`)

`Bun.SQL` selects Postgres, MySQL/MariaDB, or SQLite from `adapter` or the URL.
SQLite accepts `:memory:` and `sqlite://...`; `.all()` is available, and
`SQL.values(rowArrays)` expands a multi-row list. Errors support `instanceof`
through `PostgresError`, `SQLiteError`, `MySQLError`, and shared `SQLError`.

```ts
const mysql = new Bun.SQL("mysql://user:pass@127.0.0.1:3306/db");
const sqlite = new Bun.SQL(":memory:");
await sqlite`INSERT INTO users (name) VALUES ${Bun.SQL.values([["A"], ["B"]])}`;
```

### Adapter result and binary changes (`1.2.22`, `1.3.6`)

- MySQL results expose `affectedRows` and `lastInsertRowid`, and the adapter
  accepts the same `tls` option as Postgres.
- MySQL `TINYINT` decodes to `number`; `BIT(1)` decodes to `boolean`.
- MySQL `BINARY`, `VARBINARY`, and `BLOB` decode to `Buffer`, not UTF-8 text.
- Bulk `sql([...])` collects columns from every object, preventing later-only
  keys from being dropped.

### Errors and parameter limits (`1.3.11`)

A Postgres query over 65,535 parameters throws `PostgresError` with code
`ERR_POSTGRES_TOO_MANY_PARAMETERS` instead of panicking.

### Decoding and named parameters (`1.4-2`)

- MySQL `DATETIME`/`TIMESTAMP` and Postgres timestamps read through `.simple()`
  decode as UTC; remove manual timezone correction.
- MariaDB 10.5+ JSON columns and JSON function results decode to parsed values.
- Postgres `date`/`timestamp` infinity becomes numeric `Infinity`.
- `PGSSLMODE` is honored unless URL `sslmode` overrides it.
- `connectionTimeout` covers the whole handshake.
- SQLite `sql.unsafe()` and `sql.file()` accept named parameter objects for
  `:name`, `$name`, or `@name`. Keys retain prefixes unless the connection is
  `strict: true`.

## `bun:sqlite`

### Strictness, integers, iteration, and disposal (`1.2-guide`)

```ts
const db = new Database(":memory:", { strict: true, safeIntegers: true });
const q = db.query("SELECT * FROM tweets").as(Tweet);
for (const row of q.iterate()) {}
const { changes, lastInsertRowid } = db.run("INSERT INTO users VALUES (1,'a')");
```

- `strict` lets parameters omit `$`/`@`/`:` and errors on missing values.
- `safeIntegers` returns 64-bit integers as `BigInt`; statements can enable it
  per query.
- `.as(Class)` sets the prototype with `Object.create()` semantics; it does not
  run constructors, field initializers, or private fields.
- Statements are iterable and both statements and databases support `using`.

### Construction and introspection (`1.2.6`, `1.2.10`, `1.2.17`)

- `Database.deserialize(data, options)` accepts constructor settings such as
  `readonly`, `strict`, and `safeIntegers`.
- `customSQLiteBinary` selects a shared SQLite library per database.
- After execution, `Statement.declaredTypes` reports schema types and
  `columnTypes` reports types derived from the first result row. Expressions or
  computed columns have `null` declared type.

### Versions, typing, and failure behavior (`1.2.18`, `1.2.20`, `1.3.2`, `1.3.14`, `1.4-2`, `1.4-4`)

- The bundled engine moved to SQLite 3.50.2 and later 3.53.0.
- `db.transaction()` infers its callback return type.
- Importing `better-sqlite3` fails with a readable recommendation to use
  `bun:sqlite` instead of crashing in `dlopen`.
- `db.close()` finalizes all `db.query()` statements; `db.close(true)` also
  finalizes statements from `db.prepare()`.
- Syntax errors and unknown tables/columns set `error.code` to
  `SQLITE_ERROR`.

## S3

### Client and file handles (`1.2-guide`)

`Bun.s3` is a default `S3Client` configured from `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY`. `s3.file()` is a lazy Blob-compatible handle supporting
`text`, `json`, `arrayBuffer`, `stream`, stat, delete, and presigned URLs.
Writes accept strings, typed arrays, Blob, or Response. `writer()` performs
multipart upload for large files.

```ts
const file = Bun.s3.file("folder/data.json");
await file.write('{"ok":true}');
await file.text();
const url = Bun.s3.presign("key", { expiresIn: 3600, acl: "public-read" });
```

`Bun.file("s3://...")` and S3 URL `fetch()` PUT/DELETE work. Returning
`new Response(s3.file(...))` from `Bun.serve` produces a 302 presigned redirect
rather than proxying bytes. A custom `S3Client` can set credentials, region,
endpoint, and bucket.

### Storage class and addressing (`1.2.1`, `1.2.3`)

- S3 operations accept `storageClass`, which is signed into a presigned URL as
  `x-amz-storage-class`; one supported value is `GLACIER_IR`.
- `virtualHostedStyle: true` places the bucket in the hostname for compatible
  services.

### Listing and multipart backpressure (`1.2.9`, `1.2.18`)

`client.list()` exposes ListObjectsV2 with camel-cased options/results and
continuation tokens. Multipart writer `flush()` returns a promise that resolves
when the current part uploads and therefore provides backpressure.

### Request and response metadata (`1.3.6`, `1.3.7`, `1.4-2`)

- Operations accept `requestPayer: true` for Requester Pays buckets.
- `presign()` applies `contentDisposition` and `type` via the corresponding
  response query parameters.
- Upload methods accept `contentEncoding`; `S3Client` accepts `requestPayer`
  globally or per operation, and write/writer accept both
  `contentDisposition` and `contentEncoding`.

## Redis and Valkey

### Built-in client (`1.2.9`, `1.2.10`)

`Bun.redis` is the default `RedisClient` configured by `REDIS_URL`. It was
experimental when introduced, exposed about 66 commands as methods, and routes
others through `send(command, args)`. Idle timeout defaults to `0`, meaning no
idle close.

```ts
await Bun.redis.set("foo", "bar", "EX", 10);
const value = await Bun.redis.get("foo");
```

### Binary values and URL handling (`1.2.13`, `1.2.22`, `1.3.1`)

- `getBuffer()` returns `Uint8Array | null` without string decoding.
- A database number in `redis://host:port/2` is honored.
- Constructing with an invalid URL throws instead of silently falling back to
  localhost.

### Pub/sub and connection duplication (`1.2.23`, `1.3-guide`)

Use `connect()`, `subscribe(channel, callback)`, and `publish()`. Subscriber
callbacks receive `(message, channel)`, in that order. A subscribed connection
cannot publish; use `RedisClient.duplicate()` for a separate connection.

### TLS (`1.4-2`)

A `rediss://` client verifies the certificate against the URL host and rejects
the first command on mismatch.

## Credentials, archives, and media

### OS credential storage (`1.2.21`)

`Bun.secrets.set/get/delete` are async and use macOS Keychain Services, Linux
`libsecret`, or Windows Credential Manager.

```ts
await Bun.secrets.set({ service: "my-cli", name: "token", value: "secret" });
const token = await Bun.secrets.get({ service: "my-cli", name: "token" });
await Bun.secrets.delete({ service: "my-cli", name: "token" });
```

### Tar archives (`1.3.6`)

`Bun.Archive` builds a tar from a path-to-content map or reads archive bytes.
It supports `blob()`, `bytes()`, filtered `files()`, extraction, gzip levels
1–12, worker-pool processing, direct `Bun.write()`, and S3 destinations.

```ts
const archive = new Bun.Archive({ "hello.txt": "hello" }, {
  compress: "gzip",
  level: 12,
});
await Bun.write("s3://bucket/archive.tar.gz", archive);
```

### Image processing (`1.3.14`)

`Bun.Image`, `Bun.file(path).image()`, and `blob.image()` form a chainable
decode/transform/encode pipeline. Inputs include paths, buffers, typed arrays,
Blob/BunFile/S3File, and data URLs. Transforms include resize, rotate, flip,
flop, and modulation; outputs include JPEG, PNG, WebP, HEIC, AVIF, bytes,
buffers, blobs, Base64/data URLs, placeholders, metadata, and file writes.

Image objects are valid response bodies with automatic content type. Work other
than metadata runs off the main thread. JPEG/PNG/WebP/GIF/BMP work everywhere;
TIFF, HEIC and AVIF are unavailable on Linux. Resize filters include sharp's
named filters plus `mks2013` and `mks2021`.

## Data formats tied to storage

Native YAML import and `Bun.YAML.parse()` arrived in `1.2.21`; stringify and
binary/Blob parsing followed in `1.2.22`. YAML parsing throws `SyntaxError` on
invalid input (`1.2.23`), follows YAML 1.2 boolean rules and quotes strings
ending in a colon (`1.3.5`), and rejects NUL input (`1.4-2`). For the full set
of JSONC, JSON5, JSONL, XML and TOML behavior, see the runtime reference.
