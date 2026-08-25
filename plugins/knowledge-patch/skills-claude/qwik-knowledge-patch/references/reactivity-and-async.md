# Reactivity and Async Computations

## Async `useComputed$` callbacks

Async callbacks to `useComputed$` are deprecated and will stop working in
V2. A signal first read after an `await` is not tracked, and an initial
promise restarts rendering.

Move asynchronous work to `useTask$` or `useResource$`. Track inputs before
the first `await` when using a task:

```tsx
useTask$(async ({ track }) => {
  const id = track(idSignal);
  await loadItem(id);
});
```

## Deprecated task eagerness

The `eagerness` option of `useTask$` is deprecated since 1.13 and will be
removed in V2. Remove the option rather than carrying it into migration work.

## Reactive store membership

The membership expression `"prop" in store` creates a subscription. Reactive
consumers using it rerun when the presence of that property changes.

```ts
const hasSelection = 'selection' in state;
```

Account for this subscription when membership checks appear inside tasks or
computed expressions.

## Untracked reads

`untrack()` accepts signals and stores directly, and its callback form can
receive arguments:

```ts
const current = untrack(signal);
const snapshot = untrack(store);
const sum = untrack((a, b) => a + b, 1, 2);
```

Use `untrack()` when reading a value must not make the current consumer
reactive to it.

## Computed-signal notifications

Computed signals notify listeners only when the computed value changes. If a
dependency changes but the computation produces an equivalent result,
listeners are not notified.

Do not use a computed listener as a general notification that any dependency
was written; observe the underlying dependency when that distinction matters.
