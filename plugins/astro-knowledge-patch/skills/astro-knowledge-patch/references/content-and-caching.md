# Content Collections & Route Caching

## Live Collections (6.0)

Real-time content collections that update without rebuilds. New APIs from `astro:content`:

### Defining a Live Collection

```ts
// src/content.config.ts
import { defineLiveCollection } from 'astro:content';
import { myLoader } from './loader';

const products = defineLiveCollection({
  loader: myLoader({ apiKey: process.env.API_KEY }),
});
export const collections = { products };
```

### Querying Live Entries

```astro
---
import { getLiveEntry } from 'astro:content';
const { entry, error } = await getLiveEntry('products', Astro.params.id);
if (error) return Astro.redirect('/404');
---
<h1>{entry.data.title}</h1>
```

## `retainBody: false` for `glob()` Loader (5.17)

Reduces data store size for large content collections by omitting raw file body from `entry.body`:

```ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog', retainBody: false }),
});
```

Rendered HTML remains available via `entry.rendered.html`. Defaults to `true` for backwards compatibility.

## Route Caching (6.0, experimental)

Platform-agnostic SSR response caching with `Astro.cache`.

### Configuration

```js
import { defineConfig, memoryCache } from 'astro/config';
export default defineConfig({
  experimental: {
    cache: { provider: memoryCache() },
  },
});
```

### Usage in Pages

```astro
---
Astro.cache.set({
  maxAge: 120,
  swr: 60, // stale-while-revalidate
  tags: ['home'],
});
---
```

### Auto-invalidation with Live Collections

```ts
const product = await getEntry('products', Astro.params.slug);
Astro.cache.set(product); // invalidates when product changes
```

### API Routes

In API routes, use `context.cache` instead of `Astro.cache`:

```ts
export async function GET(context) {
  context.cache.set({ maxAge: 300 });
  // ...
}
```
