# Content, data, and Actions

## Build-time collection loaders

### `glob()` IDs

The `glob()` loader derives URL-friendly IDs from filenames. An entry's `slug` field overrides that generated ID, while `generateId` applies a collection-wide mapping and receives the source entry path; it can preserve source casing or apply another convention (`5.0-guides`).

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

### Single-file data

`file()` turns one JSON or YAML array/object, or the top-level tables of one TOML file, into entries (`5.0-guides`). Array members must have unique `id` values, object keys become IDs, and IDs are not generated automatically. A synchronous or asynchronous `parser` can handle formats such as CSV or select an array nested inside JSON.

```ts
import { file } from 'astro/loaders';

const dogs = defineCollection({
  loader: file('src/data/pets.json', {
    parser: (text) => JSON.parse(text).dogs,
  }),
});
```

The `glob()` loader parses `.toml` files natively as of `5.12.0`:

```ts
const spacecraft = defineCollection({
  loader: glob({ pattern: '*.toml', base: './src/content/spacecraft' }),
});
```

### Collection TypeScript settings and schemas

Projects that extend `astro/tsconfigs/base`, or use no built-in Astro template, must enable both `strictNullChecks` and `allowJs`. The `strict` and `strictest` templates already do so (`5.0-guides`).

Astro generates one JSON Schema per collection at `.astro/collections/<name>.schema.json`. A JSON file can use a relative `$schema` path; editor settings such as VS Code's `json.schemas` and `yaml.schemas` can associate a generated schema with file groups (`5.0-guides`).

### Rendering loader-provided Markdown

A custom loader's context provides `renderMarkdown(content)`, which uses project Markdown settings and plugins and returns `{ html, metadata }` (`5.9.0`). Store that value as the entry's `rendered` property to enable the normal `render(entry)` and `<Content />` flow:

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

### Omitting raw bodies

For large `glob()` collections, `retainBody: false` omits raw source from `entry.body` and reduces the content data store (`5.17.0`). It defaults to `true`. Rendered Markdown remains in `entry.rendered.html` and `entry.filePath` remains available.

```ts
const blog = defineCollection({
  loader: glob({
    pattern: '**/*.md',
    base: './src/content/blog',
    retainBody: false,
  }),
});
```

## Live collections

Live collections load on every request rather than persisting through the Content Layer and therefore require an on-demand adapter (`5.0-guides`). Export them from `src/live.config.ts` with `defineLiveCollection()`. There are no built-in live loaders: a custom live loader implements `loadCollection` and `loadEntry` rather than a build-time loader's `load`.

```ts
import { defineLiveCollection } from 'astro:content';
import { apiLoader } from './loaders/api-loader';

const products = defineLiveCollection({
  loader: apiLoader({ endpoint: process.env.API_URL }),
});

export const collections = { products };
```

An optional Zod schema validates and transforms results at runtime and takes precedence over types supplied by the loader. Live collections do not support runtime MDX or image optimization.

### Query results and rendering

- `getLiveCollection(name, filters)` returns `{ entries, error }`; filters are defined by the loader.
- `getLiveEntry(name, id)` returns `{ entry, error }`.
- `render(entry)` works only if the loader returned a `rendered` property.
- Loader-defined errors can coexist with `LiveEntryNotFoundError`, `LiveCollectionValidationError`, `LiveCollectionCacheHintError`, and `LiveCollectionError` from `astro/content/runtime`. Handle network, missing-entry, cache-hint, and validation failures separately.

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

## Astro DB

Text columns can declare an `enum` array to narrow their generated TypeScript type to a string union (`5.13.0`). The option performs no runtime validation, so application code must tolerate values that have been added, removed, or changed.

```ts
import { column, defineTable } from 'astro:db';

const User = defineTable({
  columns: {
    rank: column.text({ enum: ['user', 'mod', 'admin'] }),
  },
});
```

For non-Node runtimes such as Cloudflare workerd and Deno, configure `@astrojs/db` with `mode: 'web'` to use the web-runtime libSQL driver. `node` remains the default (`5.14.0`).

## Actions

### Extracting accepted input

`ActionInputSchema<T>` from `astro:actions` extracts an Action's Zod input schema (`5.16.0`). Pass it to `z.input<>` to derive the accepted input data type without duplicating the schema.

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

### React action state

The stable `withState()` helper adapts an Astro Action for React's `useActionState()`, and `getActionState<T>(context)` reads the previous state in the action handler (`5.14.0`). Import both from `@astrojs/react/actions` without their former `experimental_` prefixes.
