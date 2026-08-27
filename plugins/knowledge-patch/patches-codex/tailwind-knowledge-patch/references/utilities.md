# Utilities

## Bare values outside configured scales

Grid counts and spacing-based utilities accept unconfigured bare values (`4.0.0`). Use the ordinary candidate when a number can be derived instead of writing an arbitrary value.

```html
<div class="grid grid-cols-15 w-17 pr-29 opacity-75"></div>
```

## Gradient utilities

### Linear gradients and angles

Linear gradients use the `bg-linear-*` family. A direction or angle can be part of the utility value.

```html
<div class="bg-linear-45 from-indigo-500 via-purple-500 to-pink-500"></div>
<div class="bg-linear-to-r from-indigo-500 to-teal-400"></div>
```

Gradients interpolate in OKLAB by default. Append a modifier to select another interpolation space.

```html
<div class="bg-linear-to-r/srgb from-indigo-500 to-teal-400"></div>
<div class="bg-linear-to-r/oklch from-indigo-500 to-teal-400"></div>
```

### Conic and radial gradients

`bg-conic-*` and `bg-radial-*` compose with the same `from-*`, `via-*`, and `to-*` stops. They accept interpolation modifiers and arbitrary details such as positions.

```html
<div class="bg-conic/[in_hsl_longer_hue] from-red-600 to-red-600"></div>
<div class="bg-radial-[at_25%_25%] from-white to-zinc-900 to-75%"></div>
```

The linear, radial, and conic behavior in this section is recorded in `4.0.0`.

## Text shadows

The `4.1.0` text-shadow API has five default sizes from `text-shadow-2xs` through `text-shadow-lg`. Combine a size with `text-shadow-<color>`, or place an opacity modifier on the size to change the default shadow color's opacity.

```html
<h1 class="text-shadow-lg text-shadow-sky-300">Title</h1>
<h2 class="text-shadow-lg/30">Subtitle</h2>
```

## Colored drop shadows

Drop-shadow size and color are separate utilities. Color utilities accept opacity modifiers.

```html
<svg class="drop-shadow-xl drop-shadow-cyan-500/50">...</svg>
```

## Fractional opacity on named shadows

Named box, text, drop, and inset shadow sizes accept fractional opacity modifiers as recorded in `4.3.3`.

```html
<div class="shadow-sm/12.5 text-shadow-sm/12.5 drop-shadow-sm/12.5 inset-shadow-sm/12.5"></div>
```

## Composable masks

The `4.1.0` `mask-*` API builds linear, radial, and conic gradient masks. Directional utilities describe the masked side with stops such as `mask-b-from-*` and `mask-l-to-*`. Linear, radial, or conic pieces can compose on the same element.

```html
<img class="mask-b-from-50% mask-radial-[50%_90%] mask-radial-from-80%" src="photo.jpg" />
```

## Wrapping long content

Use `wrap-break-word` to break long words and URLs when necessary. `wrap-anywhere` also permits mid-word breaks during intrinsic-size calculation, which can keep flex content from overflowing without adding `min-w-0` to the child (`4.1.0`).

```html
<div class="flex">
  <p class="wrap-anywhere">very-long-content@example.com</p>
</div>
```

## Baseline and safe alignment

`items-baseline-last` aligns flex or grid children by their last text baseline; `self-baseline-last` applies last-baseline alignment to one item.

```html
<div class="grid grid-cols-[1fr_auto] items-baseline-last">...</div>
```

Safe alignment falls back to start alignment when centering would overflow in both directions. It works across flex and grid alignment properties by appending `-safe` to the alignment value.

```html
<ul class="flex justify-center-safe overflow-x-auto">...</ul>
```

Both alignment additions are recorded in `4.1.0`.

## Neutral palettes

The default theme adds `mauve`, `olive`, `mist`, and `taupe` as complete neutral-adjacent color palettes. These version 4.2 palettes are recorded in the `4.3.0` batch.

```html
<div class="border border-mist-200 bg-mauve-950 text-mauve-100"></div>
```

## Logical property families

The version 4.2 logical utilities recorded in `4.3.0` cover spacing, borders, size, and position:

- Block-start/end padding: `pbs-*` and `pbe-*`.
- Block-start/end margin: `mbs-*` and `mbe-*`.
- Scroll padding: `scroll-pbs-*` and `scroll-pbe-*`.
- Scroll margin: `scroll-mbs-*` and `scroll-mbe-*`.
- Block-start/end borders: `border-bs-*` and `border-be-*`.
- Logical sizing: `inline-*` and `block-*`, plus `min-inline-*`, `max-inline-*`, `min-block-*`, and `max-block-*`.
- Logical positioning: `inset-s-*`, `inset-e-*`, `inset-bs-*`, and `inset-be-*`.

```html
<div class="pbs-4 mbe-2 min-inline-0 max-block-screen inset-s-0 inset-be-8"></div>
```

`start-*` and `end-*` are deprecated; use `inset-s-*` and `inset-e-*`.

## Low-level OpenType features

Use `font-features-*` to set `font-feature-settings` for font-specific stylistic sets and other low-level OpenType features that do not have a dedicated utility (`4.3.0`). Prefer a higher-level utility such as `tabular-nums` when one exists.

```html
<div class='font-features-["tnum"]'>100.00</div>
```

## Scrollbar controls

Scrollbar width, colors, and gutters are separate concerns (`4.3.0`):

- Width: `scrollbar-auto`, `scrollbar-thin`, and `scrollbar-none`.
- Colors: `scrollbar-thumb-*` and `scrollbar-track-*`, including opacity modifiers.
- Reserved space: `scrollbar-gutter-auto`, `scrollbar-gutter-stable`, and `scrollbar-gutter-both`.

```html
<div class="scrollbar-thin scrollbar-thumb-sky-700/60 scrollbar-track-sky-100 scrollbar-gutter-stable overflow-auto"></div>
```

Use a stable gutter when showing or hiding the scrollbar would otherwise shift layout.

## Size containers

`@container-size` creates a size container rather than the inline-size container created by `@container`. It exposes block-axis container units such as `cqb` and `cqh`. Name a size container with `@container-size/{name}` (`4.3.0`).

```html
<div class="@container-size/sidebar">
  <div class="h-[50cqb]"></div>
</div>
```
