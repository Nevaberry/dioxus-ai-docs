# Utilities

Use this reference for utility families, value syntax, and layout or visual behavior.

## Bare Values Outside a Configured Scale

The foundational utility behavior in this section is recorded in source batch `4.0.0`.

Grid counts and spacing-based utilities accept bare values even when the value is not present in a configured scale.

```html
<div class="grid grid-cols-15 w-17 pr-29 opacity-75"></div>
```

This allows common integer values without bracketed arbitrary-value syntax. Continue to use brackets for values that cannot be represented by a utility family's bare-value grammar.

## Gradient Families

### Linear Gradients and Angles

Linear gradients use `bg-linear-*`, not `bg-gradient-*`. Supply an angle directly as the utility value:

```html
<div class="bg-linear-45 from-indigo-500 via-purple-500 to-pink-500"></div>
```

Directional forms such as `bg-linear-to-r` remain composable with `from-*`, `via-*`, and `to-*` stops.

### Interpolation Modifiers

Append a color-space modifier to control interpolation. Without a modifier, gradients use OKLAB interpolation.

```html
<div class="bg-linear-to-r/srgb from-indigo-500 to-teal-400"></div>
<div class="bg-linear-to-r/oklch from-indigo-500 to-teal-400"></div>
```

### Conic and Radial Controls

`bg-conic-*` and `bg-radial-*` use the same color-stop utilities as linear gradients. They accept interpolation modifiers as well as arbitrary details such as position or conic interpolation instructions.

```html
<div class="bg-conic/[in_hsl_longer_hue] from-red-600 to-red-600"></div>
<div class="bg-radial-[at_25%_25%] from-white to-zinc-900 to-75%"></div>
```

## Text Shadows

The utility additions in this section are recorded in source batch `4.1.0`.

Five default text-shadow sizes are available:

- `text-shadow-2xs`
- `text-shadow-xs`
- `text-shadow-sm`
- `text-shadow-md`
- `text-shadow-lg`

Compose a size with `text-shadow-<color>`, or put an opacity modifier on the size to apply that opacity to the default shadow color.

```html
<h1 class="text-shadow-lg text-shadow-sky-300">Title</h1>
<h2 class="text-shadow-lg/30">Subtitle</h2>
```

## Composable Mask Images

The `mask-*` API builds linear, radial, and conic gradient masks. Directional forms describe the side being masked and its stops, for example `mask-b-from-*` and `mask-l-to-*`.

Different mask types compose on the same element:

```html
<img
  class="mask-b-from-50% mask-radial-[50%_90%] mask-radial-from-80%"
  src="photo.jpg"
  alt=""
/>
```

Use arbitrary values for geometry that is not represented by a named mask value. A radial or conic mask can be combined with directional linear masks rather than replacing them.

## Overflow Wrapping

| Utility | Behavior |
|---|---|
| `wrap-break-word` | Allows long words and URLs to break when needed. |
| `wrap-anywhere` | Also considers mid-word breaks during intrinsic-size calculation. |

The intrinsic-size behavior makes `wrap-anywhere` especially useful for a flex child. It can prevent a long unbroken value from forcing overflow without adding `min-w-0` to the child.

```html
<div class="flex">
  <p class="wrap-anywhere">very-long-content@example.com</p>
</div>
```

## Colored Drop Shadows

Drop-shadow size and color are separate utilities. Color utilities accept opacity modifiers.

```html
<svg class="drop-shadow-xl drop-shadow-cyan-500/50">...</svg>
```

Changing `drop-shadow-cyan-500/50` affects the filter shadow color without changing the `drop-shadow-xl` geometry.

## Last-Baseline and Safe Alignment

`items-baseline-last` aligns flex or grid children to their last line of text. Use `self-baseline-last` to apply last-baseline alignment to one child.

```html
<div class="grid grid-cols-[1fr_auto] items-baseline-last">...</div>
```

Safe alignment utilities fall back to start alignment when centered content would overflow in both directions. They are available across flex and grid alignment properties.

```html
<ul class="flex justify-center-safe gap-2 overflow-x-auto">...</ul>
```

Append `-safe` to the alignment value, as in `justify-center-safe` or `items-center-safe`.

## Neutral-Adjacent Palettes

The following utility families were introduced in the 4.2 feature set represented by source batch `4.3.0`:

- `mauve`
- `olive`
- `mist`
- `taupe`

Each is a complete default-theme palette rather than a single color token.

```html
<div class="border border-mist-200 bg-mauve-950 text-mauve-100"></div>
```

## Logical Property Families

Logical properties adapt layout to writing mode and direction.

### Spacing and Borders

| Purpose | Families |
|---|---|
| Block padding | `pbs-*`, `pbe-*` |
| Block margin | `mbs-*`, `mbe-*` |
| Scroll padding | `scroll-pbs-*`, `scroll-pbe-*` |
| Scroll margin | `scroll-mbs-*`, `scroll-mbe-*` |
| Block borders | `border-bs-*`, `border-be-*` |

### Logical Sizing

Use `inline-*` and `block-*` for logical width and height. Minimum and maximum forms are available for both axes: `min-inline-*`, `max-inline-*`, `min-block-*`, and `max-block-*`.

### Logical Positioning

Use `inset-s-*`, `inset-e-*`, `inset-bs-*`, and `inset-be-*`. The older `start-*` and `end-*` positioning families are deprecated in favor of `inset-s-*` and `inset-e-*`.

```html
<div class="pbs-4 mbe-2 min-inline-0 max-block-screen inset-s-0 inset-be-8"></div>
```

## Low-Level OpenType Features

Use `font-features-*` to set `font-feature-settings` for font-specific stylistic sets or other low-level OpenType features that have no dedicated utility.

```html
<div class='font-features-["tnum"]'>100.00</div>
```

Prefer a higher-level semantic utility such as `tabular-nums` when one exists. Reach for `font-features-*` only when the typeface-specific feature is otherwise unavailable.

## Scrollbar Width, Color, and Gutters

Scrollbar width utilities are:

- `scrollbar-auto`
- `scrollbar-thin`
- `scrollbar-none`

Combine them with `scrollbar-thumb-*` and `scrollbar-track-*` color utilities. Both color families support opacity modifiers.

```html
<div class="scrollbar-thin scrollbar-thumb-sky-700/60 scrollbar-track-sky-100 overflow-auto"></div>
```

Control reserved scrollbar space separately:

| Utility | Reserved space |
|---|---|
| `scrollbar-gutter-auto` | Browser default |
| `scrollbar-gutter-stable` | Keep a stable gutter when appropriate |
| `scrollbar-gutter-both` | Reserve gutters on both edges |

Stable gutters can prevent layout shifts when content begins or stops overflowing.

## Size Containers

`@container` creates an inline-size container. Use `@container-size` when queries or units must also observe the block axis.

```html
<div class="@container-size/sidebar">
  <div class="h-[50cqb]"></div>
</div>
```

Size containers expose block-axis container units such as `cqb` and `cqh`. Name one with `@container-size/{name}`, as in `@container-size/sidebar`.
