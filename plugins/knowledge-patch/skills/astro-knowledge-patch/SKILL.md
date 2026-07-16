---
name: astro-knowledge-patch
description: Astro 7.0.0 compatibility. Use for Astro work.
license: MIT
version: "7.0.0"
metadata:
  author: Nevaberry
---

# Astro Knowledge Patch

Use this skill before creating, upgrading, or debugging an Astro project. Start with the breaking-change checks, then open the topic reference that matches the work.

## Index

| Reference | Topics |
|---|---|
| [Upgrading and breaking changes](references/upgrading-and-breaking-changes.md) | Runtime requirements, toolchain changes, promoted flags, removed APIs, migration paths |
| [Routing, rendering, and caching](references/routing-rendering-and-caching.md) | Server islands, redirects, endpoints, prerendering, queued rendering, route caching, advanced routing |
| [Content, data, and Actions](references/content-data-and-actions.md) | Build-time and live collections, loaders, generated schemas, Astro DB, Action input types |
| [Markdown and MDX](references/markdown-and-mdx.md) | Sätteri, unified, TOML frontmatter, highlighting, heading IDs, SmartyPants |
| [Images, fonts, and styles](references/images-fonts-and-styles.md) | Responsive images, Sharp, SVG components and optimization, Fonts API |
| [Security, sessions, and environment](references/security-sessions-and-environment.md) | CSP, typed environment variables, sessions, cookies |
| [Adapters and integrations](references/adapters-and-integrations.md) | Netlify, Node, Cloudflare, Vercel, React, Svelte, sitemap, Adapter API |
| [Configuration, tooling, and APIs](references/configuration-tooling-and-apis.md) | Typed config, programmatic build, host allowlists, compiler, logging, background dev |
| [Starlight](references/starlight.md) | Sidebar generation, default-locale links, CJK spacing |

## Breaking changes first

### Astro 7 project checks

- Markdown and MDX use Sätteri by default, with GFM enabled. Explicitly select `unified()` if the project relies on remark or rehype plugins.
- Queued rendering is stable and automatic. Remove `experimental.queuedRendering`.
- Move `cache` and `routeRules` out of `experimental`.
- Move `logger` out of `experimental` and replace `--experimentalJson` with `--json`.
- Put the standard advanced-routing handler at `src/fetch.ts` only when replacing or composing Astro's normal request pipeline.

### Astro 6 project checks

- Use Node.js 22 or later.
- Align pinned dependencies with Vite 7, Shiki 4, and Zod 4.
- Import Zod from `astro/zod`, not `astro:content`.
- Move `experimental.csp` to `security.csp`.
- Move `experimental.fonts` to top-level `fonts`.
- Replace `experimental.svgo` with `experimental.svgOptimizer`.

### Deprecated or removed forms

| Avoid | Use |
|---|---|
| `hybrid` output | Default `static` output plus per-route `prerender = false` |
| top-level Markdown plugin options | `markdown.processor: unified({ ... })` |
| `AstroCookies.consume(cookies)` | `cookies.consume()` |
| SVG `title`, `size`, or `mode` props | `aria-label`, explicit dimensions, and inline SVG |
| `experimental.serializeConfig` | Stable `astro:config/client` and `astro:config/server` |
| `experimental.session` | Stable top-level `session` configuration |
| `experimental.responsiveImages` | Stable `image.responsiveStyles` and `image.layout` |

## Markdown processor quick reference

Use unified when existing plugins must keep running:

```js
import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import remarkToc from 'remark-toc';

export default defineConfig({
  markdown: {
    processor: unified({
      remarkPlugins: [remarkToc],
    }),
  },
});
```

Use Sätteri for its Rust pipeline and native feature flags:

```js
import { satteri } from '@astrojs/markdown-satteri';

export default defineConfig({
  markdown: {
    processor: satteri({
      features: { directive: true },
    }),
  },
});
```

