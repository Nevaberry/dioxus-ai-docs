# Migration, JSX, and DOM APIs

The core changes in `1.9.0` affect compilation, package resolution, customized
built-ins, boolean attributes, and native event registration.

## Build-time HTML validation

The JSX compiler detects more invalid HTML structures that a browser would
otherwise rewrite, including nested `<a>` elements. These structures can now
fail the build instead of producing a different DOM tree at runtime.

Validation is not exhaustive across every template shape. Do not infer that a
successful build proves all generated HTML is structurally valid; fix every
reported source nesting error.

## Cross-runtime `solid-js/web` imports

Server environments export the client-side compiler methods from
`solid-js/web`, allowing a cross-environment import to resolve during a server
build. The methods remain client-only: calling one on the server throws.

Use the exports to keep shared module graphs resolvable, not to perform DOM or
client compiler work during SSR.

## Package resolution without `browser`

The package no longer publishes a `browser` field. Some bundlers resolved ESM
exports correctly and then incorrectly reapplied `browser`, so removing the
field avoids that second remapping.

Legacy resolvers that do not understand package export conditions may stop
finding the browser build. Upgrade or configure the resolver rather than
assuming the old `browser` mapping still exists.

## Customized built-in elements

An element with an `is` attribute is recognized as a custom element and gets
Solid's custom-element behavior:

```tsx
<button is="fancy-button">Open</button>
```

This covers customized built-ins rather than only autonomous custom-element
tag names.

## Explicit boolean attributes

Use the `bool:` namespace to force boolean-attribute semantics when Solid
would otherwise handle the name as a property. This is particularly useful
for custom elements with boolean attributes:

```tsx
<my-element bool:enable={isEnabled()} />
```

The namespace controls attribute semantics; it is not merely a naming
convention for the custom element.

## Non-delegated event listener objects

The `on:` syntax accepts an object with `handleEvent` and native event-listener
options:

```tsx
<div
  on:wheel={{
    handleEvent(event) {
      event.preventDefault();
    },
    passive: false,
  }}
/>
```

The object can carry `once`, `passive`, or `capture`. Use this form instead of
the deprecated `oncapture:` mechanism; it also allows future browser listener
options without requiring another JSX namespace.

