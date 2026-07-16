# Integrations and Ecosystem

Use this reference when wiring Tailwind into component styles, package aliases, build tools, formatting, or framework-free UI blocks.

## Reference a Stylesheet Without Emitting It Again

Reference-only imports are recorded in source batch `4.0.0-configuration`.

Component style blocks and CSS modules can use `@reference` to make another stylesheet's theme variables, custom utilities, and custom variants available to `@apply` and `@variant`. The referenced stylesheet is not duplicated in the output.

```css
@reference "../../app.css";

h1 {
  @apply text-2xl font-bold;
}
```

When the project uses the uncustomized default theme, reference the package directly:

```css
@reference "tailwindcss";
```

## Resolve Package Subpath Aliases

The CLI, Vite, and PostCSS integrations resolve package `imports` aliases in all of these directives:

- `@import`
- `@reference`
- `@plugin`
- `@config`

For example, given this package entry:

```json
{
  "imports": {
    "#app.css": "./src/css/app.css"
  }
}
```

A component stylesheet can use the alias directly:

```css
@reference "#app.css";
```

## Vite Integration

Vite 8 support is recorded in source batch `4.2.2`.

The `@tailwindcss/vite` integration supports Vite 8. A project can upgrade Vite without replacing the Tailwind plugin or pinning Vite to an earlier major release.

## Webpack Loader

The dedicated loader is part of the 4.2 feature set represented by source batch `4.3.0`.

Use `@tailwindcss/webpack` to run Tailwind directly in webpack instead of routing the stylesheet through the PostCSS integration.

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

## Interactive Plain-HTML Tailwind Plus Blocks

The Tailwind Plus behavior is recorded in source batch `tailwind-news`.

Every Tailwind Plus UI block has functional, accessible, interactive behavior in its plain-HTML form. This includes interaction-heavy patterns such as dialogs, dropdowns, and command palettes. Using these blocks does not require React, Vue, or hand-written behavior.

Treat the supplied HTML behavior as part of the block rather than assuming the example is visual markup that still needs a framework implementation.

## Prettier Class-List Cleanup

`prettier-plugin-tailwindcss` can perform three class-list cleanup operations together:

- sort class names;
- remove duplicate class names;
- remove unnecessary whitespace.

This means formatting can normalize both ordering and redundant class-list content instead of sorting alone.
