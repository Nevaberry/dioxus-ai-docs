# URL Rewrites, Route Masks, and Navigation Blocking

## Map public and internal URLs bidirectionally

The router-level `rewrite` option maps the browser URL to an internal URL with
`input` before route matching. It maps internal URLs back to public URLs with
`output` before links or history entries are written.

Each handler receives `{ url: URL }` and may return the mutated object, a new
`URL`, a full href string, or `undefined`. After rewriting,
`location.href` is the internal URL and `location.publicHref` is the external,
shareable URL.

```tsx
const localeRewrite = {
  input: ({ url }) => {
    url.pathname =
      url.pathname.replace(/^\/(en|fr)(?=\/|$)/, '') || '/'
    return url
  },
  output: ({ url }) => {
    url.pathname = `/en${url.pathname === '/' ? '' : url.pathname}`
    return url
  },
}

const router = createRouter({ routeTree, rewrite: localeRewrite })
```

`<Link>` and programmatic navigation apply output rewrites automatically. If an
output rewrite changes the origin, `<Link>` performs a hard navigation. The
same rewrite configuration participates in server request parsing and SSR
hydration.

## Compose rewrites around a basepath

`composeRewrites` runs input rewrites from first to last and output rewrites
from last to first, allowing transformations to unwrap in reverse order.

A configured `basepath` is automatically composed outside custom rewrites. The
router strips it before custom input and restores it after custom output.

```tsx
const legacyRewrite = {
  input: ({ url }) => {
    if (url.pathname === '/old') url.pathname = '/new'
    return url
  },
}

const router = createRouter({
  routeTree,
  basepath: '/app',
  rewrite: composeRewrites([localeRewrite, legacyRewrite]),
})
```

## Mask one runtime route with another URL

A route mask navigates to one typed runtime location while placing a different
location in the URL bar. Supply `mask` to `<Link>` or `navigate()` for a single
navigation, or register a typed `createRouteMask` result in the router's
`routeMasks` for reuse.

```tsx
const photoMask = createRouteMask({
  routeTree,
  from: '/photos/$photoId/modal',
  to: '/photos/$photoId',
  params: (prev) => ({ photoId: prev.photoId }),
})

const router = createRouter({ routeTree, routeMasks: [photoMask] })

navigate({
  to: '/photos/$photoId/modal',
  params: { photoId: 5 },
  mask: {
    to: '/photos/$photoId',
    params: { photoId: 5 },
  },
})
```

## Control mask lifetime across reloads

The runtime location is stored in browser history state. Copying or sharing the
displayed URL loses that state and loads the displayed route normally.

A local reload retains the mask by default. Set `unmaskOnReload: true` to
discard it. A per-link or per-navigation setting overrides the route-mask
setting, which overrides the router default.

```tsx
const router = createRouter({
  routeTree,
  routeMasks: [photoMask],
  unmaskOnReload: true,
})
```

## Resolve blocked navigation explicitly

`useBlocker` passes typed `current` and `next` locations to `shouldBlockFn`; a
true result blocks navigation. With `withResolver: true`, the blocker enters a
blocked state and waits. Call `proceed` to continue or `reset` to remain.

`enableBeforeUnload` separately controls the native reload or tab-close prompt.

```tsx
const { status, proceed, reset } = useBlocker({
  shouldBlockFn: () => formIsDirty,
  withResolver: true,
  enableBeforeUnload: formIsDirty,
})

if (status === 'blocked') {
  // Wire proceed() to “Leave” and reset() to “Stay”.
}
```

## Await an asynchronous blocker decision

Without resolver mode, `shouldBlockFn` may return a promise for custom UI.
Resolve `true` to cancel navigation and `false` to allow it.

```tsx
useBlocker({
  shouldBlockFn: () =>
    formIsDirty ? askWhetherToLeave().then((leave) => !leave) : false,
})
```
