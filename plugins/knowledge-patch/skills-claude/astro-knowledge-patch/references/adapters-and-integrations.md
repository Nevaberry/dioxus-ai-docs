# Adapters and integrations

## React streaming opt-out (5.2.0)

The React integration can disable streaming for incompatible libraries,
including many CSS-in-JS libraries, through `experimentalDisableStreaming`.

```js
import react from '@astrojs/react';

export default defineConfig({
  integrations: [react({ experimentalDisableStreaming: true })],
});
```

## Netlify server bundle files (5.3.0)

`includeFiles` adds paths or globs missed by dependency tracing;
`excludeFiles` removes unwanted files from the Netlify server bundle.

```js
export default defineConfig({
  adapter: netlify({
    includeFiles: ['src/locales/**/*.po'],
    excludeFiles: ['node_modules/big-package/chonky-file.bin'],
  }),
});
```

## Vercel ISR exclusions (5.4.0)

`isr.exclude` accepts regular expressions as well as literal and dynamic route
strings, allowing an entire route family to bypass ISR.

```js
export default defineConfig({
  output: 'server',
  adapter: vercel({
    isr: { exclude: ['/preview', '/auth/[page]', /^\/api\/.+/] },
  }),
});
```

## Adapter feature-support logs (5.9.0)

An object-form entry in `supportedAstroFeatures` may set
`suppress: 'default'` to hide Astro's generated diagnostic or
`suppress: 'all'` to hide both the default and adapter message. This lets an
adapter replace generic unsupported-feature output without contradictory logs.

```js
setAdapter({
  name: 'my-astro-integration',
  supportedAstroFeatures: {
    sharpImageService: {
      support: 'limited',
      message: 'Sharp is available only for prerendered pages.',
      suppress: 'default',
    },
  },
});
```

## Custom Cloudflare Workers entrypoint (5.10.0)

`workerEntryPoint` replaces the Cloudflare adapter's generated entrypoint so a
worker can export Durable Objects, queues, cron handlers, or other bindings.
Configure its path and named exports. The module must export
`createExports(manifest)`, return the default worker plus named bindings, and
send normal requests through Astro's `handle()`.

```js
export default defineConfig({
  adapter: cloudflare({
    workerEntryPoint: {
      path: 'src/worker.ts',
      namedExports: ['MyDurableObject'],
    },
  }),
});
```

```ts
import type { SSRManifest } from 'astro';
import { App } from 'astro/app';
import { handle } from '@astrojs/cloudflare/handler';
import { DurableObject } from 'cloudflare:workers';

class MyDurableObject extends DurableObject<Env> {}

export function createExports(manifest: SSRManifest) {
  const app = new App(manifest);
  return {
    default: {
      fetch(request: Request, env: Env, ctx: ExecutionContext) {
        return handle(manifest, app, request, env, ctx);
      },
    },
    MyDurableObject,
  };
}
```

## Node HTML streaming opt-out (5.11.0)

The Node adapter streams runtime HTML by default. Hosts whose CDN caching
requires complete responses can disable it:

```js
export default defineConfig({
  adapter: node({
    mode: 'standalone',
    experimentalDisableStreaming: true,
  }),
});
```

## Netlify primitives in development (5.12.0)

The Netlify adapter embeds its Vite plugin, so `astro dev` supplies local Image
CDN and Blobs services, applies Netlify redirects, rewrites, and headers,
exposes Edge Context to runtime pages, and can load variables from a linked
site. Astro images use the local Image CDN and sessions use local Blobs by
default; Netlify CLI is not required.

`devFeatures.images` defaults to `true`; `environmentVariables` defaults to
`false`. Both are configurable:

```js
export default defineConfig({
  adapter: netlify({
    devFeatures: {
      environmentVariables: true,
      images: false,
    },
  }),
});
```

## Sitemap integration controls

`customSitemaps` adds externally generated sitemap URLs to Astro's generated
`sitemap-index.xml`, useful when frameworks share a domain (5.13.0):

