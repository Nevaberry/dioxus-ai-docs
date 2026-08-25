# Content, data, and Actions

## Controlling `glob()` entry IDs (5.0-guides)

`glob()` derives URL-friendly IDs from filenames. An entry's `slug` field
overrides that generated ID. For collection-wide control, `generateId`
receives the source entry path and can preserve case or apply another mapping:

```ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

const authors = defineCollection({
  loader: glob({
    base: './src/data/authors',
    pattern: '**/*.json',
    generateId: ({ entry }) => entry.replace(/\.json$/, ''),
  }),
});
```

## Single-file collections (5.0-guides)

`file()` turns one JSON or YAML array/object, or the top-level tables of one
TOML file, into entries. Array elements must have unique `id` fields; object
keys become IDs. IDs are never synthesized. A synchronous or asynchronous
`parser` supports formats such as CSV or selects an array nested in JSON:

```ts
import { defineCollection } from 'astro:content';
import { file } from 'astro/loaders';

const dogs = defineCollection({
  loader: file('src/data/pets.json', {
    parser: (text) => JSON.parse(text).dogs,
  }),
});
```

## Collection TypeScript settings (5.0-guides)

Projects extending `astro/tsconfigs/base`, or using no built-in template, must
enable both `strictNullChecks` and `allowJs`. The `strict` and `strictest`
templates already do so.

```json
{
  "extends": "astro/tsconfigs/base",
  "compilerOptions": { "strictNullChecks": true, "allowJs": true }
}
```

## Live collections (5.0-guides)

Live collections fetch on each request, require an on-demand adapter, and are
not persisted by the Content Layer. Export them from `src/live.config.ts` with
`defineLiveCollection()`. Astro supplies no built-in live loader: a custom
loader implements `loadCollection` and `loadEntry`, not the build-time
loader's `load` method.

```ts
import { defineLiveCollection } from 'astro:content';
import { apiLoader } from './loaders/api-loader';

const products = defineLiveCollection({
  loader: apiLoader({ endpoint: process.env.API_URL }),
});
export const collections = { products };
```

An optional Zod schema validates and transforms at runtime and overrides types
supplied by the loader. Live collections do not support runtime MDX or image
optimization.

Query using `getLiveCollection(name, filters)` or `getLiveEntry(name, id)`.
They return `{ entries, error }` and `{ entry, error }`; filters are
loader-specific. `render(entry)` works only when the loader returns a
`rendered` property.

```astro
---
export const prerender = false;
import { getLiveEntry } from 'astro:content';
import { LiveEntryNotFoundError } from 'astro/content/runtime';

const id = Astro.params.id;
if (id === undefined) return Astro.redirect('/404');
const { entry, error } = await getLiveEntry('products', id);
if (error instanceof LiveEntryNotFoundError) Astro.response.status = 404;
---
```

Loaders can return custom errors. Astro's errors are
`LiveEntryNotFoundError`, `LiveCollectionValidationError`,
`LiveCollectionCacheHintError`, and `LiveCollectionError`, imported from
`astro/content/runtime`, so callers can distinguish missing, validation,
cache-hint, network, and other loader failures.

## Generated collection schemas (5.0-guides)

Astro writes `.astro/collections/<name>.schema.json` for each collection. JSON
files can opt in through a relative `$schema`; VS Code can associate the files
with JSON globs using `json.schemas` or YAML globs using `yaml.schemas`.

```json
{
  "$schema": "../../../.astro/collections/authors.schema.json",
  "name": "Armand"
}
```

## Rendering Markdown from custom loaders (5.9.0)

The loader context's `renderMarkdown(content)` uses project Markdown settings
and plugins and returns `{ html, metadata }` in the shape expected by an
entry's `rendered` property. Store that result to enable the standard
`render(entry)` and `<Content />` flow for CMS Markdown:

```ts
async load({ renderMarkdown, store }) {
  const entries = await loadFromCMS();
  store.clear();
  for (const entry of entries) {
    store.set(entry.id, {
      id: entry.id,
      data: entry,
      rendered: await renderMarkdown(entry.content),
    });
  }
}
```

## TOML in `glob()` (5.12.0)

The built-in `glob()` loader parses `.toml` files directly; no custom parser
or additional configuration is required.

```ts
const spacecraft = defineCollection({
  loader: glob({ pattern: '*.toml', base: './src/content/spacecraft' }),
});
```

## Astro DB text enums (5.13.0)

`column.text({ enum: [...] })` narrows the generated TypeScript type to a
string union. It does not validate at runtime, so application code must still
handle changed, added, or removed values.

```ts
const User = defineTable({
  columns: {
    rank: column.text({ enum: ['user', 'mod', 'admin'] }),
  },
});
```

## Actions with React state (5.14.0)

Stable `withState()` adapts an Astro Action for React's `useActionState()`;
`getActionState<T>(context)` retrieves prior state in the action handler.
Import both without the former `experimental_` prefixes from
`@astrojs/react/actions`.

```tsx
import { actions } from 'astro:actions';
import { withState } from '@astrojs/react/actions';
import { useActionState } from 'react';

export function Like() {
  const [likes, submit, pending] = useActionState(withState(actions.like), 0);
  return <form action={submit}><button disabled={pending}>{likes} ❤️</button></form>;
}
```

## Astro DB in web runtimes (5.14.0)

Configure `@astrojs/db` with `mode: 'web'` to use libSQL in non-Node runtimes
such as Cloudflare workerd or Deno. `node` remains the default mode.

```js
export default defineConfig({
  integrations: [db({ mode: 'web' })],
});
```

## Extracting Action input types (5.16.0)

`ActionInputSchema<T>` from `astro:actions` extracts an Action's Zod schema.
Pass it to `z.input<>` to get the accepted data type without duplicating the
schema:

```ts
import { type ActionInputSchema, defineAction } from 'astro:actions';
import { z } from 'astro/zod';

const contactAction = defineAction({
  accept: 'form',
  input: z.object({ email: z.string().email(), message: z.string() }),
  handler: ({ email, message }) => ({ success: true }),
});

type ContactSchema = ActionInputSchema<typeof contactAction>;
type ContactInput = z.input<ContactSchema>;
```

## Reducing stored content bodies (5.17.0)

`glob({ retainBody: false })` omits raw bodies from the content data store.
`entry.body` is then `undefined`, while rendered Markdown remains available at
`entry.rendered.html` and `entry.filePath` is preserved. The default is `true`.

```ts
const blog = defineCollection({
  loader: glob({
    pattern: '**/*.md',
    base: './src/content/blog',
    retainBody: false,
  }),
});
```

## Deferred rendering and chunked storage (7.0.1-7.2.4)

`glob({ deferRender: true })` delays Markdown and other renderable content
until a page actually renders an entry, reducing synchronization and build
memory for large collections. It defaults to `false`.

```ts
loader: glob({ pattern: '**/*.md', base: 'src/content/docs', deferRender: true })
```

`experimental.collectionStorage: 'chunked'` replaces the single
`.astro/data-store.json` file with content-addressed files under
`.astro/data-store/`. Use the object form to select chunk size:

```js
experimental: {
  collectionStorage: { type: 'chunked', chunkSize: 1024 * 1024 },
}
```

Loaders can provide an optional entry `digest`, which is also suitable as a
dynamic route's incremental-build cache key.
