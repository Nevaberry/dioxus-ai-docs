# Reactivity and Async Data

## Router query migration

Use `query` in place of the former `cache` helper. Treat this as an API rename,
not as a second cache primitive that should coexist with old calls.

Update the related async-data contracts at the same time:

- Use the added `createAsyncStorage` API where storage-backed async state is
  required.
- Account for the added `prev` argument in async-data callbacks.
- Remove the former `store` option from `cache`-era configurations.
- Read `createAsync.latest` when the latest resolved value is needed.

The response side of `query` is covered with actions because filtering,
redirects, and revalidation interact with mutation behavior. See
[Stores and actions](stores-and-actions.md).

## Server functions as typed RPC

The `solidstart-1.0.0` server-function contract preserves the TypeScript-facing
call shape while changing execution by environment:

```ts
async function greeting(name: string) {
  "use server";
  return `Hello ${name}`;
}
```

- Execute a server-side call directly.
- Turn a browser call into an RPC transparently.
- Keep the implementation server-only even though client code can call the
  typed function.
- Transport promises, streams, and async iterables across the boundary.

Because the call retains an ordinary async function interface, it can back an
existing client data library in both SSR and client-rendered applications.
Do not replace the function's TypeScript signature with a transport-specific
wrapper unless the consuming library itself requires one.

## Async mutation flow

A server-function mutation can cooperate with the router's single-flight
navigation. Destination data may begin loading after the mutation and stream
back in the mutation response while the client redirects.

Use that flow to combine update, redirect, and next-page data loading. See
[Stores and actions](stores-and-actions.md) for the complete mutation,
response, and revalidation contracts.

