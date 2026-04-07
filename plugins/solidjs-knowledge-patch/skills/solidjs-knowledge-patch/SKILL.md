---
name: solidjs-knowledge-patch
description: "SolidJS changes since training cutoff (latest: 2.0 beta, SolidStart 1.1) -- Solid 2.0 rewrites reactivity with microtask batching, split effects, async-first computations, Loading/Errored boundaries, draft-first stores, actions with optimistic updates, and DOM model cleanup. Load before working with SolidJS."
license: MIT
metadata:
  author: Nevaberry
  version: "2.0.0-beta"
---

# SolidJS 1.9+ / 2.0 Beta Knowledge Patch

Claude's baseline knowledge covers SolidJS through 1.8.x. This skill provides features from 1.9 (Sep 2024) through the 2.0 beta (Mar 2026), plus SolidStart 1.0-1.1.

## Quick Reference

### API Renames (2.0)

| 1.x | 2.0 |
|-----|-----|
| `Suspense` | `Loading` |
| `ErrorBoundary` | `Errored` |
| `mergeProps` | `merge` |
| `splitProps` | `omit` |
| `unwrap` | `snapshot` |
| `onMount` | `onSettled` |
| `classList` | `class` (object/array) |
| `createResource` | async `createMemo` + `Loading` |
| `createSelector` | `createProjection` |
| `createComputed` | split `createEffect` or `createSignal(fn)` |
| `batch()` | `flush()` |
| `use:directive` | `ref={directive(opts)}` |
| `Context.Provider` | `<Context value={...}>` |

### Import Changes (2.0)

| 1.x | 2.0 |
|-----|-----|
| `solid-js/web` | `@solidjs/web` |
| `solid-js/store` | `solid-js` (stores merged into core) |
| `solid-js/h` | `@solidjs/h` |
| `solid-js/html` | `@solidjs/html` |
| `solid-js/universal` | `@solidjs/universal` |

### Batching & Reads (2.0)

```tsx
const [count, setCount] = createSignal(0);
setCount(1);
count(); // still 0 -- reads return last committed value
flush();
count(); // now 1
```

See `references/reactivity-effects.md` for split effects, `onSettled`, dev warnings.

### Async Data (2.0)

| Pattern | Code |
|---------|------|
| Fetch data | `const user = createMemo(() => fetchUser(id()));` |
| Loading boundary | `<Loading fallback={<Spinner />}><Profile /></Loading>` |
| Revalidation check | `const pending = () => isPending(() => users());` |
| Peek stale value | `const val = () => latest(signal);` |
| Refresh after mutation | `refresh(derivedStore);` |

See `references/async-actions.md` for actions, optimistic updates, `refresh`.

### Stores (2.0)

```tsx
// Draft-first setter (produce-style)
const [store, setStore] = createStore({ user: { name: 'A' } });
setStore((s) => {
  s.user.name = 'B';
});

// 1.x-style path setter via storePath helper
setStore(storePath('user', 'name', 'B'));

// Snapshot for serialization
const plain = snapshot(store);
```

See `references/stores.md` for derived stores, projections, `deep()`, `merge`, `omit`.

### Control Flow (2.0)

```tsx
// For with accessors (keyed by identity, the default)
<For each={items()}>
  {(item, i) => <Row item={item()} index={i()} />}
</For>

// Index-style (reuse by position)
<For each={items()} keyed={false}>
  {(item, i) => <Row item={item()} index={i()} />}
</For>

// Repeat (no diffing, for skeletons/ranges)
<Repeat count={10}>{(i) => <Skeleton index={i} />}</Repeat>
```

See `references/control-flow-dom.md` for `Show`, `Switch/Match`, `Errored`, DOM changes.

### SolidStart 1.0-1.1

| Feature | Detail |
|---------|--------|
| Package | `@solidjs/start` |
| Routing | File-based via `<FileRoutes />` + `@solidjs/router` |
| Dynamic routes | `[id].tsx`, optional `[[id]].tsx`, catch-all `[...path].tsx` |
| Route groups | `(groupName)/` folders |
| Nested layouts | `blog.tsx` + `blog/` directory |
| API routes | Files in `routes/` exporting HTTP methods |
| Vite 6 | Supported since SolidStart 1.1 |
| Roadmap | SolidStart 2.0 replaces Vinxi with pure Vite ("DeVinxi") |

See `references/solidstart.md` for routing details, route config, preload.

## Reference Files

| File | Contents |
|------|----------|
| `reactivity-effects.md` | Split effects, `flush`, `onSettled`, dev warnings, ownership |
| `async-actions.md` | Async computations, `Loading`, `isPending`, actions, optimistic updates |
| `stores.md` | Draft-first setters, `storePath`, projections, `snapshot`, `merge`, `omit` |
| `control-flow-dom.md` | `For`/`Repeat`/`Show`/`Switch`, `Loading`/`Errored`, DOM attributes, directives |
| `solidstart.md` | SolidStart 1.0-1.1, file routing, layouts, DeVinxi roadmap |

## Critical Knowledge

### Solid 1.9 Changes

New features in 1.9 (the last 1.x release before 2.0):

- `bool:` attribute namespace for custom elements: `<my-el bool:enable={flag()} />`
- `on:` with `handleEvent` objects for advanced event options (passive, once, capture):

```tsx
<div
  on:wheel={{
    handleEvent(e) {
      e.preventDefault();
    },
    passive: false,
  }}
/>;
```

- Better JSX validation via JSDOM (detects invalid nesting like `<a>` inside `<a>`)
- `oncapture:` deprecated in favor of `on:` with event objects

### Top-Level Read Warning (2.0 dev)

Solid 2.0 warns in dev when you read reactive values at the top level of a component body. This catches a class of bugs where reactivity is accidentally lost.

```tsx
// BAD: warns -- destructuring loses reactivity
function Bad({ title }) {
  return <h1>{title}</h1>;
}

// GOOD: keep props object
function Good(props) {
  return <h1>{props.title}</h1>;
}

// GOOD: intentional one-time read
function OneTime(props) {
  const t = untrack(() => props.title);
  return <h1>{t}</h1>;
}
```

### Write-Under-Scope Warning (2.0 dev)

Writing to signals inside reactive scopes (effects, memos, component body) warns. Derive instead of writing back.

```tsx
// BAD: warns
createMemo(() => setDoubled(count() * 2));

// GOOD: derive
const doubled = createMemo(() => count() * 2);

// Escape hatch for internal state only
const [ref, setRef] = createSignal(null, { pureWrite: true });
```

### Context Provider Simplification (2.0)

```tsx
const Theme = createContext('light');

// 1.x
<Theme.Provider value="dark"><Page /></Theme.Provider>

// 2.0 -- context IS the provider
<Theme value="dark"><Page /></Theme>
```

### Directives via ref (2.0)

```tsx
// 1.x
<button use:tooltip={{ content: 'Save' }} />

// 2.0 -- ref with directive factory
<button ref={tooltip({ content: 'Save' })} />

// Multiple directives via array
<button ref={[autofocus, tooltip({ content: 'Save' })]} />
```
