# Runes and components

## Contents

- [Reactive dependencies](#reactive-dependencies)
- [Derived values](#derived-values)
- [State, props, and ownership](#state-props-and-ownership)
- [Component IDs and reactive classes](#component-ids-and-reactive-classes)
- [Element attachments](#element-attachments)
- [Snippets](#snippets)
- [Template declarations and syntax](#template-declarations-and-syntax)
- [Programmatic contexts](#programmatic-contexts)
- [Asynchronous rendering](#asynchronous-rendering)

## Reactive dependencies

### Await-aware derived expressions

Reactive reads on both sides of an `await` written directly in a `$derived`
expression are dependencies:

```svelte
<script>
	let a = $state(Promise.resolve(1));
	let b = $state(2);
	let total = $derived(await a + b);
</script>
```

This does not extend through an arbitrary function boundary. If the expression
calls a helper and that helper reads reactive state after awaiting, do not assume
the hidden read becomes a dependency.

### Effect subscription granularity

An effect subscribes only to reactive values read synchronously during its most
recent execution. Reads after an `await`, in a timer, or in another later
callback are not tracked.

Reading a state proxy object does not observe all of its properties. Read the
property whose changes should rerun the effect:

```js
$effect(() => state);       // does not rerun for state.value mutations
$effect(() => state.value); // observes state.value
```

These dependency rules are attributed to `5.0.0-runes`.

## Derived values

### Optimistic overrides

A `$derived` binding declared with `let` can be reassigned for optimistic UI.
The assigned value remains until a dependency changes, at which point the
derived expression recalculates it. Derived bindings before Svelte 5.25 were
read-only.

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
bindings:

```js
let { a, b } = $derived(makeValues());
```

A derived result is otherwise returned as-is; Svelte does not deep-proxy it.
By contrast, a `$state` value can be a deep proxy, but ordinary JavaScript
destructuring captures current property values rather than reactive bindings:

```js
let { done } = todos[0]; // snapshot of a property on a state proxy
```

## State, props, and ownership

### Prop fallbacks

A fallback object created while destructuring `$props()` is not converted to a
state proxy. Mutating it does not trigger a UI update:

```js
let { options = { enabled: false } } = $props();
```

### Parent-owned state

Mutating a state proxy owned by a parent can update the parent, but Svelte emits
an ownership warning unless the prop is explicitly bindable. Use a binding or a
callback when a child is intended to update parent state.

## Component IDs and reactive classes

### Hydration-stable IDs

`$props.id()` returns an ID unique to the component instance and stable between
server rendering and hydration. Use it for label, description, and ARIA
relationships:

```svelte
<script>const uid = $props.id();</script>
<label for="{uid}-name">Name</label>
<input id="{uid}-name" />
```

### Non-enumerable reactive class fields

Class fields initialized with `$state` compile to accessors on the prototype
backed by private storage. They do not appear during ordinary property
enumeration. Spreading or serializing a class instance therefore omits them
unless the class exposes those values explicitly.

The derived, prop, ID, and class-field behavior in these sections is attributed
to `5.0.0-runes`.

## Element attachments

An attachment is a function that runs with an element when the element mounts.
It can return a cleanup function that runs when the element is removed. Apply it
with `{@attach ...}`:

```svelte
<script>
	const autofocus = (node) => {
		node.focus();
		return () => {};
	};
</script>

<input {@attach autofocus} />
```

### Adapt an action

Use `fromAction` from `svelte/attachments` to preserve an existing action's
behavior as an attachment. For an action with an argument, pass a function that
returns the value as the second argument, not the value itself:

```svelte
<script>
	import { fromAction } from 'svelte/attachments';

	const title = (node, value) => {
		node.title = value;
	};
	const message = 'More details';
</script>

<div {@attach fromAction(title, () => message)}>Hover me</div>
```

### Attach through spread props

Since Svelte 5.29, `createAttachmentKey()` returns a symbol whose property acts
as an attachment when its containing object is spread onto an element. This is
primarily useful for prop objects created by libraries:

```svelte
<script>
	import { createAttachmentKey } from 'svelte/attachments';

	const props = {
		[createAttachmentKey()]: (node) => {
			node.textContent = 'attached';
		}
	};
</script>

<button {...props}>waiting</button>
```

## Snippets

### Parameter syntax

Snippet parameters allow defaults and destructuring. They do not allow rest
parameters:

```svelte
{#snippet badge({ label }, prefix = '')}
	<span>{prefix}{label}</span>
{/snippet}

{@render badge({ label: 'New' }, 'Status: ')}
```

### Export snippets

Since Svelte 5.5, a top-level snippet in a `.svelte` file can be exported from
`<script module>`. The snippet must not refer directly, or through another
snippet, to any declaration in the instance-level `<script>`:

```svelte
<script module>
	export { add };
</script>

{#snippet add(a, b)}
	{a} + {b} = {a + b}
{/snippet}
```

### Construct snippets programmatically

Use `createRawSnippet` from `svelte` when a snippet must be created
programmatically rather than with a `{#snippet ...}` block.

## Template declarations and syntax

Svelte 5.56 allows `let` and `const` declarations directly in template scope.
A declaration tag can contain multiple declarators, and a later initializer can
refer to an earlier declaration. Runes can initialize the values:

```svelte
{let count = $state(0), doubled = $derived(count * 2)}

<button onclick={() => count++}>{doubled}</button>
```

HTML comments are also accepted between attributes in an opening tag:

```svelte
<button
	<!-- explains the next attribute -->
	disabled
>
	Save
</button>
```

## Programmatic contexts

Programmatic Svelte code can use typed `createContext` calls so the context value
keeps its type without relying on an untyped key.

## Asynchronous rendering

### Pending work and eager display

In a component that uses `await`, `$effect.pending()` returns the number of
pending promises in the current boundary. Pending work in child boundaries is
excluded. `$state.eager(value)` opts a displayed value out of synchronized await
updates so immediate feedback can render while other work finishes:

```svelte
{#if $effect.pending()}<p>pending: {$effect.pending()}</p>{/if}
<a aria-current={$state.eager(pathname) === '/' ? 'page' : null} href="/">home</a>
```

The pending and eager APIs are attributed to `5.0.0-runes`.

### Await template constants

An `{@const}` declaration can await a value as part of asynchronous template
work:

```svelte
{#if task}
	{@const value = await task}
	<p>{value}</p>
{/if}
```

### Asynchronous server rendering

Svelte includes an experimental asynchronous SSR path that can wait for
asynchronous template work while rendering on the server. Treat the path as
experimental when deciding whether production behavior may depend on it.
