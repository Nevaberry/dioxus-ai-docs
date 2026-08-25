# Rewrites and Masking

## Configure bidirectional URL rewrites

Router-level `rewrite.input` maps a browser URL to the internal URL before
matching. `rewrite.output` maps an internal URL to the public URL before links
or history entries are written. Each receives `{ url: URL }` and may return the
mutated object, a new `URL`, a complete href string, or `undefined`.

`location.href` remains the internal location; `location.publicHref` is the
external shareable location. `Link` and programmatic navigation apply output
rewrites automatically. If output changes the origin, `Link` performs a hard
navigation. The same configuration applies to server request parsing and SSR
hydration.

```tsx
import { createRouter } from '@tanstack/react-router'

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

## Compose rewrites around the basepath

`composeRewrites` runs input rewrites first-to-last and output rewrites
last-to-first, so nested transformations unwrap in reverse order. A router
`basepath` is composed outside custom rewrites automatically: it is stripped
before custom input and restored after custom output.

```tsx
import { composeRewrites } from '@tanstack/react-router'

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

## Mask one runtime route as another URL

A mask navigates to one typed runtime location while placing a different
location in the URL bar. Pass `mask` to a `Link` or `navigate()` call for one
navigation. For a reusable typed mapping, create it with `createRouteMask` and
register it in router `routeMasks`.

```tsx
import { createRouteMask } from '@tanstack/react-router'

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
  mask: { to: '/photos/$photoId', params: { photoId: 5 } },
})
```

## Account for mask lifetime and reloads

The runtime location is stored in browser history state. Copying or sharing
the displayed URL loses that state and loads the displayed route normally. A
reload in the same browser retains the mask by default.

Set `unmaskOnReload: true` to discard it. A per-link or per-navigation setting
overrides the route-mask setting, and the route-mask setting overrides the
router default.

```tsx
const router = createRouter({
  routeTree,
  routeMasks: [photoMask],
  unmaskOnReload: true,
})
```
