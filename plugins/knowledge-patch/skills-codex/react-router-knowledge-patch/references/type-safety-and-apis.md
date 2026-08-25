# Type Safety and APIs

## Generated route-module types

### Route export types (`7.0.0`)

Framework type generation creates sibling imports such as `./+types/product`. The
generated `Route` namespace supplies params, loader/action data, component props, and
errors for each route export. `Node16` and `NodeNext` module resolution are supported.
Child-route `matches` and `params` remain intentionally broad because they reflect runtime
values.

```tsx
import type { Route } from "./+types/product";

export async function loader({ params }: Route.LoaderArgs) {
  return { id: params.id };
}
export default function Product({ loaderData }: Route.ComponentProps) {
  return <h1>{loaderData.id}</h1>;
}
```

A fetcher's generic is the producing function, not the resolved value type:

```ts
const fetcher = useFetcher<typeof loader>();
```

### TypeScript project wiring (`type-safety-and-config`)

Ignore `.react-router/` in source control, but include `.react-router/types/**/*` in the
TypeScript project and add the generated tree to `rootDirs` so sibling `./+types/*`
imports resolve. Run `react-router typegen` before standalone or CI `tsc`; dev and custom
servers based on `vite.createServer` keep types current automatically.

```json
{
  "include": ["app/**/*", ".react-router/types/**/*"],
  "compilerOptions": {
    "rootDirs": [".", "./.react-router/types"]
  }
}
```

```json
{
  "scripts": { "typecheck": "react-router typegen && tsc" }
}
```

### Config-driven generated types (`7.6.0`)

Future flags in `react-router.config.ts` automatically register their related types under
`.react-router/types`; remove matching manual `declare module "react-router"`
augmentations.

Generated params cover every page containing a route. Descendant params are optional,
and narrowing a key refines correlated params in the normalized union. Mounting one route
file at several paths produces a union of all parameter shapes. Later 7.6 patches support
non-JavaScript route extensions such as `.mdx`.

Generated `+types/*` no longer exports `Info`. The provisional
`react-router/route-module` entry moved to `react-router/internal`. Type declarations for
`virtual:react-router/server-build` arrived in `7.4.0` and work with
`moduleDetection: "force"` from 7.4.1.

## Typed URL construction

### Framework `href()` (`7.2.0`)

Framework Mode exports `href` from `react-router`. It validates the route pattern and
parameter names against generated config.

```tsx
import { href, Link } from "react-router";

<Link to={href("/products/:id", { id: "asdf" })} />;
```

### Optional segments and splats (`7.6.0`)

As of 7.6.2, optional static segments expand into concrete patterns; optional dynamic
parameters retain `?` and accept an optional params object. A leading `/` in a supplied
splat no longer produces a double boundary slash.

```ts
href("/users/:id?");
href("/users/:id?", { id: "42" });
href("/products/:id/detail", { id: "42" });
href("/products/*", { "*": "/1/edit" }); // "/products/1/edit"
```

`href()` also supports suffixed parameters and a route made only of one optional parameter
from `7.9.0`.

### Path generation and encoding

`generatePath` correctly interpolates a suffixed parameter such as
`/books/:id.json` from `7.12.0`.

From `8.2.0`, `href()` stringifies and URL-encodes dynamic params consistently with
`generatePath()`. Splat values keep `/` separators while encoding each segment.

```ts
href("/items/:id", { id: "a b" }); // "/items/a%20b"
href("/files/*", { "*": "a b/c d" }); // "/files/a%20b/c%20d"
```

## Loader and component data typing

### Client-loader inference (`7.6.0`)

Annotate a client loader's arguments when using it as the generic to
`useRouteLoaderData`. This prevents server serialization from being applied to a
client-only return type and preserves values such as functions.

```tsx
export function clientLoader({}: Route.ClientLoaderArgs) {
  return { greeting: () => "hello" };
}

const data = useRouteLoaderData<typeof clientLoader>("routes/home");
data?.greeting();
```

`createRoutesStub` route components receive component props such as `loaderData` from
`7.6.0`, so test components need not be rewritten to hooks.

### `loaderData` replaces `data`

In `7.6.0`, `Route.MetaArgs.data` can be `undefined` because meta may run after the same
route's loader throws or for a root 404 whose loader never ran. Guard it.

`7.8.0` adds `loaderData` next to `data` in `Route.MetaArgs`, meta matches,
`Route.ComponentProps.matches`, and `UIMatch`, while deprecating `data`. Match data can be
undefined in an error boundary. Generated `Route.MetaArgs.loaderData` is optional only
when the route exports `ErrorBoundary`.

V8 removes the old `data` fields entirely (`8.0.0`). Read `loaderData` from `MetaArgs` and
every `MetaArgs.matches` item.

```ts
export function meta({ loaderData }: Route.MetaArgs) {
  return [{ title: loaderData?.title ?? "Not found" }];
}
```

### Rich and read-only values

Framework loaders can serialize `Map`, `Set`, and `Date` without manual JSON flattening
(`framework-mode`). The unstable `unstable_SerializesTo` brand lets libraries register
additional `turbo-stream` types (`7.2.0`). Server response inference retains
`ReadonlyMap` and `ReadonlySet` as read-only (`7.8.0`).

## Typed route and router state

### Route match lookup (`7.9.0`)

Framework `unstable_useRoute(routeId)` returns typed `loaderData`, `actionData`, and
`handle` for a generated route ID. It returns `undefined` when unmatched except for
`root`. Omitting the ID targets the current route but leaves data `unknown`.

```tsx
const admin = unstable_useRoute("routes/admin");
if (!admin) throw new Error("Admin route is not matched");
console.log(admin.loaderData, admin.actionData, admin.handle);
```

### Navigation and consolidated state

`unstable_useRouterState()` collects active and pending data-router snapshots in
`7.15.0`; it is limited to Framework, Data, and RSC modes. From `7.16.0`,
`useNavigation()` preserves a discriminated union for `idle`, `loading`, and
`submitting`, so a state check narrows its other fields correctly.

### Stable fetcher snapshots (`7.15.0`)

`useFetchers()` returns the same array identity until the fetchers actually change. A
memo or effect can safely depend on the returned array without rerunning for allocation
alone.

## Meta descriptors

`MetaDescriptor` accepts multiple `LdJsonObject` values in one `script:ld+json` descriptor
from `7.16.0`.

```tsx
export function meta() {
  return [{
    "script:ld+json": [
      { "@context": "https://schema.org", "@type": "WebSite" },
      { "@context": "https://schema.org", "@type": "Organization" },
    ],
  }];
}
```

## Smaller API behavior changes

- `7.0.0`: `dataStrategy` and `patchRoutesOnNavigation` are the stable names for their
  old `unstable_` forms.
- `7.7.0`: `setSearchParams` updater callbacks receive a copy, so mutation cannot alter
  internal router state before navigation succeeds.
- `7.10.0`: custom data strategies use `shouldCallHandler()` and
  `shouldRevalidateArgs`; `shouldLoad` is deprecated.
- `7.10.0`: POP-navigation promises returned by `navigate()` span the full traversal.
- `7.15.0`: instrumentation type names and the arguments `url`, `pattern`,
  `defaultShouldRevalidate`, `mask`, and `normalizePath` lose `unstable_` prefixes.
