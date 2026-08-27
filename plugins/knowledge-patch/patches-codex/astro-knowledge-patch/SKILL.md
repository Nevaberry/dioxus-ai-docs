---
name: astro-knowledge-patch
description: Astro
version: "7.0.0"
license: MIT
metadata:
  author: Nevaberry
---


# Astro Knowledge Patch

Use this skill when creating, upgrading, integrating, or debugging an Astro project. Check the breaking changes first, then open the topic reference that matches the task. For older projects, keep the version-qualified transition notes in mind instead of applying the newest form blindly.

## Reference index

| Reference | Topics |
|---|---|
| [Upgrading and breaking changes](references/upgrading-and-breaking-changes.md) | Runtime requirements, toolchain changes, promoted flags, removed APIs, migration checks |
| [Routing, rendering, and caching](references/routing-rendering-and-caching.md) | Server islands, redirects, endpoints, prerendering, advanced routing, queued rendering, route caching |
| [Content, data, and Actions](references/content-data-and-actions.md) | Build-time and live collections, loaders, schemas, Astro DB, Action types, incremental content builds |
| [Markdown and MDX](references/markdown-and-mdx.md) | Processors, Sätteri, unified, TOML, highlighting, heading IDs, SmartyPants |
| [Images, fonts, and styles](references/images-fonts-and-styles.md) | Responsive images, Sharp, SVG components and optimization, Fonts API |
| [Security, sessions, and environment](references/security-sessions-and-environment.md) | CSP, typed environment variables, sessions, cookies |
| [Adapters and integrations](references/adapters-and-integrations.md) | Netlify, Node, Cloudflare, Vercel, React, Svelte, sitemap, Adapter API |
| [Configuration, tooling, and APIs](references/configuration-tooling-and-apis.md) | Typed config, programmatic build, host allowlists, compiler, logging, background servers |
| [Starlight](references/starlight.md) | Sidebar generation, default-locale links, CJK spacing |

## Breaking changes first

### Astro 7 checks

- Markdown and MDX use Sätteri by default with GFM enabled. Select `unified()` explicitly if the project depends on remark or rehype plugins.
- Queued rendering is stable and automatic. Remove `experimental.queuedRendering`.
- Move `cache` and `routeRules` out of `experimental`.
- Move `logger` out of `experimental` and replace `--experimentalJson` with `--json`.
- Put a custom standard advanced-routing handler at `src/fetch.ts`; without that file Astro uses the normal pipeline.

### Astro 6 checks

- Use Node.js 22 or later and align pinned packages with Vite 7, Shiki 4, and Zod 4.
- Import Zod from `astro/zod`, not `astro:content`.
- Move `experimental.csp` to `security.csp`.
- Move `experimental.fonts` to top-level `fonts`.
- Replace `experimental.svgo` with `experimental.svgOptimizer` and an optimizer implementation.
- Vite 8 belongs to the Astro 7 toolchain; keep Astro 6 projects on Vite 7.

### Removed and superseded forms

| Avoid | Use |
|---|---|
| `output: 'hybrid'` | Default static output plus `prerender = false` on runtime routes |
| Top-level Markdown plugin options | `markdown.processor: unified({ ... })` |
| `AstroCookies.consume(cookies)` | `cookies.consume()` |
| SVG `title`, `size`, or `mode` props | `aria-label`, explicit dimensions, and inline SVG behavior |
| `experimental.serializeConfig` | Stable `astro:config/client` and `astro:config/server` |
| `experimental.session` | Stable top-level `session` configuration |
| `experimental.responsiveImages` | Stable `image.responsiveStyles` and `image.layout` |
| `experimental.rawEnvValues` | Vite-aligned static `import.meta.env` behavior |
| `experimental.svgo` | `experimental.svgOptimizer: svgoOptimizer(...)` |

## Markdown processor quick reference

Keep unified when existing plugins must run:

```js
import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import remarkToc from 'remark-toc';

export default defineConfig({
  markdown: {
    processor: unified({ remarkPlugins: [remarkToc] }),
  },
});
```

Use Sätteri for its Rust pipeline and native feature flags:

```js
import { satteri } from '@astrojs/markdown-satteri';

export default {
  markdown: {
    processor: satteri({ features: { directive: true } }),
  },
};
```

Sätteri does not execute remark or rehype plugins.

## Route caching quick reference

Configure the provider and route rules at the top level:

```js
import { defineConfig, memoryCache } from 'astro/config';

export default defineConfig({
  cache: { provider: memoryCache() },
  routeRules: {
    '/blog/[...path]': { maxAge: 300, swr: 60 },
  },
});
```

Set a page policy with `Astro.cache.set()` and an endpoint policy with `context.cache.set()`. Use `maxAge`, `swr`, and `tags`; invalidate by tag or path. Passing a live content entry records an automatic invalidation dependency. The in-memory provider mainly suits the Node adapter; platform CDN providers can serve hits without invoking the server function.

## Advanced routing quick reference

Compose the request pipeline only when an application needs a proxy or explicit stage ordering:

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
  loader: apiLoader({ endpoint: process.env.API_URL }),
});

export const collections = { products };
```

Query with `getLiveCollection()` or `getLiveEntry()` and inspect the returned `error`. Live collections do not persist through the Content Layer and do not support runtime MDX or image optimization.

## Fonts quick reference

Configure fonts at the top level; provider assets are downloaded and served locally:

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

Use `<Font>` to apply or preload a configured family. Read generated URLs from `fontData` in `astro:assets`. Repeat a matching family declaration to merge selected non-Cartesian weight and style combinations.

## Security and session quick reference

Enable stable CSP with `security: { csp: true }`. Astro hashes managed inline scripts and styles. On-demand pages use response headers; prerendered pages need adapter static-header support for directives that cannot be represented in a meta element.

Import declared secrets from `astro:env/server`. Prefer `astro:env` over direct `import.meta.env` access when validation, client/server separation, or bundle secrecy matters.

Sessions are available through `Astro.session` or context `session`. Type known keys by augmenting `App.SessionData`. For cookie-less clients, load an explicit ID with `session.load(id)` and return `session.sessionId`; set `session: false` when an SSR application does not use sessions.

## Image and SVG checks

- Configure responsive layouts with `image.layout` and `image.responsiveStyles`; component values override global defaults.
- `priority` selects eager loading, synchronous decoding, and high fetch priority.
- Remote image redirects are limited to ten hops, and every hop must remain allowlisted.
- SVG rasterization is disabled by default; enable `dangerouslyProcessSVG` only for trusted sources.
- Imported SVG components are inline. Use `SvgComponent` from `astro/types` when passing them through typed APIs.
- Use `experimental.svgOptimizer` with `svgoOptimizer()` for build-time SVG component optimization.

## Tooling quick reference

- `server.allowedHosts` and `--allowed-hosts` protect dev and preview servers from untrusted Host headers.
- `mergeConfig()` and `validateConfig()` support integration-style programmatic configuration.
- `build(config, options)` accepts `devOutput` and `teardownCompiler`.
- `astro dev --background` and `astro preview --background` detach after readiness; manage them with their `status`, `logs`, and `stop` subcommands.
- Use `astro dev --ignore-lock` only for an untracked parallel foreground server.
- Configure top-level `logger` with `logHandlers.json()`, `console()`, `compose()`, or a custom entrypoint.
