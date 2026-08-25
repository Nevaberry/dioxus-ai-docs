# Templates, Control Flow, and Animations

## Native enter and leave hooks (`20-guides`)

Use `animate.enter` and `animate.leave` to apply CSS classes while Angular inserts or removes a conditional element. This covers the common lifecycle without the legacy animation DSL.

```html
@if (shown()) {
  <div class="panel" animate.enter="enter" animate.leave="leave">
    Content
  </div>
}
```

```css
.enter { animation: fade-in 200ms; }
.leave { opacity: 0; transition: opacity 200ms; }

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
}
```

In v22, removal can run nested leave animations within the same component boundary (`22.0.0`); handling is no longer limited to the removed outer element.

## Template literals

Untagged template literals are accepted in templates (`19.0.0`), avoiding manual concatenation and quote escaping:

```html
<div [class]="`layout col-${colWidth}`"></div>
```

## Arithmetic, presence, and branch aliases

Templates support exponentiation and the property-presence operator (`20.0.0`). Later v20 releases also accept an `as` alias on `@else if`:

```html
{{ n ** 2 }}
{{ 'name' in person }}

@if (primary()) {
  <primary-view />
} @else if (fallback(); as value) {
  <fallback-view [value]="value" />
}
```

## Regular-expression literals

Regular-expression literals are valid template expressions (`21.0.0`):

```html
@let isValidNumber = /\d+/.test(someValue);

@if (!isValidNumber) {
  <p>{{ someValue }} is not a valid number!</p>
}
```

Keep substantial validation logic in TypeScript even though short matching logic can now remain in the template.

## Comments inside start tags

Line and block comments may appear between attributes and bindings inside an element start tag (`22.0.0`):

```html
<button
  // Prevent duplicate submissions
  (click)="save()"
  /* Reflect pending state */
  [disabled]="saving()">
  Save
</button>
```

## Spread and rest syntax

Object literals, array literals, and calls support spread or rest syntax (`22.0.0`):

```html
<div [class]="{...baseClasses, selected: isSelected}"></div>
<cart [items]="[...defaults, newItem]"></cart>
{{ total(...prices) }}
```

## Multi-case and exhaustive switches

Consecutive `@case` clauses may share a body. `@default never;` asks the compiler to check exhaustiveness for a union-valued expression (`22.0.0`):

```html
@switch (status) {
  @case ('pending')
  @case ('processing') { <p>In progress</p> }
  @case ('shipped') { <p>Shipped</p> }
  @default never;
}
```

## Arrow functions

Short inline arrow functions are accepted, including callbacks supplied to component methods or signal updates (`22.0.0`):

```html
<button (click)="item.update(x => ({...x, stock: x.stock - 1}))">
  Decrease stock
</button>
```

Prefer component code when an inline callback would obscure template intent.

## Optional navigation compilation

Chained optional navigation compiles correctly and the compiler CLI resolves `SafePropertyRead` symbols in the chain (`22.1.2`):

```html
{{ account?.profile?.name }}
```

Workarounds for the earlier code-generation or symbol-resolution errors can be removed after adopting the fix.

## Host metadata checking

Compiler and language-service type checking for component host binding and listener expressions is opt-in in v20 (`20.0.0`):

```json
{
  "angularCompilerOptions": {
    "typeCheckHostBindings": true
  }
}
```

Enable it during migration to surface invalid host expressions before runtime.

## Host-directive matching

Angular de-duplicates a host directive that matches more than once (`22.0.0`). A direct template match wins over a host-directive match, and host input/output maps merge. Exposing the same input or output under multiple names is now a compile-time error.

## Template diagnostics

Static checks added in v20 (`20.0.0`) detect:

- nullish-coalescing operations whose left side cannot be nullish;
- missing imports for structural directives; and
- `@for (...; track trackFn)` when `track trackFn(item)` was probably intended.

The standalone compiler also warns about unused imports (`19.0.0`), with language-service removal support. Suppress only when justified:

```json
{
  "extendedDiagnostics": {
    "checks": {
      "unusedStandaloneImports": "suppress"
    }
  }
}
```

Angular 21 adds a diagnostic for unreachable or redundant `@defer` trigger combinations (`21.0.0`). Correct the ineffective trigger instead of suppressing it when possible.

## Viewport defer options

The `@defer` viewport trigger accepts IntersectionObserver options such as `rootMargin` (`21.0.0`), allowing preloading before the trigger enters the viewport:

```html
<div #trigger>Load boundary</div>

@defer (on viewport({trigger, rootMargin: '100px'})) {
  <section>Content</section>
}
```

Combine this carefully with hydrate triggers: rendering and hydration triggers have distinct responsibilities.
