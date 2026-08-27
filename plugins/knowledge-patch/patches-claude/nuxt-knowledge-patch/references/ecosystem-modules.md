# Ecosystem modules

## Nuxt Scripts

Nuxt includes composable stubs that prompt installation of `@nuxt/scripts` when a Scripts composable is used (3.12.0).

### Typed, SSR-safe script access

`useScript` exposes load state and a typed proxy. Calls made during SSR or before loading are deferred safely. Scripts load during hydration by default; set a trigger to delay them (module-major-launches).

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

Registry composables wrap common providers with typed APIs, development-time option validation, and environment-variable support. Accessible, unstyled facade components for services such as YouTube, Google Maps, and Intercom render lightweight stand-ins and hydrate the integration when its script loads (module-major-launches).

### Consent, interaction, and bundling

Load scripts through a custom trigger or explicit `load()`. `useScriptTriggerConsent()` gates loading on consent; element-event triggers defer it until clicks, scrolling, or form submission (module-major-launches).

```ts
const consent = useScriptTriggerConsent()
const { proxy } = useScript<{ greeting: () => void }>('/hello.js', {
  trigger: consent,
})

proxy.greeting()
consent.accept()
```

Set `bundle: true` to copy a remote script into public output and serve it from the same origin at `/_scripts/{hash}` (module-major-launches).

## Nuxt Icon v1

`<Icon>` supports CSS and SVG rendering per icon, and both render during SSR. CSS mode emits CSS without a client runtime; SVG mode inlines the icon in server HTML (module-major-launches).

Dynamic resolution checks the client bundle or SSR payload, then the application server endpoint and server bundle. Unknown icons fall back to Iconify through the cached server endpoint instead of each browser querying Iconify directly (module-major-launches).

## Nuxt Content v3

Content v3 replaces file-backed storage with SQL while retaining Markdown, YAML, JSON, zero-config development, server use, and static generation. Serverless deployments choose a persistent adapter from the configured database type. In browsers, the first query downloads a dump into WASM SQLite and later queries run locally (module-major-launches).

### Typed collections and queries

Define collections in `content.config.ts`; collection type, source glob, and Zod schema determine the database shape and generated utility types (module-major-launches).

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

Use the typed `queryCollection`, `queryCollectionNavigation`, `queryCollectionItemSurroundings`, and `queryCollectionSearchSections` APIs (module-major-launches).

```ts
const { data: posts } = await useAsyncData('blog', () =>
  queryCollection('posts').all(),
)
```

### Rendering and Preview API

Render queried content with `ContentRenderer`; `Slot` replaces `ContentSlot`, Prose components handle MDC, and document-driven mode is removed. Studio no longer needs a separate module: configure the provider-neutral Preview API under `content.preview` (module-major-launches).

## Nuxt UI

### v3 rewrite

Nuxt UI v3 replaces Headless UI with Reka UI primitives and integrates Tailwind CSS v4. Its interactive components provide keyboard navigation, ARIA behavior, focus management, and screen-reader support (nuxt-ui).

Semantic colors include `primary`, `secondary`, `success`, `info`, `warning`, `error`, and `neutral`, with utilities such as `bg-muted`, `text-highlighted`, and `text-muted`. Global slots and default variants configured through app config are type-checked (nuxt-ui).

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

Nuxt UI v3 also works in ordinary Vue applications through `@nuxt/ui/vite`, with theming, auto-imports, and TypeScript. With pnpm, enable `shamefully-hoist=true` or install `tailwindcss` at the project root (nuxt-ui).

### Unified v4 package

Nuxt UI v4 folds the formerly separate Pro suite into free `@nuxt/ui`; most v3 component code remains compatible because the primary migration is package unification (nuxt-ui).

```sh
npm create nuxt@latest -- -t ui
npm install @nuxt/ui@latest
```

The v4 AI chat components use Vercel AI SDK v5's `Chat` class and `parts`-based message shape (nuxt-ui).

## Nuxt Image v2

Nuxt Image v2 requires Nuxt 3.1 or later and types `$img`, `useImage()`, module options, and provider requirements such as mandatory `baseURL` fields. Upgrade with `npm install @nuxt/image@latest` (nuxt-image).

### Custom providers

Default-export a provider made with `defineProvider`; the v1 named `getImage` export no longer satisfies the contract (nuxt-image).

```ts
import { defineProvider } from '@nuxt/image/runtime'

export default defineProvider({
  getImage(src, { baseURL = '' }) {
    return { url: `${baseURL}${src}` }
  },
})
```

`useImage()` is available in Nitro event handlers for provider-aware URLs (nuxt-image):

```ts
export default defineEventHandler(() => {
  const img = useImage()
  return { url: img('/hero.jpg', { width: 1200, height: 630, fit: 'cover' }) }
})
```

### Components, providers, and layers

A `<NuxtImg>` ref exposes the native element as `imgEl`. Custom default slots on `<NuxtImg>` and `<NuxtPicture>` are typed and expose `imgAttrs`, `isLoaded`, and computed `src` (nuxt-image).

Nuxt Image v2 adds a Shopify provider configured by store `baseURL` and a GitHub provider for avatars and user content. Layers may include custom image directories and carry their own assets (nuxt-image).

### Provider migration

Remove the retired `layer0` and `edgio` providers. Replace custom-provider `joinWith` URL operations with a `formatter` and `createOperationsGenerator`. The default screen map follows Tailwind CSS and omits the former `xs` 320px and `xxl` 2560px breakpoints (nuxt-image).
