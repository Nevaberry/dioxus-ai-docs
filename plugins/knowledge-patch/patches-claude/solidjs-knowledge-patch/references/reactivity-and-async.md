# Reactivity and Async Data

## Query and async-data migration

Solid Router renamed the `cache` helper to `query`. During the same API
evolution, the `store` option was removed, `createAsyncStorage` was added, and
the async-data APIs gained a `prev` argument. Remove `store` rather than
transferring it mechanically to `query`.

`createAsync` now exposes `.latest`, allowing code to inspect its latest value
without replacing the primary accessor contract. User-supplied names are
honored by `createAsync`; do not assume the runtime discards them.

## Query response handling

Response helpers return `Response` objects, and router data helpers process or
filter those results according to their contracts. `query().handleResponse()`
preserves headers, so retain that path when status and header metadata are part
of the data protocol.

An absolute redirect produced in a server-side data call is forwarded to the
client. Older code may describe that call with the former `cache` name; apply
the behavior while migrating the helper to `query`.

## Server-only functions as RPC

The `"use server"` directive marks a function whose implementation executes
only on the server (solidstart-1.0.0):

```ts
async function greeting(name: string) {
  "use server";
  return `Hello ${name}`;
}
```

The function retains a normal TypeScript call signature. A call made on the
server invokes it directly; a call made in the browser is transformed into an
RPC. The same abstraction can therefore back a client data library during SSR
or client rendering.

The transport supports promises, streams, and async iterables. Do not collapse
these values into an unnecessary request-poll-response wrapper when the caller
can consume the richer transport directly.

## Transport compatibility

The server-function implementation changed in compatibility-sensitive ways:

- SolidStart 1.1 adopted the TanStack server-functions plugin in a breaking
  transition.
- SolidStart 1.3 changed serialization to Seroval JSON mode.
- SolidStart 1.3.0 could loop forever when an upstream returned an unexpected
  response such as an S3 XML error.
- SolidStart 1.3.2 fixes that loop; update to a fixed release before diagnosing
  repeated unexpected-response retries as application logic.

Test request and response serialization across the browser/server boundary
when upgrading either transition. A function that still type-checks may have a
different wire contract.
