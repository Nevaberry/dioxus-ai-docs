# Transforms, TypeScript, and Styles

## Expanded Lightning CSS compatibility

When `css.transformer` is set to `'lightningcss'`, CSS files can import
external CSS files and plugins can register file dependencies (since 8.1.0).
These capabilities close two previous compatibility gaps with Vite's PostCSS
transformer.

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  css: { transformer: 'lightningcss' },
})
```

Re-evaluate workarounds that existed solely because external CSS imports or
plugin-provided file dependencies were unavailable with Lightning CSS.

## Sass legacy API removal

Vite 7 removes Sass legacy API support (since 7.0.0). Before upgrading, inspect
the project's Vite configuration, Sass options, and relevant plugins for legacy
API assumptions.

Move those integrations to a supported Sass API. Keeping a legacy API setting
in place is an upgrade blocker, not a warning that Vite will continue to honor.
