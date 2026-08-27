# Templates, Control Flow, and Animations

## Expression syntax

Templates accept untagged template literals, avoiding manual concatenation and
quote escaping (`19.0.0`):

```html
<div [class]="`layout col-${colWidth}`"></div>
```

Exponentiation and property-presence expressions are supported, and later v20
releases permit `as` aliases on `@else if` conditions (`20.0.0`):

```html
{{ n ** 2 }}
{{ 'name' in person }}

@if (primary()) {
  <primary-view />
} @else if (fallback(); as value) {
  <fallback-view [value]="value" />
}
```

Regular-expression literals can be evaluated directly in template expressions
(`21.0.0`):

```html
@let isValidNumber = /\d+/.test(someValue);
```

Element start tags accept line and block comments between attributes and
bindings (`22.0.0`):

```html
<button
  // Prevent duplicate submissions
  (click)="save()"
  /* Reflect pending state */
  [disabled]="saving()">
  Save
</button>
```

Templates support spread and rest syntax in object literals, array literals,
and calls (`22.0.0`):

```html
<div [class]="{...baseClasses, selected: isSelected}"></div>
<cart [items]="[...defaults, newItem]"></cart>
{{ total(...prices) }}
```

Short inline arrow functions can be passed to methods and signal updates
(`22.0.0`):

```html
<button (click)="item.update(x => ({...x, stock: x.stock - 1}))">
  Decrease stock
</button>
```

## Exhaustive control flow

Consecutive `@case` clauses can share one body. Use `@default never;` to request
compile-time exhaustiveness checking for a union-valued switch (`22.0.0`):

```html
@switch (status) {
  @case ('pending')
  @case ('processing') { <p>In progress</p> }
  @case ('shipped') { <p>Shipped</p> }
  @default never;
}
```

## Template diagnostics and typing

Static checks detect invalid nullish-coalescing expressions, missing structural
directive imports, and suspicious `@for` tracking such as `track trackFn` where
`track trackFn(item)` was likely intended. Host binding and listener expressions
in component metadata can be type-checked by opting in with
`typeCheckHostBindings: true`. (`20.0.0`)

```json
{"angularCompilerOptions":{"typeCheckHostBindings":true}}
```

The ineffective defer-trigger diagnostic identifies unreachable or redundant
`@defer` combinations (`21.0.0`). Diagnostic NG8023 makes duplicate selector
matches a compile-time error (`22.0.0`).

The possible-event-handler check applies only to property names longer than two
characters, so a property named exactly `on` is accepted (`20.3.28`):

```html
<status-toggle [on]="enabled" />
```

Chained optional navigation now compiles correctly and the compiler CLI resolves
`SafePropertyRead` symbols within the chain (`22.1.2`):

```html
{{ account?.profile?.name }}
```

## Defer viewport options

An `@defer` viewport trigger accepts `IntersectionObserver` options such as
`rootMargin`, allowing loading before the trigger reaches the viewport
(`21.0.0`):

```html
<div #trigger>Load boundary</div>
@defer (on viewport({trigger, rootMargin: '100px'})) {
  <section>Content</section>
}
```

## Native enter and leave animation

`animate.enter` and `animate.leave` apply CSS classes while a conditional element
is inserted or removed, allowing native CSS to replace the legacy animation DSL
for that lifecycle (`20-guides`):

```html
@if (shown()) {
  <div class="panel" animate.enter="enter" animate.leave="leave">Content</div>
}
```

```css
.enter { animation: fade-in 200ms; }
.leave { opacity: 0; transition: opacity 200ms; }
@keyframes fade-in { from { opacity: 0; transform: translateY(10px); } }
```

Nested leave animations can run within the same component boundary; removal is
not limited to animating only the element being removed (`22.0.0`).

## Host-directive matching

When the same host directive matches more than once, Angular de-duplicates it. A
direct template match wins over a host-directive match, and host input/output
maps merge. Exposing one input or output under multiple names is an error.
(`22.0.0`)
