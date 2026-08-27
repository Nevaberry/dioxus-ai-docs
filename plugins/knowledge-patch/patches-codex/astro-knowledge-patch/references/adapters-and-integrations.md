# Adapters and integrations

## React and Svelte

Since 5.2.0, React integration option `experimentalDisableStreaming: true` disables streaming for incompatible libraries such as many CSS-in-JS systems.

Astro 5.14.0 supports Svelte 5.36's experimental async rendering during SSR as well as client rendering. Enable Svelte compiler `experimental.async` before using `await` in scripts, `$derived`, or markup.

The same batch stabilizes React Action state helpers: import `withState()` and `getActionState()` from `@astrojs/react/actions` without `experimental_` prefixes. `withState()` adapts an Action to `useActionState()`; `getActionState(context)` reads the preceding state in its handler.

## Netlify

Since 5.3.0, adapter `includeFiles` and `excludeFiles` accept paths or globs to add files missed by tracing or remove unwanted files from the server bundle.

Since 5.12.0, the adapter embeds Netlify's Vite plugin, so `astro dev` supplies local Image CDN and Blobs, applies redirects/rewrites/headers, exposes Edge Context on on-demand pages, and may load variables from a linked site without Netlify CLI. `devFeatures.images` defaults to `true`; `devFeatures.environmentVariables` defaults to `false`.

Since 5.15.0, Netlify automatically attaches its deployment ID to Astro-managed asset requests and internal fetches made by Actions, View Transitions, Server Islands, and Prefetch. Custom fetches can join skew protection by forwarding `import.meta.env.DEPLOY_ID` as `x-deploy-id`.

## Vercel

Since 5.4.0, `isr.exclude` accepts regular expressions as well as literal and dynamic route strings, so route families can bypass ISR.

The adapter uses the client hooks introduced in 5.15.0 when `VERCEL_SKEW_PROTECTION_ENABLED` is active, extending skew protection across Actions, View Transitions, Server Islands, and Prefetch.

## Node

Since 5.11.0, `experimentalStaticHeaders: true` lets prerendered pages receive real CSP response headers, including directives unavailable to a meta element. The Adapter API exposes the same feature for custom adapters.

Also since 5.11.0, `experimentalDisableStreaming: true` disables HTML streaming for on-demand pages when a hosting cache requires complete responses.

`@astrojs/node` 9.4, noted in 5.13.0, adds `experimentalErrorPageHost` to fetch prerendered custom error pages through an internal or alternate host rather than the incoming public host.

## Cloudflare

Since 5.6.0, `astro:env/server` works during global module initialization and experimental sessions automatically use a `SESSION` KV binding. Since 5.13.0, local `astro dev` supplies Workers KV for sessions and may connect to the remote namespace.

The custom `workerEntryPoint` option added in 5.10.0 supports Durable Objects, queues, cron handlers, and other exports. Configure its module path and `namedExports`; the module exports `createExports(manifest)`, returns default worker handlers plus named bindings, and passes normal requests through the adapter's `handle()`.

Adding the Cloudflare integration through the Astro CLI creates `wrangler.jsonc` since 5.15.0.

Astro 6.0.0 uses the target runtime throughout development and build: Cloudflare runs workerd for development, prerendering, and production, exposes local KV, D1, R2, and Durable Objects through `cloudflare:workers`, and removes `Astro.locals.runtime` workarounds.

In 6.4.0, `cf()` helpers support advanced routing by injecting `SESSION`, serving `ASSETS`, setting `locals.cfContext`, handling client IP and `waitUntil`, and serving prerendered errors. Use `@astrojs/cloudflare/fetch` with `FetchState` or the Hono middleware entrypoint.

## Sitemap

Since 5.13.0, `customSitemaps` adds external sitemap URLs to the generated `sitemap-index.xml`, useful when multiple frameworks serve one domain.

Since 5.14.0, `namespaces` independently controls `news`, `xhtml`, `image`, and `video`; all remain enabled by default. Since 6.1.0, generated i18n rewrite fallback routes are included automatically.

## Adapter API

Since 5.6.0, adapter authors can pass `prerenderedErrorPageFetch` to `app.render()` to load prerendered 404/500 pages without the default recursive HTTP fetch. The callback receives the target URL and returns a `Response`; omission preserves normal `/404` or `/500` fetching.

Since 5.9.0, an object in `supportedAstroFeatures` may use `suppress: 'default'` to hide only Astro's generated diagnostic or `suppress: 'all'` to hide both generated and adapter-provided messages.

Since 5.15.0, `AstroAdapter.client.internalFetchHeaders()` adds headers to Astro internal fetches and `client.assetQueryParams` appends asset URL parameters, enabling deployment-wide features such as skew protection.

Since 6.2.0, adapter preview entrypoints receive `allowedHosts` so their preview servers can enforce the project's `server.allowedHosts` configuration.

Astro 7.0.0 adds experimental CDN cache providers in adapter packages: `cacheNetlify()`, `cacheVercel()`, and private-beta `cacheCloudflare()` can serve cached routes at the edge without invoking a server function.
