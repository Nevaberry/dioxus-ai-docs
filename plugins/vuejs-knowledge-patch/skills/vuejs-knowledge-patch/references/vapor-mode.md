# Vue 3.6 Vapor Mode

## Overview

Vapor Mode is a new compilation mode for Vue SFCs that bypasses the virtual DOM, generating code that directly manipulates the DOM. It is 100% opt-in and supports a subset of existing Vue APIs with mostly identical behavior.

**Status**: Beta (v3.6.0-beta.1 released Dec 2025). Stable release expected later 2026.

Recommended use cases during beta:
- Partial usage in existing apps for perf-sensitive sub-pages
- Small new apps built entirely in Vapor Mode

## Opting In

Only works with Composition API using script setup. Add the `vapor` attribute:

```html
<script setup vapor>
import { ref, computed, watchEffect } from 'vue'

const count = ref(0)
const doubled = computed(() => count.value * 2)
</script>

<template>
  <button @click="count++">{{ count }} ({{ doubled }})</button>
</template>
```

## App Creation

### Pure Vapor App

No VDOM runtime included — smallest possible bundle:

```js
import { createVaporApp } from 'vue'
import App from './App.vue'

createVaporApp(App).mount('#app')
```

### Mixed VDOM + Vapor

Incremental adoption — use Vapor components inside a regular VDOM app:

```js
import { createApp, vaporInteropPlugin } from 'vue'
import App from './App.vue'

createApp(App)
  .use(vaporInteropPlugin)
  .mount('#app')
```

A Vapor app can also install `vaporInteropPlugin` to use VDOM components inside it, but this pulls in the VDOM runtime and offsets the smaller bundle benefit.

## Custom Directives in Vapor

Vapor custom directives have a different interface from VDOM directives:

```ts
type VaporDirective = (
  node: Element | VaporComponentInstance,
  value?: () => any,      // reactive getter for binding value
  argument?: string,
  modifiers?: DirectiveModifiers,
) => (() => void) | void  // optional cleanup function
```

The `value` parameter is a reactive getter. Use `watchEffect` for reactive effects. Optionally return a cleanup function:

```ts
const vHighlight: VaporDirective = (el, color) => {
  watchEffect(() => {
    ;(el as HTMLElement).style.backgroundColor = color?.() ?? 'yellow'
  })
  return () => {
    ;(el as HTMLElement).style.backgroundColor = ''
  }
}
```

## Feature Restrictions

**Not supported in Vapor Mode:**
- Options API (only Composition API with script setup)
- `app.config.globalProperties`
- `getCurrentInstance()` — returns `null` in Vapor components
- `@vue:xxx` per-element lifecycle events (e.g., `@vue:mounted`)

**Supported features:**
- All Composition API: `ref`, `reactive`, `computed`, `watch`, `watchEffect`, lifecycle hooks
- `<Teleport>` (VDOM `<Teleport>` can render Vapor content)
- `<Suspense>` (VDOM `<Suspense>` can wrap Vapor components)
- `<Transition>` and `<TransitionGroup>`
- `v-model`, `v-if`/`v-else`/`v-else-if`, `v-for`, `v-show`, `v-once`
- `v-bind()` in CSS
- Slots, props, emits, attrs fallthrough
- `defineExpose`, `defineProps`, `defineEmits`
- Custom directives (with Vapor-specific interface above)

## VDOM Interop Limitations

When `vaporInteropPlugin` is installed, Vapor and VDOM components can be nested inside each other. Standard props, events, and slots work, but edge cases exist:

**Known issue:** Vapor slots cannot be rendered with `slots.default()` inside a VDOM component — `renderSlot` must be used instead.

**Recommendation:** Have distinct "regions" in your app where it's one mode or another. Avoid deeply mixed nesting, especially with VDOM-based component libraries in Vapor Mode.

## Additional Vapor APIs

These were added during the alpha/beta cycle:

- `defineVaporComponent` — component definition with type inference
- `defineVaporCustomElement` — custom element definition with type inference
- `v-once` for slot outlets
- Dynamic component support via `createDynamicComponent`
