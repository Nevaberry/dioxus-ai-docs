# Migration, JSX, and DOM APIs

## Build-time HTML validation

Since 1.9.0, the JSX compiler detects more invalid HTML structures that a
browser would silently rewrite, including nested `<a>` elements. These
structures can now fail the build instead of producing a different DOM tree at
runtime.

Validation is still incomplete across all template shapes. Treat a passing
build as a useful check, not proof that every generated tree is valid HTML.
When a new compiler version rejects a structure, fix the source markup instead
of depending on browser repair.

## Cross-runtime `solid-js/web` exports

Server environments export client compiler methods from `solid-js/web` so
shared imports resolve during server builds. The methods remain client-only:
invoking one on the server still throws. Separate successful resolution from
runtime safety when sharing modules between SSR and the browser.

## Package resolution without `browser`

The package no longer publishes a `browser` field. Some bundlers reapplied that
field after resolving ESM exports, so keeping it produced incorrect builds.
Resolvers must now understand package export conditions; legacy resolvers may
fail to find the browser build and should be upgraded or configured for
conditional exports.

## Customized built-in elements

An intrinsic JSX element with an `is` attribute receives Solid's custom-element
behavior:

```tsx
<button is="fancy-button">Open</button>
```

Use this form for a customized built-in element rather than treating it as an
ordinary built-in button.

## Explicit boolean attributes

The `bool:` namespace forces boolean-attribute semantics for names Solid would
otherwise handle as properties. It is particularly useful for custom elements:

```tsx
<my-element bool:enable={isEnabled()} />
```

Use it only when presence and absence of the attribute carry the state; it is
not merely shorthand for assigning a boolean property.

## Listener objects for non-delegated events

The `on:` syntax accepts an event-listener object with `handleEvent` and browser
listener options:

```tsx
<div
  on:wheel={{
    handleEvent(event) {
      event.preventDefault();
    },
    passive: false,
    capture: true,
    once: true,
  }}
/>
```

Supported options include `once`, `passive`, and `capture`. This form replaces
the deprecated `oncapture:` mechanism and can accommodate additional listener
options without requiring another JSX namespace.
