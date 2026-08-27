# Integrations and Ecosystem

Use this reference for component styles, build-tool integrations, CLI watch behavior, browser builds, formatting, and framework-free UI blocks.

## Reference a stylesheet without duplicating it

Since `4.0.0-configuration`, component style blocks and CSS modules can use `@reference` to expose theme variables, custom utilities, and custom variants to `@apply` or `@variant` without copying the referenced stylesheet into the output.

```css
@reference "../../app.css";

h1 {
  @apply text-2xl font-bold;
}
```

Reference `tailwindcss` directly when the project uses the uncustomized default theme.

The CLI, Vite, and PostCSS integrations resolve package subpath aliases in `@import`, `@reference`, `@plugin`, and `@config`. For example, a package import mapping of `"#app.css": "./src/css/app.css"` allows:

```css
@reference "#app.css";
```

## Select a first-party build integration

### Vite

The first-party `@tailwindcss/vite` integration supports Vite 8 (`4.2.2`). Upgrade Vite without replacing the Tailwind plugin or pinning Vite to an earlier major.

### webpack

The `4.3.0` batch adds the version 4.2 `@tailwindcss/webpack` loader. It runs Tailwind directly in webpack rather than routing CSS through the PostCSS integration.

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

## Poll when CLI filesystem events are unreliable

Since `4.3.3`, `@tailwindcss/cli` accepts `--watch --poll` or `--watch --poll=<milliseconds>`. Polling works when filesystem events are absent or unreliable and avoids loading `@parcel/watcher`, including in environments where that dependency cannot load.

```console
npx @tailwindcss/cli -i input.css -o output.css --watch --poll=500
```

Use an explicit interval when the default polling cadence is too expensive or too slow for the environment.

## Rely on built-in CSS nesting processing

CSS nesting is handled even when Lightning CSS does not run (`4.3.3`), including in `@tailwindcss/browser` and Tailwind Play.

```css
.card {
  &:hover { color: red; }
}
```

Do not add an extra nesting transform solely to make these Tailwind environments understand nested rules.

## Use interactive plain-HTML blocks

The `tailwind-news` batch reports that Tailwind Plus UI blocks—including dialogs, dropdowns, and command palettes—are functional, accessible, and interactive in their plain-HTML form. A project can use those blocks without React, Vue, or hand-written behavior.

Evaluate the supplied behavior against project-specific accessibility and interaction requirements, especially when adapting the markup.

## Clean class lists with Prettier

`prettier-plugin-tailwindcss` can remove unnecessary whitespace and duplicate class names while sorting class lists (`tailwind-news`). Keep the plugin in the formatting toolchain when class ordering and deduplication should happen automatically.
