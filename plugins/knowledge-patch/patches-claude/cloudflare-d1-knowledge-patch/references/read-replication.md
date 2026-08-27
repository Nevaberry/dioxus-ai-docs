# Read Replication

## Sessions and sequential consistency

Use `env.DB.withSession()` to group a logical application’s queries with
sequential consistency. D1 creates and routes read replicas automatically.

Carry a session bookmark forward when the consistency requirement spans more
than one session:

```ts
const bookmark =
  request.headers.get("x-d1-bookmark") ?? "first-unconstrained";
const session = env.DB.withSession(bookmark);
const result = await session
  .prepare("SELECT * FROM Customers WHERE CompanyName = 'Bs Beverages'")
  .run();
response.headers.set("x-d1-bookmark", session.getBookmark() ?? "");
```

Coverage attribution: `2025`.

## Choosing the first-query constraint

`withSession()` is equivalent to `withSession("first-unconstrained")`. In
either form, the first query may use the primary or a replica.

Use `"first-primary"` when the session must begin from the latest primary
database version:

```ts
const unconstrained = env.DB.withSession();
const latest = env.DB.withSession("first-primary");
```

## Database-level controls

Read replication is enabled per database. The database REST endpoint accepts
`read_replication.mode` with either `"auto"` or `"disabled"`. A `GET` to the
same endpoint exposes the current value in the returned database object’s
`read_replication` property.

```sh
curl -X PUT "https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"read_replication":{"mode":"auto"}}'
```

After replication is disabled, replicas may continue processing requests for
up to 24 hours. Sessions remain usable while replication is disabled.

## Replica placement

D1 currently creates one replica in every supported region, including the
primary’s region:

- `ENAM`
- `WNAM`
- `WEUR`
- `EEUR`
- `APAC`
- `OC`

Replica locations may change. A database with a jurisdiction constraint keeps
its replicas within that jurisdiction.

## API and metadata boundaries

Sessions are available only through the D1 Workers binding, not the REST API.

Remote D1 results expose `served_by_region` and `served_by_primary` whether or
not Sessions or replication are in use. Both fields are `undefined` during
local `wrangler dev`.

`D1Result.meta.timings.sql_duration_ms` measures database SQL execution time and
excludes network time.

## Billing

Read replicas add no separate storage or compute charge. Queries continue to be
billed through `rows_read` and `rows_written`, as they are without replicas.
