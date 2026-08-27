# Data fetching and state

## Stable keys and shared ownership

Each explicit `useAsyncData` key must always denote the same data. `useFetch` derives a key automatically. During prerendering, shared data can be deduplicated and cached across routes when `experimental.sharedPrerenderData` is enabled (3.10.0).

```ts
export default defineNuxtConfig({
  experimental: { sharedPrerenderData: true },
})
```

Calls sharing a key also share refs, refreshes, cached-data access, and in-flight work; watched changes across consumers are coalesced (3.17.0). Reactive keys may be refs, computed refs, or getters. When a resolved key changes, Nuxt starts the new request and retains the old data during loading; the old cache entry is removed after its final consumer unmounts (3.17.0, 3.18.0).

```ts
const userId = ref('123')
const { data: user } = useAsyncData(
  () => `user-${userId.value}`,
  () => fetchUser(userId.value),
)
```

Cached async data is purged when it has no consumers. Set `experimental.purgeCachedData: false` only for code that intentionally relies on the older indefinite lifetime. `experimental.granularCachedData` remains a separate, disabled compatibility switch (3.17.0).

## Cancellation and completion

Handlers receive an abort signal in their second argument. Pass it to downstream requests. Nuxt aborts cancel-deduplicated refreshes and the latest pending handler on `clear()`; callers can pass an owned signal to `refresh()` or `execute()` (4.2.0).

```ts
const { refresh } = await useAsyncData('users', (_app, { signal }) =>
  $fetch('/api/users', { signal }),
)

const controller = new AbortController()
refresh({ signal: controller.signal })
controller.abort()
```

An in-flight request cannot overwrite data after it has been cleared. Async-data processing that bails out now settles its status rather than leaving it unresolved (4.5.2).

## Cached-data and request deduplication details

Concurrent callers for one key deduplicate `getCachedData`, and Nuxt checks cached data again after the initial fetch. `useFetch` updates its derived key even with `watch: false`, hashes `FormData` bodies correctly, and does not let cleared in-flight work restore stale data (4.4.0).

Use absent-value types as `undefined`, not `null`, when narrowing `useAsyncData` or `useFetch` results (release-catalogs).

`createUseFetch` and `createUseAsyncData` create fully typed wrappers with shared defaults. An object supplies defaults overridden by call-site options; a callback can inspect and merge current options. Wrappers defined in a composables directory participate in SSR key injection (4.4.0).

```ts
export const useApiFetch = createUseFetch((options) => ({
  ...options,
  baseURL: options.baseURL ?? useRuntimeConfig().public.baseApiUrl,
}))
```

## Preview mode and payload invalidation

`usePreviewMode()` exposes reactive `enabled` and `state`. Enabling preview mode reruns `useAsyncData` and `useFetch` and bypasses payload-cached data (3.11.0). Nuxt re-checks preview mode after a prerendered page hydrates, so hydration follows the current preview state (4.5.2).

Generated payload URLs are cache-busted automatically when the app manifest is enabled, preventing a new deployment from reusing stale payloads (3.11.0).

## Payload extraction for cacheable routes

Payload extraction covers prerender, ISR, SWR, and cache route rules, allowing client navigation to consume `_payload.json` rather than refetch. In development it applies with `nitro.static: true` or a matching `isr`, `swr`, `prerender`, or `cache` rule (3.21.0).

```ts
export default defineNuxtConfig({
  routeRules: { '/products/**': { isr: 3600 } },
})
```

Client payload mode inlines a cached route's payload into its initial HTML while retaining `_payload.json` for later navigation. A runtime LRU payload cache is always active; `experimental.payloadExtraction: 'client'` remains opt-in before compatibility version 5 (4.4.0).

```ts
export default defineNuxtConfig({
  experimental: { payloadExtraction: 'client' },
})
```

The experimental async-data handler extractor moves `useAsyncData` and `useLazyAsyncData` handlers into dynamic chunks. On prerendered sites, handlers whose results already exist in payloads can then be omitted from the client bundle (4.2.0).

## `callOnce` behavior

Use `{ mode: 'navigation' }` for work that should run once per navigation while avoiding duplicate execution between SSR and hydration (3.15.0).

```ts
await callOnce(() => counter.value++, { mode: 'navigation' })
```

A rejected callback is removed from the `callOnce` cache, so later calls retry instead of receiving a permanently cached rejection (4.4.0).

## Cookie and application state helpers

`clearNuxtState` resets a `useState` entry to its initializer rather than leaving it `undefined` (4.4.0).

```ts
const count = useState('counter', () => 0)
count.value = 42
clearNuxtState('counter') // 0
```

Set `refresh: true` on `useCookie` when assigning the same value should renew expiry, such as for sliding sessions (4.4.0).

```ts
const session = useCookie('session-id', { maxAge: 3600, refresh: true })
session.value = session.value
```

Cookie Store synchronization is enabled by default. Disable it with `experimental.cookieStore: false` when the browser integration is unwanted (release-catalogs).
