# Development Server, HMR, Globs, and Assets

## Bundled ESM with HMR

Experimental bundled development retains HMR while serving bundled ESM (since
8.1.0). It is aimed at large browser applications where one request per module
creates significant startup or reload overhead.

```sh
vite --experimental-bundle
```

The equivalent configuration is `experimental.bundledDev: true`. The mode is
still limited, so test HMR behavior in the target framework before relying on
it.

## Case-insensitive glob matching

`import.meta.glob` accepts `caseSensitive: false` to match filenames regardless
of case (since 8.1.0):

```ts
const modules = import.meta.glob('./dir/module*.js', {
  caseSensitive: false,
})
```

Use the option deliberately when a convention or imported content permits
multiple filename casings. Leaving it out preserves case-sensitive matching.

## Custom HTML asset sources

`html.additionalAssetSources` teaches Vite about asset-bearing custom elements
and nonstandard attributes (since 8.1.0). Referenced files then participate in
normal Vite asset processing.

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  html: {
    additionalAssetSources: {
      'html-import': {
        srcAttributes: 'src',
      },
      img: {
        srcAttributes: ['data-src-dark', 'data-src-light'],
      },
    },
  },
})
```

`srcAttributes` may be a single attribute string or an array of attribute
names, as the two entries demonstrate.
