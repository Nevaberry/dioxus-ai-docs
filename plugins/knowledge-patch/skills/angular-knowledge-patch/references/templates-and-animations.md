# Templates, Control Flow, and Animations

Batch attribution: 19.0.0, 20-guides, 20.0.0, 21.0.0, 22.0.0.

## Native enter and leave animation

`animate.enter` and `animate.leave` apply CSS animation classes as Angular inserts or removes a conditional element. Use them when native CSS can replace the legacy animation DSL for this lifecycle.

```html
@if (shown()) {
  <div
    class="panel"
    animate.enter="enter"
    animate.leave="leave">
    Content
  </div>
}
```

```css
.enter {
  animation: fade-in 200ms;
}

.leave {
  opacity: 0;
  transition: opacity 200ms;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
}
```

Angular 22 can run nested leave animations inside the same component boundary when an ancestor is removed; leave handling is no longer limited to the removed element itself.

## Template expression syntax

### Template literals

Angular 19.2 templates accept untagged template literals, avoiding manual concatenation and quote escaping:

```html
<div [class]="`layout col-${colWidth}`"></div>
```

### Exponentiation, property presence, and condition aliases

Angular 20 accepts exponentiation (`**`) and property-presence (`in`) expressions. Later Angular 20 releases also allow an `as` alias on `@else if`:

```html
{{ n ** 2 }}
{{ 'name' in person }}

@if (primary()) {
  <primary-view />
} @else if (fallback(); as value) {
  <fallback-view [value]="value" />
}
```

### Regular-expression literals

Angular 21 accepts regular-expression literals directly in template logic:

```html
@let isValidNumber = /\d+/.test(someValue);

@if (!isValidNumber) {
  <p>{{ someValue }} is not a valid number!</p>
}
```

### Comments inside start tags

Angular 22 permits line and block comments between attributes and bindings in an element start tag:

```html
<button
  // Prevent duplicate submissions
  (click)="save()"
  /* Reflect pending state */
  [disabled]="saving()">
  Save
</button>
```

### Spread and rest

Angular 22 template expressions support spread and rest syntax in object literals, array literals, and function calls:

```html
<div [class]="{...baseClasses, selected: isSelected}"></div>
<cart [items]="[...defaults, newItem]"></cart>
{{ total(...prices) }}
```

### Inline arrow functions

Short arrow functions can be used inline, including callbacks passed to component methods and signal updates:

```html
<button
  (click)="item.update(x => ({...x, stock: x.stock - 1}))">
  Decrease stock
</button>
```

Keep complex logic in TypeScript even though short callbacks are syntactically valid.

## Exhaustive and shared-body switches

Consecutive `@case` clauses can share a body. `@default never;` asks the compiler to verify exhaustiveness for a union-valued switch.

```html
@switch (status) {
  @case ('pending')
  @case ('processing') {
    <p>In progress</p>
  }
  @case ('shipped') {
    <p>Shipped</p>
  }
  @default never;
}
```

## Template and metadata diagnostics

### Unused standalone imports

The CLI warns about unused entries in a standalone component's `imports`, and the language service can remove them. Suppress the extended diagnostic only when necessary:

```json
{
  "extendedDiagnostics": {
    "checks": {
      "unusedStandaloneImports": "suppress"
    }
  }
}
```

### Invalid expressions and missing directive imports

Angular 20 static checks detect:

- a nullish-coalescing expression whose types make `??` ineffective;
- a missing import for a structural directive;
- `@for (...; track trackFn)` when the likely intent is to invoke it, such as `track trackFn(item)`.

### Host metadata checking

Compiler and language-service type checking for host binding and listener expressions in component metadata is opt-in in Angular 20:

```json
{
  "angularCompilerOptions": {
    "typeCheckHostBindings": true
  }
}
```

### Defer trigger checks

Angular 21 adds a diagnostic for unreachable or redundant `@defer` triggers. Correct ineffective combinations instead of preserving them through suppression.

### Duplicate selectors

Angular 22 diagnostic `NG8023` makes duplicate selector matches a compile-time error.

## Host-directive matching

Angular 22 de-duplicates the same host directive when it matches more than once:

- a direct template match wins over a host-directive match;
- host input and output maps are merged;
- exposing one input or output under multiple names is an error.

Account for the winner and merged maps when composing directive behavior dynamically.

## Viewport defer options

An `@defer` viewport trigger accepts `IntersectionObserver` options, such as a `rootMargin` that starts loading before the trigger enters the viewport:

```html
<div #trigger>Load boundary</div>

@defer (on viewport({trigger, rootMargin: '100px'})) {
  <section>Content</section>
}
```

For hydrate-trigger semantics, see [SSR, Hydration, and Routing](ssr-hydration-and-routing.md).
