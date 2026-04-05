# Svelte 5 Runes Reference

Runes are compiler instructions using `$` prefix. They work in `.svelte`, `.svelte.js`, and `.svelte.ts` files.

## $state — Reactive state

Replaces Svelte 4's implicit `let` reactivity.

```svelte
<script>
  let count = $state(0);       // primitive
  let items = $state([1, 2]);  // deeply reactive (Proxy-based)
</script>
```

### $state.raw — Shallow reactivity

Only reassignment triggers updates (no Proxy). Better performance for large arrays/objects you replace wholesale.

```js
let data = $state.raw([1, 2, 3]);
data.push(4);         // NO update
data = [...data, 4];  // triggers update
```

### $state.snapshot — Plain copy

Returns a non-reactive plain object/array. Use when passing state to external libraries (e.g., `structuredClone`-like).

```js
let obj = $state({ nested: { x: 1 } });
console.log($state.snapshot(obj)); // plain object
```

## $derived — Computed values

Replaces `$:` for derivations. Dependencies tracked at runtime.

```svelte
<script>
  let count = $state(0);
  let doubled = $derived(count * 2);

  // Complex derivations:
  let total = $derived.by(() => {
    return items.reduce((sum, i) => sum + i.price, 0);
  });
</script>
```

## $effect — Side effects

Replaces `$:` for side effects. Runs after DOM update. Dependencies tracked at runtime.

```svelte
<script>
  let count = $state(0);

  $effect(() => {
    document.title = `Count: ${count}`;
    return () => { /* cleanup on re-run or destroy */ };
  });
</script>
```

Key differences from `$:`:
- Only runs in the browser (not SSR)
- Runs after DOM updates (not before rendering)
- Dependencies determined at runtime (immune to refactoring)
- Runs as often as needed (not once per tick)

### $effect.pre

Runs before DOM updates (equivalent to Svelte 4's `beforeUpdate`).

```js
$effect.pre(() => {
  // runs before DOM is updated
});
```

## $props — Component props

Replaces `export let`. Uses destructuring syntax.

```svelte
<script>
  // Basic
  let { name, count = 0 } = $props();

  // Rename reserved words
  let { class: klass, ...rest } = $props();

  // Don't destructure for spreading all
  let props = $props();
</script>
<div class={klass} {...rest}>...</div>
```

## $bindable — Opt-in two-way binding

In runes mode, props are NOT bindable by default. Mark with `$bindable()`:

```svelte
<script>
  let { value = $bindable('default') } = $props();
</script>

<!-- Parent: <Input bind:value={text} /> -->
```

## $inspect — Dev-only debugging

Stripped from production builds. Logs when tracked values change.

```svelte
<script>
  let count = $state(0);
  $inspect(count);                    // console.log on change
  $inspect(count).with(console.trace); // custom handler
</script>
```

## Shared reactive logic (.svelte.js/.svelte.ts)

Runes work in `.svelte.js` and `.svelte.ts` files — use for reusable reactive logic outside components.

```js
// counter.svelte.js
export function createCounter(initial = 0) {
  let count = $state(initial);
  return {
    get count() { return count },
    increment: () => count += 1,
    reset: () => count = initial,
  };
}
```

```svelte
<script>
  import { createCounter } from './counter.svelte.js';
  const counter = createCounter();
</script>
<button onclick={counter.increment}>{counter.count}</button>
```
