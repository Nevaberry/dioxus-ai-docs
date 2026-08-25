# Routing and Rendering

## Link navigation

### Navigation-aware handlers (`15.3.0`)

`Link.onNavigate` runs only for client-side SPA navigations, rather than for
every click. Its event supports `preventDefault()`, so use it for navigation
guards and cancellation.

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

### Local pending state (`15.3.0`)

The Client Component hook `useLinkStatus()` returns a `pending` boolean during
navigation. Its caller must render as a descendant of the corresponding
`Link`.

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

### Prefetch control (`15.4.0`)

`router.prefetch()` accepts `onInvalidate`, which runs when prefetched data
becomes stale and can prefetch the route again. `Link` also accepts
`prefetch="auto"` as an explicit alias for its default
`prefetch={undefined}` behavior.

```tsx
router.prefetch('/dashboard', {
  onInvalidate: () => router.prefetch('/dashboard'),
})
```

### Link transition types (`16.2.0`)

In the App Router, `transitionTypes` passes each string to
`React.addTransitionType` during navigation:

```tsx
<Link href="/about" transitionTypes={['slide']}>About</Link>
```

Pages Router links ignore the prop, allowing a shared link component.

## Missing routes and route fallbacks

### Global not-found metadata (`15.4.0`)

With `experimental.globalNotFound` enabled, `app/global-not-found.tsx` can
export metadata as well as the global 404 UI.

```tsx
export const metadata = { title: 'Page not found' }

export default function GlobalNotFound() {
  return <html><body><h1>Page not found</h1></body></html>
}
```

### Intercepted-route prerendering (`15.4.0`)

Partial prerendering supports intercepted dynamic routes; those route patterns
do not need to forgo PPR.

### Required parallel-route defaults (`16.0.0`)

Every parallel-route slot must contain `default.js`. A missing fallback fails
the build. Call `notFound()` or return `null` to preserve the former fallback
behavior when no visible UI is needed.

```tsx
import { notFound } from 'next/navigation'

export default function Default() {
  notFound()
}
```

### Root params remain server-only (`15.4.0`)

The former `unstable_rootParams` API was unsupported in Client Components and
had to remain in Server Components. It was subsequently removed in Next.js 16.

## Error boundaries and retrying

### Component-level framework boundaries (`16.2.0`)

Client Components can wrap any subtree with `unstable_catchError()` from
`next/error`. The fallback receives call-site props and `ErrorInfo`. Framework
control-flow errors such as `redirect()` and `notFound()` pass through, and
the captured state clears on navigation to a different route.

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

### Server-aware retries (`16.2.0`)

An `error.tsx` component can receive `unstable_retry()`. It refreshes the
router and resets the boundary inside a transition, re-fetching data and
re-rendering the segment. Unlike `reset()`, it handles failures from data
fetching and Server Component rendering and is preferred for most retries.

## Scrolling and focus

### Smooth scrolling (`16.0.0`)

Automatic handling of `scroll-behavior: smooth` was removed. Opt in by
rendering `<html data-scroll-behavior="smooth">`.

### Browser-like focus handling (`16.2.0`)

`experimental.appNewScrollHandler` opted into App Router scrolling and focus
management based on React Fragment refs. After navigation it blurs the active
element instead of focusing the first focusable descendant deep in the new
segment, matching browser navigation behavior.

The reworked fragment-scroll and focus handler became the default in the
canary line described by `release-catalogs`, so remove assumptions that it is
always gated by the experimental flag.

## Instant navigation

### Explicitly blocking routes (`16.3.0`)

With Cache Components enabled, development and builds diagnose server work
that delays navigation. Stream the work behind `Suspense`, cache it with
`use cache`, or explicitly accept a server-bound page or layout:

```ts
export const instant = false
```

### Immediate-state tests (`16.3.0`)

`@next/playwright` exports `instant()`, which scopes assertions to UI available
immediately after an action rather than content arriving after a network round
trip.

```ts
import { instant } from '@next/playwright'

await instant(page, async () => {
  await page.click('a[href="/products/hats"]')
  await expect(page.getByText('Checking inventory...')).toBeVisible()
})
```

## Development interaction (`15.4.0`)

Restart the development server directly from either the error overlay or the
development-indicator preferences.
