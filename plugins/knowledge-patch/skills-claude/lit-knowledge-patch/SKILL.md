---
name: lit-knowledge-patch
description: Lit
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Lit Knowledge Patch

Use this skill when a Lit task involves reactive property defaults, template
typing, experimental signals, server-side rendering, or template compilation.
Identify the package and feature in use before applying guidance: core Lit,
`@lit-labs/signals`, `@lit-labs/ssr`, and `@lit-labs/compiler` have separate
compatibility concerns.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Core components](references/core-components.md) | Reactive defaults, development warnings, class maps, SVG render roots, private accessors, directive result typing |
| [Signals](references/signals.md) | `SignalWatcher`, binding-level `watch()`, effects, signal-aware template tags, mixin API typing |
| [SSR and compiler](references/ssr-and-compiler.md) | SSR lifecycle callbacks, renderer migration, DOM shims, Node typings, compiler setup and eligibility |

## Start With Compatibility Breaks

### Migrate custom SSR renderers before SSR 4.0

Lit SSR 4.0 replaces generator-based `ElementRenderer` behavior with a
thunk/trampoline interface. Treat a custom renderer written against 3.x as
incompatible until its implementation has been adapted.

Before upgrading:

1. Locate every `ElementRenderer` implementation.
2. Find methods that return or delegate through generators.
3. Port them to the 4.0 thunk/trampoline contract.
4. Exercise the custom-renderer path with representative components.

See [SSR and compiler](references/ssr-and-compiler.md) for the related SSR
runtime and typing changes.

### Do not remain on compiler 1.0.0

Compiler 1.0.0 can mix up values when an attribute part and an element part
are adjacent. Upgrade to 1.0.1 or later before trusting output for templates
with adjacent parts.

After upgrading, inspect a compiled sample. A successful transform removes the
authored `html` tag call and emits template metadata plus a result containing
`_$litType$` and `values`.

## Restore Property Defaults With `useDefault`

Use `useDefault: true` when a reactive property has a declared initial value
that should behave as the component's default.

```ts
import {LitElement} from 'lit';

class ThemeElement extends LitElement {
  static properties = {
    theme: {reflect: true, useDefault: true},
  };

  theme = 'light';
}
```

With this option:

- initialization does not count the initial value as a change;
- the initial value is not reflected on initialization;
- removing the corresponding attribute restores the initial value.

This is especially useful for reflected properties whose attribute may be
temporarily supplied and then removed. See
[Core components](references/core-components.md) for other core behavior.

## Choose the Right Signal Update Scope

`@lit-labs/signals` is experimental. Choose update scope deliberately.

### Component-level tracking

Extend `SignalWatcher(LitElement)` when signals read during rendering should
request an update of the component:

```ts
import {LitElement, html} from 'lit';
import {SignalWatcher, signal} from '@lit-labs/signals';

const count = signal(0);

class SharedCounter extends SignalWatcher(LitElement) {
  render() {
    return html`<p>${count.get()}</p>`;
  }
}
```

### Binding-level tracking

Use `watch()` when a signal change should process only one binding:

```ts
import {LitElement, html} from 'lit';
import {SignalWatcher, signal, watch} from '@lit-labs/signals';

const count = signal(0);

class PinpointCounter extends SignalWatcher(LitElement) {
  render() {
    return html`<p>${watch(count)}</p>`;
  }
}
```

### Reactions outside reactive updates

Use `this.effect()` for signal reactions independent of a reactive update.
Effects run after pending DOM and element updates by default. Set
`beforeUpdate: true` when the callback must run first:

```ts
this.effect(
  () => console.log(this.aSignal.get()),
  {beforeUpdate: true},
);
```

For direct signal interpolation and custom tag composition, read
[Signals](references/signals.md).

## Control SSR Lifecycle Behavior Explicitly

Lit SSR 3.3 can invoke `connectedCallback()` during server rendering. Enable it
globally before rendering:

```js
globalThis.litSsrCallConnectedCallback = true;
```

From SSR 4.1, `LitElementRenderer` also provides configuration for disabling
SSR or calling `connectedCallback()` on `LitElement` subclasses. Make this an
explicit renderer choice; do not assume browser connection semantics during
server rendering.

SSR 4.1's DOM shim includes `ShadowRoot`, includes `document` in event paths,
and implements `MutationObserver`, `ResizeObserver`, and
`IntersectionObserver`. Code that touches those APIs can use the shim, but
should still be tested on the server-render path.

## Compile Only Eligible Templates

Register `compileLitTemplates()` as a TypeScript pre-transform. JavaScript is
also handled when it passes through the TypeScript transform.

```js
import typescript from '@rollup/plugin-typescript';
import {compileLitTemplates} from '@lit-labs/compiler';

export default {
  plugins: [
    typescript({
      transformers: {
        before: [compileLitTemplates()],
      },
    }),
  ],
};
```

The compiler optimizes only well-formed templates whose `html` tag comes
directly from `lit` or `lit-html`.

- Renamed named imports are eligible.
- Namespace imports are eligible.
- Re-exported tags are not eligible.
- Dynamic bindings inside `textarea`, `title`, `style`, or `script` make a
  template ineligible.

See [SSR and compiler](references/ssr-and-compiler.md) for import examples and
the emitted shape to verify.

## Apply Core Typing and Rendering Improvements

When working with current core Lit behavior:

- build or mutate a typed `ClassInfo` object before passing it to `classMap()`;
- pass an `SVGElement` directly as the container to `render()`;
- expect standard-decorated private reactive accessors to schedule updates;
- preserve generic directive result types so template type checking retains
  rendered-type information;
- install synchronous development-warning suppression immediately after an
  import when needed, because warnings are deferred to the following
  microtask.

The complete examples and constraints are in
[Core components](references/core-components.md).

## Validation Checklist

Before completing a Lit change:

- Confirm which package owns the behavior.
- For SSR 4.x, audit custom renderers for the generator-interface break.
- For compiler use, confirm direct tag provenance and eligible binding
  locations.
- Check compiler output for `_$litType$` and `values`.
- For signals, distinguish component updates, one-binding updates, and
  independent effects.
- For reflected defaults, test attribute removal as well as initialization.
- For server lifecycle callbacks, set the flag or renderer configuration
  before rendering.
- Keep `@types/node` explicit in SSR 4.0 projects when the consumer needs Node
  typings, because it is a ranged peer dependency.
