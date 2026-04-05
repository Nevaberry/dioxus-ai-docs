---
name: svelte-knowledge-patch
description: Svelte changes since training cutoff (latest: 5.0.0) — runes ($state, $derived, $effect, $props), snippets replacing slots, callback props replacing events, mount/hydrate API. Load before working with Svelte.
version: "5.0.0"
license: MIT
metadata:
  author: Nevaberry
---

# Svelte Knowledge Patch

Claude Opus 4.6 knows Svelte through 4.x and SvelteKit through 1.x. It is **unaware** of the features below, which cover Svelte 5.0 (released 2024-10-22).

## Index

| Topic | Reference | Key features |
|---|---|---|
| Runes | [references/runes.md](references/runes.md) | $state, $state.raw, $state.snapshot, $derived, $derived.by, $effect, $effect.pre, $props, $bindable, $inspect |
| Snippets & events | [references/snippets-and-events.md](references/snippets-and-events.md) | {#snippet}, {@render}, children prop, callback props, mount/hydrate/unmount, Component type |

---

## Quick Reference: Svelte 4 to 5 Migration

| Svelte 4 | Svelte 5 |
|---|---|
| `let count = 0` (top-level) | `let count = $state(0)` |
| `$: doubled = count * 2` | `let doubled = $derived(count * 2)` |
| `$: { sideEffect() }` | `$effect(() => { sideEffect() })` |
| `export let name` | `let { name } = $props()` |
| `export let value` + `bind:value` | `let { value = $bindable() } = $props()` |
| `<slot />` | `{@render children?.()}` with `let { children } = $props()` |
| `<slot name="header" />` | `{@render header()}` with `let { header } = $props()` |
| `<slot item={entry} />` + `let:item` | `{@render item(entry)}` + `{#snippet item(data)}...{/snippet}` |
| `on:click={handler}` | `onclick={handler}` |
| `on:click\|preventDefault` | `onclick={(e) => { e.preventDefault(); handler(e) }}` |
| `createEventDispatcher()` | Callback props: `let { onclick } = $props()` |
| `<svelte:component this={C} />` | `<C />` (dynamic by default) |
| `new Component({ target })` | `mount(Component, { target })` |
| `$$props` / `$$restProps` | `let props = $props()` / `let { ...rest } = $props()` |

---

## Runes

Runes are `$`-prefixed compiler instructions for reactivity. They work in `.svelte`, `.svelte.js`, and `.svelte.ts` files.

```svelte
<script>
  // Reactive state
  let count = $state(0);
  let items = $state([{ text: 'hello' }]); // deeply reactive

  // Computed values
  let doubled = $derived(count * 2);

  // Side effects (browser-only, runs after DOM update)
  $effect(() => {
    document.title = `Count: ${count}`;
    return () => { /* cleanup */ };
  });
</script>

<button onclick={() => count++}>
  {count} (doubled: {doubled})
</button>
```

### Props and bindings

```svelte
<script>
  let { label, count = 0, class: klass, ...rest } = $props();
  let { value = $bindable('') } = $props(); // opt-in two-way binding
</script>
```

---

## Snippets

Replace slots with `{#snippet}` and `{@render}`:

```svelte
<!-- Card.svelte -->
<script>
  let { title, children, footer } = $props();
</script>
<div class="card">
  <h2>{title}</h2>
  {@render children?.()}
  {#if footer}
    <div class="footer">{@render footer()}</div>
  {/if}
</div>

<!-- Usage -->
<Card title="Hello">
  <p>Default content goes here</p>
  {#snippet footer()}
    <button>OK</button>
  {/snippet}
</Card>
```

---

## Events

Event handlers are regular properties. No more `on:` directive or `createEventDispatcher`.

```svelte
<button onclick={handler}>Click</button>
```

Components accept callback props:

```svelte
<!-- Child -->
<script>
  let { onchange } = $props();
</script>
<input onchange={(e) => onchange?.(e.target.value)} />
```

---

## Component API

Components are functions. Use `mount`, `hydrate`, `unmount` from `'svelte'`:

```js
import { mount, unmount } from 'svelte';
import App from './App.svelte';
const app = mount(App, { target: document.body, props: { name: 'world' } });
// unmount(app, { outro: true });
```

SSR: `import { render } from 'svelte/server'`

---

## Shared Reactive Logic

Use `.svelte.js` / `.svelte.ts` files for runes outside components:

```js
// store.svelte.js
export function createTodos() {
  let items = $state([]);
  return {
    get items() { return items },
    add: (text) => items.push({ text, done: false }),
  };
}
```

---

## Reference Files

| File | Contents |
|---|---|
| [runes.md](references/runes.md) | $state, $state.raw, $state.snapshot, $derived, $derived.by, $effect, $effect.pre, $props, $bindable, $inspect, .svelte.js files |
| [snippets-and-events.md](references/snippets-and-events.md) | {#snippet}, {@render}, children prop, event properties, callback props, mount/hydrate/unmount, Component type, migration |
