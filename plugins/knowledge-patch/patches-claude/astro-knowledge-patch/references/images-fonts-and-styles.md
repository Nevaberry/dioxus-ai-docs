# Images, fonts, and styles

## Cropping and responsive layouts (5.0.0)

With the default Sharp service, Astro 5's
`experimental.responsiveImages` adds `fit` and `position` for cropping to
requested dimensions and predefined responsive layouts that generate
appropriate `srcset` and `sizes` values.

```astro
<Image src={logo} fit="cover" width={200} height={200} />
<Image src={rocket} width={800} height={600} layout="responsive" />
```

In 5.4.0 the same flag makes standard Markdown and MDX images responsive.

## Stable responsive images and priority (5.10.0)

Responsive images no longer need a flag. Set site defaults under `image`; a
component's `layout` overrides the global default. `priority` applies
`loading="eager"`, `decoding="sync"`, and `fetchpriority="high"`.

```js
export default defineConfig({
  image: {
    responsiveStyles: true,
    layout: 'constrained',
  },
});
```

```astro
<Image src="/hero.jpg" alt="Mountain panorama" layout="full-width" priority />
```

While using the Astro 5 experimental form, the low-specificity generated
styles default on. Set `image.experimentalDefaultStyles: false` if those
unlayered rules conflict with application CSS or Tailwind cascade layers
(5.9.0).

## Imported SVG components (5.0.0)

Astro 5 initially required `experimental.svg` for default imports of local SVG
files as inline Astro components. Native `<svg>` attributes such as `width`,
`height`, `fill`, and `stroke` become component props.

SVG components are stable from 5.7.0 and no longer need the flag. Since 5.6.0
they do not accept `title`, `size`, or `mode`, are always inline, and receive
no default `role`. Use an accessible label, role, and explicit dimensions:

```astro
<Logo aria-label="My company logo" role="img" width={64} height={64} />
```

Use the built-in `SvgComponent` type when passing an imported component
through a typed API (5.14.0):

```ts
import type { SvgComponent } from 'astro/types';

type IconProps = { icon: SvgComponent };
```

## SVG optimization (5.16.0)

The original build-time optimizer used `experimental.svgo: true` for SVGO's
recommended settings or a custom SVGO configuration object for plugin control.

Astro 6.2 replaces that option with pluggable `experimental.svgOptimizer`.
Any `SvgOptimizer` implementation is accepted; `svgoOptimizer()` supplies the
built-in SVGO implementation (6.2.0):

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

Optimization applies to imported SVG components at build time.

## Safe SVG image processing (6.3.0)

The image pipeline does not rasterize SVG image sources by default because SVG
can contain active content. Only trusted projects should restore the previous
behavior:

```js
export default defineConfig({
  image: { dangerouslyProcessSVG: true },
});
```

Importing an SVG as a component is unaffected.

## Remote image redirects (6.3.0)

Remote optimization follows at most ten redirects. Every URL in the chain
must match `image.domains` or `image.remotePatterns`; Astro throws if any hop
leaves the allowlist.

```js
export default defineConfig({
  image: { domains: ['example.com', 'cdn.example.com'] },
});
```

## Image backgrounds and resize kernels (5.17.0)

Image transformations accept any CSS color in `background`, allowing a
transparent source converted to JPEG to use a chosen background instead of
black. The option works with `<Image>` and `getImage()`.

```astro
<Image src={product} format="jpeg" background="white" alt="Product" />
```

Sharp's site-wide `kernel` selects the resize algorithm; the default for
downsizing is `lanczos3`. It cannot be set per image.

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

## Sharp codec defaults (6.1.0)

Sharp global service configuration accepts `jpeg`, `webp`, `avif`, and `png`
encoding defaults. A component's `quality` still wins over these settings.

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

Astro supports Sharp 0.35; pnpm projects on that release no longer need to
approve Sharp's build script (7.0.1-7.2.4).

## Experimental Fonts API (5.7.0)

The Astro 5 `experimental.fonts` array supports local fonts and built-in
Google, Fontsource, and Bunny providers, optimizes files, generates fallbacks,
and can expose a CSS variable. `<Font>` from `astro:assets` controls applying
and preloading the family.

```js
import { defineConfig, fontProviders } from 'astro/config';

export default defineConfig({
  experimental: {
    fonts: [{
      provider: fontProviders.google(),
      name: 'Roboto',
      cssVariable: '--font-roboto',
    }],
  },
});
```

From 5.15.0, `<Font preload>` may be an array of filters over `weight`,
`style`, and `subset`. Fields within a filter intersect; separate filters add
matches. A requested weight matches a variable font range containing it.

```astro
<Font
  cssVariable="--font-roboto"
  preload={[{ subset: 'latin', style: 'normal' }, { weight: '400' }]}
/>
```

In 5.14.0, `getFontData('--font-roboto')` exposes family and generated source
URLs for consumers such as Open Graph renderers.

## Stable top-level fonts (6.0-guides)

Astro 6 moves families to top-level `fonts`. Provider files are downloaded and
served locally. Built-ins cover Adobe, Bunny, Fontshare, Fontsource, Google,
Google Icons, NPM, and local files. Provider defaults are weight 400, normal
and italic styles, Latin subset, a sans-serif fallback, and WOFF2.

The local provider declares `options.variants`; its `src` can list alternate
formats, and omitted weight and style are inferred:

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

`fontData` from `astro:assets` is keyed by CSS variable and exposes generated
variant source URLs:

```ts
import { fontData } from 'astro:assets';

const url = fontData['--font-roboto'][0].src[0].url;
```

To request non-Cartesian weight/style combinations, repeat a family with the
same name, variable, and provider but different selectors. Astro merges them;
for example, one declaration can request normal 500/600 and another italic
500 without downloading italic 600.

Builds copy fonts to `_astro/fonts`. Clear `.astro/fonts` for the development
cache or `node_modules/.astro/fonts` for the build cache.

## Fetchable font URLs during prerendering (6.2.0)

`experimental_getFontFileURL(path, context.url)` resolves an Astro-managed
`fontData` path against the request during prerendering. Build-time image
generators such as Satori can then fetch the public URL:

```ts
import { fontData, experimental_getFontFileURL } from 'astro:assets';

const path = fontData['--font-roboto'][0]?.src[0]?.url;
if (path === undefined) throw new Error('Font not found');
const url = experimental_getFontFileURL(path, context.url);
const data = await fetch(url).then((response) => response.arrayBuffer());
```
