# Code Splitting and Navigation

## Encapsulate a file route in a directory

Move a file route from `posts.tsx` to `posts/route.tsx` without extra
configuration. This keeps the route and its related split files together.

## Use automatic splitting only through a bundler plugin

`autoCodeSplitting` is a bundler-plugin feature; `@tanstack/router-cli` alone
does not implement it. Automatic splitting lazily extracts only `component`,
`errorComponent`, `pendingComponent`, and `notFoundComponent`.

Loaders, `beforeLoad`, search validation, context, static data, links, scripts,
styles, and all other matching configuration remain in the critical chunk.
Place the router plugin before the framework plugin.

```ts
plugins: [
  tanstackRouter({ autoCodeSplitting: true }),
  react(),
]
```

## Define manual lazy file boundaries

Without automatic splitting, retain critical options in the normal route file
and move the four supported render options into a matching `.lazy.tsx` file
created with `createLazyFileRoute`.

```tsx
// routes/posts.tsx
export const Route = createFileRoute('/posts')({ loader: fetchPosts })

// routes/posts.lazy.tsx
export const Route = createLazyFileRoute('/posts')({ component: Posts })
```

The `__root` route cannot be split. When a route has no critical configuration,
remove its empty normal file; the generated route tree supplies a virtual
anchor for the lazy file.

## Split code-based routes and loaders

Attach a `createLazyRoute` result to a code-defined route with `Route.lazy()`.
A loader can instead be imported by name with `lazyFn`, although its context
usually needs an explicit `LoaderContext` type. File-based loaders can only be
split by automatic splitting with customized bundling options.

```tsx
// posts.lazy.tsx
export const Route = createLazyRoute('/posts')({ component: Posts })

const postsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/posts',
}).lazy(() => import('./posts.lazy').then((mod) => mod.Route))

const dataRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/report',
  loader: lazyFn(() => import('./loader'), 'loader'),
})
```

## Reuse lazy components after resolution

Since 1.170.28, a code-split lazy route component remains resolved across
later visits. Revisiting the route does not show pending UI solely to resolve
that same component again.

## Resolve blocked navigation explicitly

`useBlocker.shouldBlockFn` receives typed `current` and `next` locations. A
true result blocks navigation. With `withResolver: true`, the blocker enters
the blocked state and waits for the returned `proceed` or `reset` callback.
`enableBeforeUnload` independently controls the native reload or tab-close
prompt.

```tsx
const { status, proceed, reset } = useBlocker({
  shouldBlockFn: () => formIsDirty,
  withResolver: true,
  enableBeforeUnload: formIsDirty,
})

if (status === 'blocked') {
  // Connect proceed() to Leave and reset() to Stay.
}
```

## Make asynchronous blocker decisions

Without resolver mode, `shouldBlockFn` may return a promise for custom UI.
Resolve it to `true` to cancel navigation or `false` to permit navigation.

```tsx
useBlocker({
  shouldBlockFn: () =>
    formIsDirty ? askWhetherToLeave().then((leave) => !leave) : false,
})
```
