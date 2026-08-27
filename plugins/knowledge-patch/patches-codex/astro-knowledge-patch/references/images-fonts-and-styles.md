# Images, fonts, and styles

## Responsive images and transformations

Astro 5.0.0 introduced `fit`, `position`, and predefined responsive layouts behind `experimental.responsiveImages` for the default Sharp service. Layouts such as the original `responsive` form generate `srcset` and `sizes`; `fit` and `position` crop to requested dimensions. In 5.4.0 the same flag made Markdown and MDX images responsive.

In 5.9.0, `image.experimentalDefaultStyles` controlled the low-specificity responsive defaults and defaulted to `true`; disable it when unlayered styles conflict with CSS cascade layers such as Tailwind's.

Since 5.10.0, responsive behavior is stable. Configure `image.responsiveStyles` and a global `image.layout` of `constrained`, `fixed`, or `full-width`; component `layout` wins. The `priority` prop sets `loading="eager"`, `decoding="sync"`, and `fetchpriority="high"`.

Since 5.17.0, `<Image>` and `getImage()` accept any CSS color as `background`, useful when converting transparent input to JPEG.

## Remote image safety

Remote Markdown images have used Astro's image service by default since 5.4.0. Use an HTML `<img>` to bypass processing; assets in `public/` are not processed.

Since 6.3.0, optimization follows at most ten redirects. Every URL in the chain must match `image.domains` or `image.remotePatterns`; leaving the allowlist is an error.

## SVG components and optimization

In 5.0.0, `experimental.svg` allowed a local `.svg` default import to render as an inline Astro component and accept native SVG attributes. The 5.6.0 API removed `title`, `size`, and `mode`, removed the default `role`, and made inline behavior unconditional. Use `aria-label`, explicit dimensions, and an explicit role. SVG imports became stable in 5.7.0, so remove `experimental.svg`.

Since 5.14.0, use `SvgComponent` from `astro/types` to type props that accept imported SVG components.

Astro 5.16.0 introduced build-time optimization as `experimental.svgo: true | SvgoOptions`. In 6.2.0 this became pluggable `experimental.svgOptimizer`; pass Astro's `svgoOptimizer(options)` to keep SVGO or supply another `SvgOptimizer` implementation:

```js
import { defineConfig, svgoOptimizer } from 'astro/config';

export default defineConfig({
  experimental: {
    svgOptimizer: svgoOptimizer({
      plugins: ['preset-default', { name: 'removeViewBox' }],
    }),
  },
});
```

Since 6.3.0, the image pipeline does not rasterize SVG input by default because SVG may contain active content. Set `image.dangerouslyProcessSVG: true` only for trusted input. Component imports are unaffected.

## Sharp configuration

Since 5.17.0, Sharp's site-wide `kernel` selects its resize algorithm; the default for downsizing is `lanczos3`, and it cannot be overridden per image.

Since 6.1.0, the global Sharp service accepts per-codec `jpeg`, `webp`, `avif`, and `png` defaults. A per-image `quality` still wins:

```js
image: {
  service: {
    config: {
      jpeg: { mozjpeg: true },
      webp: { effort: 6, alphaQuality: 80 },
      avif: { effort: 4, chromaSubsampling: '4:2:0' },
      png: { compressionLevel: 9 },
    },
  },
}
```

Astro 7.0.1-7.2.4 supports Sharp 0.35. pnpm projects using it no longer need to approve Sharp's build script.

## Font configuration

The Fonts API started under `experimental.fonts` in 5.7.0 with local files and built-in Google, Fontsource, and Bunny providers, local serving, optimization, fallback generation, CSS variables, and the `<Font>` component for application and preload.

In 6.0-guides, move families to top-level `fonts`. Built-in providers include Adobe, Bunny, Fontshare, Fontsource, Google, Google Icons, NPM, and local files. Provider defaults select weight 400, normal and italic styles, Latin, a sans-serif fallback, and WOFF2. The local provider uses `options.variants`; `src` may list alternate formats, and omitted weight/style values are inferred.

```js
import { defineConfig, fontProviders } from 'astro/config';

export default defineConfig({
  fonts: [{
    provider: fontProviders.local(),
    name: 'Poppins',
    cssVariable: '--font-poppins',
    options: {
      variants: [{
        src: [
          './src/assets/fonts/Poppins-regular.woff2',
          './src/assets/fonts/Poppins-regular.woff',
        ],
      }],
    },
  }],
});
```

To select non-Cartesian weight/style combinations, repeat a family with the same name, CSS variable, and provider but different selectors; Astro merges the variants. For example, one declaration can select normal 500/600 and another italic 500 only.

Builds copy files to `_astro/fonts`. Clear `.astro/fonts` for the development cache or `node_modules/.astro/fonts` for the build cache.

## Font data and preloading

Astro 5.14.0 added `getFontData(cssVariable)` for generated family and URL data. Since 6.0-guides, use the `fontData` object from `astro:assets`, keyed by CSS variable; its variant/source records expose generated URLs.

Since 5.15.0, `<Font preload>` may be an array of filters over `weight`, `style`, and `subset`. Fields in one filter are ANDed, filters are additive, and a requested weight matches a variable-font range containing it.

Since 6.2.0, `experimental_getFontFileURL(path, context.url)` resolves a `fontData` path during prerendering so build-time image generators can fetch the managed file without relying on internal paths.
