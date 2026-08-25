# Caching and Prefetching

## Early preview names (`15.4.0`)

The 15.4 canary line exposed caching and routing work through experimental flags. Preserve the old names only when maintaining that line:

- `dynamicIO` previewed the caching and prerendering model later named `cacheComponents` in Next.js 16.
- `clientSegmentCache` previewed client-router and segment caching.
- `turbopackPersistentCaching` previewed persistent compiler caching.
- `globalNotFound` enabled global 404 handling.
- `devtoolSegmentExplorer` enabled route exploration.
- `browserDebugInfoInTerminal` previewed browser-log forwarding.

```ts
const nextConfig = {
  experimental: {
    browserDebugInfoInTerminal: true,
    dynamicIO: true,
    clientSegmentCache: true,
    devtoolSegmentExplorer: true,
    globalNotFound: true,
    turbopackPersistentCaching: true,
  },
}
```

Prefer the later stable or renamed forms when the installed version supplies them.

## Enabling Cache Components (`16.0-guide`)

Enable Cache Components before using `use cache`.

```ts
const nextConfig = { cacheComponents: true }
export default nextConfig
```

The directive may cache all exports in a file, one async component, or one async function. Because layout and page segments are separate entries, a fully cached route needs the directive in both.

At module level, exported functions must be async. Starting with 16.3.1, exported literal values can coexist with the directive; the async requirement applies only to functions.

```ts
'use cache'

export const source = 'catalog'

export async function getSource() {
  return source
}
```

## Compiler-generated keys (`16.0-guide`)

Each cache key includes:

- The build ID, so a new build invalidates all entries.
- A function ID derived from location and signature.
- Serialized arguments or props.
- Captured outer-scope values.
- An HMR hash during development.

Different arguments or closure values therefore create separate entries. Do not construct a key manually.

```tsx
async function loadForUser(userId: string) {
  async function getData(filter: string) {
    'use cache'
    return (await fetch(`/api/users/${userId}/data?filter=${filter}`)).json()
  }
  return getData('active')
}
```

## Serialization and pass-through composition (`16.0-guide`)

Arguments follow Server Component serialization, while return values follow the less restrictive Client Component serialization. Cached code may return JSX, but class and `URL` instances cannot be cache-key inputs.

Non-serializable children and Server Actions may pass through as references without affecting the entry only when the cached function does not inspect or invoke them.

```tsx
async function CachedShell({ children }: { children: React.ReactNode }) {
  'use cache'
  return <main><header>Cached</header>{children}</main>
}
```

## Request data and `React.cache` isolation (`16.0-guide`)

Cached scopes cannot directly read `cookies()`, `headers()`, or request-time `searchParams`. Resolve those values outside the boundary and pass serializable arguments in.

```tsx
import { cookies } from 'next/headers'

export default async function Page() {
  const theme = (await cookies()).get('theme')?.value ?? 'light'
  return <CachedTheme theme={theme} />
}

async function CachedTheme({ theme }: { theme: string }) {
  'use cache'
  return <div data-theme={theme}>Cached content</div>
}
```

Each cached scope gets isolated `React.cache` state. Values placed in a React cache outside the boundary are not visible inside it.

## Storage and browser behavior (`16.0-guide`)

Server entries use in-memory storage by default. They typically do not survive requests on serverless instances, but persist on self-hosted servers, where `cacheMaxMemorySize` bounds memory use. Custom `cacheHandlers` or a platform-provided `'use cache: remote'` handler may supply external storage.

Browser entries honor the `stale` value with a 30-second minimum. Static export is unsupported, and adapter behavior depends on the deployment platform.

## Lifetime and tags (`16.0-guide`)

The default profile is five minutes stale, 15 minutes revalidate, and no time-based expiry. `cacheLife()` selects another profile, while `cacheTag()` associates entries for invalidation across server and client cache layers.

```ts
import { cacheLife, cacheTag } from 'next/cache'

export async function getProducts() {
  'use cache'
  cacheLife('hours')
  cacheTag('products')
  return (await fetch('/api/products')).json()
}
```

Cache `expire` and `revalidate` values are normalized and validated earlier in `release-catalogs`, including explicit handling for `Infinity`. Invalid values therefore surface closer to configuration.

## Invalidation and refresh (`16.0.0`)

`revalidateTag(tag, profile)` accepts a `cacheLife` profile such as `'max'`, a custom profile, or an inline `{ expire: seconds }` value. It gives stale-while-revalidate behavior. The single-argument form is deprecated.

`updateTag()` is available only in Server Actions. It expires tagged data immediately for read-your-writes behavior. The Action-only `refresh()` refreshes uncached data displayed elsewhere without touching cached content.

```ts
'use server'

import { refresh, updateTag } from 'next/cache'

export async function saveProfile() {
  await db.profiles.save()
  updateTag('profile')
  refresh()
}
```

## Cache diagnostics and build timeouts (`16.0-guide`)

Set `NEXT_PRIVATE_DEBUG_CACHE=1` for verbose cache and ISR logs. During development, cached-function logs are replayed with a `Cache` prefix.

```sh
NEXT_PRIVATE_DEBUG_CACHE=1 npm run dev
```

Prerendering waits 50 seconds before timing out when cached code awaits request-specific or uncached Promises created outside its boundary. Calling `cookies()` or `headers()` directly inside the cached function fails immediately.

## Prefetch invalidation and segment reuse (`15.4.0`, `16.0.0`)

`router.prefetch(href, { onInvalidate })` can run code after prefetched data becomes stale and optionally prefetch again. Segment prefetching downloads shared layouts once, fetches only missing segments, cancels work as links leave the viewport, reprioritizes hover and re-entry, and automatically re-prefetches invalidated data.

## One-response prefetching and cached navigations (`16.2.0`)

`experimental.prefetchInlining` reduces prefetching to one response per link by bundling all route segments. It trades that request reduction for duplication of shared-layout data.

`experimental.cachedNavigations` caches static and dynamic Server Component data obtained from navigation and initial HTML. It requires `cacheComponents: true` and makes repeated visits instant.

## Instant routes and Partial Prefetching (`16.3.0`)

Cache Components applications surface server work that blocks an instant route in the development overlay, terminal, and relevant build diagnostics. Stream work behind `Suspense`, cache it, or add `export const instant = false` to the page or layout.

Top-level `partialPrefetching: true` fetches and session-caches one reusable loading shell per distinct route. `prefetch={true}` adds content known synchronously or through build-known caches. `export const prefetch = 'allow-runtime'` also includes request-time cached content, at higher server cost.
