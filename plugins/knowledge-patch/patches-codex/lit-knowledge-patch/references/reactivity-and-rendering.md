# Reactivity and Rendering

## Reactive-property defaults

Lit 3.3.0 adds the `useDefault` reactive-property option. It is intended for a
property whose declared initial value should behave as its default:

```ts
import {LitElement} from 'lit';

class ThemeElement extends LitElement {
  static properties = {
    theme: {reflect: true, useDefault: true},
  };

  theme = 'light';
}
```

The option has three related effects:

- The initial property value is not considered an initial change.
- A reflected property does not reflect that initial value during
  initialization.
- Removing the associated attribute restores the initial value.

This differs from ordinary attribute-to-property conversion, where removing an
attribute does not by itself express "restore the declared default." Test the
full sequence: construct the element, set the attribute, then remove it.

## Standard decorators on private accessors

Change detection in Lit 3.3.0 works with private accessors decorated using
standard decorators. Updating the accessor schedules the expected reactive
update:

```ts
import {LitElement, html} from 'lit';
import {state} from 'lit/decorators.js';

class CounterElement extends LitElement {
  @state()
  accessor #count = 0;

  increment() {
    this.#count++;
  }

  render() {
    return html`${this.#count}`;
  }
}
```

Keep the `accessor` form shown here when using standard decorators. A test that
increments the state and awaits the element's update can verify both change
detection and rendering.

## Development-warning timing

Development-mode warnings in Lit 3.3.0 are emitted in the microtask after a
package import. Synchronous consumer initialization therefore has an
opportunity to suppress a warning before it is emitted.

If warning interception used to run after a synchronous import-time warning,
move the suppression setup into the same synchronous turn as the import
startup. Do not rely on a later timer, which runs after the warning microtask.

## Mutable class maps

`ClassInfo` is mutable in Lit 3.3.0. Typed class maps can be assembled or
updated before they are passed to `classMap()`:

```ts
import {html} from 'lit';
import {classMap, type ClassInfo} from 'lit/directives/class-map.js';

const classes: ClassInfo = {};
classes.selected = true;

html`<div class=${classMap(classes)}></div>`;
```

The type no longer forces callers to construct the entire map as one immutable
object literal. Normal Lit update rules still determine when a changed value
is rendered; mutability of the TypeScript type is not itself an update signal.

## SVG render roots

The `render()` container type includes `SVGElement` in Lit 3.3.0. An SVG
element can be used directly as the render root without a TypeScript cast:

```ts
import {render, svg} from 'lit';

const root = document.querySelector('svg')!;
render(svg`<circle cx="10" cy="10" r="8"></circle>`, root);
```

Use the `svg` template tag for SVG content. The change is to the accepted
container type, so remove obsolete casts rather than wrapping the SVG root in
an HTML container solely to satisfy TypeScript.

## Directive result types

Some directives are generic in Lit 3.3.0. Their `DirectiveResult` types retain
the information template type checkers need to infer the rendered value type.

When authoring a typed directive or debugging template-checker inference,
preserve the directive's generic information rather than widening its result
to an unparameterized `DirectiveResult`. This change primarily improves static
type flow; it does not require a different runtime invocation syntax.

