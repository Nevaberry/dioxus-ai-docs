# Images, CSS, and Assets

Batch attributions used here: `15.5.0`, `16.0.0`, `16.2-guide`, `16.2.0`, and `16.3.0`.

## Image quality allowlists

Next.js `15.5.0` warns when an image requests a quality other than `75` without an `images.qualities` allowlist. In Next.js 16, the `quality` prop is restricted to the configured list, whose default contains only `75`.

```ts
const nextConfig = {
  images: { qualities: [75, 100] },
}

export default nextConfig
```

In Next.js 16, a requested value not present in the list is coerced to the closest configured quality (`16.0.0`). Audit callers before narrowing the list so that a silent nearest-value choice is acceptable.

## Local image query allowlists

Local sources containing query strings require a matching `images.localPatterns` entry in Next.js 16 (`15.5.0`). The `search` property has three distinct meanings:

- Omit `search` to permit any query string for the matching path.
- Set an exact query, such as `'?v=1'`, to permit only that query.
- Set `search: ''` to forbid all query strings.

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

Do not omit `search` when the intention is to disallow arbitrary cache-busting or user-controlled queries.

## Image optimizer defaults and network boundaries

Next.js 16 changes several optimizer defaults (`16.0.0`):

- `minimumCacheTTL` rises from 60 seconds to 14,400 seconds.
- `16` is removed from the default `imageSizes` list.
- Quality requests are coerced to the closest configured allowlisted value.
- Optimization of local/private IP addresses is blocked by default.
- Remote image fetching follows at most three redirects by default.

Enable `images.dangerouslyAllowLocalIP` only for a trusted private network. Set `images.maximumRedirects: 0` when remote optimization must reject every redirect. Treat these as network trust controls, not just performance tuning.

## `ImageResponse` rendering changes

`ImageResponse` adds support for these CSS capabilities in `16.2.0`:

- Inline CSS variables.
- `text-indent`.
- `text-decoration-skip-ink`.
- `box-sizing`.
- `display: contents`.
- `position: static`.
- Percentage `gap` values.

Its default font changes from Noto Sans to Geist Sans. Existing generated social images or metadata images can shift even when their source code is unchanged; use an explicit font when pixel stability matters.

## Multiple app icon formats

The App Router automatically handles same-basename icons with different extensions in `16.2.0`. For example, `icon.svg` and `icon.png` each produce a separate `<link>` element, allowing the browser to choose a supported format. Do not rename one merely to avoid a basename collision.

## Modern Sass API

The `sass-loader` 16 upgrade enables the modern Sass API, syntax, and features in Next.js `16.0.0`. Review custom loader options written for the legacy API when upgrading.

## Lightning CSS transform controls

`experimental.lightningCssFeatures` can override Browserslist for individual transforms (`16.2-guide`):

- `include` forces a transform.
- `exclude` prevents a transform.

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

Use this only when a targeted transform must differ from the project's normal browser targets.

## PostCSS configuration

Turbopack loads `postcss.config.ts` in addition to `.js` and `.cjs` configuration files (`16.2-guide`).

Monorepos can opt into package-local lookup in `16.3.0`: the nearest PostCSS configuration is resolved for each CSS file, with the project-root configuration as a fallback.

```ts
export default {
  experimental: { turbopackLocalPostcssConfig: true },
}
```

Enable package-local lookup when workspaces genuinely need different PostCSS pipelines; otherwise keep one root configuration for predictable transforms.
