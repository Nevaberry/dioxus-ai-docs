---
name: lit-knowledge-patch
description: Lit
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Lit Knowledge Patch

Use this skill when working with Lit reactive properties, rendering, Signals,
server-side rendering, or template compilation. Check the project's installed
package versions and imports first, because the guidance spans the core
packages and experimental `@lit-labs` packages that version independently.

## Reference index

| Reference | Topics |
| --- | --- |
| [reactivity-and-rendering.md](references/reactivity-and-rendering.md) | Reactive-property defaults, decorated private accessors, development warnings, `ClassInfo`, SVG roots, and directive result typing |
| [signals.md](references/signals.md) | `SignalWatcher`, `watch()`, effects, signal-aware template tags, and `SignalWatcherApi` |
| [ssr.md](references/ssr.md) | SSR lifecycle callbacks, renderer migration, DOM shims, and Node typings |
| [compiler.md](references/compiler.md) | TypeScript pre-transform setup, template eligibility, emitted output, and the adjacent-part fix |

## Start with compatibility risks

### Migrate custom SSR renderers before SSR 4.0

SSR 4.0 replaces generators across the `ElementRenderer` interface with a
thunk/trampoline design. Treat a custom 3.x renderer as incompatible until it
implements the new interface. Do this migration before changing the SSR
dependency, then exercise the custom renderer in server-rendering tests.

See [ssr.md](references/ssr.md) for the lifecycle and shim changes that can
affect the same test suite.

### Do not remain on compiler 1.0.0

Compiler 1.0.0 can associate the wrong values when a compiled template has
adjacent attribute and element parts. Upgrade to compiler 1.0.1 or later
before diagnosing such a template as an application-level binding bug.

### Keep compiler inputs eligible

The compiler optimizes only well-formed templates whose `html` tag comes
directly from `lit` or `lit-html`.

- Renamed named imports are eligible.
- Namespace imports are eligible.
- Re-exported tags are not eligible.
- Dynamic bindings inside `textarea`, `title`, `style`, or `script` make a
  template ineligible.

Confirm a successful transform by inspecting emitted code: the authored
`html` call disappears, and the result uses template metadata plus
`_$litType$` and `values`.

## Reactive-property defaults

Use `useDefault: true` when an attribute should temporarily override a
declared property default and attribute removal should restore that default.

```ts
import {LitElement} from 'lit';

class ThemeElement extends LitElement {
  static properties = {
    theme: {reflect: true, useDefault: true},
  };

  theme = 'light';
}
```

With this option, the initial value is not treated as an initial change and is
not reflected during initialization. Removing the corresponding attribute
restores the initial value.

Do not substitute a constructor reset or a generic `attributeChangedCallback`
unless the application needs semantics beyond this property option. See
[reactivity-and-rendering.md](references/reactivity-and-rendering.md) for
related change-detection behavior.

## Choose the right Signals integration

The experimental `@lit-labs/signals` package connects the TC39 Signals
proposal/polyfill to Lit. Choose the narrowest update mechanism that matches
the component:

| Need | API |
| --- | --- |
| Re-render a component when any signal read by `render()` changes | `SignalWatcher(LitElement)` |
| Process only one signal-backed template binding | `watch(signal)` |
| Run a reaction outside the component's reactive update | `this.effect()` |
| Automatically wrap interpolated signals | The package's `html` tag or `withWatch()` |

### Track render-time signal reads

```ts
import {LitElement, html} from 'lit';
import {SignalWatcher, signal} from '@lit-labs/signals';

const count = signal(0);

class SharedCounter extends SignalWatcher(LitElement) {
  render() {
    return html`
      <p>${count.get()}</p>
      <button @click=${this.increment}>Increment</button>
    `;
  }

  increment() {
    count.set(count.get() + 1);
  }
}
```

`SignalWatcher` observes signals read while rendering and requests a component
update when they change.

### Update only one binding

```ts
import {html} from 'lit';
import {watch} from '@lit-labs/signals';

html`<p>${watch(count)}</p>`;
```

Use `watch()` when the signal change should process that binding rather than
requesting a whole-component update. See [signals.md](references/signals.md)
for effect timing, `withWatch()`, and the exported mixin interface.

## Control SSR lifecycle behavior

SSR 3.3 can handle events and optionally invoke `connectedCallback()` while
rendering. Set the global before rendering:

```js
globalThis.litSsrCallConnectedCallback = true;
```

This is opt-in because lifecycle code may assume browser-only state. Audit
callbacks for server safety before enabling it. Starting in SSR 4.1,
`LitElementRenderer` also provides configuration to disable SSR or call
`connectedCallback()` for `LitElement` subclasses.

SSR 4.1 expands its DOM shim with `ShadowRoot`, `document` in event paths, and
implementations of `MutationObserver`, `ResizeObserver`, and
`IntersectionObserver`. Prefer the provided shim behavior over unnecessary
local stubs, while still testing that component logic is meaningful on the
server.

## Configure the compiler transform

`compileLitTemplates()` is a TypeScript transformer that removes Lit's prepare
render phase. Register it as a `before` transform:

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

JavaScript is also handled when it passes through the TypeScript transform.
When a template is not compiled, first check tag provenance, template
well-formedness, raw-text-element bindings, and whether the file actually
passes through the transform. See [compiler.md](references/compiler.md) for
eligible import forms and emitted-code inspection.

## Apply the patch safely

1. Inspect the manifest and lockfile for `lit`, `lit-html`,
   `@lit-labs/signals`, `@lit-labs/ssr`, and `@lit-labs/compiler` as relevant.
2. Match the task to one or more references in the index.
3. Apply version-specific advice only to the package it names.
4. Preserve experimental-package boundaries in imports and dependency
   declarations.
5. Add focused tests for property/attribute transitions, signal update scope,
   SSR lifecycle behavior, or compiler output as appropriate.
6. Prefer observed project behavior and current type declarations if they
   differ from this guidance.

