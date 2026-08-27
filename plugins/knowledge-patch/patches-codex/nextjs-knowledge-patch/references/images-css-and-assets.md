# Images, CSS, and Assets

## Image configuration

### Quality allowlist (`15.5.0`)

Next.js 15.5 warns when an image requests a quality other than `75` without an
`images.qualities` allowlist. Next.js 16 restricts the `quality` prop to the
configured list, whose default contains only `75`.

```ts
const nextConfig = { images: { qualities: [75, 100] } }
export default nextConfig
```

### Local query allowlist (`15.5.0`)

In Next.js 16, local image sources containing query strings require a matching
`images.localPatterns` entry. Omitting `search` permits any query; an exact
string permits only that query; `search: ''` forbids queries.

```ts
const nextConfig = {
  images: {
    localPatterns: [
      { pathname: '/photo.jpg', search: '?v=1' },
      { pathname: '/assets/**', search: '' },
    ],
  },
}
export default nextConfig
```

### Optimizer defaults and network boundaries (`16.0.0`)

- The default minimum cache TTL rose from 60 to 14,400 seconds.
- `16` was removed from the default `imageSizes`.
- A requested quality is coerced to the closest configured quality.
- Local-IP optimization is blocked unless
  `images.dangerouslyAllowLocalIP` is enabled for a trusted private network.
- Remote optimization follows at most three redirects by default;
  `images.maximumRedirects: 0` disables redirects.

## Generated images and icons

### `ImageResponse` rendering (`16.2.0`)

`ImageResponse` supports inline CSS variables, `text-indent`,
`text-decoration-skip-ink`, `box-sizing`, `display: contents`,
`position: static`, and percentage `gap` values. Its default font changed from
Noto Sans to Geist Sans, which can alter existing generated output.

### Multiple icon formats (`16.2.0`)

The App Router handles same-basename icons with different extensions, such as
`icon.svg` and `icon.png`. It emits a separate `<link>` for each so browsers can
choose a supported format.

## CSS tooling

### Modern Sass API (`16.0.0`)

The `sass-loader` 16 upgrade enables the modern Sass API, syntax, and features.

### Explicit Lightning CSS transforms (`16.2-guide`)

`experimental.lightningCssFeatures` overrides Browserslist for individual
transforms: `include` forces transpilation and `exclude` prevents it.

```ts
const nextConfig = {
  experimental: {
    useLightningcss: true,
    lightningCssFeatures: {
      include: ['light-dark'],
      exclude: ['nesting'],
    },
  },
}
export default nextConfig
```

### TypeScript PostCSS config (`16.2-guide`)

Turbopack loads `postcss.config.ts` in addition to `.js` and `.cjs` PostCSS
configuration files.

### Package-local PostCSS config (`16.3.0`)

Monorepos can resolve the nearest PostCSS configuration for each CSS file,
falling back to the project-root configuration.

```ts
export default {
  experimental: { turbopackLocalPostcssConfig: true },
}
```
