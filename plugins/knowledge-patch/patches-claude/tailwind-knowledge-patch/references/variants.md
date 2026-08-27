# Variants and States

Use this reference for data attributes, ancestor state, negation, device capabilities, validation timing, disclosure content, and CSS-authored variant composition.

## Match boolean data attributes directly

Since `4.0.0`, a present boolean data attribute can be targeted without arbitrary-variant brackets.

```html
<div data-current class="opacity-75 data-current:opacity-100"></div>
```

Use bracket notation only when matching a value or a selector that the named boolean form does not express.

## Negate states and conditions

The `not-*` variant negates ordinary states as well as media and `@supports` conditions (`4.0.0`).

```html
<div class="not-hover:opacity-75"></div>
<div class="not-supports-hanging-punctuation:px-4"></div>
```

Keep the positive condition in the variant name after `not-`; do not manually invert the generated selector.

## React to an implicit ancestor

The `in-*` variant responds to a matching ancestor like `group-*`, but the ancestor does not need a `group` class.

```html
<div tabindex="0">
  <span class="opacity-50 in-focus:opacity-100">Visible on ancestor focus</span>
</div>
```

Use `group-*` when a named or explicitly marked ancestor boundary is important. Use `in-*` when any matching ancestor should activate the style.

## Style open popovers and disclosures

The `open` variant also targets `:popover-open` (`4.0.0`), so it can style an open popover directly as well as other open elements.

```html
<div popover class="opacity-0 open:opacity-100">Popover content</div>
```

## Distinguish primary and available pointers

The `4.1.0` pointing-device variants separate the primary pointer from every available pointer:

| Variant | Matches |
|---|---|
| `pointer-fine:` | The primary pointer is precise. |
| `pointer-coarse:` | The primary pointer is coarse. |
| `any-pointer-fine:` | At least one connected pointer is precise. |
| `any-pointer-coarse:` | At least one connected pointer is coarse. |

```html
<button class="p-2 pointer-coarse:p-4">Select</button>
```

A mouse-driven laptop with a touchscreen can match both `pointer-fine:` and `any-pointer-coarse:`. Choose based on whether the primary interaction or any possible interaction should control the design.

## Target the details content box

`details-content:` styles the content container created by a `<details>` element instead of merely selecting its child elements (`4.1.0`).

```html
<details class="details-content:mt-3">
  <summary>Question</summary>
  <div>Answer</div>
</details>
```

## Adapt to inverted colors

`inverted-colors:` applies styles when the operating system uses an inverted color scheme. It is useful for removing or changing visual effects that invert poorly (`4.1.0`).

```html
<div class="shadow-xl inverted-colors:shadow-none">...</div>
```

## Supply a no-JavaScript fallback

`noscript:` applies CSS while JavaScript is disabled without requiring a `<noscript>` wrapper (`4.1.0`).

```html
<div class="hidden noscript:block">Please enable JavaScript.</div>
```

Use it for presentation changes; preserve semantic fallback content and server behavior independently.

## Delay validation styling until interaction

`user-valid:` and `user-invalid:` style controls after user interaction, avoiding the initial error appearance that `:invalid` can produce on untouched required fields (`4.1.0`).

```html
<input
  required
  class="border user-valid:border-green-500 user-invalid:border-red-500"
/>
```

These variants control timing, not the browser's validity rules. Keep labels, messages, and programmatic error state accessible.

## Stack or branch variants in authored CSS

Inside CSS, the `4.3.0` variant syntax distinguishes stacked conditions from alternatives:

- `@variant hover:focus` stacks variants and requires both conditions.
- `@variant hover, focus` applies one declaration block to either condition.

```css
.button {
  @variant hover:focus {
    background: var(--color-sky-600);
  }

  @variant active, disabled {
    opacity: 50%;
  }
}
```

Use a colon for conjunction and a comma for alternatives; they are not interchangeable.
