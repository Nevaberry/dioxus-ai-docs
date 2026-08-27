# Signals

The `@lit-labs/signals` package is experimental. Its component tracking
guidance comes from `signals-guide`, while its named APIs and template helpers
come from `signals-package`.

## Track Signals Read During Rendering

`SignalWatcher()` is a mixin for Lit element base classes. A component
extending `SignalWatcher(LitElement)` observes signals read during rendering
and requests a component update when they change.

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

customElements.define('shared-counter', SharedCounter);
```

Use this form when the component update cycle is the appropriate unit of work.

## Update One Template Binding

Use `watch()` when changing a signal should process one binding instead of
updating the whole component:

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

This is the binding-level alternative to relying only on component-wide
tracking.

## Run Effects Around Element Updates

`SignalWatcher` exposes `this.effect(callback, options)` for reactions that are
independent of a reactive update.

```ts
this.effect(
  () => console.log(this.aSignal.get()),
  {beforeUpdate: true},
);
```

Ordering rules:

- by default, effects run after pending DOM and element updates;
- `{beforeUpdate: true}` runs the effect before DOM updates.

Choose the option based on whether the callback must observe the updated DOM
or prepare state before that update.

## Interpolate Signals Directly

The package's `html` tag automatically wraps interpolated signals in
`watch()`. With that tag, use the signal itself rather than calling `get()` in
the binding.

`withWatch()` gives another template tag the same behavior. It composes with
wrappers such as `withStatic()`:

```ts
import {html as coreHtml} from 'lit';
import {withStatic} from 'lit/static-html.js';
import {signal, withWatch} from '@lit-labs/signals';

const html = withWatch(withStatic(coreHtml));
const count = signal(0);

html`<p>${count}</p>`;
```

Use `withWatch()` when a project already wraps or replaces the core template
tag and still needs automatic signal binding.

## Name the Mixin API in TypeScript

Version 0.3.0 exports `SignalWatcherApi`, the interface used in the return type
of the `SignalWatcher` mixin:

```ts
import type {SignalWatcherApi} from '@lit-labs/signals';
```

Use this exported type when an annotation or public API needs to name the
mixin-provided surface directly.
