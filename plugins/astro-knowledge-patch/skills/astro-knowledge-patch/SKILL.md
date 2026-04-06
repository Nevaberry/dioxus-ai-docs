---
name: astro-knowledge-patch
description: "Astro changes since training cutoff (latest: 6.0) — Fonts API, live collections, CSP, route caching, ClientRouter, Zod 4/Vite 7/Shiki 4. Load before working with Astro."
version: "6.0"
license: MIT
metadata:
  author: Nevaberry
---

# Astro Knowledge Patch (5.16 – 6.0)

Covers Astro 5.16 through 6.0 (December 2025 – March 2026). Claude Opus 4.6 knows Astro through 4.x. It is **unaware** of the features below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Breaking changes | [references/breaking-changes.md](references/breaking-changes.md) | Node 22+, removed APIs, Zod 4, Vite 7, Shiki 4 |
| Content & caching | [references/content-and-caching.md](references/content-and-caching.md) | Live collections, `retainBody`, route caching (`Astro.cache`) |
| Fonts & assets | [references/fonts-and-assets.md](references/fonts-and-assets.md) | Built-in Fonts API, SVGO optimization, image `background` prop |
| Security (CSP) | [references/security.md](references/security.md) | `security.csp` config, auto-generated hashes, directives |

---

## Breaking Changes (6.0)

| Change | Detail |
|---|---|
| Node.js minimum | **22+** (dropped 18 & 20) |
| Removed APIs | `Astro.glob()`, `emitESMImage()`, `<ViewTransitions />` (use `<ClientRouter />`) |
| Content collections | Legacy content collections removed |
| Zod | Upgraded to **Zod 4** (Zod 3 no longer supported) |
| i18n | `i18n.redirectToDefaultLocale` default behavior changed |
| Dependencies | **Vite 7**, **Shiki 4** |

## Built-in Fonts API (6.0)

Configure fonts in `astro.config` with automatic self-hosting and optimized fallbacks:

```js
import { defineConfig, fontProviders } from 'astro/config';
export default defineConfig({
  fonts: [
    {
      name: 'Roboto',
      cssVariable: '--font-roboto',
      provider: fontProviders.fontsource(),
    },
  ],
});
```

Use the `<Font />` component from `astro:assets`:

```astro
---
import { Font } from 'astro:assets';
---
<Font cssVariable="--font-roboto" preload />
<style is:global>
  body { font-family: var(--font-roboto); }
</style>
```

Providers: `fontProviders.fontsource()`, `fontProviders.google()`.

## Live Collections (6.0)

Real-time content collections that update without rebuilds:

```ts
// src/content.config.ts
import { defineLiveCollection } from 'astro:content';
import { myLoader } from './loader';

const products = defineLiveCollection({
  loader: myLoader({ apiKey: process.env.API_KEY }),
});
export const collections = { products };
```

```astro
---
import { getLiveEntry } from 'astro:content';
const { entry, error } = await getLiveEntry('products', Astro.params.id);
if (error) return Astro.redirect('/404');
---
<h1>{entry.data.title}</h1>
```

## Content Security Policy (6.0)

Astro auto-generates hashes for inline scripts/styles. Simple mode:

```js
export default defineConfig({
  security: { csp: true },
});
```

Full config at `security.csp` — see [references/security.md](references/security.md).

## Route Caching (6.0, experimental)

Platform-agnostic SSR response caching:

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
  swr: 60, // stale-while-revalidate
  tags: ['home'],
});
---
```

Auto-invalidates with live collections:

```ts
const product = await getEntry('products', Astro.params.slug);
Astro.cache.set(product); // invalidates when product changes
```

In API routes, use `context.cache` instead of `Astro.cache`.

## Image Background Prop (5.17)

Control background color when converting to non-transparent formats:

```astro
<Image src={myImage} format="jpeg" background="white" alt="Product" />
```

Also works with `getImage()`:

```ts
const img = await getImage({ src: heroImage, format: 'jpeg', background: 'white' });
```

## Smaller Additions

### `ActionInputSchema` Utility Type (5.16)

Extract input schema from an action definition:

```ts
import { type ActionInputSchema, defineAction } from 'astro:actions';
import { z } from 'astro/zod';

const myAction = defineAction({
  accept: 'form',
  input: z.object({ email: z.string().email() }),
  handler: ({ email }) => ({ success: true }),
});

type MySchema = ActionInputSchema<typeof myAction>;
```

### Experimental SVGO (5.16)

Automatic SVG optimization in the asset pipeline:

```js
export default defineConfig({
  experimental: {
    svgo: true,
    // or: svgo: { plugins: ['preset-default', { name: 'removeViewBox', active: false }] }
  },
});
```

### `retainBody: false` for `glob()` Loader (5.17)

Reduces data store size by omitting raw body from `entry.body`:

```ts
const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog', retainBody: false }),
});
```

Rendered HTML remains available via `entry.rendered.html`.

### Cloudflare: `cloudflare:workers` (6.0)

Replaces `Astro.locals.runtime` for accessing Cloudflare bindings:

```astro
---
import { env } from "cloudflare:workers";
const kv = env.MY_KV_NAMESPACE;
const visits = await kv.get("visits");
---
```

## Reference Files

| File | Contents |
|---|---|
| [breaking-changes.md](references/breaking-changes.md) | Node 22+, removed APIs, Zod 4, dependency upgrades |
| [content-and-caching.md](references/content-and-caching.md) | Live collections, `retainBody`, route caching |
| [fonts-and-assets.md](references/fonts-and-assets.md) | Fonts API, SVGO, image background prop |
| [security.md](references/security.md) | CSP configuration and directives |