Sätteri does not execute remark or rehype plugins.

## Route caching quick reference

Configure the provider and route rules at the top level:

```js
import { defineConfig, memoryCache } from 'astro/config';

export default defineConfig({
  cache: { provider: memoryCache() },
  routeRules: {
    '/blog/[...path]': {
      maxAge: 300,
      swr: 60,
    },
  },
});
```

Set a page response policy with `Astro.cache.set()` and an endpoint policy with `context.cache.set()`. Use `maxAge`, `swr`, and `tags`; invalidate later by tag or path. Passing a live content entry to `set()` records an automatic invalidation dependency.

Use `memoryCache()` mainly with the Node adapter. Platform adapters also expose experimental CDN providers that can serve hits without invoking the server function.

## Advanced routing quick reference

Compose the request pipeline only when the application needs a proxy or explicit stage ordering:

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

`astro/fetch` and `astro/hono` expose rendering, redirect, session, Action, middleware, page, cache, and i18n stages. Cloudflare projects should also apply the adapter's `cf()` helper for bindings, assets, context, and error pages.

## Live collections quick reference

Define live collections in `src/live.config.ts`. They require an on-demand adapter and a custom loader with `loadCollection` and `loadEntry`:

```ts
import { defineLiveCollection } from 'astro:content';
import { apiLoader } from './loaders/api-loader';

const products = defineLiveCollection({
  loader: apiLoader({
    endpoint: process.env.API_URL,
  }),
});

export const collections = { products };
```

Query with `getLiveCollection()` or `getLiveEntry()` and inspect the returned `error`. Live collections do not persist through the Content Layer and do not support runtime MDX or image optimization.

## Fonts quick reference

Configure fonts at the top level. Provider assets are downloaded and served locally:

```js
import { defineConfig, fontProviders } from 'astro/config';

export default defineConfig({
  fonts: [{
    provider: fontProviders.google(),
    name: 'Roboto',
    cssVariable: '--font-roboto',
    weights: [400, 700],
  }],
});
```

Use `<Font>` to apply or preload a configured family. Read generated URLs from the `fontData` object in `astro:assets`. Repeat a matching family declaration to merge selected non-Cartesian weight and style combinations.

## Security and session quick reference

Enable stable CSP with:

```js
export default defineConfig({
  security: { csp: true },
});
```

Astro generates hashes for managed inline scripts and styles. On-demand pages use response headers; prerendered pages need adapter static-header support for directives that cannot be represented in a meta element.

Import declared secrets from `astro:env/server`. Prefer `astro:env` declarations over direct `import.meta.env` access when validation, client/server separation, or bundle secrecy matters.

Sessions are available through `Astro.session` or context `session`. Type known keys by augmenting `App.SessionData`. For cookie-less clients, load an explicit ID with `session.load(id)` and return `session.sessionId`.

## Image and SVG checks

- Responsive layouts are configured through `image.layout` and `image.responsiveStyles`; component values override global defaults.
- `priority` applies eager loading, synchronous decoding, and high fetch priority.
- Remote image redirects are limited to ten hops, and every hop must remain allowlisted.
- SVG image rasterization is disabled by default; enable `dangerouslyProcessSVG` only for trusted sources.
- Imported SVG components are inline and stable. Use `SvgComponent` from `astro/types` when passing them through typed APIs.
- Use `experimental.svgOptimizer` with `svgoOptimizer()` for build-time SVG component optimization.

## Tooling quick reference

- `server.allowedHosts` and `--allowed-hosts` protect dev and preview servers from untrusted Host headers.
- `mergeConfig()` and `validateConfig()` support integration-style programmatic configuration.
- `build(config, options)` accepts `devOutput` and `teardownCompiler`.
- `astro dev --background` detaches after readiness; manage it with `astro dev status`, `logs`, and `stop`.
- Configure top-level `logger` with `logHandlers.json()`, `console()`, or `compose()`.
