# Utilities and Variants

## Gradient Changes (v4.0)

`bg-gradient-*` renamed to **`bg-linear-*`**. New gradient types added:

```html
<!-- Linear with angle -->
<div class="bg-linear-45 from-indigo-500 to-pink-500">
  <!-- Interpolation modifier (srgb, oklch, hsl) -->
  <div class="bg-linear-to-r/oklch from-indigo-500 to-teal-400">
    <!-- Conic gradient -->
    <div class="bg-conic/[in_hsl_longer_hue] from-red-600 to-red-600">
      <!-- Radial gradient with position -->
      <div class="bg-radial-[at_25%_25%] from-white to-zinc-900"></div>
    </div>
  </div>
</div>
```

## Container Queries (v4.0)

Built-in — no longer needs `@tailwindcss/container-queries` plugin:

```html
<div class="@container">
  <div class="grid-cols-1 @sm:grid-cols-3 @max-md:grid-cols-1"></div>
</div>
```

Range queries combine min and max: `@min-md:@max-xl:hidden`

Custom container breakpoints via `--container-*` in `@theme`.

## Text Shadow (v4.1)

Sizes: `text-shadow-2xs`, `text-shadow-xs`, `text-shadow-sm`, `text-shadow-md`, `text-shadow-lg`

Color: `text-shadow-<color>` (e.g., `text-shadow-sky-300`)

Opacity shorthand on size utility: `text-shadow-lg/50`

```html
<p class="text-shadow-sm">Subtle shadow</p>
<button class="text-sky-950 text-shadow-2xs text-shadow-sky-300">
  Embossed
</button>
<p class="text-shadow-lg/20">20% opacity shadow</p>
```

## Mask Utilities (v4.1)

Composable mask system with directional linear and radial masks.

### Linear Masks

Direction + from/to values: `mask-{t,r,b,l}-from-<value>` and `mask-{t,r,b,l}-to-<value>`
```html
<!-- Fade from bottom starting at 50% -->
<div class="mask-b-from-50% bg-[url(/img/photo.jpg)]"></div>
<!-- Controlled fade range -->
<div class="mask-l-from-50% mask-l-to-90% bg-[url(/img/photo.jpg)]"></div>
```

### Radial Masks

`mask-radial-from-<value>`, `mask-radial-to-<value>`, `mask-radial-at-<position>`

### Composing Masks

Multiple masks combine together:

```html
<!-- Bottom fade + radial fade -->
<div
  class="mask-b-from-50% mask-radial-from-80% bg-[url(/img/photo.jpg)]"
></div>
```

## Overflow-Wrap (v4.1)

`wrap-break-word` — breaks long words to prevent overflow.

`wrap-anywhere` — same but allows mid-word breaks for intrinsic sizing. Better in flex containers, replaces the `min-w-0` hack.

## Colored Drop Shadows (v4.1)

`drop-shadow-<color>` with optional opacity modifier:

```html
<div class="drop-shadow-lg drop-shadow-cyan-500/50">
```

## New Alignment Utilities (v4.1)

`items-baseline-last` / `self-baseline-last` — align to last line of text baseline.

`justify-center-safe` (and other `-safe` variants) — falls back to `start` alignment when container overflows, preventing content from being clipped.

## New Variants (v4.1)

| Variant | Target |
|---------|--------|
| `pointer-fine` / `pointer-coarse` | Primary input device precision |
| `any-pointer-fine` / `any-pointer-coarse` | Any connected input device |
| `details-content` | Content container of `<details>` element |
| `inverted-colors` | OS inverted colors mode |
| `noscript` | JavaScript disabled |
| `user-valid` / `user-invalid` | Form validation after user interaction (not on page load) |
