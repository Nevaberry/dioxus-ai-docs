# Reactivity and Async Data

## Query and async-data APIs

### Migrate `cache` to `query`

In Solid Router releases, `cache` was renamed to `query`, and the old `store`
option was removed. Rename the helper and do not carry that option into new
code.

The async-data surface also gained `createAsyncStorage`, a `prev` argument,
and `createAsync().latest`. When supplying names, expect
`createAsync` to honor them rather than substituting a fixed value.

### Preserve query response headers

Use `query().handleResponse()` when processing a query response; it preserves
the response headers. Keep this behavior in mind when migrating code that used
the earlier `cache` name.

## Server functions

### Keep a normal call shape around server-only execution

From the `solidstart-1.0.0` batch, a function containing `"use server"`
executes only on the server:

```ts
async function greeting(name: string) {
  "use server";
  return `Hello ${name}`;
}
```

A call made on the server remains a direct function call. The same call from
the browser becomes an RPC without changing the TypeScript-facing API. This
lets server functions sit behind existing client data libraries in either SSR
or client-rendered applications.

### Use the rich transport deliberately

The server-function transport supports promises, streams, and async iterables,
not only simple JSON-shaped return values. Preserve the ordinary function
abstraction while accounting for execution location and transport behavior.

## Transport evolution

### Check compatibility across SolidStart 1.x

SolidStart 1.1 adopted the TanStack server-functions plugin in a
maintainer-described breaking transition. SolidStart 1.3 then changed
serialization to Seroval JSON mode.

SolidStart 1.3.0 could loop indefinitely when it received an unexpected
response, such as an S3 XML error. The regression is fixed in 1.3.2; upgrade
to a release with that fix rather than treating every server-function response
as guaranteed JSON.

## Mutation-to-navigation flow

### Stream destination data with the mutation

The `solidstart-1.0.0` server-function transport allows Solid Router to begin
loading a destination page after a mutation and stream that data back in the
mutation response while the browser redirects.

Use this single-flight flow when a mutation leads to navigation. It combines
the update, redirect, and destination data load instead of waiting for a new
post-navigation request.
