# Code Splitting, Route Generation, and Build Tooling

## Encapsulate a route in its own directory

Move a file route from `posts.tsx` to `posts/route.tsx` without additional
configuration. Related route and split files can then be colocated in the same
directory.

## Enable automatic file-route splitting

`autoCodeSplitting` is a bundler-plugin feature; `@tanstack/router-cli` alone
cannot perform it. The plugin lazily extracts only `component`,
`errorComponent`, `pendingComponent`, and `notFoundComponent`.

Loaders, `beforeLoad`, search validation, context, static data, links, scripts,
styles, and other matching configuration stay in the critical chunk.

```ts
plugins: [
  tanstackRouter({ autoCodeSplitting: true }),
  react(), // Keep the framework plugin after the router plugin.
]
```

## Create manual lazy file boundaries

Without automatic splitting, keep critical options in a normal route file.
Place the four supported render options in the matching `.lazy.tsx` file with
`createLazyFileRoute`.

The `__root` route cannot be split. If a route has no critical configuration,
delete the empty normal file; the generated route tree provides a virtual
anchor.

```tsx
// routes/posts.tsx
export const Route = createFileRoute('/posts')({ loader: fetchPosts })

// routes/posts.lazy.tsx
export const Route = createLazyFileRoute('/posts')({ component: Posts })
```

## Split code-defined routes and loaders

Attach a `createLazyRoute` result to a code-defined route with `Route.lazy()`.

```tsx
// posts.lazy.tsx
export const Route = createLazyRoute('/posts')({ component: Posts })

const postsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/posts',
}).lazy(() => import('./posts.lazy').then((mod) => mod.Route))
```

Import a loader by name with `lazyFn`. Its context generally requires an
explicit `LoaderContext` type. File-based loaders can only be split through
automatic splitting with customized bundling options.

```tsx
const dataRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/report',
  loader: lazyFn(() => import('./loader'), 'loader'),
})
```

## Reuse resolved lazy components

Since 1.170.28, the router retains a resolved code-split lazy route component
for later visits. Revisiting the route does not show pending UI merely to
resolve the same component again.

## Preserve punctuation in virtual routes

The route generator preserves dots in explicit virtual route paths and
pathless layout IDs instead of treating them as flat-file separators. Leading
and trailing underscores in virtual `route()` paths are literal URL
characters.

Physical file routes still use bracket escapes for literal underscore
segments. That includes index routes beneath pathless layouts, `physical()`
prefixes, and `__virtual.ts` subtrees.

## Resolve TypeScript aliases in virtual config

Virtual route configuration files can import through aliases from `tsconfig`.
The generator resolves those aliases while loading the configuration.

## Parse non-JSX TypeScript transforms correctly

When a filename is available, route and Start import-protection transforms
parse plain TypeScript files without JSX. Angle-bracket type assertions are no
longer interpreted as JSX.

## Use custom tokens containing regex characters

File-based generation accepts custom `routeToken` and `indexToken` values that
start with regex metacharacters such as `+`.

## Isolate multiple plugin instances

Each router plugin instance carries explicit context instead of global route
metadata. Multiple instances therefore do not cross-transform one another's
route files.

## Use current build-tool peers

`@tanstack/router-plugin` supports Rsbuild, accepts Vite 8 as a peer, and
supports `vite-plugin-solid` beginning with `3.0.0-0`.

## Preserve route state during HMR

React route HMR preserves state for auto-split components and lowercase-named
functions. Development transforms cover split component groups and the
unsplit root shell, pending, and error options.

Aliased route imports retain generated properties, and
`createRootRouteWithContext` calls with type arguments are recognized by Vite
Fast Refresh. Webpack and Rspack no longer import the optional
`react-refresh/runtime` package for route HMR.

## Use package intent tooling

`@tanstack/intent` provides AI-agent skills and CLI entry points for
Router and Start packages.
