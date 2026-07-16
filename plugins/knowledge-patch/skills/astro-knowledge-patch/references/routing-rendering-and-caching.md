# Routing, rendering, and caching

## Static and on-demand rendering

Astro 5 folded the old `hybrid` mode into the default `static` output (`5.0.0`). Install an adapter and export `prerender = false` only from routes that should run on demand; other routes remain prerendered.

Server islands let a cached static page defer a personalized or otherwise dynamic server component and provide fallback content independently (`5.0.0`). An island can set its own response headers, works on platforms that compress pages automatically, and receives encrypted props using a server-generated key.

## Redirects and canonical URLs

### Trailing slashes

On-demand routes redirect slash variants, including paths with repeated trailing slashes, to the form selected by `trailingSlash` (`5.2.0`). Production uses 301 for GET and method-preserving 308 for other methods. Development reports an error instead, making invalid internal links visible.

```js
export default defineConfig({
  trailingSlash: 'never', // or 'always'
});
```

### Configured external redirects

Values in `redirects` can be absolute HTTP or HTTPS URLs (`5.2.0`). With an adapter, use the object form to pair an external `destination` with a `status`:

```js
export default defineConfig({
  redirects: {
    '/about': 'https://example.com/about',
    '/news': {
      status: 302,
      destination: 'https://example.com/news',
    },
  },
});
```

## Endpoints

An endpoint with a `GET` export also handles `HEAD` automatically: Astro runs `GET` and removes the response body (`5.3.0`). Export a dedicated `HEAD` handler only when its behavior must differ.

## Prefetching

With `experimental.clientPrerender` enabled, `prefetch()` accepts a browser Speculation Rules `eagerness` hint: `immediate`, `eager`, `moderate`, or `conservative` (`5.6.0`). `immediate` is the default.

```ts
import { prefetch } from 'astro:prefetch';

prefetch('/dashboard', { eagerness: 'conservative' });
```

## Prerendered dynamic routes

Astro warns when multiple dynamic routes prerender the same pathname and identifies both the routes and collision (`5.14.0`). Set `experimental.failOnPrerenderConflict: true` to convert the warning into a build failure.

The `getStaticPaths()` context includes `routePattern`, exposing the original dynamic segment pattern for localization and other helpers that derive `params` and `props` (`5.14.0`):

```astro
---
export function getStaticPaths({ routePattern }) {
  console.log(routePattern); // [...locale]/[files]/[slug]
  return [{ params: { locale: 'en', files: 'docs', slug: 'intro' } }];
}
---
```

For integrations, routes passed to `astro:routes:resolved` expose `fallbackRoutes` when i18n uses `fallbackType: 'rewrite'` (`6.1.0`). Each entry describes an additional locale pathname; the sitemap integration includes these generated fallbacks automatically.

## Queued rendering

Astro's two-pass rendering strategy was initially enabled with the nested flag `experimental.queuedRendering.enabled` (`6.0.0`):

```js
export default defineConfig({
  experimental: {
    queuedRendering: { enabled: true },
  },
});
```

Queued rendering is stable and enabled automatically in Astro 7 (`7.0.0`); remove the experimental opt-in.

## Route caching

### Response directives and dependencies

The preview API configured a provider under `experimental.cache` and set directives with `Astro.cache.set()` in pages or `context.cache.set()` in endpoints (`6.0.0`). `memoryCache()` is primarily suited to the Node adapter.

```js
import { defineConfig, memoryCache } from 'astro/config';

export default defineConfig({
  experimental: {
    cache: { provider: memoryCache() },
  },
});
```

```astro
---
Astro.cache.set({
  maxAge: 120,
  swr: 60,
  tags: ['home'],
});
---
```

The directive supports a fresh lifetime, stale-while-revalidate window, and tags. Passing a live content entry to `set()` records it as a dependency instead; changing that entry invalidates the cached response.

### Stable configuration and invalidation

Astro 7 moves `cache` and `routeRules` out of `experimental` (`7.0.0`). Route rules apply directives to route groups, and `cache.invalidate()` purges entries by `tags` or `path`. The page and endpoint cache APIs otherwise stay the same.

```js
export default defineConfig({
  cache: { provider: memoryCache() },
  routeRules: {
    '/blog/[...path]': { maxAge: 300, swr: 60 },
  },
});
```

### CDN providers

Astro 7 also offers manually configured experimental CDN providers that serve cache hits at the edge without invoking the server function (`7.0.0`):

- `cacheNetlify()` from `@astrojs/netlify/cache`;
- `cacheVercel()` from `@astrojs/vercel/cache`;
- private-beta `cacheCloudflare()` from `@astrojs/cloudflare/cache`.

Pair the provider with its corresponding adapter.

## Advanced routing

Advanced routing makes Astro's request pipeline available as composable Fetch handlers (`6.3.0`). `astro/fetch` and `astro/hono` expose stages for rendering, canonical trailing slashes, redirects, sessions, Actions, middleware, pages, caching, and i18n.

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

Hono applications can compose the individual stages with custom middleware and control their order:

```ts
import { Hono } from 'hono';
import { actions, middleware, pages, i18n } from 'astro/hono';

const app = new Hono();
app.use(actions());
app.use(middleware());
app.use(pages());
app.use(i18n());
export default app;
```

In Astro 7, place the standard advanced-routing handler at `src/fetch.ts` to activate it (`7.0.0`). Without that file, Astro uses the normal pipeline.

The Cloudflare adapter supplies both Fetch and Hono helpers for platform-specific behavior; see the adapters reference (`6.4.0`).
