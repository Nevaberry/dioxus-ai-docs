# Caching and Prefetching

## Cache Components

### Enabling and directive scope (`16.0-guide`)

Enable Cache Components before using `use cache`:

```ts
const nextConfig = { cacheComponents: true }
export default nextConfig
```

The directive may cover every export in a file, one async component, or one
async function. A fully cached route needs the directive in both its layout
and page because those segments are separate cache entries.

At file scope, exported functions must be async. As clarified in `16.3.1`,
literal exports may coexist with them:

```ts
'use cache'

export const source = 'catalog'

export async function getSource() {
  return source
}
```

### Compiler-generated keys (`16.0-guide`)

A key includes the build ID, a function ID derived from its location and
signature, serialized arguments or props, and captured outer-scope values.
Development also includes an HMR hash. New builds invalidate all entries;
different arguments or closure values create separate entries. Do not assemble
keys manually.

### Serialization and pass-through composition (`16.0-guide`)

Arguments follow Server Component serialization, while returned values follow
the broader Client Component serialization. Cached functions can return JSX,
but class and `URL` instances cannot be cache-key inputs. Non-serializable
children and Server Actions can pass through by reference only when cached code
does not inspect or invoke them.

### Request data and React cache isolation (`16.0-guide`)

Cached scopes cannot directly read `cookies()`, `headers()`, or request-time
`searchParams`. Resolve those outside and pass serializable values in. Each
cached scope also has isolated `React.cache` state, so values placed in a React
cache outside the boundary are unavailable inside it.

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

### Storage and lifetime (`16.0-guide`)

Server entries use memory by default. They generally do not survive requests
on serverless instances, but persist on self-hosted servers, where
`cacheMaxMemorySize` bounds them. Custom `cacheHandlers` and a
platform-provided `'use cache: remote'` handler are available. Browser entries
honor `stale` with a 30-second minimum. Static export is unsupported, and
adapter support varies by platform.

The default profile is 5 minutes stale, 15 minutes revalidate, and no
time-based expiry. `cacheLife` changes it, while `cacheTag` associates entries
for cross-layer invalidation.

```ts
import { cacheLife, cacheTag } from 'next/cache'

export async function getProducts() {
  'use cache'
  cacheLife('hours')
  cacheTag('products')
  return (await fetch('/api/products')).json()
}
```

### Invalidation APIs (`16.0.0`)

- `revalidateTag(tag, profile)` takes a named/custom `cacheLife` profile or an
  inline `{ expire: seconds }` value and provides stale-while-revalidate
  behavior. The one-argument form is deprecated.
- Server Action-only `updateTag()` expires tagged data immediately with
  read-your-writes semantics.
- Server Action-only `refresh()` refreshes uncached data shown elsewhere
  without touching cached content.

Cache `expire` and `revalidate` values are normalized and validated earlier in
the line documented by `release-catalogs`, including explicit handling for
`Infinity`, so invalid values surface closer to configuration.

### Diagnostics and timeouts (`16.0-guide`)

Set `NEXT_PRIVATE_DEBUG_CACHE=1` for verbose cache and ISR logs. Development
replays cached-function logs with a `Cache` prefix.

```sh
NEXT_PRIVATE_DEBUG_CACHE=1 npm run dev
```

During prerendering, a cached function that awaits request-specific or
uncached Promises created outside its boundary times out after 50 seconds.
Calling `cookies()` or `headers()` directly inside the boundary fails
immediately.

## Segment prefetching

### Incremental route prefetching (`16.0.0`)

Prefetching downloads a shared layout once and then requests only segments
missing from the cache. It cancels work when a link leaves the viewport,
prioritizes hover and viewport re-entry, and prefetches again after
invalidation. Expect more individual requests but less total data.

### One-response prefetching (`16.2.0`)

`experimental.prefetchInlining` combines all prefetched segment data for a
route into one response. This reduces prefetching to one request per link, but
duplicates shared-layout data instead of reusing it from the segment cache.

```ts
export default { experimental: { prefetchInlining: true } }
```

### Cached navigations (`16.2.0`)

`experimental.cachedNavigations` independently caches static and dynamic
Server Component data from navigations and initial HTML loads for instant
repeat visits. It requires Cache Components.

```ts
export default {
  cacheComponents: true,
  experimental: { cachedNavigations: true },
}
```

### Partial Prefetching (`16.3.0`)

Top-level `partialPrefetching` makes production prefetching fetch and
session-cache one reusable loading shell per distinct route instead of one
response per link. The Navigation Inspector can pause at that shell during
development.

```ts
const nextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
}
export default nextConfig
```

`<Link prefetch={true}>` also fetches per-link synchronous or cached content
known at build time. `export const prefetch = 'allow-runtime'` extends that
work to request-time cached content at the cost of more server load.
