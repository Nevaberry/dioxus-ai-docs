# Runes and components

The rune semantics in this reference are attributed to `5.0.0-runes`.

## Dependency tracking

### Await-aware derived dependencies

Reactive reads after an `await` written directly in a `$derived` expression
remain dependencies. This does not apply when the `await` is hidden inside a
function called by the expression.

```svelte
<script>
	let a = $state(Promise.resolve(1));
	let b = $state(2);
	let total = $derived(await a + b);
</script>
```

### Effect dependency granularity

An effect subscribes only to reactive values read synchronously during its
latest run. Reads after `await` or inside timers are not tracked. Reading a
state proxy object does not subscribe to mutations of all of its properties;
read the property that should trigger the effect.

```js
$effect(() => state);       // does not rerun when only state.value changes
$effect(() => state.value); // reruns when state.value changes
```

## Derived and state values

### Overridable derived values

A `$derived` binding declared with `let` can be reassigned for optimistic UI.
The override remains until a dependency changes and the expression recalculates.
Derived values were read-only before Svelte 5.25.

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
bindings. A derived result is otherwise returned as-is rather than being
deep-proxied. Ordinary destructuring from a `$state` proxy captures the current
values and does not keep the destructured variables reactive.

```js
let { a, b } = $derived(makeValues()); // individually reactive
let { done } = todos[0];               // current value only
```

### Prop fallbacks and ownership

A fallback object supplied while destructuring `$props()` is an ordinary
object, not a state proxy, so mutating the fallback does not update the UI.
Mutating a parent-owned state proxy does update the parent, but emits an
ownership warning unless the prop is explicitly bindable.

```js
let { options = { enabled: false } } = $props();
```

Use a binding or callback for intentional child-to-parent writes.

### Reactive class fields are non-enumerable

A class field initialized with `$state` compiles to a prototype accessor backed
by a private field. It therefore does not appear during property enumeration.
Expose the value explicitly when serializing or spreading a class instance.

## Asynchronous UI

### Pending work and eager feedback

In a component that uses `await`, `$effect.pending()` reports the number of
pending promises in the current boundary and excludes child boundaries.
`$state.eager(value)` lets displayed state update immediately instead of waiting
for synchronized asynchronous updates.

```svelte
{#if $effect.pending()}<p>pending: {$effect.pending()}</p>{/if}
<a aria-current={$state.eager(pathname) === '/' ? 'page' : null} href="/">home</a>
```

### Awaited template constants and server rendering

An `{@const}` declaration can await a value as part of asynchronous template
work:

```svelte
{#if task}
	{@const value = await task}
	<p>{value}</p>
{/if}
```

Svelte also has an experimental asynchronous SSR path that can wait for this
kind of asynchronous template work during server rendering.

## Component identity and context

### Hydration-stable IDs

`$props.id()` returns an ID unique to a component instance and stable across
server rendering and hydration. Use it for label, description, and ARIA
relationships.

```svelte
<script>const uid = $props.id();</script>
<label for="{uid}-name">Name</label>
<input id="{uid}-name" />
```

### Typed programmatic contexts

Programmatic Svelte code can create typed contexts with `createContext`,
preserving the context value type without relying on untyped keys.

## Attachments

### Element lifecycle behavior

An attachment runs with an element when it mounts and may return cleanup logic
for removal. Apply one with `{@attach ...}`:

```svelte
<script>
	const autofocus = (node) => {
		node.focus();
		return () => {};
	};
</script>

<input {@attach autofocus} />
```

### Adapt actions with `fromAction`

`fromAction` exposes an existing action as an attachment. For a parameterized
action, its second argument is a function that returns the parameter value, not
the value itself.

```svelte
<script>
	import { fromAction } from 'svelte/attachments';
	const title = (node, value) => { node.title = value; };
	const message = 'More details';
</script>

<div {@attach fromAction(title, () => message)}>Hover me</div>
```

### Attach through spread props

Since Svelte 5.29, `createAttachmentKey()` returns a symbol whose object property
acts as an attachment when the object is spread onto an element. This is useful
for library-authored prop objects.

```svelte
<script>
	import { createAttachmentKey } from 'svelte/attachments';
	const props = {
		[createAttachmentKey()]: (node) => { node.textContent = 'attached'; }
	};
</script>

<button {...props}>waiting</button>
```

## Snippets and template syntax

### Snippet parameters

Snippet parameters allow defaults and destructuring, but not rest parameters.

```svelte
{#snippet badge({ label }, prefix = '')}
	<span>{prefix}{label}</span>
{/snippet}

{@render badge({ label: 'New' }, 'Status: ')}
```

### Exported and programmatic snippets

Since Svelte 5.5, a top-level snippet can be exported from `<script module>` when
it has no direct or transitive reference to instance-script declarations:

```svelte
<script module>
	export { add };
</script>

{#snippet add(a, b)}
	{a} + {b} = {a + b}
{/snippet}
```

Use `createRawSnippet` from `svelte` when a snippet must be constructed
programmatically instead of with a `{#snippet ...}` block.

### Template declaration tags

Svelte 5.56 accepts `let` and `const` declaration tags in template scope. One
tag can declare multiple values, and a later initializer can reference an
earlier declaration, including when runes initialize the values.

```svelte
{let count = $state(0), doubled = $derived(count * 2)}
<button onclick={() => count++}>{doubled}</button>
```

### Comments between attributes

HTML comments are accepted between attributes in an opening tag:

```svelte
<button
	<!-- explains the next attribute -->
	disabled
>
	Save
</button>
```
