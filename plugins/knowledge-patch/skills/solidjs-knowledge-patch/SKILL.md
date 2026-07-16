---
name: solidjs-knowledge-patch
description: SolidJS current compatibility guidance. Use for SolidJS work.
license: MIT
version: null
metadata:
  author: Nevaberry
---

# SolidJS Knowledge Patch

Use these rules when changing SolidJS, Solid Router, or SolidStart code. Identify
which package owns an API before applying a migration: similarly named data,
response, and route helpers do not necessarily share a package or runtime.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration and UI](references/migration-and-ui.md) | Compiler validation, package resolution, customized built-ins, boolean attributes, non-delegated events |
| [Reactivity and async](references/reactivity-and-async.md) | `query`, async-data helpers, server functions, streaming RPC |
| [Routing and SolidStart](references/routing-and-solidstart.md) | Filesystem routes, route definitions, preloading, navigation, SolidStart runtime and request APIs |
| [Stores and actions](references/stores-and-actions.md) | Action lifecycle, submissions, form encoding, revalidation, responses, redirects, single-flight mutations |

Read only the reference files relevant to the task, but read both routing and
actions when a mutation redirects or revalidates route data.

## Upgrade triage

Check these migration-sensitive changes first:

| Symptom or old pattern | Required adjustment |
| --- | --- |
| Router data helper named `cache` | Rename it to `query`; do not carry the removed `store` option forward |
| Route option named `load` | Rename it to `preload` |
| Public router type named `Route` | Use `RouteDescription` |
| Capture listener written with `oncapture:` | Use an `on:` listener object with `capture: true` |
| Nested anchors or another browser-rewritten tree | Fix the source HTML; more invalid structures now fail compilation |
| SSR succeeds at importing a client compiler method | Do not call it on the server; server exports exist for resolution and still throw when invoked |
| Legacy resolver depends on the package `browser` field | Move to export-condition-aware resolution |
| SolidStart server call receives an unexpected non-JSON response | Ensure a release containing the 1.3.2 transport fix is installed |

Do not treat successful module resolution as proof that an API is safe in the
current runtime.

## JSX and DOM quick reference

Use `is` to opt a customized built-in element into custom-element handling:

```tsx
<button is="fancy-button">Open</button>
```

Use `bool:` when an attribute needs boolean-attribute semantics instead of the
property behavior Solid would otherwise select:

```tsx
<my-element bool:enable={enabled()} />
```

For non-delegated events, pass an event-listener object to `on:` when browser
listener options are required:

```tsx
<div
  on:wheel={{
    handleEvent(event) {
      event.preventDefault();
    },
    passive: false,
    capture: true,
  }}
/>
```

The object may carry `once`, `passive`, and `capture`. Prefer this extensible
form over `oncapture:`.

## Router data and action quick reference

Apply the current names and behaviors together:

| API | Current contract |
| --- | --- |
| `query` | Replaces `cache`; response handling preserves headers |
| `createAsyncStorage` | Provides the storage-oriented async-data variant |
| `createAsync` | Exposes `.latest`; user-provided names are honored |
| `action` | Supports `onComplete`, exposes errors, and returns the processed response |
| `Submission` | Import from the package top level |
| `SearchParams` | Import as a public type; values can be optional or arrays |
| `usePreloadRoute` | Obtain the route-preloading helper |
| `preloadRoute` | Pass a string path when that is the available route description |

Remember these lifecycle details:

- Clear only completed actions during navigation.
- Expect an action's supplied name to be hashed rather than replaced with
  the fixed name `mutate`.
- Treat an empty string or empty array as a request for no revalidation.
- Expect form actions to use URL-encoded bodies by default.
- Pass `URLSearchParams` only when the encoding is not
  `multipart/form-data`.

## Filesystem routing quick reference

Compose generated routes with an application-selected router:

```tsx
import { FileRoutes } from "@solidjs/start/router";
import { Router } from "@solidjs/router";

export default function App() {
  return (
    <Router>
      <FileRoutes />
    </Router>
  );
}
```

`FileRoutes` exposes the generated configuration as both a component and a
regular function. Use the function form when the router needs direct access to
the configuration.

Apply these filename rules:

- Use parenthesized parts for route groups and tree shaping that should not
  participate in URL matching.
- Use `[[name]]` for an optional parameter.
- Use `[...name]` for a catch-all parameter whose value is one slash-delimited
  string.

Configure a route module with a named `route` export:

```tsx
import type { RouteDefinition } from "@solidjs/router";

export const route = {
  matchFilters: { id: /^\d+$/ },
} satisfies RouteDefinition;

export default function Story() {
  return <main>Story</main>;
}
```

Do not repeat `component` in `route`; SolidStart lazy-wraps the default export
and injects it as the route component.

## Server execution and transport

Mark a function with the directive when its implementation must execute only
on the server:

```ts
async function greeting(name: string) {
  "use server";
  return `Hello ${name}`;
}
```

Keep its ordinary TypeScript call shape. A server-side invocation remains a
direct call, while a browser invocation becomes an RPC. The transport can
carry promises, streams, and async iterables, so it can sit behind an existing
client data library in either SSR or client-rendered code.

For mutations followed by navigation, allow the router to start destination
loading and stream that data in the mutation response. This avoids serializing
the mutation, redirect, and next-page fetch into a waterfall.

Treat server-function transport upgrades as compatibility-sensitive:

- SolidStart 1.1 switched to the TanStack server-functions plugin.
- SolidStart 1.3 switched serialization to Seroval JSON mode.
- SolidStart 1.3.2 fixes the 1.3.0 loop on unexpected responses such as S3 XML
  errors.

## Request and response quick reference

Export `OPTIONS` from a filesystem API route when the endpoint must answer a
CORS preflight directly:

```ts
export function OPTIONS() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    },
  });
}
```

Type request-local state by augmenting `App.RequestEventLocals`, and import
`getServerFunctionMeta` from `@solidjs/start` rather than its deprecated
`@solidjs/start/server` location.

Expect response helpers to return `Response` objects. Preserve headers through
`query().handleResponse()`, forward absolute redirects created by server-side
data calls, and retain every `Set-Cookie` header on redirect responses.

## SolidStart runtime checks

Before changing configuration or deployment code:

- Distinguish the Vite-based SolidStart 2 alpha runtime from the 1.x Vinxi
  runtime.
- Use `vite preview` with the alpha line.
- Import server-side types from `@solidjs/start/server` where needed.
- Expect API routes to honor the configured base URL.
- Configure the public-assets directory when the project does not use
  `public`.
- Keep v1 fixes on the `1.x` line while evaluating alpha migration work.
