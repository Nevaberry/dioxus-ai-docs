# Ecosystem modules

Use this reference for current Nuxt Scripts, Icon, Content, UI, and Image package contracts. Confirm each installed module major before applying its migration guidance.

## Contents

- [Documentation sources](#documentation-sources)
- [Nuxt Scripts](#nuxt-scripts)
- [Nuxt Icon](#nuxt-icon)
- [Nuxt Content](#nuxt-content)
- [Nuxt UI](#nuxt-ui)
- [Nuxt Image](#nuxt-image)

## Documentation sources

### Install Nuxt Scripts from composable prompts (3.12.0)

Nuxt provides composable stubs that prompt installation of `@nuxt/scripts` when a Nuxt Scripts composable is used in a project without the module.

### Consume packaged Nuxt documentation sources (3.17.0)

Install `@nuxt/docs` to access the raw Markdown and YAML sources used by the Nuxt documentation site.

## Nuxt Scripts

### Access third-party scripts through an SSR-safe proxy (module-major-launches)

`useScript` exposes load state and a typed proxy. Calls made during SSR or before the remote script is available are deferred safely. Scripts load during Nuxt hydration by default; use a trigger to delay them.

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

### Prefer typed registry composables for known providers (module-major-launches)

First-party registry composables wrap common providers with typed APIs, development-time option validation, and environment-variable support.

```ts
const { proxy } = useScriptFathomAnalytics({ site: undefined })
proxy.trackPageview()
```

### Use accessible headless facades (module-major-launches)

Registry facade components for providers such as YouTube, Google Maps, and Intercom render an accessible, unstyled stand-in and hydrate the real integration after its script loads.

```vue
<ScriptYouTubePlayer video-id="d_IFKP1Ofq0" />
```

### Gate scripts on consent or interaction (module-major-launches)

Use a custom trigger or explicit `load()`. `useScriptTriggerConsent()` waits for user consent; element-event triggers can wait for clicks, scroll, or form submission.

```ts
const consent = useScriptTriggerConsent()
const { proxy } = useScript<{ greeting: () => void }>('/hello.js', {
  trigger: consent,
})

proxy.greeting()
consent.accept()
```

### Bundle a remote script as a first-party asset (module-major-launches)

Set `bundle: true` to copy a remote script into public output and serve it from the same origin at `/_scripts/{hash}`.

```ts
useScript(
  'https://cdn.jsdelivr.net/npm/js-confetti@latest/dist/js-confetti.browser.js',
  { bundle: true },
)
```

## Nuxt Icon

### Choose SSR-rendered CSS or SVG icons (module-major-launches)

Nuxt Icon v1's `<Icon>` supports per-icon CSS and SVG rendering. Both render during SSR. CSS mode emits an icon through CSS without a client runtime; SVG mode inlines it into server HTML.

```vue
<Icon name="i-lucide-activity" />
```

### Understand dynamic icon delivery (module-major-launches)

Nuxt Icon resolves an icon from the client bundle or SSR payload first, then from the application server endpoint and server bundle. Unknown dynamic icons fall back to Iconify through that cached server endpoint instead of every client contacting Iconify directly.

## Nuxt Content

### Migrate to SQL-backed Content storage (module-major-launches)

Nuxt Content v3 replaces file-backed storage with SQL while retaining Markdown, YAML, and JSON inputs and zero-config development, server, and static-generation workflows. Serverless deployments select a persistent adapter from the configured database type. In the browser, the first query downloads a dump into WASM SQLite and later queries run locally.

### Define typed collections in `content.config.ts` (module-major-launches)

Specify each collection's type, source glob, and Zod schema. These definitions control the database shape and generated utility types.

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

### Query collections through typed utilities (module-major-launches)

Use `queryCollection`, `queryCollectionNavigation`, `queryCollectionItemSurroundings`, and `queryCollectionSearchSections`. Their types derive from collection definitions.

```ts
const { data: posts } = await useAsyncData('blog', () =>
  queryCollection('posts').all(),
)
```

### Render queried content and remove v2 APIs (module-major-launches)

Render a queried value with `ContentRenderer`. Use `Slot` instead of removed `ContentSlot`, and Prose components for MDC rendering. Document-driven mode from Content v2 is removed.

```vue
<ContentRenderer v-if="page" :value="page" />
```

### Configure the integrated Preview API (module-major-launches)

Content v3 includes a provider-neutral Preview API, so Studio does not require a separate module.

```ts
export default defineNuxtConfig({
  content: { preview: { api: 'https://api.nuxt.studio' } },
})
```

## Nuxt UI

### Migrate the v3 primitive and styling stack (nuxt-ui)

Nuxt UI v3 replaces Headless UI with Reka UI primitives and integrates Tailwind CSS v4. Recheck component migration details and styling while relying on built-in keyboard navigation, ARIA attributes, focus management, and screen-reader behavior.

### Use semantic tokens and typed theming (nuxt-ui)

The design system provides `primary`, `secondary`, `success`, `info`, `warning`, `error`, and `neutral` color aliases plus utilities such as `bg-muted`, `text-highlighted`, and `text-muted`. Configure global slots and default variants in app config; their shapes are type-checked.

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

### Use Nuxt UI in a standalone Vue application (nuxt-ui)

Install the Vite plugin for theming, auto-imports, and TypeScript outside Nuxt. With pnpm, either set `shamefully-hoist=true` or install `tailwindcss` in the project root.

```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import ui from '@nuxt/ui/vite'

export default defineConfig({
  plugins: [vue(), ui()],
})
```

### Use the unified Nuxt UI v4 package (nuxt-ui)

Nuxt UI v4 folds the formerly separate Pro suite into the free `@nuxt/ui` package. Most v3 component code remains compatible because the principal migration is package unification.

```sh
npm create nuxt@latest -- -t ui
npm install @nuxt/ui@latest
```

### Match AI SDK v5 message shapes (nuxt-ui)

Nuxt UI v4 chat components support Vercel AI SDK v5's `Chat` class and `parts`-based message format. Use that shape for current chat integrations.

## Nuxt Image

### Upgrade with the v2 compatibility and type contract (nuxt-image)

Nuxt Image v2 requires Nuxt 3.1 or later and fully types `$img`, `useImage()`, module options, and provider-specific requirements such as a mandatory `baseURL`.

```sh
npm install @nuxt/image@latest
```

### Default-export custom providers through `defineProvider` (nuxt-image)

The v1 named `getImage` export no longer satisfies the provider contract.

```ts
import { defineProvider } from '@nuxt/image/runtime'

export default defineProvider({
  getImage(src, { baseURL = '' }) {
    return { url: `${baseURL}${src}` }
  },
})
```

### Generate provider-aware URLs in server endpoints (nuxt-image)

`useImage()` is available directly in Nitro handlers.

```ts
export default defineEventHandler(() => {
  const img = useImage()
  return {
    url: img('/hero.jpg', { width: 1200, height: 630, fit: 'cover' }),
  }
})
```

### Access the image element and typed custom slots (nuxt-image)

A `<NuxtImg>` template ref exposes its native image element as `imgEl`. Custom default slots for `<NuxtImg>` and `<NuxtPicture>` provide typed `imgAttrs`, `isLoaded`, and computed `src` values.

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

### Configure Shopify and GitHub providers (nuxt-image)

Nuxt Image v2 adds a Shopify provider configured with the store `baseURL` and a GitHub provider for avatars and user content.

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

### Carry image directories inside layers (nuxt-image)

Custom image directories within Nuxt layers are supported, allowing a layer to package its own image assets.

### Remove retired providers and update operations (nuxt-image)

The deprecated `layer0` and `edgio` providers are removed. Replace custom-provider `joinWith` URL-parameter logic with a `formatter` function and `createOperationsGenerator`. The default screen map follows Tailwind CSS and no longer includes `xs` at 320px or `xxl` at 2560px.
