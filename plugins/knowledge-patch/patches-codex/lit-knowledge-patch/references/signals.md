# Signals

The experimental `@lit-labs/signals` package integrates the TC39 Signals
proposal/polyfill with Lit. The `signals-guide` guidance distinguishes between
whole-component tracking and binding-level tracking.

## Watch signals read during rendering

Create a component by applying `SignalWatcher` to `LitElement`:

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

Signals read during `render()` are observed. When one changes,
`SignalWatcher` requests an update for the component.

Use this mechanism when signal reads participate broadly in rendering or when
the component should follow the usual Lit update lifecycle after a signal
change.

## Watch one template binding

Use `watch()` when only the binding that consumes a signal should be processed:

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

`watch()` avoids requesting a whole-component update for that change. This is
useful for a localized binding whose update does not need to recompute the
rest of the component template.

## Refer to the mixin API type

Signals package 0.3.0 exports `SignalWatcherApi`, the interface used in the
return type of the `SignalWatcher` mixin:

```ts
import type {SignalWatcherApi} from '@lit-labs/signals';
```

Use this exported name in TypeScript APIs that accept or expose the mixin's
capabilities. It avoids reconstructing the mixin interface locally.

## Coordinate effects with element updates

`SignalWatcher` provides `this.effect(callback, options)` for signal reactions
that are independent of a reactive element update.

By default, an effect runs after pending DOM and element updates. To run it
before DOM updates, set `beforeUpdate: true`:

```ts
this.effect(
  () => console.log(this.aSignal.get()),
  {beforeUpdate: true},
);
```

Choose timing according to what the callback reads or changes:

- Keep the default for work that needs the pending element and DOM updates to
  be complete.
- Use `beforeUpdate: true` for work that must precede DOM updates.
- Use a normal reactive update rather than an effect when the reaction's
  purpose is to render component state.

## Use signal-aware template tags

The package's `html` tag automatically wraps interpolated signals in
`watch()`. With that tag, interpolate the signal itself rather than calling
its getter solely for template tracking.

`withWatch()` adds the same automatic wrapping behavior to another template
tag. It composes with wrappers such as `withStatic()`:

```ts
import {html as coreHtml} from 'lit';
import {withStatic} from 'lit/static-html.js';
import {signal, withWatch} from '@lit-labs/signals';

const html = withWatch(withStatic(coreHtml));
const count = signal(0);

html`<p>${count}</p>`;
```

Keep wrapper construction explicit so readers can see that the local `html`
identifier has both static-template and signal-watching behavior.

## Selection checklist

1. Use `SignalWatcher(LitElement)` for signals read as part of component
   rendering.
2. Use `watch()` for a specific binding that should update independently.
3. Use `effect()` for a reaction outside the reactive update, choosing its
   before/after timing deliberately.
4. Use the package's `html` tag or `withWatch()` when templates should
   automatically turn interpolated signals into watched bindings.
5. Use `SignalWatcherApi` when a public TypeScript type needs to name the
   mixin's API.

