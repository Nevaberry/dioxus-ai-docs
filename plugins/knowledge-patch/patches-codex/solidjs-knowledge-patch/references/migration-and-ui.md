# Migration, JSX, and DOM APIs

## Compiler validation

### Correct browser-rewritten markup

Since 1.9.0, the JSX compiler catches more invalid HTML structures that a
browser would otherwise rewrite, including nested `<a>` elements. The
validation is not complete for every template shape, but newly detected cases
can fail at build time. Fix the source structure instead of depending on the
browser's corrected DOM tree.

## Package and runtime resolution

### Treat server exports as resolution shims

In 1.9.0, server environments export client-side compiler methods from
`solid-js/web`, allowing cross-environment imports to resolve. Those methods
remain client-only: calling one on the server still throws. Separate import
resolution from runtime capability checks.

### Resolve browser builds through export conditions

The 1.9.0 package removed its `browser` field after some bundlers reapplied it
incorrectly following ESM export resolution. A legacy resolver without package
export-condition support may no longer find the browser build correctly.
Update the resolver rather than restoring an assumption about the removed
field.

## Customized elements

### Detect customized built-ins with `is`

Since 1.9.0, a JSX element with an `is` attribute receives Solid's custom
element handling, including customized built-in elements:

```tsx
<button is="fancy-button">Open</button>
```

### Force boolean-attribute behavior

The `bool:` namespace introduced in 1.9.0 forces boolean-attribute semantics
when Solid would otherwise select property behavior. This is particularly
useful for custom elements:

```tsx
<my-element bool:enable={isEnabled()} />
```

## Non-delegated events

### Use listener objects for browser options

Since 1.9.0, `on:` accepts an object containing `handleEvent` and event
listener options such as `once`, `passive`, and `capture`:

```tsx
<div
  on:wheel={{
    handleEvent(event) {
      event.preventDefault();
    },
    passive: false,
    capture: true,
  }}
/>
```

This form supersedes the deprecated `oncapture:` mechanism and allows future
browser listener options without requiring additional JSX syntax.
