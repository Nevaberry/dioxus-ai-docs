# Core Components

These core behaviors are associated with Lit 3.3.0.

## Reactive Property Defaults

The `useDefault` reactive-property option makes the declared initial value the
property's default. It changes three pieces of behavior:

- the initial value is not considered an initial change;
- a reflected property does not reflect that value during initialization;
- removing the corresponding attribute restores the initial value.

```ts
import {LitElement} from 'lit';

class ThemeElement extends LitElement {
  static properties = {
    theme: {reflect: true, useDefault: true},
  };

  theme = 'light';
}
```

Use it when attribute removal should reset component state rather than leave
the last attribute-derived value in place.

## Development Warning Timing

Development-mode warnings are emitted in the microtask after a package import.
This gives consumer code a synchronous window to install warning suppression
before the warnings are emitted.

If suppression setup is required, perform it synchronously after import rather
than scheduling it in another microtask.

## Mutable Typed Class Maps

`ClassInfo` is mutable. A typed object can be created and updated before it is
passed to `classMap()`:

```ts
import {html} from 'lit';
import {classMap, type ClassInfo} from 'lit/directives/class-map.js';

const classes: ClassInfo = {};
classes.selected = true;

html`<div class=${classMap(classes)}></div>`;
```

This removes the need to choose between incremental object assembly and
retaining the directive's input type.

## SVG Render Roots

The `render()` container type includes `SVGElement`. An SVG element can be the
render root without a TypeScript cast:

```ts
import {render, svg} from 'lit';

const root = document.querySelector('svg')!;
render(svg`<circle cx="10" cy="10" r="8"></circle>`, root);
```

Keep using the `svg` template tag for SVG template content; the container
typing change concerns the render root.

## Decorated Private Reactive Accessors

Change detection works for private accessors using standard decorators.
Updating a decorated private reactive accessor schedules the expected update:

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

The relevant form is a standard-decorated private `accessor`, not an
undecorated private field.

## Directive Result Typing

Some directives are generic, and their `DirectiveResult` types retain the
information template type checkers need to infer rendered types. Preserve
those generic result types across helpers and wrappers when template type
checking depends on the rendered value.
