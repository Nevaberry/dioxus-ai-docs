# Utilities

Use this reference when choosing current utility names and composing gradients, masks, shadows, logical layouts, containers, scrollbars, and typography.

## Use bare values outside configured scales

In `4.0.0`, grid counts and spacing-based utilities accept bare values that are not present in a configured scale.

```html
<div class="grid grid-cols-15 w-17 pr-29 opacity-75"></div>
```

Prefer a bare value when it follows the utility's ordinary value grammar. Reserve arbitrary bracket notation for values that cannot be expressed directly.

## Compose gradient backgrounds

### Linear gradients and angles

Use `bg-linear-*`, not the former `bg-gradient-*` family. Directions and direct angles both compose with the usual stops.

```html
<div class="bg-linear-to-r from-indigo-500 via-purple-500 to-pink-500"></div>
<div class="bg-linear-45 from-indigo-500 via-purple-500 to-pink-500"></div>
```

Gradients interpolate in OKLAB by default. Append a color-space modifier to choose another interpolation mode.

```html
<div class="bg-linear-to-r/srgb from-indigo-500 to-teal-400"></div>
<div class="bg-linear-to-r/oklch from-indigo-500 to-teal-400"></div>
```

### Conic and radial gradients

The `bg-conic-*` and `bg-radial-*` families use `from-*`, `via-*`, and `to-*` stops. They accept interpolation modifiers, arbitrary positions, and explicit stop positions (`4.0.0`).

```html
<div class="bg-conic/[in_hsl_longer_hue] from-red-600 to-red-600"></div>
<div class="bg-radial-[at_25%_25%] from-white to-zinc-900 to-75%"></div>
```

## Compose text, box, inset, and drop shadows

The five default text-shadow sizes introduced in `4.1.0` run from `text-shadow-2xs` through `text-shadow-lg`. Combine a size with `text-shadow-<color>`, or add an opacity modifier to the size to affect its default color.

```html
<h1 class="text-shadow-lg text-shadow-sky-300">Title</h1>
<h2 class="text-shadow-lg/30">Subtitle</h2>
```

Drop-shadow size and color are separate utilities. Color utilities accept opacity modifiers.

```html
<svg class="drop-shadow-xl drop-shadow-cyan-500/50">...</svg>
```

Since `4.3.3`, named box, text, drop, and inset shadow sizes accept fractional opacity modifiers:

```html
<div class="shadow-sm/12.5 text-shadow-sm/12.5 drop-shadow-sm/12.5 inset-shadow-sm/12.5"></div>
```

## Build composable image masks

The `4.1.0` `mask-*` API builds linear, radial, and conic gradient masks. Directional utilities describe the masked side with stops such as `mask-b-from-*` and `mask-l-to-*`; different mask components can be combined on one element.

```html
<img class="mask-b-from-50% mask-radial-[50%_90%] mask-radial-from-80%" src="photo.jpg" />
```

## Wrap overflow-prone text

Use `wrap-break-word` for long words and URLs. Use `wrap-anywhere` when mid-word breaks must participate in intrinsic-size calculation; this can prevent flex overflow without adding `min-w-0` to the child (`4.1.0`).

```html
<div class="flex">
  <p class="wrap-anywhere">very-long-content@example.com</p>
</div>
```

## Align by the last baseline or safely center

`items-baseline-last` aligns flex or grid children to their last text baseline. `self-baseline-last` applies last-baseline alignment to one child.

```html
<div class="grid grid-cols-[1fr_auto] items-baseline-last">...</div>
```

Safe alignment utilities from `4.1.0` fall back to start alignment when centered content would overflow in both directions. Append `-safe` to the relevant alignment value across flex and grid properties.

```html
<ul class="flex justify-center-safe overflow-x-auto">...</ul>
```

## Use logical-property families

The `4.3.0` batch describes version 4.2 writing-mode-aware families:

| Purpose | Families |
|---|---|
| Block spacing | `pbs-*`, `pbe-*`, `mbs-*`, `mbe-*` |
| Scroll spacing | `scroll-pbs-*`, `scroll-pbe-*`, `scroll-mbs-*`, `scroll-mbe-*` |
| Block borders | `border-bs-*`, `border-be-*` |
| Logical sizing | `inline-*`, `block-*`, and their `min-*` and `max-*` forms |
| Logical positioning | `inset-s-*`, `inset-e-*`, `inset-bs-*`, `inset-be-*` |

```html
<div class="pbs-4 mbe-2 min-inline-0 max-block-screen inset-s-0 inset-be-8"></div>
```

Use `inset-s-*` and `inset-e-*` instead of the deprecated `start-*` and `end-*` families.

## Style scrollbars and reserve gutter space

Choose scrollbar width with `scrollbar-auto`, `scrollbar-thin`, or `scrollbar-none`. Combine it with `scrollbar-thumb-*` and `scrollbar-track-*` colors; both accept the ordinary color forms, including opacity modifiers.

Reserve space with `scrollbar-gutter-auto`, `scrollbar-gutter-stable`, or `scrollbar-gutter-both` to avoid layout shifts (`4.3.0`).

```html
<div class="scrollbar-thin scrollbar-thumb-sky-700/60 scrollbar-track-sky-100 scrollbar-gutter-stable overflow-auto"></div>
```

## Create size containers

`@container` creates an inline-size container. `@container-size` creates a size container and exposes block-axis container units such as `cqb` and `cqh`; name it with `@container-size/{name}` (`4.3.0`).

```html
<div class="@container-size/sidebar">
  <div class="h-[50cqb]"></div>
</div>
```

## Use neutral-adjacent palettes

The `4.3.0` batch adds the version 4.2 `mauve`, `olive`, `mist`, and `taupe` palettes as complete default-theme color scales.

```html
<div class="border border-mist-200 bg-mauve-950 text-mauve-100"></div>
```

These names behave like other default color palettes, including shade suffixes and opacity modifiers.

## Reach for low-level font features last

Use `font-features-*` to set `font-feature-settings` for font-specific stylistic sets or other OpenType behavior without a dedicated utility (`4.3.0`). Prefer a higher-level utility such as `tabular-nums` whenever one expresses the intent.

```html
<div class='font-features-["tnum"]'>100.00</div>
```
