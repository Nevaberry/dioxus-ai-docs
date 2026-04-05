---
name: astro-knowledge-patch
description: Astro changes since training cutoff (latest: 6.0) — Sessions API, Fonts API, live collections, CSP, route caching, responsive images, SVG components, astro:config, Rust compiler, Cloudflare workerd dev. Load before working with Astro.
license: MIT
metadata:
  author: Nevaberry
  version: "6.0"
---

# Astro 5.0+ Knowledge Patch

Claude's baseline knowledge covers Astro through 4.x. This skill provides features from 5.0 (December 2024) through 6.0 (March 2026).

## Quick Reference

### Sessions API (5.7+)

| Operation | Syntax |
|-----------|--------|
| Get value | `await Astro.session.get('cart')` |
| Set value | `Astro.session.set('cart', items)` |
| Load by ID | `await session.load(sessionId)` |
| In actions | `session` from handler context |
| In API routes | `session` from `APIContext` |
| Type-safe | Extend `App.SessionData` in `src/env.d.ts` |


### Fonts API (6.0)

| Pattern | Example |
|---------|---------|
| Configure | `fonts: [{ name: 'Roboto', cssVariable: '--font-roboto', provider: fontProviders.fontsource() }]` |
| Use in head | `<Font cssVariable="--font-roboto" preload />` |
| Apply style | `font-family: var(--font-roboto)` |
| Providers | `fontProviders.google()`, `.fontsource()`, `.local()`, `.adobe()`, `.bunny()` |
| Font data | `import { fontData } from 'astro:assets'` then `fontData['--font-roboto']` |
| Preload filter | `<Font preload={[{ subset: 'latin', weight: '400' }]} />` |

See `references/fonts-and-assets.md` for local fonts, Tailwind integration, granular config.

### Live Collections (6.0)

| API | Import |
|-----|--------|
| Define | `import { defineLiveCollection } from 'astro:content'` |
| Get entry | `const { entry, error } = await getLiveEntry('products', id)` |
| Get collection | `const { entries, error } = await getLiveCollection('products', filterOpts)` |
| Config file | `src/live.config.ts` |

See `references/content-and-caching.md` for loaders, error handling, route caching.

### Content Security Policy (6.0)

```js
// Simple mode
export default defineConfig({ security: { csp: true } });

// Full config
export default defineConfig({
  security: {
    csp: {
      algorithm: 'SHA-512',
      directives: ["default-src 'self'"],
      scriptDirective: { hashes: ['sha384-hash'], resources: ["'self'"] },
    },
  },
});
```

See `references/security.md` for directives, adapter headers, migration from beta.

### Responsive Images (5.10+)

| Prop | Values |
|------|--------|
| `layout` | `'constrained'`, `'fixed'`, `'full-width'` |
| `priority` | `true` (sets eager loading, high fetchpriority) |
| `fit` | `'cover'`, `'contain'`, `'fill'`, etc. |
| `position` | `'center top'`, `'left bottom'`, etc. |

```js
// Global config
export default defineConfig({
  image: { responsiveStyles: true, layout: 'constrained' },
});
```

### SVG Components (5.7+)

```astro
---
import Logo from './logo.svg';
import type { SvgComponent } from 'astro/types';
---
<Logo width={64} height={64} fill="currentColor" />
```

### `astro:config` Virtual Module (5.7+)

```ts
import { trailingSlash, base } from 'astro:config/client';
import { srcDir } from 'astro:config/server';
```

### Breaking Changes (6.0)

| Change | Detail |
|--------|--------|
| Node.js | **22+** required (18 & 20 dropped) |
| Removed | `Astro.glob()`, `emitESMImage()`, `<ViewTransitions />` (use `<ClientRouter />`), legacy collections |
| Zod | **Zod 4** -- import from `astro/zod` |
| Vite | **7** |
| Shiki | **4** |
| Cloudflare | `cloudflare:workers` replaces `Astro.locals.runtime` |
| Dev server | Uses Vite Environment API -- runs actual production runtime (workerd, etc.) |

### Route Caching (6.0, experimental)

```astro
---
Astro.cache.set({ maxAge: 120, swr: 60, tags: ['home'] });
---
```

```js
// Config
import { defineConfig, memoryCache } from 'astro/config';
export default defineConfig({
  experimental: { cache: { provider: memoryCache() } },
});
```

Auto-invalidates with live collections: `Astro.cache.set(product)`.

### Experimental Features (6.0)

| Feature | Flag | Purpose |
|---------|------|---------|
| Rust compiler | `rustCompiler: true` + `@astrojs/compiler-rs` | Faster, better diagnostics |
| Queued rendering | `queuedRendering: { enabled: true }` | Up to 2x faster rendering |
| Route caching | `cache: { provider: memoryCache() }` | SSR response caching |
| SVGO | `svgo: true` | Automatic SVG optimization |

## Reference Files

| File | Contents |
|------|----------|
| [content-and-caching.md](references/content-and-caching.md) | Live collections, route caching, renderMarkdown, TOML, retainBody |
| [fonts-and-assets.md](references/fonts-and-assets.md) | Fonts API, SVGO, image background, responsive images, SVG components |
| [security.md](references/security.md) | CSP configuration, directives, adapter headers |
| [breaking-changes.md](references/breaking-changes.md) | Node 22+, Zod 4, Vite 7, Shiki 4, removed APIs, dev server refactor |

## Critical Knowledge

### React 19 Actions Integration (5.14+)

```tsx
import { actions } from 'astro:actions';
import { withState } from '@astrojs/react/actions';
import { useActionState } from 'react';

export function Like({ postId }: { postId: string }) {
  const [state, action, pending] = useActionState(
    withState(actions.like),
    0,
  );
  return (
    <form action={action}>
      <input type="hidden" name="postId" value={postId} />
      <button disabled={pending}>{state} likes</button>
    </form>
  );
}
```

Server-side: use `getActionState<number>(ctx)` from `@astrojs/react/actions`.

### Content Loader `renderMarkdown` (5.9+)

```ts
export function myLoader(): Loader {
  return {
    name: 'my-loader',
    async load({ renderMarkdown, store }) {
      const entries = await fetchFromCMS();
      for (const entry of entries) {
        store.set(entry.id, {
          id: entry.id,
          data: entry,
          rendered: await renderMarkdown(entry.content),
        });
      }
    },
  };
}
```

### Cloudflare Workers (6.0)

```astro
---
import { env } from "cloudflare:workers";
const kv = env.MY_KV_NAMESPACE;
const visits = await kv.get("visits");
---
<p>Visits: {visits}</p>
```

Replaces `Astro.locals.runtime`. Works in dev via workerd (real runtime).
