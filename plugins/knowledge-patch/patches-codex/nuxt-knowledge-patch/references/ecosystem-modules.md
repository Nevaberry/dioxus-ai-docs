# Ecosystem modules

Use current Nuxt Scripts, Icon, Content, UI, and Image package APIs and migration contracts.

## Nuxt Content

### Collection query utilities (module-major-launches)

The v3 Vue API centers on `queryCollection`, `queryCollectionNavigation`, `queryCollectionItemSurroundings`, and `queryCollectionSearchSections`, all typed from the collection definitions.

```ts
const { data: posts } = await useAsyncData('blog', () =>
  queryCollection('posts').all(),
)
```

### Content rendering and v2 removals (module-major-launches)

`ContentRenderer` renders queried content, `Slot` replaces `ContentSlot`, and Prose components provide MDC rendering. The v2 document-driven mode was removed.

```vue
<ContentRenderer v-if="page" :value="page" />
```

### Integrated Preview API (module-major-launches)

Studio no longer needs a separate module: Content v3 exposes a provider-neutral Preview API configured under `content.preview`.

```ts
export default defineNuxtConfig({
  content: { preview: { api: 'https://api.nuxt.studio' } },
})
```

### SQL-backed Content storage (module-major-launches)

Nuxt Content v3 replaces file-backed storage with SQL while retaining Markdown, YAML, and JSON inputs and zero-config development, server, and static-generation support. Serverless deployments select a persistent adapter from the configured database type; in the browser, the first query downloads a dump into WASM SQLite and later queries run locally.

### Typed content collections (module-major-launches)

Collections are defined in `content.config.ts`; their type, source glob, and Zod schema drive the database shape and generated utility types.

```ts
import { defineCollection, z } from '@nuxt/content'

export const collections = {
  posts: defineCollection({
    type: 'page',
    source: 'blog/**/*.md',
    schema: z.object({ date: z.date() }),
  }),
}
```

## Nuxt Icon

### Layered dynamic icon delivery (module-major-launches)

Nuxt Icon resolves icons from the client bundle or SSR payload first, then its application server endpoint and server bundle. Unknown dynamic icons fall back to Iconify through that cached server endpoint, rather than every client querying Iconify directly.

### Nuxt Icon SSR rendering modes (module-major-launches)

Nuxt Icon v1's `<Icon>` supports CSS and SVG rendering per icon, with both modes rendered during SSR. CSS mode emits the icon through CSS without a client runtime, while SVG mode inlines it into the server-rendered HTML.

```vue
<Icon name="i-lucide-activity" />
```

## Nuxt Image

### Component element and slot access (nuxt-image)

A `<NuxtImg>` template ref exposes its native image element as `imgEl`. The custom default slots of `<NuxtImg>` and `<NuxtPicture>` are also typed and provide `imgAttrs`, `isLoaded`, and the computed `src`.

```vue
<script setup lang="ts">
const image = useTemplateRef('image')
onMounted(() => console.log(image.value?.imgEl))
</script>

<template>
  <NuxtImg ref="image" src="/image.jpg" custom>
    <template #default="{ imgAttrs, isLoaded, src }">
      <img v-bind="imgAttrs" :src="src">
      <span v-if="!isLoaded">Loading...</span>
    </template>
  </NuxtImg>
</template>
```

### Custom provider contract (nuxt-image)

Custom providers must now default-export a provider created with `defineProvider`; the v1 named `getImage` export no longer implements the provider contract.

```ts
import { defineProvider } from '@nuxt/image/runtime'

export default defineProvider({
  getImage(src, { baseURL = '' }) {
    return { url: `${baseURL}${src}` }
  },
})
```

### Image directories in layers (nuxt-image)

Custom image directories inside Nuxt layers are now supported, allowing a layer to carry its own image assets.

### Image helpers in server endpoints (nuxt-image)

`useImage()` is now available directly in Nitro event handlers, so server routes can generate provider-aware image URLs.

```ts
export default defineEventHandler(() => {
  const img = useImage()
  return { url: img('/hero.jpg', { width: 1200, height: 630, fit: 'cover' }) }
})
```

### Nuxt Image v2 compatibility and types (nuxt-image)

Nuxt Image v2 requires Nuxt 3.1 or later. It fully types `$img`, `useImage()`, module options, and provider-specific requirements such as a mandatory `baseURL`; upgrade with `npm install @nuxt/image@latest`.

### Provider and breakpoint migration (nuxt-image)

The deprecated `layer0` and `edgio` providers are removed. Custom providers that used `joinWith` for URL parameters must move to a `formatter` function with `createOperationsGenerator`; the default screen map now follows Tailwind CSS and no longer includes `xs` at 320px or `xxl` at 2560px.

