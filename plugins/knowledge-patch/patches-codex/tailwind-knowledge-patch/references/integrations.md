# Integrations and Ecosystem

## Reference-only stylesheet imports

Use `@reference` in component style blocks or CSS modules when `@apply` or `@variant` needs access to theme variables, custom utilities, or custom variants. A reference exposes those definitions without duplicating the referenced stylesheet in the output.

```css
@reference "../../app.css";

h1 {
  @apply text-2xl font-bold;
}
```

If the project uses the uncustomized default theme, reference `tailwindcss` directly.

The CLI, Vite, and PostCSS integrations resolve package subpath aliases in `@import`, `@reference`, `@plugin`, and `@config`. For example, this package mapping:

```json
{
  "imports": {
    "#app.css": "./src/css/app.css"
  }
}
```

supports this reference:

```css
@reference "#app.css";
```

These reference and alias behaviors are part of the `4.0.0-configuration` batch.

## Vite

The first-party `@tailwindcss/vite` integration supports Vite 8 as recorded in `4.2.2`. Upgrade Vite without replacing the Tailwind plugin or pinning Vite to an earlier major.

## webpack loader

The version 4.2 `@tailwindcss/webpack` loader, recorded in batch `4.3.0`, runs Tailwind directly in webpack rather than sending CSS through the PostCSS integration.

```js
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
  plugins: [new MiniCssExtractPlugin()],
  module: {
    rules: [
      {
        test: /\.css$/i,
        use: [
          MiniCssExtractPlugin.loader,
          "css-loader",
          "@tailwindcss/webpack",
        ],
      },
    ],
  },
};
```

## CLI polling watch mode

As recorded in `4.3.3`, `@tailwindcss/cli` accepts either `--watch --poll` or `--watch --poll=<milliseconds>`. Use polling where file-system events are unavailable or unreliable.

```console
npx @tailwindcss/cli -i input.css -o output.css --watch --poll=500
```

Polling avoids loading `@parcel/watcher`, so it also works in environments where that dependency cannot be loaded.

## CSS nesting without Lightning CSS

CSS nesting is handled even when Lightning CSS does not run, including in `@tailwindcss/browser` and Tailwind Play (`4.3.3`).

```css
.card {
  &:hover {
    color: red;
  }
}
```

## Tailwind Plus plain HTML

The `tailwind-news` guidance records that every Tailwind Plus UI block is functional, accessible, and interactive in its plain-HTML form. This includes dialogs, dropdowns, and command palettes; these blocks do not require React, Vue, or hand-written behavior.

## Prettier class cleanup

`prettier-plugin-tailwindcss` can remove unnecessary whitespace and duplicate class names while it sorts class lists. This class-list cleanup is also recorded in `tailwind-news`.
