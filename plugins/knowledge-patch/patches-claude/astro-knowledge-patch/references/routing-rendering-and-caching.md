# Routing, rendering, and caching

## Server islands and mixed rendering (5.0.0)

Server islands let a cached static page defer personalized or dynamic
server-rendered components. Each island has independent loading and fallback
content, can set its own response headers, works with platforms that
automatically compress pages, and receives props encrypted with a
server-generated key.

The default output is static. With an adapter installed, opt individual routes
into runtime rendering:

```astro
---
export const prerender = false;
---
```

## Canonical and external redirects (5.2.0)

Runtime routes redirect slash variants, including repeated trailing slashes,
to the form selected by `trailingSlash`. Production uses 301 for GET and the
method-preserving 308 for other methods. Development reports an error so
incorrect internal links stay visible.

The `redirects` map accepts absolute HTTP or HTTPS destinations. With an
adapter, object entries can specify a status:

```js
export default defineConfig({
  trailingSlash: 'never',
  redirects: {
    '/about': 'https://example.com/about',
    '/news': { status: 302, destination: 'https://example.com/news' },
  },
});
```

## Automatic HEAD handling (5.3.0)

An endpoint with `GET` also handles `HEAD`: Astro executes `GET` but removes
the response body. Export a distinct `HEAD` handler only when behavior must
differ.

## Prefetch eagerness (5.6.0)

With `experimental.clientPrerender`, `prefetch()` accepts a Speculation Rules
`eagerness` value: `immediate` (default), `eager`, `moderate`, or
`conservative`.

```ts
import { prefetch } from 'astro:prefetch';

prefetch('/dashboard', { eagerness: 'conservative' });
```

## Loading prerendered error pages (5.6.0)

Adapter code may pass `prerenderedErrorPageFetch` to `app.render()` to load
prerendered 404 and 500 pages without Astro's default recursive HTTP request.
When omitted, Astro fetches `/404` or `/500` normally. The callback receives a
URL and returns an appropriately status-coded `Response`.

## Prerender collisions and route patterns (5.14.0)

Astro warns when multiple dynamic routes prerender the same pathname and names
the routes and path involved. Make the condition fatal in CI with:

```js
export default defineConfig({
  experimental: { failOnPrerenderConflict: true },
});
```

The `getStaticPaths()` context also exposes `routePattern`, the original
dynamic segment pattern, for localization and other parameter helpers:

```astro
---
export function getStaticPaths({ routePattern }) {
  console.log(routePattern); // [...locale]/[files]/[slug]
  return [{ params: { locale: 'en', files: 'docs', slug: 'intro' } }];
}
---
```

## Queued rendering (6.0.0)

Astro 6 can opt into two-pass rendering with the nested experimental flag:

```js
export default defineConfig({
  experimental: { queuedRendering: { enabled: true } },
});
```

Queued rendering is stable and enabled automatically in Astro 7 (7.0.0).

## Response caching (6.0.0)

Astro 6 configures a provider under `experimental.cache`. A page calls
`Astro.cache.set()` and an endpoint calls `context.cache.set()` with `maxAge`,
`swr`, and `tags`. Supplying a live content entry instead records a dependency
that invalidates the response when the entry changes. The built-in memory
provider is primarily appropriate for the Node adapter.

Astro 7 moves configuration to top-level `cache` and adds `routeRules` plus
`cache.invalidate()` by tag or path (7.0.0):

```js
import { defineConfig, memoryCache } from 'astro/config';

export default defineConfig({
  cache: { provider: memoryCache() },
  routeRules: {
    '/blog/[...path]': { maxAge: 300, swr: 60 },
  },
});
```

Netlify and Vercel expose manually configured experimental CDN providers,
`cacheNetlify()` and `cacheVercel()`, which can serve hits at the edge without
invoking the server function. Cloudflare's `cacheCloudflare()` is private beta.

## i18n fallback routes (6.1.0)

Routes passed to `astro:routes:resolved` expose `fallbackRoutes`, including the
extra locale routes generated for `fallbackType: 'rewrite'`. Integrations can
enumerate their pathnames; the sitemap integration includes them automatically.

## Advanced routing (6.3.0)

Advanced routing exposes the request pipeline as composable fetch handlers.
`astro/fetch` and `astro/hono` provide rendering, trailing-slash, redirect,
session, Action, middleware, page, cache, and i18n stages. Use this to proxy
selected traffic or control stage ordering:

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

Hono exposes equivalent individual middleware:

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

In Astro 7, place the standard handler in `src/fetch.ts`; without that file,
the normal request pipeline remains active (7.0.0).

## Incremental static builds (7.0.1-7.2.4)

Enable `experimental.incrementalBuild` and return a `cacheKey` for each dynamic
route from `getStaticPaths()`. Astro skips a page when both its module
dependencies and cache key are unchanged. Preserve `node_modules/.astro/`
between CI builds so skipped output can be restored.

```js
return posts.map((post) => ({
  params: { slug: post.slug },
  props: { post },
  cacheKey: post.digest,
}));
```

Content entries may expose a loader-provided `digest` for this purpose.
Out-of-process adapter prerenderers may return a `PrerenderResult` with
`{ response, metadata }` so content and image dependencies participate. A bare
`Response` is still valid.

## Pagination URL formatting (7.0.1-7.2.4)

`paginate()` accepts `format(url)` to replace each generated URL, for example
to append `.html` for a host that requires suffixes:

```js
return paginate(items, {
  pageSize: 10,
  format: (url) => `${url}.html`,
});
```
