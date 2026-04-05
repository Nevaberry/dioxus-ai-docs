# Fonts & Asset Pipeline

## Built-in Fonts API (6.0)

Configure fonts in `astro.config` with automatic self-hosting, optimized fallbacks, and preload hints.

### Configuration

```js
import { defineConfig, fontProviders } from 'astro/config';
export default defineConfig({
  fonts: [
    {
      name: 'Roboto',
      cssVariable: '--font-roboto',
      provider: fontProviders.fontsource(),
    },
  ],
});
```

### `<Font />` Component

Import from `astro:assets`:

```astro
---
import { Font } from 'astro:assets';
---
<Font cssVariable="--font-roboto" preload />
<style is:global>
  body { font-family: var(--font-roboto); }
</style>
```

### Available Providers

| Provider | Import |
|---|---|
| Fontsource | `fontProviders.fontsource()` |
| Google Fonts | `fontProviders.google()` |

## Experimental SVGO (5.16)

Automatic SVG optimization via SVGO in the asset pipeline:

```js
import { defineConfig } from 'astro/config';
export default defineConfig({
  experimental: {
    svgo: true,
  },
});
```

With custom SVGO plugin configuration:

```js
export default defineConfig({
  experimental: {
    svgo: {
      plugins: ['preset-default', { name: 'removeViewBox', active: false }],
    },
  },
});
```

## Image `background` Prop (5.17)

Control background color when converting images to non-transparent formats (e.g. PNG to JPEG). Previously defaulted to black.

### `<Image />` Component

```astro
---
import { Image } from 'astro:assets';
import myImage from './my-image.png';
---
<Image src={myImage} format="jpeg" background="white" alt="Product" />
<Image src={myImage} format="jpeg" background="#f8fafc" alt="Banner" />
```

### `getImage()`

```ts
const img = await getImage({ src: heroImage, format: 'jpeg', background: 'white' });
```
