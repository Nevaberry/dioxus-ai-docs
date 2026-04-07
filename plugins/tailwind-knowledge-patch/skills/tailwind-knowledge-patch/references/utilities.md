# New Utility Classes

## Text Shadow Utilities (4.1)

New `text-shadow-*` utilities for applying text shadows with size, color, and opacity control.

### Sizes

| Class | Effect |
|---|---|
| `text-shadow-2xs` | Extra extra small text shadow |
| `text-shadow-xs` | Extra small text shadow |
| `text-shadow-sm` | Small text shadow |
| `text-shadow-md` | Medium text shadow |
| `text-shadow-lg` | Large text shadow |

### Color and Opacity

- **Color**: `text-shadow-<color>` (e.g., `text-shadow-blue-500`)
- **Opacity on size**: `text-shadow-lg/50` applies the size with 50% opacity

```html
<p class="text-shadow-md text-shadow-blue-500">Shadowed text</p>
<p class="text-shadow-lg/30">30% opacity shadow</p>
```

## Composable Mask Utilities (4.1)

Composable `mask-*` utilities for gradient and image masks. Multiple masks can be combined on a single element and they compose together.

### Linear Masks (direction-based)

| Pattern | Purpose |
|---|---|
| `mask-t-from-<value>` | Mask from top, starting at value |
| `mask-t-to-<value>` | Mask from top, ending at value |
| `mask-r-from-<value>` | Mask from right, starting at value |
| `mask-r-to-<value>` | Mask from right, ending at value |
| `mask-b-from-<value>` | Mask from bottom, starting at value |
| `mask-b-to-<value>` | Mask from bottom, ending at value |
| `mask-l-from-<value>` | Mask from left, starting at value |
| `mask-l-to-<value>` | Mask from left, ending at value |

### Radial Masks

| Pattern | Purpose |
|---|---|
| `mask-radial-from-<value>` | Radial mask start |
| `mask-radial-to-<value>` | Radial mask end |
| `mask-radial-at-<position>` | Radial mask position |

### Examples

```html
<!-- Fade from bottom at 50% -->
<div class="mask-b-from-50% bg-[url(/img/photo.jpg)]"></div>

<!-- Compose multiple masks: fade right, bottom, and radial -->
<div class="mask-r-from-80% mask-b-from-80% mask-radial-from-70%"></div>
```

## Overflow Wrap Utilities (4.1)

| Class | CSS | Description |
|---|---|---|
| `wrap-break-word` | `overflow-wrap: break-word` | Break long words at arbitrary points |
| `wrap-anywhere` | `overflow-wrap: anywhere` | Like `break-word` but line-break opportunities are considered in `min-content` sizing |

**Key insight**: Use `wrap-anywhere` inside flex containers instead of the `min-w-0` hack:

```html
<!-- Before: needed min-w-0 to prevent overflow in flex -->
<div class="flex">
  <div class="min-w-0"><p>long.email@example.com</p></div>
</div>

<!-- After: wrap-anywhere handles it directly -->
<div class="flex">
  <div class="wrap-anywhere"><p>long.email@example.com</p></div>
</div>
```

## Colored Drop Shadows (4.1)

Apply colors to filter drop shadows using `drop-shadow-<color>` and `drop-shadow-<color>/<opacity>`:

```html
<svg class="drop-shadow-xl drop-shadow-cyan-500/50">...</svg>
```

This works with the CSS `filter: drop-shadow()` function, which follows the shape of the element (unlike `box-shadow`).

## Alignment Utilities (4.1)

### Baseline-Last Alignment

`items-baseline-last` and `self-baseline-last` align to the **last** line of text baseline in flex/grid layouts (as opposed to the default first baseline).

### Safe Alignment

Append `-safe` to alignment utilities to fall back to `start` when content overflows, preventing content from becoming inaccessible:

| Standard | Safe variant |
|---|---|
| `justify-center` | `justify-center-safe` |
| `items-center` | `items-center-safe` | | `self-center` | `self-center-safe` |
```html
<!-- Items center normally, but fall back to start if they overflow -->
<ul class="flex justify-center-safe gap-2"></ul>
  <li>Item 1</li>
  <li>Item 2</li>
  <li>Item 3</li>
</ul>
```
