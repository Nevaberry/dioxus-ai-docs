# Data fetching and state

Use async data, payload caches, cookies, preview mode, and state helpers with current identity and lifetime semantics.

## Application state and cookies

### Auto-imported watcher cleanup (since 3.18.0)

Vue's `onWatcherCleanup` is now a Nuxt auto-import, so watcher-owned resources can be released without an explicit Vue import.

```ts
watch(source, () => {
  const timer = setInterval(runTask, 1000)
  onWatcherCleanup(() => clearInterval(timer))
})
```

### Cookie Store integration defaults on (release-catalogs)

`experimental.cookieStore` is `true` by default. Disable it explicitly when browser Cookie Store synchronization is unwanted.

```ts
export default defineNuxtConfig({
  experimental: { cookieStore: false },
})
```

### Failed `callOnce` work can be retried (since 4.4.0)

A rejected `callOnce` promise is removed from its cache, so a later call can retry the work instead of receiving the permanently cached rejection.

### Navigation-scoped `callOnce` (since 3.15.0)

Pass `mode: 'navigation'` to run a `callOnce` callback once per navigation while still avoiding duplicate execution between the initial server render and client hydration.

```ts
await callOnce(() => counter.value++, { mode: 'navigation' })
```

### Refreshing cookie expiry without changing its value (since 4.4.0)

Set `refresh: true` on `useCookie` to renew expiry when assigning the same value, which supports sliding session expiration.

```ts
const session = useCookie('session-id', { maxAge: 3600, refresh: true })
session.value = session.value
```

### Resetting state to its initializer (since 4.4.0)

`clearNuxtState` now resets a `useState` entry to its initializer instead of leaving it `undefined`.

```ts
const count = useState('counter', () => 0)
count.value = 42
clearNuxtState('counter') // 0
```

### Shared state for keyed async data (since 3.17.0)

Every `useAsyncData` or `useFetch` call with the same key now shares its underlying refs. Refreshing the key updates every consumer, and watched dependency changes across multiple consumers are coalesced into one fetch.

## Async-data identity and execution

### Abortable async-data handlers and refreshes (since 4.2.0)

`useAsyncData` handlers now receive an abort signal in their second argument. Nuxt aborts cancel-deduplicated refreshes and the latest pending handler on `clear()`; callers can also pass their own signal to `refresh()` or `execute()`.

```ts
const { refresh } = await useAsyncData('users', (_app, { signal }) =>
  $fetch('/api/users', { signal }))
const controller = new AbortController()
refresh({ signal: controller.signal })
controller.abort()
```

### Async-data status after bailouts (since 4.5.2)

When async-data processing bails out, its status now settles instead of remaining in an unresolved state.

### Custom `useFetch` and `useAsyncData` factories (since 4.4.0)

`createUseFetch` and `createUseAsyncData` create fully typed custom composables with shared defaults. An object supplies defaults that call-site options override; a callback receives the current options and controls merging, and composables-directory definitions are registered for SSR key injection.

```ts
export const useApiFetch = createUseFetch((options) => ({
  ...options,
  baseURL: options.baseURL ?? useRuntimeConfig().public.baseApiUrl,
}))
```

### Empty data-fetching values are `undefined` (release-catalogs)

The current data-fetching types use `undefined`, not `null`, for absent values. Narrow `useAsyncData` and `useFetch` results accordingly.

### Extracted async-data handlers (since 4.2.0)

The experimental handler extractor moves `useAsyncData` and `useLazyAsyncData` handlers into dynamically imported chunks. On prerendered sites, handlers whose results are already in payloads can then be removed from the client bundle.

```ts
export default defineNuxtConfig({ experimental: { extractAsyncDataHandlers: true } })
```

### Reactive async-data keys (since 3.17.0)

`useAsyncData` keys can now be refs, computed refs, or getter functions. Changing the resolved key fetches the new entry and cleans up the old entry once it has no remaining consumers.

```ts
const userId = ref('123')
const { data: user } = useAsyncData(
  () => `user-${userId.value}`,
  () => fetchUser(userId.value),
)
```

### Retained data when reactive async-data keys change (since 3.18.0)

When a computed `useAsyncData` key changes, Nuxt now retains the old data instead of discarding it during the key change.

## Payloads, caching, and preview

### Async-data cache and key semantics (since 4.4.0)

Concurrent callers sharing a key now deduplicate `getCachedData`, which is checked again after the initial fetch. `useFetch` also updates its key with `watch: false`, hashes `FormData` bodies correctly for deduplication, and prevents an in-flight request from overwriting data after it is cleared.

### Async-data cache lifetime controls (since 3.17.0)

Cached async data is now purged after its consumers unmount instead of remaining indefinitely. Applications relying on the old lifetime can disable `experimental.purgeCachedData`; additional compatibility-sensitive caching changes remain behind the disabled-by-default `experimental.granularCachedData` flag.

```ts
export default defineNuxtConfig({
  experimental: { purgeCachedData: false },
})
```

### Automatic payload cache busting (since 3.11.0)

When the Nuxt app manifest is enabled, generated payload URLs are now cache-busted automatically so a deployment does not leave clients using stale payload data.

### Client-mode payload extraction for cached routes (since 4.4.0)

The new client mode inlines a cached route's payload in its initial HTML while retaining `_payload.json` for client navigation. A runtime LRU payload cache is active for everyone; the client mode remains opt-in until compatibility version 5.

```ts
export default defineNuxtConfig({
  experimental: { payloadExtraction: 'client' },
})
```

### Payload extraction for cached routes (since 3.21.0)

Payload extraction now covers ISR, SWR, and cache route rules, so client navigation can use cacheable `_payload.json` data instead of refetching it. In development it works with `nitro.static: true`, or for routes using `isr`, `swr`, `prerender`, or `cache` rules.

```ts
export default defineNuxtConfig({
  routeRules: { '/products/**': { isr: 3600 } },
})
```

### Preview mode after prerender hydration (since 4.5.2)

Nuxt re-checks preview mode after a prerendered page hydrates, keeping the hydrated page aligned with the current preview state.

### Preview mode invalidates async data (since 3.11.0)

`usePreviewMode()` exposes reactive `enabled` and `state` values. Enabling preview mode reruns `useAsyncData` and `useFetch` calls and bypasses data cached in the payload.

```ts
const { enabled, state } = usePreviewMode()
```

### Shared data during prerendering (since 3.10.0)

`useAsyncData` and `useFetch` calls can be deduplicated and cached across prerendered routes. Each explicit async-data key must always identify the same data; `useFetch` generates its key automatically.

```ts
export default defineNuxtConfig({
  experimental: { sharedPrerenderData: true },
})
```
