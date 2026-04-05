# Stores

## Import Change (2.0)

Stores are now exported from `solid-js` directly. The `solid-js/store` subpath is gone.

```tsx
// 1.x
import { createStore } from 'solid-js/store';

// 2.0
import { createStore, reconcile, snapshot, storePath } from 'solid-js';
```

## Draft-First Setters (2.0)

The primary update form is a callback that receives a mutable draft (produce-style).

```tsx
const [store, setStore] = createStore({ greeting: 'hi', list: [] });

setStore((s) => {
  s.greeting = 'hello';
  s.list.push('value');
});
```

### Return a value for shallow replacement

When returning a value from the setter, it performs a shallow diff/replacement:

```tsx
setStore((s) => {
  return { ...s, list: [] }; // shallow diff
});
```

## storePath (compat helper)

For teams migrating from 1.x path-style setters:

```tsx
// 2.0 preferred: draft-first
setStore((s) => {
  s.user.address.city = 'Paris';
});

// 1.x-style path setter via storePath
setStore(storePath('user', 'address', 'city', 'Paris'));
```

`storePath` supports indices, filters, ranges, and a delete sentinel:

```tsx
setStore(storePath('items', { from: 1, to: 4, by: 2 }, 99));
setStore(storePath('nickname', storePath.DELETE));
```

## snapshot (replaces unwrap)

Produces a non-reactive plain value for serialization/interop. Generates new objects where necessary, preserves unchanged references.

```tsx
const [store] = createStore({ user: { name: 'A' } });
const plain = snapshot(store);
JSON.stringify(plain); // safe, non-reactive
```

## deep() Helper

Store tracking is normally property-level. Use `deep(store)` for deep observation (serialization, logging, "watch everything"):

```tsx
createEffect(
  () => deep(store),
  (snapshot) => {
    // runs when anything inside store changes
    console.log('store changed:', snapshot);
  },
);
```

## merge (replaces mergeProps)

General-purpose reactive merge. Key change: **`undefined` is a real value** (it overrides, not "skip this key").

```tsx
const merged = merge(defaults, overrides);

// undefined overrides explicitly
const result = merge({ a: 1, b: 2 }, { b: undefined });
// result.b is undefined
```

## omit (replaces splitProps)

Creates a reactive view without the listed keys. No extra object allocation.

```tsx
const rest = omit(props, 'class', 'style');
rest.onClick; // accessible
'class' in rest; // false
```

## Derived Signals: createSignal(fn)

Pass a function to `createSignal` for a "writable memo" -- derived but also settable:

```tsx
const [count, setCount] = createSignal(0);
const [doubled] = createSignal(() => count() * 2);
// doubled() is always count * 2, but can also be written via its setter
```

## Derived Stores: createStore(fn)

Function-form creates a derived store. The derive function receives a draft to mutate.

```tsx
const [cache] = createStore(
  (draft) => {
    draft.total = items().length;
  },
  { total: 0 },
);
```

## createProjection

Mutable derived store for patterns like selection. If the derive function returns a value, it is reconciled into the projection (keyed by `options.key`, default `"id"`).

```tsx
// Selection without notifying every row
const [selectedId, setSelectedId] = createSignal('a');

const selected = createProjection((s) => {
  const id = selectedId();
  s[id] = true;
  if (s._prev != null) delete s[s._prev];
  s._prev = id;
}, {});
```

Async projection with reconciliation:

```tsx
const users = createProjection(
  async () => {
    return await api.listUsers();
  },
  [],
  { key: 'id' },
);
```

## reconcile

Diffing function for updating stores from new server data:

```tsx
setStore((s) => {
  reconcile(serverTodos, 'id')(s.todos);
});
```

## Removals

| Removed | Replacement |
|---------|-------------|
| `mergeProps` | `merge` |
| `splitProps` | `omit` |
| `unwrap` | `snapshot` |
| `createSelector` | `createProjection` / `createStore(fn)` |
| `solid-js/store` import | `solid-js` (stores in core) |
