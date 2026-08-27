# Replication and data location

## Sessions and bookmarks

Read replication uses the Workers binding Sessions API to group a logical
application's queries with sequential consistency:

```ts
const bookmark =
  request.headers.get("x-d1-bookmark") ?? "first-unconstrained";
const session = env.DB.withSession(bookmark);
const result = await session
  .prepare("SELECT * FROM Customers WHERE CompanyName = 'Bs Beverages'")
  .run();
response.headers.set("x-d1-bookmark", session.getBookmark() ?? "");
```

Carry `getBookmark()` into a later session when consistency must span session
boundaries. D1 creates and routes read replicas automatically.

`withSession()` and `withSession("first-unconstrained")` allow the first query
to run on either the primary or a replica. Use
`withSession("first-primary")` when the first query must begin from the latest
primary database version:

```ts
const unconstrained = env.DB.withSession();
const latest = env.DB.withSession("first-primary");
```

Sessions exist only on the D1 Workers binding, not the REST API.

## Database replication controls

Read replication is enabled per database. Send `read_replication.mode` as
`"auto"` or `"disabled"` to the database REST endpoint:

```sh
curl -X PUT "https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"read_replication":{"mode":"auto"}}'
```

A GET to the same endpoint returns the mode on the database object's
`read_replication` property. Disabling can take up to 24 hours before replicas
stop processing requests. Sessions continue to work while replication is
disabled.

D1 currently creates a replica in each supported region, including the
primary's region: `ENAM`, `WNAM`, `WEUR`, `EEUR`, `APAC`, and `OC`. Replica
locations can change.

Replicas add no separate storage or compute charge. Queries continue to be
billed through `rows_read` and `rows_written` as they are without replicas.

## Result metadata boundaries

All remote D1 results include `served_by_region` and `served_by_primary`,
regardless of whether Sessions or replication are used. Both are `undefined`
during local `wrangler dev`.

`D1Result.meta.timings.sql_duration_ms` measures database SQL execution and
does not include network time.

## Primary placement hints

By default, D1 places a new primary near the location from which database
creation was requested. When most writes originate somewhere else, provide a
creation-time hint:

```sh
wrangler d1 create new-database --location=weur
```

Supported hints are `wnam`, `enam`, `weur`, `eeur`, `apac`, and `oc`. D1 uses
the lowest-latency available location, so a hint does not guarantee exact
placement. `sam`, `afr`, and `me` are unsupported, and D1 databases do not run
in those regions.

## Jurisdictions

The 2025 database-jurisdiction capability guarantees where a database runs
and stores data. A jurisdiction is a creation-time constraint: it cannot be
added or changed afterward. Supported values are `eu` and `fedramp`:

```sh
npx wrangler@latest d1 create db-with-jurisdiction --jurisdiction=eu
```

When both `--jurisdiction` and `--location` are present, the jurisdiction takes
precedence and D1 ignores the location hint.

The jurisdiction limits where the database runs and persists data; it does not
limit where Workers can access it. When read replication is enabled, all
replicas stay within the database's jurisdiction.
