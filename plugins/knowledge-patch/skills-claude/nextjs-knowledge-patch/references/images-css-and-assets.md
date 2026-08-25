# Images, CSS, and Assets

## Image quality allowlists (`15.5.0`)

Next.js 15.5 warns when an image requests a quality other than `75` without an `images.qualities` allowlist. Next.js 16 restricts the `quality` prop to values in that configured list. The default list contains only `75`.

```ts
const nextConfig = { images: { qualities: [75, 100] } }

export default nextConfig
```

## Local image query allowlists (`15.5.0`)

In Next.js 16, local image sources containing query strings require a matching `images.localPatterns` entry.

- Omitting `search` permits any query.
- An exact string permits only that query.
- `search: ''` forbids query strings.

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

## Optimizer defaults and network boundaries (`16.0.0`)

Image optimization changes several defaults and trust boundaries:

- Minimum cache TTL rises from 60 seconds to 14,400 seconds.
- `16` is removed from the default `imageSizes` list.
- A requested quality is coerced to the closest configured quality.
- Optimization of local IPs is blocked unless `images.dangerouslyAllowLocalIP` is enabled for a trusted private network.
- Remote optimization follows at most three redirects by default; `images.maximumRedirects: 0` disables redirects.

## Modern Sass API (`16.0.0`)

The upgrade to `sass-loader` 16 enables the modern Sass API, syntax, and features.

## Lightning CSS transform controls (`16.2-guide`)

`experimental.lightningCssFeatures` overrides Browserslist for individual transforms. `include` forces a transform, while `exclude` prevents it.

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

## TypeScript PostCSS configuration (`16.2-guide`)

Turbopack loads `postcss.config.ts` in addition to `.js` and `.cjs` PostCSS configuration files.

## Expanded `ImageResponse` rendering (`16.2.0`)

`ImageResponse` supports inline CSS variables, `text-indent`, `text-decoration-skip-ink`, `box-sizing`, `display: contents`, `position: static`, and percentage `gap` values.

Its default font changes from Noto Sans to Geist Sans. Existing generated images can therefore render differently after an upgrade.

## Multiple app icon formats (`16.2.0`)

The App Router handles same-basename icons with different extensions, such as `icon.svg` and `icon.png`. It emits a separate `<link>` for every format so the browser can select one it supports.

## Package-local PostCSS (`16.3.0`)

In a monorepo, `experimental.turbopackLocalPostcssConfig` resolves the nearest PostCSS configuration for each CSS file and falls back to the project-root configuration.

```ts
export default {
  experimental: { turbopackLocalPostcssConfig: true },
}
```
