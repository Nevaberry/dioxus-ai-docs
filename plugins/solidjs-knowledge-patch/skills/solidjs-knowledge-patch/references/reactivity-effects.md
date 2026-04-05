# Reactivity and Effects

## Microtask Batching (2.0)

All updates are batched by default via microtasks. Setters queue work; reads return the last committed value until the batch flushes. `batch()` is removed.

```tsx
const [count, setCount] = createSignal(0);
const [name, setName] = createSignal('Alice');

setCount(1);
setName('Bob');
// Neither read reflects the new value yet
count(); // 0
name(); // "Alice"

flush(); // Apply all pending updates now
count(); // 1
name(); // "Bob"
```

Use `flush()` sparingly -- it forces synchronous settling. Most useful in tests or before imperative DOM reads:

```tsx
function handleSubmit() {
  setSubmitted(true);
  flush(); // DOM is now up to date
  inputRef.focus();
}
```

## Split Effects (2.0)

Effects have two phases: **compute** (tracks dependencies, no side effects) and **apply** (runs side effects, can return cleanup).

```tsx
// 2.0 split effect
createEffect(
  () => name(), // compute: tracks dependencies
  (value) => {
    // apply: runs after flush, receives computed value
    el().title = value;
    return () => {
      /* cleanup */
    };
  },
);
```

Compare with 1.x single-function effect:

```tsx
// 1.x
createEffect(() => {
  el().title = name();
});
```

### With initial value

```tsx
createEffect(
  () => [a(), b()],
  (deps, prev) => {
    console.log('changed from', prev, 'to', deps);
  },
  undefined, // initial value for prev
);
```

### createRenderEffect

Same split pattern, but runs before user effects (render phase). Tears down when dependencies change.

```tsx
createRenderEffect(
  () => count(),
  (value) => {
    updateDOM(value);
  },
);
```

## onSettled (replaces onMount)

`onSettled` runs when the current activity is settled (after mount, or when reactive graph is idle). Unlike `onMount`, it can return a cleanup function.

```tsx
onSettled(() => {
  measureLayout();
  const onResize = () => measureLayout();
  window.addEventListener('resize', onResize);
  return () => window.removeEventListener('resize', onResize);
});
```

`onSettled` and `createTrackedEffect` cannot create nested primitives (breaking change from 1.x). They return a cleanup function.

## createTrackedEffect

Single-callback effect for special cases. May re-run in async situations -- not the default choice.

```tsx
createTrackedEffect(() => {
  // Single callback form, may re-run with async
  console.log(count());
});
```

## Dev Warnings

### Top-level reactive read

Reading reactive values at the top level of a component body warns in dev. Move reads into JSX expressions, `createMemo`, `createEffect`, or wrap in `untrack`.

```tsx
// WARNS: top-level read
function Bad(props) {
  const n = props.count; // loses reactivity
  return <div>{n}</div>;
}

// OK: read in JSX (tracked)
function Good(props) {
  return <div>{props.count}</div>;
}

// OK: intentional one-time read
function Snapshot(props) {
  const n = untrack(() => props.count);
  return <div>{n}</div>;
}
```

This also applies inside control-flow function children (Show/Match/For callbacks):

```tsx
// WARNS: reactive read in callback body
<Show when={user()}>
  {(u) => {
    const name = u().name; // warns
    return <span>{name}</span>;
  }}
</Show>

// OK: read in JSX expression
<Show when={user()}>{(u) => <span>{u().name}</span>}</Show>
```

### Write inside reactive scope

Writing to signals inside effects, memos, or component body warns. Use event handlers, `onSettled`, or untracked blocks instead.

```tsx
// OPT-IN: allow writes in owned scope (internal state only)
const [ref, setRef] = createSignal(null, { pureWrite: true });
```

## Ownership Changes (2.0)

### createRoot is owned by parent

In 2.0, a root created inside an existing owned scope is owned by that parent and disposed when the parent is disposed.

```tsx
function Widget() {
  createRoot((dispose) => {
    const [count, setCount] = createSignal(0);
    onCleanup(() => console.log('cleaned up'));
  });
  // Root is disposed when Widget unmounts
}
```

### Explicit detachment

For truly global/detached singletons, detach explicitly:

```tsx
export const singleton = runWithOwner(null, () => {
  const [value, setValue] = createSignal(0);
  return { value, setValue };
});
```

## Removals

| Removed | Replacement |
|---------|-------------|
| `batch` | `flush()` |
| `onMount` | `onSettled` |
| `onError` / `catchError` | Effect `error` callback or `Errored` boundary |
| `on` helper | No longer necessary with split effects |
| `createComputed` | Split `createEffect`, function-form `createSignal`/`createStore`, or `createMemo` |
