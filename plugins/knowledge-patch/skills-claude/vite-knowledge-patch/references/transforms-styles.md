# Transforms, TypeScript, and Styles

## Remove the Sass Legacy API

Vite `7.0.0` removes support for the Sass legacy API. Projects still relying
on that interface must migrate before upgrading to Vite 7.

Search both project configuration and dependencies that customize Sass. A
successful install alone does not show that the removed build-time interface
is no longer used.

## Use Expanded Lightning CSS Interoperability

Since `8.1.0`, projects using `css.transformer: 'lightningcss'` can:

- Import external CSS files from CSS files.
- Let plugins register file dependencies.

These capabilities remove two earlier compatibility gaps with the PostCSS
transformer.

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  css: { transformer: 'lightningcss' },
})
```

Plugin authors can register the files their CSS work depends on, while
applications can keep external CSS imports when selecting Lightning CSS.
