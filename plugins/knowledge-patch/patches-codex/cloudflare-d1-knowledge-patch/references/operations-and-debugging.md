# Operations and debugging

## HTTP API authorization

Database writes through the HTTP API require a token that explicitly grants
`D1:Edit`. `D1:Read` combined with `Edit` on another Cloudflare product does
not authorize D1 writes.

## Account storage

The maximum D1 storage per account on the Workers paid plan is 1 TB, increased
from 250 GB in the 2025 update.

## Error diagnostics

D1 database and prepared-statement methods throw ordinary `Error` objects.
Current Wrangler releases put the detailed diagnostic in `message`. Releases
before 3.1.1 instead put it in `cause.message`:

```ts
try {
  await env.DB.exec(sql);
} catch (error) {
  const e = error as Error & { cause?: { message?: string } };
  console.error(e.cause?.message ?? e.message);
}
```

## Retry candidates

Retry operations affected by:

- database code or storage resets;
- lost connections;
- transient remote-node resolution failures;
- disconnected request streams.

For a disconnected stream, also keep the connection open until execution
finishes.

D1 automatically retries qualifying read-only queries up to two times. That
does not replace application-level retry policy for other idempotent work.
Inspect `meta.total_attempts` to see the number of execution attempts.

## Conditions requiring remediation

Do not blindly retry maximum account or database size errors. Delete data,
upgrade the plan, or shard.

Storage timeouts, queue overload, isolate-memory resets, and CPU-limit resets
call for query optimization, spreading load, smaller operations, or sharding.
