# Routing and Rendering

Batch attributions used here: `15.3.0`, `15.4.0`, `16.0.0`, `16.2.0`, `16.3.0`, and `release-catalogs`.

## Navigation-aware links

### `onNavigate`

`Link` accepts `onNavigate` for client-side SPA navigations (`15.3.0`). It is narrower than an ordinary click handler: modified clicks, downloads, and other non-SPA interactions do not invoke it as a navigation. Call `preventDefault()` to cancel the route change, such as for an unsaved-work guard.

```tsx
import Link from 'next/link'

<Link
  href="/dashboard"
  onNavigate={(event) => {
    if (!window.confirm('Leave this page?')) event.preventDefault()
  }}
>
  Dashboard
</Link>
```

### `useLinkStatus`

The Client Component hook `useLinkStatus` returns `{ pending }` for an in-progress navigation (`15.3.0`). The component calling it must be rendered as a descendant of the corresponding `Link`; it does not provide a global router-pending signal.

```tsx
'use client'

import Link, { useLinkStatus } from 'next/link'

function Pending() {
  const { pending } = useLinkStatus()
  return pending ? <span>Loading...</span> : null
}

export function Navigation() {
  return (
    <Link href="/dashboard">
      Dashboard <Pending />
    </Link>
  )
}
```

### Navigation transition types

In the App Router, `transitionTypes` on `Link` forwards each supplied string to `React.addTransitionType` during navigation (`16.2.0`). The Pages Router silently ignores this prop, so a shared link wrapper can use it safely.

```tsx
<Link href="/about" transitionTypes={['slide']}>
  About
</Link>
```

## Global and unmatched routes

With `experimental.globalNotFound` enabled, `app/global-not-found.tsx` may export metadata (`15.4.0`). Because this file is the complete global response, render its `html` and `body` elements.

```tsx
export const metadata = { title: 'Page not found' }

export default function GlobalNotFound() {
  return (
    <html>
      <body><h1>Page not found</h1></body>
    </html>
  )
}
```

`unstable_rootParams` was server-only and unsupported in Client Components in `15.4.0`; it was removed in Next.js 16. Do not introduce new uses.

## Parallel-route fallbacks

Every parallel-route slot must define `default.js` in Next.js 16 (`16.0.0`). Missing fallbacks fail the build. To reproduce the old implicit fallback, either return `null` or call `notFound()` explicitly.

```tsx
import { notFound } from 'next/navigation'

export default function Default() {
  notFound()
}
```

## Framework-aware error boundaries

### Component-level boundaries

A Client Component can call `unstable_catchError()` from `next/error` to place a framework-aware boundary anywhere in its tree (`16.2.0`). The fallback receives the wrapped component's call-site props as its first argument and `ErrorInfo` as its second. Control-flow errors such as `redirect()` and `notFound()` pass through instead of being mistaken for failures, and the captured state clears when navigation moves to another route.

```tsx
'use client'

import { unstable_catchError, type ErrorInfo } from 'next/error'

function Fallback(
  { title }: { title: string },
  { error, unstable_retry }: ErrorInfo,
) {
  return (
    <button onClick={() => unstable_retry()}>
      {title}: {error.message}
    </button>
  )
}

export default unstable_catchError(Fallback)
```

### Server-aware retries

An `error.tsx` boundary receives `unstable_retry()` in `ErrorInfo` (`16.2.0`). It refreshes the router and resets the boundary inside a transition, so it can recover from errors thrown during data fetching or Server Component rendering. Prefer it to `reset()` for most retry buttons because `reset()` cannot re-run those server phases.

```tsx
'use client'

import type { ErrorInfo } from 'next/error'

export default function Error({ error, unstable_retry }: ErrorInfo) {
  return (
    <button onClick={() => unstable_retry()}>
      Retry: {error.message}
    </button>
  )
}
```

## Scroll and focus behavior

Automatic smooth-scroll handling is removed in Next.js 16 (`16.0.0`). Opt in explicitly on the document element:

```tsx
<html data-scroll-behavior="smooth">
```

The experimental App Router scroll/focus handler in `16.2.0` uses React Fragment refs and browser-like focus behavior. After navigation it blurs the active element instead of focusing the first focusable descendant deep in the new segment.

```ts
export default {
  experimental: { appNewScrollHandler: true },
}
```

In the `release-catalogs` canary line, this reworked fragment-scroll and focus handler is enabled by default, so remove assumptions that it is always gated by `experimental.appNewScrollHandler` when testing canary builds.

## Instant route enforcement

With Cache Components enabled, Next.js `16.3.0` reports server work that delays navigation in the development overlay and terminal; `next build` emits the same guidance when the work prevents prerendering. Choose one of these responses:

- Stream the work behind `Suspense`.
- Cache it with `use cache`.
- Explicitly accept a server-bound page or layout.

```ts
export const instant = false
```

See the caching reference for the associated partial-prefetching and loading-shell controls.
