# JSX, Events, and Serialization

## Accessing raw store content

`unwrapStore()` exposes the underlying contents of a store. Use it when an
API such as structured cloning or IndexedDB cannot accept the reactive proxy.

```ts
import { unwrapStore } from '@builder.io/qwik';

const copy = structuredClone(unwrapStore(store));
```

The returned value bypasses the store proxy. Do not treat raw mutations as
reactive store updates.

## Direct build-constant exports

Import `isDev`, `isBrowser`, and `isServer` directly from
`@builder.io/qwik`. The older `@builder.io/qwik/build` entry point remains
available.

```ts
import { isBrowser, isDev, isServer } from '@builder.io/qwik';
```

## Qwik City MDX components

Imported MDX accepts a `components` prop for substituting custom components.
MDX JavaScript expressions can use props, and Qwik honors default-exported
MDX layout components.

```tsx
import { component$ } from '@builder.io/qwik';
import Content from './markdown.mdx';
import MyComponent from './my-component';

export default component$(() => (
  <Content components={{ MyComponent }} />
));
```

## View-transition event

Qwik dispatches a `CustomEvent` named `qviewTransition` when a view
transition starts. Code listening for the transition should use that exact
case-sensitive event name.

## Reads without reactive subscriptions

`untrack()` accepts a signal or store directly. Its callback form also
accepts arguments:

```ts
const signalValue = untrack(signal);
const plainStoreRead = untrack(store);
const result = untrack((a, b) => a + b, 1, 2);
```

Use these forms for reads that must not subscribe the current reactive
consumer.
