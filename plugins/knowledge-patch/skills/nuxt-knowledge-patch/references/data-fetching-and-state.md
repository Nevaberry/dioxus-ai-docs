# Data fetching and state

Use this reference for async-data identity, shared refs, cancellation, payload extraction, cache lifetime, preview behavior, cookies, and Nuxt state helpers.

## Contents

- [Keys, sharing, and handler execution](#keys-sharing-and-handler-execution)
- [Cancellation and custom factories](#cancellation-and-custom-factories)
- [Cache lifetime and payloads](#cache-lifetime-and-payloads)
- [One-time work and state reset](#one-time-work-and-state-reset)
- [Cookie synchronization and expiry](#cookie-synchronization-and-expiry)

## Keys, sharing, and handler execution

### Keep prerendered keys globally consistent (3.10.0)

Enable shared prerender data to deduplicate and cache `useAsyncData` and `useFetch` work across prerendered routes:

```ts
export default defineNuxtConfig({
  experimental: { sharedPrerenderData: true },
})
```

Every explicit async-data key must always identify the same data across all routes. `useFetch` generates its own key.

### Expect keyed callers to share refs (3.17.0)

All `useAsyncData` or `useFetch` calls with the same key share their underlying refs. Refreshing the key updates every consumer, and watched-dependency changes across consumers are coalesced into one fetch.

### Use reactive async-data keys for changing identities (3.17.0)

Pass a ref, computed ref, or getter as the `useAsyncData` key. When its resolved value changes, Nuxt fetches the new entry and removes the old entry after its last consumer is gone.

```ts
const userId = ref('123')
const { data: user } = useAsyncData(
  () => `user-${userId.value}`,
  () => fetchUser(userId.value),
)
```

### Retain prior data across reactive key changes (3.18.0)

When a computed `useAsyncData` key changes, Nuxt keeps the old data while the new key is resolved instead of immediately discarding it.

### Coordinate cache lookup and request identity (4.4.0)

Concurrent callers with the same key deduplicate `getCachedData`, and Nuxt checks the cache again after the initial fetch. `useFetch` updates its generated key even when `watch: false`, hashes `FormData` request bodies correctly for deduplication, and prevents an in-flight request from restoring data after it has been cleared.

### Treat empty data as `undefined` (release-catalogs)

Current `useAsyncData` and `useFetch` result types use `undefined`, not `null`, for an absent value. Narrow results and initialize fallbacks accordingly.

## Cancellation and custom factories

### Propagate async-data abort signals (4.2.0)

Handlers receive an abort signal in their second argument. Nuxt aborts cancel-deduplicated refreshes and the latest pending handler on `clear()`. A caller can also supply its own signal to `refresh()` or `execute()`.

```ts
const { refresh } = await useAsyncData('users', (_app, { signal }) =>
  $fetch('/api/users', { signal }))

const controller = new AbortController()
refresh({ signal: controller.signal })
controller.abort()
```

### Build typed fetch and async-data composables (4.4.0)

Use `createUseFetch` and `createUseAsyncData` to make fully typed composables with shared defaults. An object provides defaults that call-site options override; a callback receives current options and controls merging. Definitions inside a composables directory participate in SSR key injection.

```ts
export const useApiFetch = createUseFetch((options) => ({
  ...options,
  baseURL: options.baseURL ?? useRuntimeConfig().public.baseApiUrl,
}))
```

### Extract async-data handlers experimentally (4.2.0)

`experimental.extractAsyncDataHandlers` moves `useAsyncData` and `useLazyAsyncData` handlers into dynamically imported chunks. On prerendered pages whose values already exist in payloads, those handler chunks can be omitted from the client bundle.

```ts
export default defineNuxtConfig({
  experimental: { extractAsyncDataHandlers: true },
})
```

## Cache lifetime and payloads

### Control cache cleanup after unmount (3.17.0)

Cached async data is purged after its consumers unmount instead of remaining indefinitely. Disable `experimental.purgeCachedData` only when an application depends on the old lifetime. More compatibility-sensitive cache changes remain behind disabled-by-default `experimental.granularCachedData`.

```ts
export default defineNuxtConfig({
  experimental: { purgeCachedData: false },
})
```

### Invalidate data when preview mode changes (3.11.0)

`usePreviewMode()` returns reactive `enabled` and `state`. Enabling preview mode reruns `useAsyncData` and `useFetch` and bypasses values cached in the payload.

```ts
const { enabled, state } = usePreviewMode()
```

### Expect automatic payload cache busting (3.11.0)

When the Nuxt app manifest is enabled, generated payload URLs carry automatic cache busting so clients do not retain stale payloads after deployment.

### Extract payloads for cache route rules (3.21.0)

Payload extraction applies to ISR, SWR, and cache route rules. Client navigation can consume cacheable `_payload.json` data instead of refetching. During development it works with `nitro.static: true` and for routes using `isr`, `swr`, `prerender`, or `cache` rules.

```ts
export default defineNuxtConfig({
  routeRules: { '/products/**': { isr: 3600 } },
})
```

### Evaluate client-mode payload extraction (4.4.0)

The client mode inlines a cached route's payload in its initial HTML while retaining `_payload.json` for later client navigation. A runtime LRU payload cache is active generally; client mode remains opt-in until compatibility version 5.

```ts
export default defineNuxtConfig({
  experimental: { payloadExtraction: 'client' },
})
```

## One-time work and state reset

### Scope `callOnce` to navigation (3.15.0)

Pass `mode: 'navigation'` to execute a callback once per navigation while still avoiding duplicate work between initial server rendering and client hydration.

```ts
await callOnce(() => counter.value++, { mode: 'navigation' })
```

### Retry failed `callOnce` work (4.4.0)

A rejected `callOnce` promise is removed from its cache. A later invocation retries the callback instead of receiving a permanently cached rejection.

### Reset `useState` to its initializer (4.4.0)

`clearNuxtState` restores the initializer's result rather than leaving the state `undefined`.

```ts
const count = useState('counter', () => 0)
count.value = 42
clearNuxtState('counter') // 0
```

## Cookie synchronization and expiry

### Refresh expiry without changing the cookie value (4.4.0)

Set `refresh: true` on `useCookie` when assigning the same value should renew expiry, such as for sliding sessions.

```ts
const session = useCookie('session-id', { maxAge: 3600, refresh: true })
session.value = session.value
```

### Disable Cookie Store integration when unwanted (release-catalogs)

`experimental.cookieStore` defaults to `true`. Opt out when browser Cookie Store synchronization is not desired.

```ts
export default defineNuxtConfig({
  experimental: { cookieStore: false },
})
```
