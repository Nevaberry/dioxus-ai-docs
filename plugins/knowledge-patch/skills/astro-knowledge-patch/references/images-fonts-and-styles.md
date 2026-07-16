# Images, fonts, and styles

## Responsive images

### Layouts, cropping, and defaults

Behind `experimental.responsiveImages`, the original responsive-image preview added `fit` and `position` cropping for requested dimensions with the default Sharp service, plus `constrained`, `fixed`, and `full-width` layouts that generate `srcset` and `sizes` (`5.0.0`). Astro `5.10.0` made responsive image configuration stable:

```js
import { defineConfig } from 'astro/config';

export default defineConfig({
  image: {
    responsiveStyles: true,
    layout: 'constrained',
  },
});
```

A component-level `layout` overrides the global default. The `priority` prop marks a critical image with `loading="eager"`, `decoding="sync"`, and `fetchpriority="high"`:

```astro
<Image
  src="/hero.jpg"
  alt="Mountain panorama"
  layout="full-width"
  priority
/>
```

During the experimental phase, `image.experimentalDefaultStyles` defaulted to `true` and could be disabled when its low-specificity, unlayered CSS interfered with a project's cascade layers, notably Tailwind CSS layers (`5.9.0`). The stable control is `image.responsiveStyles`.

### Markdown and remote sources

Standard Markdown image syntax for a remote URL is processed through Astro's image service by default (`5.4.0`). Use an HTML `<img>` to skip optimization for one remote image; images from `public/` remain unprocessed. The responsive-image preview also applied responsive properties and styles to images in Markdown and MDX (`5.4.0`), behavior now controlled by the stable image configuration.

Remote optimization follows at most ten redirects (`6.3.0`). Every URL in the chain must match `image.domains` or `image.remotePatterns`; Astro throws if any hop leaves the allowlist.

## Image transformations

### Background, resize kernel, and codec defaults

`background` accepts any CSS color for transparent sources converted to an opaque format such as JPEG (`5.17.0`). It works in both `<Image>` and `getImage()`:

```astro
<Image src={product} format="jpeg" background="white" alt="Product" />
```

The Sharp service's site-wide `kernel` setting selects the resize algorithm (`5.17.0`); it cannot be selected per image, and the default for downsizing is `lanczos3`.

```js
export default defineConfig({
  image: {
    service: {
      entrypoint: 'astro/assets/services/sharp',
      config: { kernel: 'mks2021' },
    },
  },
});
```

Sharp also accepts global `jpeg`, `webp`, `avif`, and `png` encoding defaults (`6.1.0`). A per-image `quality` still wins over the codec default.

```js
export default defineConfig({
  image: {
    service: {
      config: {
        jpeg: { mozjpeg: true },
        webp: { effort: 6, alphaQuality: 80 },
        avif: { effort: 4, chromaSubsampling: '4:2:0' },
        png: { compressionLevel: 9 },
      },
    },
  },
});
```

### SVG source safety

Astro no longer rasterizes SVG sources through the image pipeline by default because an SVG can contain active content (`6.3.0`). Trusted projects can restore processing with `image.dangerouslyProcessSVG: true`. This setting does not affect SVG component imports.

## SVG components and optimization

Local SVG files were first importable as inline Astro components behind `experimental.svg` (`5.0.0`); native `<svg>` attributes such as `width`, `height`, `fill`, and `stroke` become component props. The feature is stable without a flag as of `5.7.0`.

Compatibility changes from `5.6.0` still apply:

- replace the removed `title` prop with `aria-label`;
- replace `size` with explicit `width` and `height`;
- remove component and configuration `mode` because SVG components are always inline;
- add an explicit `role` when accessibility semantics require one, because Astro supplies no default.

Use `SvgComponent` from `astro/types` when a prop or helper accepts any imported SVG component, instead of spelling the type as `typeof import('*.svg')` (`5.14.0`).

```ts
import type { SvgComponent } from 'astro/types';

type IconProps = { icon: SvgComponent };
```

Build-time SVG optimization began with `experimental.svgo` and either the recommended settings or a custom SVGO plugin object (`5.16.0`). `experimental.svgOptimizer` replaced it with a provider-neutral `SvgOptimizer` interface in `6.2.0`. Use the built-in `svgoOptimizer()` when SVGO is desired:

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

Imported SVG components are optimized during the build.

## Fonts

### Configuration and providers

The initial Fonts API used `experimental.fonts`, built-in providers such as Google, Fontsource, and Bunny, automatic optimization and fallback generation, and a `<Font>` component from `astro:assets` (`5.7.0`). Astro 6 moves families to top-level `fonts` (`6.0-guides`), downloads provider files, and serves them locally.

Built-in providers cover Adobe, Bunny, Fontshare, Fontsource, Google, Google Icons, NPM packages, and local files. Remote-provider defaults select weight 400, normal and italic styles, the Latin subset, a sans-serif fallback, and WOFF2. A local provider instead declares `options.variants`; each variant's `src` can include fallback formats, and omitted weight and style values are inferred.

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

The `<Font>` component applies a configured family and can preload it. Its `preload` prop can be an array of filters over `weight`, `style`, and `subset` (`5.15.0`). Fields within one filter are combined, filters are additive, and an exact requested weight also matches a variable-font range containing it.

```astro
<Font
  cssVariable="--font-roboto"
  preload={[{ subset: 'latin', style: 'normal' }, { weight: '400' }]}
/>
```

### Selecting non-Cartesian variants

Repeating a font with the same `name`, `cssVariable`, and provider merges the selected variants (`6.0-guides`). This avoids downloading every Cartesian weight/style combination:

```js
fonts: [
  {
    provider: fontProviders.google(),
    name: 'Roboto',
    cssVariable: '--font-roboto',
    weights: [500, 600],
    styles: ['normal'],
  },
  {
    provider: fontProviders.google(),
    name: 'Roboto',
    cssVariable: '--font-roboto',
    weights: [500],
    styles: ['italic'],
  },
]
```

### Programmatic font data and caches

The earlier `getFontData()` API accepted a CSS variable and exposed family records and generated file URLs (`5.14.0`). Astro 6 exposes `fontData` from `astro:assets`, keyed by CSS variable (`6.0-guides`):

```ts
import { fontData } from 'astro:assets';

const path = fontData['--font-roboto'][0].src[0].url;
```

During prerendering, the `experimental_getFontFileURL()` helper resolves a managed path against `context.url` to produce a fetchable URL for build-time renderers such as Satori (`6.2.0`).

Static builds copy font assets to `_astro/fonts`. Delete `.astro/fonts` to clear the development font cache or `node_modules/.astro/fonts` to clear the build cache (`6.0-guides`).
