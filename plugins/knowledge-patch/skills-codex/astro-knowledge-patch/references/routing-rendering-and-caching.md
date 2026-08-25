# Routing, rendering, and caching

## Server islands and route rendering

Server islands in 5.0.0 let a cached static page defer personalized or dynamic server-rendered components with independent loading and fallback content. An island may set its own response headers, works behind automatic page compression, and encrypts props with a server-generated key.

The default output is static; after adding an adapter, opt a route into runtime rendering with `export const prerender = false`.

## Redirects and canonical paths

Since 5.2.0, rendered routes redirect slash variants, including repeated trailing slashes, to the `trailingSlash` form. Production uses 301 for GET and method-preserving 308 for other methods; development reports an error so incorrect links remain visible. Configuration redirects may also target absolute HTTP or HTTPS URLs; with an adapter, use `{ destination, status }` for an explicit external status.

## Endpoints and prefetching

Since 5.3.0, a `GET` endpoint automatically handles `HEAD` by running `GET` and returning the response without a body. Export `HEAD` separately only for different behavior.

With `experimental.clientPrerender`, the 5.6.0 `prefetch(url, { eagerness })` option accepts Speculation Rules values `immediate` (default), `eager`, `moderate`, and `conservative`.

## Prerendered routes and pagination

Since 5.14.0, colliding dynamic routes that prerender the same pathname produce a warning naming the routes and path. Set `experimental.failOnPrerenderConflict: true` to fail the build. The `getStaticPaths()` context also exposes `routePattern`, the original dynamic segment pattern, for helpers that derive complex or localized params.

Since 6.1.0, routes passed to `astro:routes:resolved` expose `fallbackRoutes` generated for i18n `fallbackType: 'rewrite'`; integrations can enumerate them and the sitemap integration includes them automatically.

In 7.0.1-7.2.4, `paginate(items, { format(url) })` can replace every generated URL, for example to append `.html`.

## Queued rendering

Astro 6.0.0 introduced the two-pass renderer behind:

```js
experimental: { queuedRendering: { enabled: true } }
```

It is stable and enabled automatically in 7.0.0; remove the experimental option.

## Response caching

Astro 6.0.0 introduced response caching under `experimental.cache`. Configure a provider, then set page policy through `Astro.cache.set()` or endpoint policy through `context.cache.set()` using `maxAge`, `swr`, and `tags`. Passing a live content entry records an invalidation dependency. The in-memory provider is primarily for the Node adapter.

In 7.0.0, move `cache` and `routeRules` to top-level configuration. `routeRules` applies policies to route groups, and `cache.invalidate()` purges by `tags` or `path`:

```js
import { defineConfig, memoryCache } from 'astro/config';

export default defineConfig({
  cache: { provider: memoryCache() },
  routeRules: {
    '/blog/[...path]': { maxAge: 300, swr: 60 },
  },
});
```

The same release adds manually configured experimental edge providers: `cacheNetlify()`, `cacheVercel()`, and the private-beta `cacheCloudflare()`. These can serve hits without invoking the server function.

## Advanced routing

Astro 6.3.0 exposes the request pipeline through `astro/fetch` and `astro/hono`. Available stages cover rendering, trailing slashes, redirects, sessions, Actions, middleware, pages, cache, and i18n. Use `FetchState` to proxy or conditionally call `astro(state)`, or order the Hono middleware explicitly.

```ts
import { FetchState, astro } from 'astro/fetch';

export default {
  fetch(request: Request) {
    const state = new FetchState(request);
    if (state.url.pathname.startsWith('/api')) {
      return fetch(new URL(state.url.pathname, 'https://api.example.com'));
    }
    return astro(state);
  },
};
```

The Cloudflare helpers added in 6.4.0 supply `SESSION` KV, `ASSETS`, `locals.cfContext`, client IP, `waitUntil`, and prerendered error-page behavior. Call `cf(state, env, ctx)` and return an asset response before `astro(state)`, or install `cf()` from the Hono entrypoint.

In 7.0.0, place the standard handler in `src/fetch.ts` to activate it. Without that file, Astro retains its normal request pipeline.

## Incremental static builds

In 7.0.1-7.2.4, enable `experimental.incrementalBuild` and return a `cacheKey` for each dynamic route from `getStaticPaths()`. Astro skips output only when both module dependencies and the key are unchanged. Preserve `node_modules/.astro/` in CI so skipped output can be restored. Loader-provided content `digest` values are suitable keys.

Out-of-process adapter prerenderers may return `{ response, metadata }` as a `PrerenderResult` so content and optimized-image dependencies participate; a bare `Response` remains valid.
