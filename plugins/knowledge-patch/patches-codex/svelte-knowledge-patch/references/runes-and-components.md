# Runes and components

## Reactive dependency tracking

### Dependencies across `await`

In `$derived`, a reactive read after an `await` written directly in the derived
expression remains a dependency (`5.0.0-runes`). This special handling does not
extend to an `await` hidden inside a helper called by that expression.

```svelte
<script>
	let a = $state(Promise.resolve(1));
	let b = $state(2);
	let total = $derived(await a + b);
</script>
```

### Effect reads are synchronous and per-run

An `$effect` subscribes only to reactive values synchronously read during its
latest execution. Reads after `await` or inside timers do not become
dependencies. Reading a state proxy object does not observe later changes to
its properties; read the particular property that should trigger the effect.

```js
$effect(() => state);       // does not rerun for state.value mutations
$effect(() => state.value); // reruns when state.value changes
```

## Derived and state values

### Overridable derived values

A `$derived` binding declared with `let` can be reassigned for optimistic UI.
The assigned value remains until a dependency next changes and recalculates the
derived expression. Derived bindings were read-only before Svelte 5.25.

```svelte
<script>
	let { post } = $props();
	let likes = $derived(post.likes);
	function optimisticLike() {
		likes += 1;
	}
</script>
```

### Destructuring and proxy behavior

Destructuring directly from `$derived(...)` creates individually reactive
bindings. Other derived results are returned as-is rather than deep-proxied.
By contrast, destructuring a `$state` proxy is ordinary JavaScript and captures
non-reactive property values.

```js
let { a, b } = $derived(makeValues()); // reactive bindings
let { done } = todos[0];               // property snapshot
```

### Pending and eager asynchronous UI

Within a component that uses `await`, `$effect.pending()` reports pending
promises in the current boundary and excludes child boundaries.
`$state.eager(value)` opts a displayed value out of synchronized await updates,
allowing immediate feedback while asynchronous work finishes.

```svelte
{#if $effect.pending()}<p>pending: {$effect.pending()}</p>{/if}
<a aria-current={$state.eager(pathname) === '/' ? 'page' : null} href="/">home</a>
```

## Props, identity, and classes

### Fallbacks and state ownership

Fallback objects produced while destructuring `$props()` are not state
proxies. Mutating such a fallback does not update the UI. Mutating a
parent-owned state proxy does update it, but emits an ownership warning unless
the prop is explicitly bindable.

```js
let { options = { enabled: false } } = $props();
```

Mark the prop bindable before using it for intentional writes to parent state.

### Hydration-stable IDs

`$props.id()` returns a component-instance ID that is stable across server
rendering and hydration. Use it for label, description, and ARIA relationships.

```svelte
<script>const uid = $props.id();</script>
<label for="{uid}-name">Name</label>
<input id="{uid}-name" />
```

### Reactive class-field enumeration

Class fields initialized with `$state` compile to prototype accessors backed
by private fields, so they are non-enumerable. Spreading or serializing an
instance will not include them; expose serializable values explicitly.

## Element attachments

### Attach lifecycle behavior

An attachment runs with an element when it mounts and may return cleanup logic
for removal. Apply it with `{@attach ...}`.

```svelte
<script>
	const autofocus = (node) => {
		node.focus();
		return () => {};
	};
</script>

<input {@attach autofocus} />
```

### Adapt existing actions

`fromAction` from `svelte/attachments` converts an existing action into an
attachment. When the action takes an argument, pass a function that returns
the value as the second argument, not the value itself.

```svelte
<script>
	import { fromAction } from 'svelte/attachments';
	const title = (node, value) => { node.title = value; };
	const message = 'More details';
</script>

<div {@attach fromAction(title, () => message)}>Hover me</div>
```

### Put attachments in spread props

Since Svelte 5.29, `createAttachmentKey()` returns a symbol whose property acts
as an attachment when its containing object is spread onto an element. This is
primarily useful for library-authored prop objects.

```svelte
<script>
	import { createAttachmentKey } from 'svelte/attachments';
	const props = {
		[createAttachmentKey()]: (node) => { node.textContent = 'attached'; }
	};
</script>

<button {...props}>waiting</button>
```

## Snippets and template declarations

### Snippet parameter limits

Snippet parameters accept defaults and destructuring, but not rest parameters.

```svelte
{#snippet badge({ label }, prefix = '')}
	<span>{prefix}{label}</span>
{/snippet}

{@render badge({ label: 'New' }, 'Status: ')}
```

### Export snippets safely

Since Svelte 5.5, a top-level snippet in a `.svelte` file can be exported from
`<script module>`. It must not depend, directly or through another snippet, on
declarations from the instance-level `<script>`.

```svelte
<script module>
	export { add };
</script>

{#snippet add(a, b)}
	{a} + {b} = {a + b}
{/snippet}
```

Use `createRawSnippet` from `svelte` for advanced programmatic snippet
construction instead of a `{#snippet ...}` block.

### Declare values in template scope

Svelte 5.56 accepts `let` and `const` declaration tags in template scope. One
tag may contain multiple declarators, and later initializers can use earlier
declarations, including rune-initialized values.

```svelte
{let count = $state(0), doubled = $derived(count * 2)}
<button onclick={() => count++}>{doubled}</button>
```

HTML comments are accepted between attributes inside an opening tag:

```svelte
<button
	<!-- explains the next attribute -->
	disabled
>
	Save
</button>
```

## Programmatic contexts and asynchronous templates

Programmatic Svelte context creation supports typed `createContext` usage, so
context values retain their types without untyped keys.

An `{@const}` declaration can await a value in asynchronous template work:

```svelte
{#if task}
	{@const value = await task}
	<p>{value}</p>
{/if}
```

Svelte also has an experimental asynchronous server-rendering path that waits
for asynchronous template work while producing SSR output. Treat it as
experimental when choosing production behavior.
