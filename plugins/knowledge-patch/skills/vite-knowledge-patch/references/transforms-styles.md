# Transforms, TypeScript, and Styles

## Lightning CSS compatibility

When `css.transformer` is `'lightningcss'`, CSS files can import external CSS
files (since 8.1.0):

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  css: {
    transformer: 'lightningcss',
  },
})
```

Plugins used with the Lightning CSS transformer can also register file
dependencies. External CSS imports and plugin file-dependency registration
close two earlier compatibility gaps with the PostCSS transformer.

## Sass legacy API removal

Vite no longer supports the Sass legacy API (since 7.0.0). Migrate any project
or integration that still depends on that deprecated API before upgrading;
there is no compatibility path through the removed support.
