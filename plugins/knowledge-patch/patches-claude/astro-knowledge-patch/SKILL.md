---
name: astro-knowledge-patch
description: Astro
version: "7.0.0"
license: MIT
metadata:
  author: Nevaberry
---


# Astro Knowledge Patch

Use this skill before creating, upgrading, or debugging an Astro project. Check
the breaking changes first, then open the reference matching the task.

## Index

| Reference | Topics |
|---|---|
| [Upgrading and breaking changes](references/upgrading-and-breaking-changes.md) | Runtime and dependency baselines, promoted flags, changed defaults, removed APIs |
| [Routing, rendering, and caching](references/routing-rendering-and-caching.md) | Server islands, redirects, endpoints, prerendering, advanced routing, response caching |
| [Content, data, and Actions](references/content-data-and-actions.md) | Content loaders, live collections, generated schemas, Astro DB, Actions, incremental content |
| [Markdown and MDX](references/markdown-and-mdx.md) | TOML, remote images, highlighting, heading IDs, SmartyPants, unified and Sätteri |
| [Images, fonts, and styles](references/images-fonts-and-styles.md) | Responsive images, Sharp, SVG components and optimization, Fonts API |
| [Security, sessions, and environment](references/security-sessions-and-environment.md) | Typed environment variables, CSP, sessions, cookies |
| [Adapters and integrations](references/adapters-and-integrations.md) | Netlify, Node, Cloudflare, Vercel, React, Svelte, sitemap, Adapter API |
| [Configuration, tooling, and APIs](references/configuration-tooling-and-apis.md) | Typed config, programmatic build, host allowlists, logging, background servers |
| [Starlight](references/starlight.md) | Sidebar generation, locale fallback links, CJK spacing |

## Breaking changes first

### Astro 7 project checks

- Markdown and MDX use Sätteri by default with GFM enabled. Select `unified()`
  explicitly if the project depends on remark or rehype plugins.
- Queued rendering is stable and automatic. Remove
  `experimental.queuedRendering`.
- Move `cache`, `routeRules`, and `logger` out of `experimental`.
- Replace `--experimentalJson` with `--json`.
- Put a custom standard-pipeline handler at `src/fetch.ts`; without that file,
  Astro uses the normal request pipeline.

### Astro 6 project checks

- Use Node.js 22 or later.
- Align pinned dependencies with Vite 7, Shiki 4, and Zod 4. Astro 6.1 warns
  when top-level Vite 8 is installed.
- Import Zod from `astro/zod`, not `astro:content`.
- Move `experimental.csp` to `security.csp`.
- Move `experimental.fonts` to top-level `fonts`.
- Replace `experimental.svgo` with `experimental.svgOptimizer` and an
  optimizer implementation such as `svgoOptimizer()`.
- Remove `experimental.rustCompiler` when moving to the Astro 7 toolchain,
  where the Rust compiler is the only compiler.

### Removed, deprecated, or superseded forms

| Avoid | Use |
|---|---|
| `output: 'hybrid'` | Default static output and `prerender = false` on runtime routes |
| `experimental.session` | Stable top-level `session` configuration |
| `experimental.serializeConfig` | Stable `astro:config/client` and `astro:config/server` |
| `experimental.responsiveImages` | Stable `image.responsiveStyles` and `image.layout` |
| `experimental.csp` | `security.csp` |
| `experimental.fonts` | Top-level `fonts` |
| `experimental.svgo` | `experimental.svgOptimizer` |
| `experimental.rawEnvValues` | `experimental.staticImportMetaEnv` |
| top-level Markdown plugin options | `markdown.processor: unified({ ... })` |
| `AstroCookies.consume(cookies)` | `cookies.consume()` |
| SVG `title`, `size`, or `mode` props | `aria-label`, explicit dimensions, inline SVG |
| React `experimental_withState` helpers | Stable helpers from `@astrojs/react/actions` |

## Markdown processor quick reference

Use unified when existing plugins must keep running:

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

Use Sätteri for its Rust pipeline and native features:

```js
import { defineConfig } from 'astro/config';
import { satteri } from '@astrojs/markdown-satteri';

export default defineConfig({
  markdown: {
    processor: satteri({ features: { directive: true } }),
  },
});
```

Sätteri does not execute remark or rehype plugins.

## Route caching quick reference

Configure the provider and route policies at the top level:

```js
import { defineConfig, memoryCache } from 'astro/config';

export default defineConfig({
  cache: { provider: memoryCache() },
  routeRules: {
    '/blog/[...path]': { maxAge: 300, swr: 60 },
  },
});
```

Set a page policy with `Astro.cache.set()` and an endpoint policy with
`context.cache.set()`. Use `maxAge`, `swr`, and `tags`; invalidate later by tag
or path. Passing a live content entry to `set()` records an automatic
invalidation dependency. The memory provider mainly suits the Node adapter;
platform adapters also expose experimental CDN providers.

## Advanced routing quick reference

Compose the request pipeline only when the application needs a proxy or
explicit stage ordering:

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

`astro/fetch` and `astro/hono` expose rendering, redirect, session, Action,
middleware, page, cache, and i18n stages. Cloudflare handlers should also apply
the adapter's `cf()` helper for bindings, assets, context, and error pages.

## Live collections quick reference

Define live collections in `src/live.config.ts`. They require an on-demand
adapter and a custom loader with `loadCollection` and `loadEntry`:

```ts
import { defineLiveCollection } from 'astro:content';
import { apiLoader } from './loaders/api-loader';

const products = defineLiveCollection({
  loader: apiLoader({ endpoint: process.env.API_URL }),
});

export const collections = { products };
```

Query with `getLiveCollection()` or `getLiveEntry()` and inspect the returned
`error`. Live collections are not persisted by the Content Layer and do not
support runtime MDX or image optimization. `render(entry)` requires a loader-
supplied `rendered` property.

## Fonts quick reference

Configure fonts at the top level. Provider assets are downloaded and served
locally:

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

Use `<Font>` to apply or preload a family. Read generated URLs from `fontData`
in `astro:assets`. Repeat a matching family declaration to merge selected
non-Cartesian weight and style combinations.

## Security and session quick reference

Enable stable CSP with:

```js
import { defineConfig } from 'astro/config';

export default defineConfig({
  security: { csp: true },
});
```

Astro hashes managed inline scripts and styles. Runtime pages use response
headers; prerendered pages need adapter static-header support for directives a
meta element cannot represent.

Import declared secrets from `astro:env/server`. Prefer `astro:env` to direct
`import.meta.env` access when validation, client/server separation, or bundle
secrecy matters.

Sessions are available through `Astro.session` or context `session`. Type known
keys by augmenting `App.SessionData`. For cookie-less clients, call
`session.load(id)` and return `session.sessionId`; set `session: false` when the
application does not use sessions.

## Image and SVG checks

- Configure responsive layouts through `image.layout` and
  `image.responsiveStyles`; component values override global defaults.
- `priority` applies eager loading, synchronous decoding, and high fetch
  priority.
- Remote image redirects stop after ten hops, and every hop must be allowlisted.
- SVG rasterization is disabled by default. Enable `dangerouslyProcessSVG`
  only for trusted sources.
- Imported SVG components are inline. Use `SvgComponent` from `astro/types`
  when passing them through typed APIs.
- Use `experimental.svgOptimizer` with `svgoOptimizer()` for build-time SVG
  component optimization.

## Tooling checks

- Protect dev and preview servers with `server.allowedHosts` or
  `--allowed-hosts`.
- Use `mergeConfig()` and `validateConfig()` for integration-style
  programmatic configuration.
- `build(config, options)` accepts `devOutput` and `teardownCompiler`.
- `astro dev --background` and `astro preview --background` detach after
  readiness; manage them with `status`, `logs`, and `stop` subcommands.
- Use `astro dev --ignore-lock` only for an unmanaged parallel foreground
  server; it cannot combine with background or forced mode.
- Configure top-level `logger` with JSON, console, composed, or custom
  entrypoint handlers.
