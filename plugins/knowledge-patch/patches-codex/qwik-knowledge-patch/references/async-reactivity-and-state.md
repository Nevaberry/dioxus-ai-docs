# Async Reactivity and State

## Async computed functions

Async callbacks to `useComputed$` are deprecated and will stop working in
Qwik V2. Signals first read after an `await` are not tracked, and an initial
promise restarts rendering. Use `useTask$` or `useResource$` for asynchronous
work instead of relying on an async computed callback.

## Raw store access

`unwrapStore()` exposes a store's underlying content for APIs such as
structured cloning and IndexedDB:

```ts
import { unwrapStore } from '@builder.io/qwik';

const copy = structuredClone(unwrapStore(store));
```

## Reactive store membership

The expression `"prop" in store` creates a subscription. A reactive consumer
that performs this membership check updates when the property's presence
changes, even if it did not read the property's value.

## `useTask$` eagerness deprecation

The `eagerness` option of `useTask$` is deprecated as of 1.13 and is removed
in V2. Remove the option and use supported task scheduling behavior.

## Expanded `untrack()`

`untrack()` can accept a signal or store directly. Its callback form also
accepts arguments, allowing a read or calculation without creating reactive
subscriptions:

```ts
const signalValue = untrack(signal);
const storeValue = untrack(store);
const result = untrack((a, b) => a + b, 1, 2);
```

Use this only when later changes should not cause the current reactive
consumer to rerun.

## Computed-signal notifications

Computed signals notify listeners only when their computed value changes. If
a dependency changes but recomputation produces an equivalent result,
listeners are not notified.

Source batches: `v1.8-1.13`, `v1.14-1.19`.
