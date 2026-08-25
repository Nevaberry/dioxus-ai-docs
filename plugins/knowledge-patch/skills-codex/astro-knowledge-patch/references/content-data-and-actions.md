# Content, data, and Actions

## Build-time loader IDs and parsing

The 5.0-guides behavior for `glob()` is:

- IDs are URL-friendly forms of filenames.
- An entry's `slug` overrides its generated ID.
- `generateId({ entry })` receives the source entry path and can preserve casing or apply another collection-wide mapping.

```ts
const authors = defineCollection({
  loader: glob({
    base: './src/data/authors',
    pattern: '**/*.json',
    generateId: ({ entry }) => entry.replace(/\.json$/, ''),
  }),
});
```

Also in 5.0-guides, `file()` turns one JSON or YAML array/object, or the top-level tables of a TOML file, into entries. Array items need unique `id` values; object keys become IDs; IDs are not generated automatically. A sync or async `parser` can parse CSV or select a nested array:

```ts
const dogs = defineCollection({
  loader: file('src/data/pets.json', {
    parser: (text) => JSON.parse(text).dogs,
  }),
});
```

Projects extending `astro/tsconfigs/base`, or no built-in Astro template, must enable both `strictNullChecks` and `allowJs`; the `strict` and `strictest` templates already do.

Since 5.12.0, `glob()` parses `.toml` files natively. Since 5.17.0, `retainBody: false` omits raw `entry.body` to shrink large data stores while retaining `entry.rendered.html` and `entry.filePath`; it defaults to `true`.

## Generated schemas

Astro writes one schema per collection to `.astro/collections/<name>.schema.json` (5.0-guides). JSON files can use a relative `$schema`; VS Code `json.schemas` and `yaml.schemas` can associate it with file groups.

## Live collections

Live collections in 5.0-guides fetch at request time, require an on-demand adapter, and do not persist through the Content Layer. Export them from `src/live.config.ts` with `defineLiveCollection()`. There are no built-in live loaders: a custom loader implements `loadCollection` and `loadEntry`, not the build-time loader's `load`.

An optional Zod schema validates and transforms at runtime and overrides loader-supplied types. Runtime MDX and image optimization are unsupported.

`getLiveCollection(name, filters)` returns `{ entries, error }`; `getLiveEntry(name, id)` returns `{ entry, error }`. Filters are loader-specific. `render(entry)` works only if the loader supplied `rendered`. Handle loader errors or Astro's `LiveEntryNotFoundError`, `LiveCollectionValidationError`, `LiveCollectionCacheHintError`, and `LiveCollectionError` from `astro/content/runtime` rather than treating every missing result alike.

## Rendering loader-provided Markdown

Since 5.9.0, a custom loader's context provides `renderMarkdown(content)`, using project Markdown settings and returning `{ html, metadata }`. Store it as the entry's `rendered` value to enable `render(entry)` and `<Content />`:

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

## Deferred rendering and storage

In 7.0.1-7.2.4, `glob({ deferRender: true })` delays rendering supported content until a page renders it, reducing sync/build memory; the default is `false`.

The same batch adds `experimental.collectionStorage: 'chunked'`, which replaces `.astro/data-store.json` with content-addressed files under `.astro/data-store/`. Use `{ type: 'chunked', chunkSize }` to choose a chunk size.

Content entries can expose an optional loader-provided `digest`, suitable as an incremental `getStaticPaths()` cache key.

## Astro DB

Since 5.13.0, `column.text({ enum: [...] })` narrows the generated TypeScript type to a string union but performs no runtime validation. Application code must tolerate enum evolution.

Since 5.14.0, `@astrojs/db` accepts `mode: 'web'` for libSQL in non-Node runtimes such as workerd and Deno; `node` remains the default.

## Actions and framework state

Astro 5.14.0 stabilizes `withState()` and `getActionState<T>()` from `@astrojs/react/actions`. `withState()` adapts an Astro Action for React `useActionState()`, while `getActionState(context)` retrieves prior state in the handler; remove the former `experimental_` prefixes.

Since 5.16.0, `ActionInputSchema<T>` from `astro:actions` extracts an Action's Zod schema. Use `z.input<ActionInputSchema<typeof action>>` to obtain accepted input data without duplicating the schema.
