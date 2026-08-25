---
name: solidjs-knowledge-patch
description: SolidJS
version: null
license: MIT
metadata:
  author: Nevaberry
---


# SolidJS Knowledge Patch

Use these rules when working with SolidJS, Solid Router, or SolidStart. First
identify which package and runtime own an API: similarly named route, data,
response, and server helpers are not interchangeable.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration and UI](references/migration-and-ui.md) | Compiler validation, package resolution, JSX custom elements, boolean attributes, event listeners |
| [Reactivity and async](references/reactivity-and-async.md) | Router queries, async-data helpers, server functions, RPC transport |
| [Routing and SolidStart](references/routing-and-solidstart.md) | Filesystem routes, route definitions, navigation, SolidStart runtime and request APIs |
| [Stores and actions](references/stores-and-actions.md) | Action lifecycle, submissions, forms, revalidation, responses, redirects |

Read both routing and actions guidance when a mutation redirects or
revalidates route data.

## Migration triage

Check these compatibility-sensitive patterns first:

| Existing pattern or symptom | Adjustment |
| --- | --- |
| Router data helper named `cache` | Rename it to `query`; remove the old `store` option |
| Route option named `load` | Rename it to `preload` |
| Public router type named `Route` | Use `RouteDescription` |
| Capture listener written with `oncapture:` | Use an `on:` listener object with `capture: true` |
| Nested anchors or another browser-rewritten tree | Correct the invalid HTML; more structures fail compilation |
| Client compiler method imported during SSR | Resolution can succeed, but invoking the client-only method still throws |
| Resolver relies on the package `browser` field | Use export-condition-aware package resolution |
| SolidStart server call loops on a non-JSON response | Use a release containing the 1.3.2 transport fix |

Successful module resolution does not prove that an API is callable in the
current runtime.

## JSX and DOM quick reference

### Customized built-in elements

An `is` attribute opts a customized built-in element into Solid's custom
element behavior:

```tsx
<button is="fancy-button">Open</button>
```

### Boolean attributes

Use `bool:` when the attribute needs boolean-attribute semantics rather than
the property behavior Solid would otherwise choose:

```tsx
<my-element bool:enable={enabled()} />
```

### Non-delegated event options

Pass an event-listener object to `on:` when a non-delegated listener needs
browser options:

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

The object may include `once`, `passive`, and `capture`. Prefer it over the
deprecated `oncapture:` syntax.

## Router data quick reference

Apply the current API names and contracts together:

| API | Current contract |
| --- | --- |
| `query` | Replaces `cache`; `handleResponse()` preserves headers |
| `createAsyncStorage` | Provides the storage-oriented async-data helper |
| `createAsync` | Exposes `.latest` and honors a supplied name |
| `action` | Supports `onComplete`, exposes errors, and returns a processed response |
| `Submission` | Import from the router package's top level |
| `SearchParams` | Import as a public type; values may be optional or arrays |
| `usePreloadRoute` | Obtains the route-preloading helper |
| `preloadRoute` | Accepts a string path |

Remember these action and form details:

- Clear only completed actions during navigation.
- A supplied action name is hashed instead of being replaced by `"mutate"`.
- Empty string and empty array revalidation values mean no revalidation.
- Form actions use URL-encoded bodies by default.
- Accept `URLSearchParams` only when encoding is not `multipart/form-data`.

## Filesystem routing quick reference

### Select the router around generated routes

`FileRoutes` exposes the generated configuration as both a component and a
regular function, allowing the application to choose and configure its
router:

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

Use the function form when the router needs the generated configuration
directly.

### Configure a route module

Export a named `route` object for router configuration:

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
and supplies it as the component.

Use these filesystem naming rules:

- Parenthesized parts shape the route tree without participating in URL
  matching.
- `[[name]]` declares an optional parameter.
- `[...name]` declares a catch-all whose value is one slash-delimited string.

## Server execution and transport

Place the directive inside a function whose implementation must execute only
on the server:

```ts
async function greeting(name: string) {
  "use server";
  return `Hello ${name}`;
}
```

Keep the normal TypeScript call shape. A server invocation remains direct,
while a browser invocation becomes an RPC. The transport can carry promises,
streams, and async iterables, so server functions can back existing client
data libraries in SSR and client-rendered applications.

For a mutation followed by navigation, let the router start destination
loading and stream that data in the mutation response. This combines the
update, redirect, and next-page load instead of creating a serial waterfall.

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

Type request-local state by augmenting `App.RequestEventLocals`. Import
`getServerFunctionMeta` from `@solidjs/start`; the older
`@solidjs/start/server` export is deprecated.

Treat response helpers as `Response` producers. Preserve headers through
`query().handleResponse()`, forward absolute redirects produced inside
server-side `cache` calls, and retain every `Set-Cookie` value on redirect
responses.

## SolidStart runtime checks

Before changing configuration or deployment code:

- Distinguish the stable Vite Environment API foundation from older 1.x
  Vinxi applications and earlier 2.x alpha assumptions.
- Expect the stable line to use Vite 8, Rolldown, and direct deployment-plugin
  integration while continuing to target Solid 1.
- Use `vite preview`; when Nitro's preview plugin is active, preview delegates
  to Nitro even for a static build without a server entry.
- Import server-side types from `@solidjs/start/server` where needed.
- Expect API routes to honor the configured base URL.
- Configure the public-assets directory when the project does not use
  `public`.
- Keep fixes for applications remaining on v1 on the `1.x` line.
