# Type Safety and APIs

## Contents

- [Generated route-module types](#generated-route-module-types)
- [TypeScript project wiring](#typescript-project-wiring)
- [Typed `href()` and path construction](#typed-href-and-path-construction)
- [Loader and action inference](#loader-and-action-inference)
- [Route component and match data](#route-component-and-match-data)
- [Navigation and location APIs](#navigation-and-location-apis)
- [Meta descriptors](#meta-descriptors)
- [Data strategy APIs](#data-strategy-apis)
- [Route config utility types](#route-config-utility-types)

## Generated route-module types

Framework type generation creates sibling-style `./+types/<route>` modules with typed params,
loader/action data, errors, and route export arguments.

```tsx
import type { Route } from "./+types/product";

export async function loader({ params }: Route.LoaderArgs) {
  return { id: params.id };
}

export default function Product({ loaderData }: Route.ComponentProps) {
  return <h1>{loaderData.id}</h1>;
}
```

The generated layout supports TypeScript `Node16` and `NodeNext` module resolution. Child-route
`matches` and `params` are deliberately broader because runtime descendants can contribute
values.

Generated params cover every matched page containing the route. Descendant parameters are
optional keys, and narrowing one key refines correlated parameters in the normalized union. If
one route module is mounted at multiple paths, typegen unions all parameter shapes rather than
choosing one. Non-JavaScript route extensions such as `.mdx` are supported.

Generated `+types/*` modules no longer export `Info`. The provisional
`react-router/route-module` entry moved to `react-router/internal`; both are internal surfaces,
so remove `Info` imports and avoid depending on the internal entry unless unavoidable.

## TypeScript project wiring

React Router owns `.react-router/types`; ignore the overall `.react-router/` directory in source
control, but include its type tree in TypeScript and use `rootDirs` so `./+types/*` resolves as a
sibling of the application route.

```json
{
  "include": ["app/**/*", ".react-router/types/**/*"],
  "compilerOptions": {
    "rootDirs": [".", "./.react-router/types"]
  }
}
```

`react-router dev` and custom servers using `vite.createServer` keep generated types current.
Standalone and CI checks must run type generation explicitly:

```json
{
  "scripts": {
    "typecheck": "react-router typegen && tsc"
  }
}
```

Future/config flags generate their matching registration under `.react-router/types`; do not
duplicate it with manual module augmentation. In v8, middleware-related gating types and the
Data Mode `Future` augmentation are removed because the behavior is unconditional.

## Typed `href()` and path construction

Framework Mode exports `href` from `react-router`. It validates the route pattern and parameter
names against generated route configuration.

```tsx
import { href, Link } from "react-router";

<Link to={href("/products/:id", { id: "asdf" })} />;
```

As of 7.6.2, optional static segments expand to concrete accepted patterns. Optional dynamic
parameters keep their `?` and accept an optional parameter object. A splat value beginning with
`/` does not add an extra slash at the boundary.

```ts
href("/users/:id?");
href("/users/:id?", { id: "42" });
href("/products/:id", { id: "42" });
href("/products/:id/detail", { id: "42" });
href("/products/*", { "*": "/1/edit" }); // "/products/1/edit"
```

`href()` also handles a parameter followed by a suffix and a route consisting only of one
optional parameter. As of 8.2.0 it stringifies and URL-encodes dynamic values like
`generatePath()`. Splats preserve `/` while encoding their individual segments.

```ts
href("/items/:id", { id: "a b" }); // "/items/a%20b"
href("/files/*", { "*": "a b/c d" }); // "/files/a%20b/c%20d"
```

`generatePath()` likewise interpolates suffixed parameters:

```ts
generatePath("/books/:id.json", { id: "42" }); // "/books/42.json"
```

## Loader and action inference

The generic passed to `useFetcher` is the producing function type, not the resulting data type;
use `useFetcher<typeof loader>()`, not `useFetcher<LoaderData>()`:

```ts
const fetcher = useFetcher<typeof loader>();
```

To prevent `useRouteLoaderData<typeof clientLoader>` from applying server serialization to a
client loader result, annotate the client-loader arguments. This preserves client-only values
such as functions.

```tsx
export function clientLoader({}: Route.ClientLoaderArgs) {
  return { greeting: () => "hello" };
}

const data = useRouteLoaderData<typeof clientLoader>("routes/home");
data?.greeting();
```

Redirect responses are excluded during loader-data inference. Loaders/actions may return
`undefined`, and framework serialization preserves supported rich values. Library authors can
use `unstable_SerializesTo` to register types handled by the turbo-stream serializer.

## Route component and match data

Route components receive generated props such as `loaderData`, `actionData`, `params`, and
`matches`. `createRoutesStub` also passes route component props, so tests need not rewrite a
component to use hooks.

```tsx
const RoutesStub = createRoutesStub([{
  path: "/",
  loader: () => ({ message: "hello" }),
  Component({ loaderData }) {
    return <p>{(loaderData as { message: string }).message}</p>;
  },
}]);
```

`loaderData` was introduced alongside the old `data` fields in `Route.MetaArgs`,
`Route.MetaArgs.matches`, other meta-match types, `Route.ComponentProps.matches`, and `UIMatch`.
In v8 the deprecated `data` fields are removed; always use `loaderData`.

At match level, loader data can be `undefined` while an error boundary renders. Generated
`Route.MetaArgs.loaderData` is optional only for a route that exports `ErrorBoundary`. Guard
data from earlier matches because an ancestor loader may have failed. Meta for the route itself
can also run on a root 404 or after its loader throws.

```ts
export function meta({ loaderData }: Route.MetaArgs) {
  return [{ title: loaderData?.title ?? "Not found" }];
}
```

Framework Mode's provisional `unstable_useRoute(routeId)` provides typed `loaderData`,
`actionData`, and `handle` for a generated ID. It returns `undefined` if the route is not matched,
except for `root`. Without an ID it targets the current route but leaves data as `unknown`.

```tsx
const admin = unstable_useRoute("routes/admin");
if (!admin) throw new Error("Admin route is not matched");
console.log(admin.loaderData, admin.actionData, admin.handle);
```

The `root` route ID is reserved; route configuration rejects explicit reuse elsewhere.

## Navigation and location APIs

The `useNavigation()` return type is a discriminated union. Branch on `state` before using fields
specific to `idle`, `loading`, or `submitting`.

The `setSearchParams` updater receives a copy of the current `URLSearchParams`, so mutating it
does not mutate router state before the navigation commits. This keeps a blocked navigation
consistent with `useLocation().search`.

`useFetchers()` has stable snapshot identity until fetchers actually change. `fetcher.reset()`
returns one fetcher to its initial idle state; it replaced `unstable_reset()`.

`unstable_useRouterState()` is available only with Framework, Data, and RSC data routers. It
combines an always-populated active snapshot and a navigation-time pending snapshot, including
location, search params, params, matches, navigation type/state, and submission data.

## Meta descriptors

`MetaDescriptor` supports an array of `LdJsonObject` values in one `script:ld+json` descriptor,
allowing `<Meta />` to emit multiple schemas in one script.

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

## Data strategy APIs

Custom strategies should use `match.shouldCallHandler()` and
`match.shouldRevalidateArgs`; rename `match.unstable_shouldCallHandler()` and
`match.unstable_shouldRevalidateArgs` rather than supporting both. `match.shouldLoad` is
deprecated because it cannot express the same handler decision. A strategy that omits required
route results now produces route errors for those missing results.

## Route config utility types

`@react-router/remix-config-routes-adapter` exports `DefineRouteFunction` for one route callback
as well as `DefineRoutesFunction` for the overall callback. `@react-router/dev` accepts `.mts`
and `.mjs` route-config files.

The generated virtual module `virtual:react-router/server-build` has declarations, including
when TypeScript `moduleDetection` is `force` on patched v7 releases.
