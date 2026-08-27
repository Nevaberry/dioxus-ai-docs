# Operations and Debugging

## HTTP API permissions

An API token used for database writes through the D1 HTTP API must explicitly
have `D1:Edit`. A token with `D1:Read` plus `Edit` on another Cloudflare product
cannot write to D1.

Coverage attribution: `2025`.

## Automatic read-only retries

D1 automatically attempts a retryable read-only query up to two additional
times. The result metadata reports the number of execution attempts as
`total_attempts`.

Automatic read-only classification currently covers statements containing only:

- `SELECT`
- `EXPLAIN`
- `WITH`

Applications should continue to retry other business-level idempotent queries
themselves. If an attempted automatic retry makes a modification, D1 rolls it
back to guard against side effects.

## Execution metadata

`D1Result.meta` includes:

- `served_by_region`, identifying the serving region;
- `served_by_primary`, indicating whether the primary served the request;
- `timings.sql_duration_ms`, measuring SQL execution inside the database and
  excluding network time.

Serving-region fields appear on all remote D1 results whether or not Sessions or
read replication are used. During local `wrangler dev`, they are `undefined`.

The result’s `results` field is an empty array when a query returns no rows and
`null` when results do not apply.

## Reading error details

D1 database and prepared-statement methods throw ordinary `Error` objects. In
current Wrangler versions, detailed diagnostics are in `message`. Versions
before 3.1.1 instead put the detail in `cause.message`.

```ts
try {
  await env.DB.exec(sql);
} catch (error) {
  const e = error as Error & { cause?: { message?: string } };
  console.error(e.cause?.message ?? e.message);
}
```

## Choose remediation by error class

Retry candidates include:

- database code or storage resets;
- lost connections;
- transient remote-node resolution failures;
- disconnected request streams.

For a disconnected stream, also keep the connection open through query
execution.

Do not blindly retry resource and capacity failures:

- Maximum account or database size requires deletion, a plan upgrade, or
  sharding.
- Storage timeouts, queue overload, isolate-memory resets, and CPU-limit resets
  require query optimization, load spreading, smaller operations, or sharding.
