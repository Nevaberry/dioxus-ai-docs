# Svelte 5 Snippets, Events, and Component API

## Snippets replace slots

Slots are deprecated in Svelte 5. Use `{#snippet}` to define and `{@render}` to render.

### Default content — `children` prop

Content inside component tags becomes the `children` snippet prop. The name `children` is reserved.

```svelte
<!-- Card.svelte -->
<script>
  let { children } = $props();
</script>
<div class="card">
  {@render children?.()}
</div>

<!-- Usage -->
<Card>
  <p>This becomes the children snippet</p>
</Card>
```

### Named snippets

Replace named slots. Snippets can receive parameters (replaces `let:` directive).

```svelte
<!-- Parent -->
<DataTable {items}>
  {#snippet header()}
    <tr><th>Name</th><th>Age</th></tr>
  {/snippet}

  {#snippet row(item)}
    <tr><td>{item.name}</td><td>{item.age}</td></tr>
  {/snippet}

  {#snippet empty()}
    <tr><td colspan="2">No data</td></tr>
  {/snippet}
</DataTable>

<!-- DataTable.svelte -->
<script>
  let { items, header, row, empty } = $props();
</script>
<table>
  <thead>{@render header()}</thead>
  <tbody>
    {#if items.length}
      {#each items as item}
        {@render row(item)}
      {/each}
    {:else}
      {@render empty?.()}
    {/if}
  </tbody>
</table>
```

### Standalone snippets

Snippets can be defined and used locally (not just as component props):

```svelte
{#snippet figure(src, caption)}
  <figure>
    <img {src} alt={caption} />
    <figcaption>{caption}</figcaption>
  </figure>
{/snippet}

{@render figure('/photo1.jpg', 'First photo')}
{@render figure('/photo2.jpg', 'Second photo')}
```

## Event handlers

### DOM events — properties not directives

`on:event` directive replaced with `onevent` property:

```svelte
<!-- Svelte 4 -->
<button on:click={handler}>Click</button>
<button on:click|preventDefault={handler}>Click</button>
<button on:click={one} on:click={two}>Click</button>

<!-- Svelte 5 -->
<button onclick={handler}>Click</button>
<button onclick={(e) => { e.preventDefault(); handler(e); }}>Click</button>
<button onclick={(e) => { one(e); two(e); }}>Click</button>
```

Capture: `<button onclickcapture={handler}>`.

### Component events — callback props

`createEventDispatcher` is deprecated. Pass callbacks as props:

```svelte
<!-- SearchInput.svelte -->
<script>
  let { onsearch, value = $bindable('') } = $props();
</script>
<input bind:value onkeydown={(e) => e.key === 'Enter' && onsearch?.(value)} />

<!-- Parent -->
<SearchInput onsearch={(query) => search(query)} />
```

### Event forwarding via spread

```svelte
<script>
  let { ...props } = $props();
</script>
<button {...props}>Click me</button>
```

## Component instantiation

Components are functions, not classes.

### mount / hydrate / unmount

```js
import { mount, hydrate, unmount } from 'svelte';
import App from './App.svelte';

// Client-side mount
const app = mount(App, {
  target: document.getElementById('app'),
  props: { name: 'world' },
  intro: true, // play intro transitions
});

// Hydrate server-rendered HTML
const app = hydrate(App, {
  target: document.getElementById('app'),
  props: { name: 'world' },
});

// Unmount (with optional outro transitions)
unmount(app, { outro: true }); // returns Promise
```

Note: `mount` and `hydrate` are not synchronous — `onMount` callbacks haven't fired when they return. Use `flushSync` from `'svelte'` if needed.

### Server-side rendering

```js
import { render } from 'svelte/server';
import App from './App.svelte';

const { html, head } = render(App, { props: { message: 'hello' } });
```

### Dynamic components

`<svelte:component>` is no longer needed — components can be used dynamically directly:

```svelte
<script>
  let Component = $state(ComponentA);
</script>
<Component />
```

Dot notation also works: `<item.component {...item.props} />`.

## TypeScript

Use `Component` type instead of deprecated `SvelteComponent`:

```ts
import type { Component } from 'svelte';

// Define component shape
export declare const MyButton: Component<{
  label: string;
  onclick?: () => void;
}>;
```

`ComponentEvents` and `ComponentType` are deprecated.

## Migration

- Automated: `npx sv migrate svelte-5`
- Per-component in VS Code: "Migrate Component to Svelte 5 Syntax"
- New CLI: `npx sv create` (replaces `create-svelte`)
- Vite plugin: `@sveltejs/vite-plugin-svelte` v4
