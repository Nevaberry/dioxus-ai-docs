# Caching and Prefetching

Batch attributions used here: `15.4.0`, `16.0-guide`, `16.0.0`, `16.2.0`, `16.3.0`, and `release-catalogs`.

## Cache Components setup and directive scope

Enable Cache Components before adding `use cache` (`16.0-guide`):

```ts
// next.config.ts
const nextConfig = { cacheComponents: true }
export default nextConfig
```

The directive can apply at three scopes:

- At file scope, caching every export. Every exported function in that file must be async.
- Inside one async component.
- Inside one async function.

A layout and page are distinct cache entries. Put the directive in both when the whole route should be cached.

```tsx
async function CachedShell({ children }: { children: React.ReactNode }) {
  'use cache'
  return <main><header>Cached</header>{children}</main>
}
```

The earlier `experimental.dynamicIO` preview flag in `15.4.0` was renamed to `cacheComponents` in Next.js 16. Do not combine the old and new names.

## Compiler-generated cache keys

Do not build cache keys manually. Next.js includes all of these inputs (`16.0-guide`):

- The build ID, so a deployment invalidates prior entries.
- A function ID derived from its source location and signature.
- Serialized function arguments or component props.
- Captured outer-scope values.
- An HMR hash during development.

Different arguments or closure values therefore create separate entries automatically.

```tsx
async function loadForUser(userId: string) {
  async function getData(filter: string) {
    'use cache'
    return (await fetch(`/api/users/${userId}/data?filter=${filter}`)).json()
  }

  return getData('active')
}
```

The entry above varies by both `userId` and `filter`.

## Serialization and composition

Arguments use Server Component serialization. Class instances and `URL` instances cannot be cache-key inputs. Return values use the less restrictive Client Component serialization, so a cached function may return JSX (`16.0-guide`).

Non-serializable children and Server Actions can pass through a cached component as references without affecting the entry only when cached code does not inspect the child or invoke the Action. This makes a cached shell around dynamic content possible, but does not make arbitrary non-serializable values safe key material.

## Request data and cache isolation

A cached scope cannot directly read:

- `cookies()`.
- `headers()`.
- Request-time `searchParams`.

Resolve those values outside the scope and pass only the serializable data that affects the result (`16.0-guide`).

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

Cached scopes also receive an isolated `React.cache` scope. A value placed in a React cache outside the boundary is not visible from inside it.

## Storage, profiles, and platform behavior

Server entries use an in-memory store by default (`16.0-guide`). On serverless instances, that store typically does not survive across requests; on self-hosted servers it can persist and is bounded by `cacheMaxMemorySize`.

Applications can supply custom `cacheHandlers`, and a deployment environment can provide a `'use cache: remote'` handler. Support varies by adapter. Static export does not support these cached entries.

Browser entries honor a profile's `stale` value, with a minimum of 30 seconds. The default profile is:

- Five minutes stale.
- Fifteen minutes revalidate.
- No time-based expiry.

Call `cacheLife()` to select another profile. Cache lifetime values for `expire` and `revalidate` are normalized and validated earlier in the `release-catalogs` canary line, including explicit handling for `Infinity`; expect invalid values to fail close to configuration.

```ts
import { cacheLife, cacheTag } from 'next/cache'

export async function getProducts() {
  'use cache'
  cacheLife('hours')
  cacheTag('products')
  return (await fetch('/api/products')).json()
}
```

`cacheTag()` associates the entry with tags that can invalidate both server and client cache layers.

## Invalidation and refresh semantics

Next.js 16 separates three operations (`16.0.0`):

| API | Context | Behavior |
| --- | --- | --- |
| `revalidateTag(tag, profile)` | Server contexts | Stale-while-revalidate according to a `cacheLife` profile |
| `updateTag(tag)` | Server Actions only | Immediately expires tagged content for read-your-writes |
| `refresh()` | Server Actions only | Refreshes uncached content shown elsewhere without touching cached content |

`revalidateTag()` accepts a profile such as `'max'`, a custom named profile, or an inline `{ expire: seconds }`. Its old one-argument form is deprecated.

```ts
'use server'

import { refresh, updateTag } from 'next/cache'

export async function saveProfile() {
  await db.profiles.save()
  updateTag('profile')
  refresh()
}
```

Use `updateTag` after a mutation when the Action must immediately read the new value. Use profiled `revalidateTag` when eventual consistency is acceptable.

## Cache diagnostics and prerender stalls

Set the private diagnostic flag for verbose cache and ISR output (`16.0-guide`):

```sh
NEXT_PRIVATE_DEBUG_CACHE=1 npm run dev
```

Development replays logs produced by cached functions and prefixes them with `Cache`.

During prerendering, a cached function times out after 50 seconds if it waits for a request-specific or uncached Promise that was created outside its boundary. Calling `cookies()` or `headers()` directly inside the cached function fails immediately instead of waiting for that timeout. Resolve request values first, and create uncached work on the correct side of the cache boundary.

## Link and router prefetch controls

`router.prefetch()` accepts `onInvalidate`, which runs when prefetched data becomes stale (`15.4.0`). The callback can schedule another prefetch.

```tsx
'use client'

import { useRouter } from 'next/navigation'

export function WarmDashboard() {
  const router = useRouter()

  return (
    <button
      onMouseEnter={() =>
        router.prefetch('/dashboard', {
          onInvalidate: () => router.prefetch('/dashboard'),
        })
      }
    >
      Dashboard
    </button>
  )
}
```

`<Link prefetch="auto">` is an explicit alias for the default `prefetch={undefined}` behavior (`15.4.0`).

Partial prerendering also supports intercepted dynamic routes as of `15.4.0`; do not disable PPR merely because a route is intercepted and dynamic.

## Segment-aware prefetching

Next.js 16 route prefetching downloads a shared layout once and requests only segments missing from the cache (`16.0.0`). It may make more individual requests while transferring less total data. The scheduler:

- Cancels prefetch work when a link leaves the viewport.
- Prioritizes hover and viewport re-entry.
- Automatically prefetches again after invalidation.

## Single-response and cached navigation experiments

`experimental.prefetchInlining` combines every prefetched segment for one route into one response (`16.2.0`):

```ts
export default {
  experimental: { prefetchInlining: true },
}
```

This reduces prefetching to one request per link but duplicates shared-layout data instead of reusing it from the segment cache.

`experimental.cachedNavigations` independently caches static and dynamic Server Component data from navigations and initial HTML loads for instant repeat visits. It requires Cache Components.

```ts
export default {
  cacheComponents: true,
  experimental: { cachedNavigations: true },
}
```

## Partial Prefetching and instant routes

With Cache Components, `partialPrefetching` fetches and session-caches one reusable loading shell for each distinct route in production instead of one response per link (`16.3.0`). The Navigation Inspector can pause a development navigation at that shell.

```ts
const nextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
}

export default nextConfig
```

The associated controls have deliberately different costs:

- Default partial prefetching fetches the reusable loading shell.
- `<Link prefetch={true}>` also fetches per-link synchronous or cached content known at build time.
- `export const prefetch = 'allow-runtime'` extends prefetch work to request-time cached content, increasing server load.

When development or build diagnostics identify server work that blocks an instant route, stream it behind `Suspense`, cache it with `use cache`, or put `export const instant = false` in the page or layout to accept the server-bound navigation explicitly.
