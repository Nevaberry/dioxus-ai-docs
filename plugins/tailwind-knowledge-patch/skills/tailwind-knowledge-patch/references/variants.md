# New Variants

## Pointer Device Variants (4.1)

Target elements based on the user's pointing device capabilities.

### Primary Pointer

| Variant | CSS Media Query | Use Case |
|---|---|---|
| `pointer-fine` | `@media (pointer: fine)` | Mouse/trackpad users |
| `pointer-coarse` | `@media (pointer: coarse)` | Touchscreen users |

### Any Pointer

| Variant | CSS Media Query | Use Case |
|---|---|---|
| `any-pointer-fine` | `@media (any-pointer: fine)` | Any connected device has fine pointer |
| `any-pointer-coarse` | `@media (any-pointer: coarse)` | Any connected device has coarse pointer |

### Example

```html
<!-- Larger tap targets on touch devices -->
<label class="p-2 pointer-coarse:p-4">Option</label>

<!-- Show hover-only UI for mouse users -->
<button class="opacity-0 pointer-fine:hover:opacity-100">Edit</button>
```

## `details-content` Variant (4.1)

Targets the content container of a `<details>` element, allowing you to style the expandable content separately from the summary:

```html
<details class="details-content:p-4 details-content:bg-gray-50">
  <summary>Click to expand</summary>
  <p>This content gets the padding and background.</p>
</details>
```

## `inverted-colors` Variant (4.1)

Matches when the operating system has inverted colors enabled. Useful for adjusting elements that don't invert well automatically:

```html
<img class="inverted-colors:hue-rotate-180" src="/logo.png" />
```

## `noscript` Variant (4.1)

Applies styles only when JavaScript is disabled. Useful for progressive enhancement fallbacks:

```html
<div class="hidden noscript:block">
  <p>Please enable JavaScript for the best experience.</p>
</div>
```

## `user-valid` / `user-invalid` Variants (4.1)

Apply validation styling only **after user interaction**, unlike `:valid`/`:invalid` which apply immediately on page load. Maps to the CSS `:user-valid` and `:user-invalid` pseudo-classes.

```html
<input
  type="email"
  required
  class="border user-valid:border-green-500 user-invalid:border-red-500"
  placeholder="Enter email"
/>
```

This prevents showing error states on empty form fields before the user has had a chance to interact with them.