### Shopify and GitHub providers (nuxt-image)

Nuxt Image v2 adds a Shopify provider configured with the store `baseURL`, plus a GitHub provider for avatars and user content.

```ts
export default defineNuxtConfig({
  image: {
    provider: 'shopify',
    shopify: { baseURL: 'https://your-store.myshopify.com' },
  },
})
```

```vue
<NuxtImg provider="github" src="nuxt" width="50" height="50" />
```

## Nuxt Scripts

### Consent and interaction triggers (module-major-launches)

Scripts can load through a custom trigger or an explicit `load()` call. `useScriptTriggerConsent()` gates loading on user consent, while element-event triggers can defer scripts until interactions such as clicks, scrolling, or form submissions.

```ts
const consent = useScriptTriggerConsent()
const { proxy } = useScript<{ greeting: () => void }>('/hello.js', {
  trigger: consent,
})

proxy.greeting()
consent.accept()
```

### First-party script bundling (module-major-launches)

Set `bundle: true` to copy a remote third-party script into the application's public output and serve it from the same origin at `/_scripts/{hash}`.

```ts
useScript('https://cdn.jsdelivr.net/npm/js-confetti@latest/dist/js-confetti.browser.js', {
  bundle: true,
})
```

### First-party script registry (module-major-launches)

Registry composables wrap common providers with typed APIs, development-time option validation, and environment-variable support.

```ts
const { proxy } = useScriptFathomAnalytics({ site: undefined })
proxy.trackPageview()
```

### Headless script facades (module-major-launches)

The registry includes accessible, unstyled facade components for providers such as YouTube, Google Maps, and Intercom. They render a lightweight stand-in and hydrate the third-party integration when its script loads.

```vue
<ScriptYouTubePlayer video-id="d_IFKP1Ofq0" />
```

### Nuxt Scripts installation prompts (since 3.12.0)

Nuxt includes composable stubs that prompt the developer to install `@nuxt/scripts` when a Nuxt Scripts composable is used.

### Typed, SSR-safe third-party script access (module-major-launches)

Nuxt Scripts' `useScript` exposes load state and a typed proxy that safely defers calls made during SSR or before the script is available. Scripts load during Nuxt hydration by default, but a trigger can delay them.

```ts
declare global {
  interface Window {
    helloWorld: { greeting: () => void }
  }
}

const { proxy, onLoaded } = useScript('/hello.js', {
  trigger: 'onNuxtReady',
  use: () => window.helloWorld,
})

onLoaded(api => console.log(api))
proxy.greeting()
```

## Nuxt UI

### AI SDK v5 chat components (nuxt-ui)

The v4 AI chat components support Vercel AI SDK v5's `Chat` class and its `parts`-based message format, which is the shape to use when integrating the current chat APIs.

### Nuxt UI v3 platform rewrite (nuxt-ui)

Nuxt UI v3 replaces Headless UI with Reka UI primitives and integrates Tailwind CSS v4. The rewrite changes the migration surface while making keyboard navigation, ARIA attributes, focus management, and screen-reader behavior part of the interactive components.

### Semantic design tokens and typed theming (nuxt-ui)

The v3 design system provides the `primary`, `secondary`, `success`, `info`, `warning`, `error`, and `neutral` color aliases plus theme-aware utilities such as `bg-muted`, `text-highlighted`, and `text-muted`. Global component slots and default variants are type-checked through app config.

```ts
export default defineAppConfig({
  ui: {
    button: {
      slots: { base: 'font-bold rounded-lg' },
      defaultVariants: { size: 'md', color: 'error' },
    },
  },
})
```

### Standalone Vue support (nuxt-ui)

Nuxt UI v3 works in ordinary Vue applications through its Vite plugin, with theming, auto-imports, and TypeScript support outside Nuxt. With pnpm, either set `shamefully-hoist=true` or install `tailwindcss` in the project root.

```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import ui from '@nuxt/ui/vite'

export default defineConfig({
  plugins: [vue(), ui()],
})
```

### Unified Nuxt UI v4 package (nuxt-ui)

Nuxt UI v4 folds the formerly separate Pro component suite into the free `@nuxt/ui` package. Most v3 component code remains compatible because migration focuses on unification; use the first command below for a new starter or the second in an existing project.

```sh
npm create nuxt@latest -- -t ui
npm install @nuxt/ui@latest
```

## Package discovery

### Packaged documentation sources (since 3.17.0)

Install `@nuxt/docs` to consume the raw Markdown and YAML sources used by the Nuxt documentation site.
