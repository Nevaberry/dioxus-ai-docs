# Type Safety and APIs

## Generated route-module types

Framework Mode generates sibling `./+types/<route>` modules with typed arguments
and props for params, loader data, action data, handles, matches, and errors. The
system introduced in 7.0.0 supports TypeScript `Node16` and `NodeNext` module
resolution.

```tsx
import type { Route } from "./+types/product";

export async function loader({ params }: Route.LoaderArgs) {
  return { id: params.id };
}

export default function Product({ loaderData }: Route.ComponentProps) {
  return <h1>{loaderData.id}</h1>;
}
```

Child-route `matches` and `params` are deliberately broader than a single local
pattern because runtime matches can include descendant values. A fetcher's generic
is the producing function type: use `useFetcher<typeof loader>()`, not a manually
declared loader-data shape.

### Wire typegen into TypeScript

Ignore `.react-router/` as generated output, but include `.react-router/types/**/*`
in the TypeScript project and use `rootDirs` so `./+types/*` resolves as a sibling.

```json
{
  "include": ["app/**/*", ".react-router/types/**/*"],
  "compilerOptions": {
    "rootDirs": [".", "./.react-router/types"]
  }
}
```

Run type generation before standalone compilation:

```json
{
  "scripts": {
    "typecheck": "react-router typegen && tsc"
  }
}
```

`react-router dev` and custom servers using `vite.createServer` keep types current
automatically.

### Registration and generated-export changes

As of 7.6.0, future flags in `react-router.config.ts` enable their corresponding
generated types automatically; remove matching manual `declare module
"react-router"` augmentation. Type generation also:

- Includes descendant parameters as optional keys and narrows correlated parameter
  unions when one key is checked.
- Unions parameter shapes when one route file is mounted at multiple paths.
- Supports non-JavaScript route extensions such as `.mdx` in later 7.6 patches.
- No longer exports `Info` from `+types/*`.

The provisional `react-router/route-module` entry point moved to
`react-router/internal`; code on this unstable surface must update its import.

The virtual `virtual:react-router/server-build` module gained generated types in
7.4.0, including support for `moduleDetection: "force"` in 7.4.1.

## Route component and stub props

Since 7.6.0, components in `createRoutesStub` receive route component props such as
`loaderData`, so tests do not need to rewrite prop-based components to hooks.

```tsx
const RoutesStub = createRoutesStub([{
  path: "/",
  loader: () => ({ message: "hello" }),
  Component({ loaderData }) {
    return <p>{(loaderData as { message: string }).message}</p>;
  },
}]);
```

## Typed path construction

### Framework `href()`

Framework Mode's `href` from `react-router` validates route patterns and parameter
names against generated route configuration (7.2.0).

```tsx
import { href, Link } from "react-router";

<Link to={href("/products/:id", { id: "asdf" })} />;
```

The behavior was refined in 7.6.2 within the 7.6.0 line:

- Optional static segments expand to concrete accepted patterns.
- Optional dynamic parameters retain `?` and accept an optional parameter object.
- A splat value beginning with `/` no longer adds an extra boundary slash.

```ts
href("/users/:id?");
href("/users/:id?", { id: "42" });
href("/products/:id/detail", { id: "42" });
href("/products/*", { "*": "/1/edit" }); // "/products/1/edit"
```

As of 7.9.0, `href()` correctly handles a parameter followed by an extension and a
route made only of one optional parameter. As of 8.2.0, it stringifies and
URL-encodes dynamic values like `generatePath()`; splats preserve `/` separators and
encode each segment separately.

```ts
href("/items/:id", { id: "a b" }); // "/items/a%20b"
href("/files/*", { "*": "a b/c d" }); // "/files/a%20b/c%20d"
```

`generatePath()` also correctly interpolates parameters followed by text in the same
segment as of 7.12.0.

```ts
generatePath("/books/:id.json", { id: "42" });
```

## Loader data in meta and matches

`Route.MetaArgs.data` became possibly `undefined` in 7.6.0 because meta can run
after its route loader throws or for a root 404 whose loader did not run. Guard it.

```ts
export function meta({ data }: Route.MetaArgs) {
  return [{ title: data?.title ?? "Not found" }];
}
```

In 7.8.0, `loaderData` was added beside deprecated `data` on `Route.MetaArgs`, meta
matches, `Route.ComponentProps.matches`, and `UIMatch`. Match values can be
`undefined` during boundary rendering. Generated `Route.MetaArgs.loaderData` is
optional only when the route exports an `ErrorBoundary`, but earlier matched loaders
may also have failed, so guard match-level access.

In 8.0.0, all deprecated match `data` fields were removed. Use `loaderData` on the
meta argument and every match.

The `hasErrorBoundary` field was also removed from route objects, `<Route>`, lazy
definitions, and `MapRoutePropertiesFunction` in 8.0.0; error-boundary presence is
inferred automatically.

## Typed match access

Framework Mode's provisional `unstable_useRoute(routeId)` in 7.9.0 returns typed
`loaderData`, `actionData`, and `handle` for a generated route ID. It returns
`undefined` when the route is unmatched, except for `root`. With no ID it targets the
current route but leaves its data as `unknown`.

```tsx
const admin = unstable_useRoute("routes/admin");
if (!admin) throw new Error("Admin route is not matched");
console.log(admin.loaderData, admin.actionData, admin.handle);
```

## Serialization type hooks

The 7.2.0 provisional `unstable_SerializesTo` brand lets library authors register
types supported by the router's `turbo-stream` serialization. Framework loader
values can include maps, sets, and dates. Server response types preserve
`ReadonlyMap` and `ReadonlySet` as of 7.8.0.

For a client loader returning non-serializable browser values, annotate its argument
as `Route.ClientLoaderArgs`; this prevents
`useRouteLoaderData<typeof clientLoader>` from incorrectly applying the server
serialization transform (7.6.0).

## Navigation and document metadata types

`useNavigation()` is a discriminated union over `idle`, `loading`, and `submitting`
as of 7.16.0, so a state check narrows all state-specific fields.

`MetaDescriptor` also accepts an array of `LdJsonObject` values for
`script:ld+json` as of 7.16.0, allowing one `<Meta />` script to hold several schemas.

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
