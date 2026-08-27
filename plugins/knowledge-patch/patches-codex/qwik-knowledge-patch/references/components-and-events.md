# Components and Events

## Qwik City MDX components

Imported MDX content accepts a `components` prop for custom component
bindings. JavaScript expressions in the MDX can use props, and a
default-exported MDX layout component is honored.

```tsx
import { component$ } from '@builder.io/qwik';
import Content from './markdown.mdx';
import MyComponent from './my-component';

export default component$(() => (
  <Content components={{ MyComponent }} />
));
```

## View-transition event

Qwik emits a `CustomEvent` named `qviewTransition` when a view transition
starts. Integration code can listen for that exact event to coordinate work
with the transition lifecycle.

## Error boundaries

Qwik provides an `ErrorBoundary` component. The behavior of
`useErrorBoundary` was also corrected in 1.13; use the framework component
and hook for component-tree error handling.

Source batch: `v1.8-1.13`.