```js
sitemap({
  customSitemaps: [
    'https://example.com/blog/sitemap.xml',
    'https://example.com/helpcenter/sitemap.xml',
  ],
})
```

`namespaces` independently enables or disables the `news`, `xhtml`, `image`,
and `video` XML namespaces. All remain enabled by default (5.14.0):

```js
sitemap({ namespaces: { video: false } })
```

The integration also includes locale fallback routes exposed to integration
hooks (6.1.0).

## Alternate Node error-page host (5.13.0)

`@astrojs/node` 9.4 adds `experimentalErrorPageHost`, which fetches
prerendered custom error pages through an internal host rather than the
incoming public host. This helps reverse-proxy and container deployments.

```js
export default defineConfig({
  adapter: node({ experimentalErrorPageHost: 'http://localhost:4321' }),
});
```

## Cloudflare storage during development (5.13.0)

The Cloudflare adapter supplies local Workers KV during `astro dev`, including
as the transparent store for Astro sessions. Development can instead connect
to the remote production namespace when real data is needed.

## Async Svelte server rendering (5.14.0)

The Svelte integration supports Svelte 5.36's experimental asynchronous SSR,
not only client-rendered components. Enable the compiler option before using
`await` in scripts, `$derived` expressions, or markup.

```js
export default {
  compilerOptions: { experimental: { async: true } },
};
```

## Deployment skew protection (5.15.0)

Netlify automatically adds its deployment ID to Astro-managed assets and
internal requests from Actions, View Transitions, Server Islands, and Prefetch.
Custom requests can join the same deployment by forwarding
`import.meta.env.DEPLOY_ID` as `x-deploy-id`.

```ts
await fetch('/api/endpoint', {
  headers: { 'x-deploy-id': import.meta.env.DEPLOY_ID },
});
```

An `AstroAdapter` can implement the mechanism with
`client.internalFetchHeaders()` and `client.assetQueryParams`. The former adds
headers to internal requests; the latter appends parameters to asset URLs.

```ts
const deployId = process.env.DEPLOY_ID;

setAdapter({
  name: 'example-adapter',
  serverEntrypoint: 'example-adapter/ssr.js',
  client: {
    internalFetchHeaders: () => deployId ? { 'x-deploy-id': deployId } : {},
    assetQueryParams: deployId
      ? new URLSearchParams({ deployId })
      : undefined,
  },
});
```

The Vercel adapter uses these hooks when
`VERCEL_SKEW_PROTECTION_ENABLED` is on, extending protection to the same Astro
client systems.

## Cloudflare scaffolding (5.15.0)

Adding the Cloudflare integration with the Astro CLI creates `wrangler.jsonc`
automatically.

## Production runtimes during development (6.0.0)

Astro 6's Vite Environment API pipeline allows adapters to use their target
runtime during both development and build. Cloudflare now runs `workerd`
during development, prerendering, and production; exposes local KV, D1, R2,
and Durable Object bindings through `cloudflare:workers`; and removes the need
for `Astro.locals.runtime` workarounds.

## Adapter preview host allowlists (6.2.0)

Adapter preview entrypoints receive `allowedHosts` on their options object and
can enforce the project's existing `server.allowedHosts` policy.

## Cloudflare advanced-routing helpers (6.4.0)

`@astrojs/cloudflare/fetch` exports `cf()`, which adds `SESSION` KV injection,
`ASSETS` serving, `locals.cfContext`, client IP handling, `waitUntil`, and
prerendered error pages. Call it first and return an asset response before
continuing through Astro:

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

Hono applications use the middleware form from its separate entrypoint:

```ts
import { cf } from '@astrojs/cloudflare/hono';

app.use(cf());
```

## Platform cache providers (7.0.0)

Astro 7 offers manually configured experimental CDN cache providers that can
serve hits without invoking the server function: `cacheNetlify()` from
`@astrojs/netlify/cache`, `cacheVercel()` from `@astrojs/vercel/cache`, and the
private-beta `cacheCloudflare()` from `@astrojs/cloudflare/cache`.
