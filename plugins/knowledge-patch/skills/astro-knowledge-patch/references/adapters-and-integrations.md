# Adapters and integrations

## Adapter API

### Error-page loading

Adapter authors can pass `prerenderedErrorPageFetch` to `app.render()` when prerendered `404` and `500` pages must be loaded without Astro's normal recursive HTTP request (`5.6.0`). The callback receives the error-page URL and returns an appropriately status-coded `Response`. When omitted, Astro fetches `/404` or `/500` normally.

The Node adapter's `experimentalErrorPageHost` instead changes the host used for that fetch, which is useful behind a reverse proxy or in a container where an internal address is safer or faster (`5.13.0`).

### Feature-support diagnostics

An object-form entry in `supportedAstroFeatures` can set `suppress: 'default'` to hide Astro's generated support message or `suppress: 'all'` to hide both the generated and adapter-provided messages (`5.9.0`). This lets an adapter replace generic diagnostics without duplicating them.

```js
setAdapter({
  name: 'my-adapter',
  supportedAstroFeatures: {
    sharpImageService: {
      support: 'limited',
      message: 'Sharp is available only for prerendered pages.',
      suppress: 'default',
    },
  },
});
```

### Client fetch and asset hooks

`AstroAdapter.client.internalFetchHeaders()` adds headers to Astro-managed internal fetches, and `client.assetQueryParams` appends query parameters to managed asset URLs (`5.15.0`). These hooks apply consistently to Actions, View Transitions, Server Islands, and Prefetch and can implement deployment skew protection.

```ts
setAdapter({
  name: 'example-adapter',
  serverEntrypoint: 'example-adapter/ssr.js',
  client: {
    internalFetchHeaders: () =>
      deployId ? { 'x-deploy-id': deployId } : {},
    assetQueryParams: deployId
      ? new URLSearchParams({ deployId })
      : undefined,
  },
});
```

### Preview and static-header capabilities

Adapter preview entrypoints receive `allowedHosts` in their options so a custom preview server can enforce `server.allowedHosts` (`6.2.0`).

Adapters can advertise the experimental static-header feature for prerendered CSP response headers. Netlify and Vercel exposed it in `5.10.0`; Node and the custom Adapter API added it in `5.11.0`.

## Netlify

### Bundle contents

`includeFiles` and `excludeFiles` accept file paths or globs for adding files missed by dependency tracing or removing unwanted files from the server bundle (`5.3.0`).

```js
netlify({
  includeFiles: ['src/locales/**/*.po'],
  excludeFiles: ['node_modules/big-package/chonky-file.bin'],
})
```

### Local platform primitives

The adapter embeds Netlify's Vite plugin, so `astro dev` provides local Image CDN and Blobs, applies Netlify redirects, rewrites, and headers, exposes Edge Context to on-demand pages, and can load variables from a linked site (`5.12.0`). Astro images use the local Image CDN and sessions use local Blobs by default; Netlify CLI is not required.

Under `devFeatures`, `devFeatures.images` defaults to `true` and `devFeatures.environmentVariables` defaults to `false`:

```js
netlify({
  devFeatures: {
    environmentVariables: true,
    images: false,
  },
})
```

### Deployment skew protection

Netlify adds the deployment ID automatically to Astro-managed asset requests and internal fetches across Actions, View Transitions, Server Islands, and Prefetch (`5.15.0`). Custom fetches can participate by forwarding `import.meta.env.DEPLOY_ID` as `x-deploy-id`.

## Node

- `experimentalStaticHeaders` emits real CSP headers for prerendered pages, enabling policies that cannot fit in CSP meta elements (`5.11.0`).
- `experimentalDisableStreaming` turns off the adapter's default HTML streaming for hosts whose CDN caching requires a complete response (`5.11.0`).
- `experimentalErrorPageHost` selects an alternate host for loading prerendered custom error pages (`5.13.0`).

```js
node({
  mode: 'standalone',
  experimentalStaticHeaders: true,
  experimentalDisableStreaming: true,
  experimentalErrorPageHost: 'http://localhost:4321',
})
```

## Cloudflare

### Runtime and bindings

The Vite Environment API-based Astro 6 pipeline lets adapters use their target runtime during development. The Cloudflare adapter runs `workerd` during development, prerendering, and production and exposes local KV, D1, R2, and Durable Object bindings through `cloudflare:workers` (`6.0.0`). This replaces `Astro.locals.runtime` workarounds.

Earlier adapter updates made `astro:env/server` usable during module initialization (`5.6.0`), automatically selected a `SESSION` KV binding for sessions (`5.6.0`), and added local KV during `astro dev` with an option to connect to the remote namespace (`5.13.0`). Adding Cloudflare with the Astro CLI scaffolds `wrangler.jsonc` (`5.15.0`).

### Custom Workers entrypoint

`workerEntryPoint` replaces the generated worker entrypoint when a deployment needs Durable Objects, queues, cron handlers, or other named exports (`5.10.0`). Configure a module path and the exported names. That module exports `createExports(manifest)`, returns a default worker plus the named bindings, and forwards ordinary requests to Astro's `handle()`.

```js
cloudflare({
  workerEntryPoint: {
    path: 'src/worker.ts',
    namedExports: ['MyDurableObject'],
  },
})
```

### Advanced-routing helpers

`@astrojs/cloudflare/fetch` and `@astrojs/cloudflare/hono` export `cf()` helpers for advanced routing (`6.4.0`). They inject `SESSION` KV, serve `ASSETS`, populate `locals.cfContext`, handle client IP data and `waitUntil`, and serve prerendered error pages.

In a Fetch handler, call `cf(state, env, ctx)` and return any asset response before continuing through `astro(state)`:

```ts
import { astro, FetchState } from 'astro/fetch';
import { cf } from '@astrojs/cloudflare/fetch';

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const state = new FetchState(request);
    const asset = await cf(state, env, ctx);
    if (asset) return asset;
    return astro(state);
  },
};
```

Hono uses the middleware form from `@astrojs/cloudflare/hono`.

## Vercel

`isr.exclude` accepts regular expressions in addition to literal and dynamic route strings, so route families can bypass ISR (`5.4.0`):

```js
vercel({
  isr: { exclude: ['/preview', '/auth/[page]', /^\/api\/.+/] },
})
```

When `VERCEL_SKEW_PROTECTION_ENABLED` is set, the adapter uses Astro's client header and asset query hooks to extend skew protection to Actions, View Transitions, Server Islands, and Prefetch (`5.15.0`).

## Framework integrations

### React

The React integration's `experimentalDisableStreaming` option supports libraries that cannot consume streamed SSR output, including many CSS-in-JS libraries (`5.2.0`).

Stable `withState()` and `getActionState<T>()` helpers from `@astrojs/react/actions` integrate Astro Actions with React `useActionState()` without the old `experimental_` prefixes (`5.14.0`).

### Svelte

The Svelte integration supports Svelte 5.36's experimental asynchronous rendering during SSR as well as on the client (`5.14.0`). Enable Svelte's `compilerOptions.experimental.async` before using `await` in component scripts, `$derived` expressions, or markup.

## Sitemap

In `@astrojs/sitemap`, `customSitemaps` adds external sitemap URLs to the generated `sitemap-index.xml`, useful when several systems serve one domain (`5.13.0`). The `namespaces` option independently enables or disables the `news`, `xhtml`, `image`, and `video` XML namespaces; all remain enabled by default (`5.14.0`).

When i18n uses `fallbackType: 'rewrite'`, generated `fallbackRoutes` are included in the sitemap automatically (`6.1.0`).
