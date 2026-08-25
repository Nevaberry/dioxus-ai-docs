# Routing and Rendering

## Navigation-aware links (`15.3.0`)

`Link` accepts `onNavigate`, which runs for client-side SPA navigations rather than every click. Its event supports `preventDefault()`, so use it for navigation guards and cancellation.

```tsx
<Link
  href="/dashboard"
  onNavigate={(event) => {
    if (!window.confirm('Leave this page?')) event.preventDefault()
  }}
>
  Dashboard
</Link>
```

The Client Component hook `useLinkStatus()` returns a `pending` boolean for an in-progress navigation. The component calling it must render as a descendant of the corresponding `Link`.

```tsx
'use client'

import Link, { useLinkStatus } from 'next/link'

function Pending() {
  const { pending } = useLinkStatus()
  return pending ? <span>Loading...</span> : null
}

export function Navigation() {
  return <Link href="/dashboard">Dashboard <Pending /></Link>
}
```

## Explicit and renewable prefetching (`15.4.0`)

`prefetch="auto"` is an explicit alias for the default `prefetch={undefined}` link behavior.

`router.prefetch()` accepts `onInvalidate`, allowing code to react when prefetched data becomes stale and optionally warm it again.

```tsx
'use client'

import { useRouter } from 'next/navigation'

export function WarmDashboard() {
  const router = useRouter()
  return (
    <button onMouseEnter={() => router.prefetch('/dashboard', {
      onInvalidate: () => router.prefetch('/dashboard'),
    })}>
      Dashboard
    </button>
  )
}
```

## Global not-found metadata (`15.4.0`)

With `experimental.globalNotFound` enabled, `app/global-not-found.tsx` may export metadata for the global 404 page.

```tsx
export const metadata = { title: 'Page not found' }

export default function GlobalNotFound() {
  return <html><body><h1>Page not found</h1></body></html>
}
```

## Intercepted routes and partial prerendering (`15.4.0`)

Partial prerendering supports intercepted dynamic routes, so these route patterns do not have to opt out of PPR.

## Incremental segment prefetching (`16.0.0`)

Modern prefetching downloads a shared layout once and requests only segments missing from the cache. It cancels work when a link leaves the viewport, reprioritizes hover and viewport re-entry, and prefetches again after invalidation. This can produce more individual requests while transferring less total data.

## Smooth scrolling (`16.0.0`)

Automatic handling of `scroll-behavior: smooth` is removed. Opt in explicitly on the document element.

```tsx
<html data-scroll-behavior="smooth">
```

## Required parallel-route fallbacks (`16.0.0`)

Every parallel-route slot needs a `default.js`; omission is a build failure. Call `notFound()` or return `null` for a deliberately empty fallback.

## Link view transitions (`16.2.0`)

In the App Router, `transitionTypes` passes every supplied string to `React.addTransitionType` during navigation.

```tsx
<Link href="/about" transitionTypes={['slide']}>About</Link>
```

Pages Router links silently ignore this prop, so a shared link component may still expose it.

## Component-level framework error boundaries (`16.2.0`)

Client Components can use `unstable_catchError()` from `next/error` to place framework-aware error boundaries anywhere in the tree. The fallback receives its call-site props and `ErrorInfo`. Control-flow errors such as `redirect()` and `notFound()` pass through correctly, and navigation to another route clears the error state.

```tsx
'use client'

import { unstable_catchError, type ErrorInfo } from 'next/error'

function Fallback(
  { title }: { title: string },
  { error, unstable_retry }: ErrorInfo,
) {
  return <button onClick={() => unstable_retry()}>{title}: {error.message}</button>
}

export default unstable_catchError(Fallback)
```

## Server-aware retries (`16.2.0`)

An `error.tsx` component's `unstable_retry()` prop refreshes the router and resets its boundary inside a transition. It re-fetches data and re-renders the segment, including errors from data fetching or the Server Component phase. Prefer it to `reset()` for most retries.

```tsx
'use client'

import type { ErrorInfo } from 'next/error'

export default function Error({ error, unstable_retry }: ErrorInfo) {
  return <button onClick={() => unstable_retry()}>Retry: {error.message}</button>
}
```

## Prefetch response and navigation experiments (`16.2.0`)

`experimental.prefetchInlining` places all prefetched segment data for one route in a single response. This reduces prefetching to one request per link but duplicates shared-layout data instead of reusing it from the segment cache.

```ts
export default { experimental: { prefetchInlining: true } }
```

`experimental.cachedNavigations` separately caches static and dynamic Server Component data from navigations and initial HTML loads for instant repeat visits. It requires Cache Components.

```ts
export default {
  cacheComponents: true,
  experimental: { cachedNavigations: true },
}
```

## Browser-like focus handling (`16.2.0`, `release-catalogs`)

`experimental.appNewScrollHandler: true` opted into reworked App Router scroll and focus management using React Fragment refs. After navigation it blurs the active element instead of focusing the first focusable descendant deep in the new segment, matching browser behavior.

The reworked fragment-scroll and focus handler became the canary-line default in `release-catalogs`; do not continue treating the experimental opt-in as universally necessary after that transition.

## Instant routes (`16.3.0`)

With Cache Components enabled, the development overlay and terminal identify server work that delays navigation, and `next build` reports the same guidance when it stops prerendering. Put work behind `Suspense`, cache it with `use cache`, or explicitly accept a server-bound page or layout.

```ts
export const instant = false
```

## Partial Prefetching (`16.3.0`)

The top-level `partialPrefetching` flag makes production prefetching fetch and session-cache one reusable loading shell per distinct route rather than one response per link. The Navigation Inspector can pause a navigation at that shell during development.

```ts
const nextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
}

export default nextConfig
```

`<Link prefetch={true}>` additionally includes per-link synchronous or cached content known at build time. `export const prefetch = 'allow-runtime'` extends the work to request-time cached content, increasing server load.
