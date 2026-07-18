---
name: tailwind-knowledge-patch
description: Tailwind CSS
license: MIT
version: 4.2.2
metadata:
  author: Nevaberry
---

# Tailwind CSS Knowledge Patch

Use this patch when configuring, migrating, or extending a Tailwind CSS project. Start with the migration notes, then open the topic reference that matches the work.

## Reference Index

| Reference | Topics |
|---|---|
| [Configuration and Theming](references/configuration.md) | `@theme`, token namespaces, source detection, legacy configuration, custom utilities |
| [Integrations and Ecosystem](references/integrations.md) | `@reference`, package aliases, Vite, webpack, Tailwind Plus, Prettier |
| [Migration and Compatibility](references/migration.md) | Renames, removed configuration options, browser fallbacks, logical-property migration |
| [Utilities](references/utilities.md) | Gradients, masks, shadows, wrapping, alignment, logical properties, scrollbars, containers |
| [Variants and States](references/variants.md) | Data and ancestor states, negation, pointers, validation, details, popovers, CSS variant composition |

## Migration Hazards First

### Use the CSS-first entry point

```css
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.68 0.14 250);
  --breakpoint-3xl: 120rem;
}
```

- Define framework tokens in a top-level `@theme`; a `:root` custom property alone does not create a utility or variant.
- Use `@config` and `@plugin` only as bridges for legacy JavaScript configuration and plugins.
- Do not carry forward `corePlugins`, `safelist`, or `separator`; they are unsupported. Replace safelisting with `@source inline()`.

### Update renamed and deprecated classes

| Old form | Current form | Note |
|---|---|---|
| `bg-gradient-to-r` | `bg-linear-to-r` | Linear gradients use the `bg-linear-*` family. |
| `start-*` | `inset-s-*` | Logical inline-start positioning. |
| `end-*` | `inset-e-*` | Logical inline-end positioning. |

Explicit gradient color-space modifiers such as `/srgb` and `/oklch` are optional; unmodified gradients interpolate in OKLAB.

### Keep compatibility behavior in mind

Fallbacks cover `oklab`, opacity-modified colors, and registered-custom-property implementations used by shadows, transforms, and gradients. Explicit gradient interpolation degrades to the browser default when unsupported; test visual fidelity when older browsers matter.

## Theme and Configuration Quick Reference

### Theme block modes

| Form | Behavior |
|---|---|
| `@theme { ... }` | Defines tokens and emits used variables. |
| `@theme inline { ... }` | Inlines referenced values into generated utilities. |
| `@theme static { ... }` | Emits every variable in the block, even when unused. |
| `--color-*: initial` | Removes one default namespace and its generated utilities. |
| `--*: initial` | Removes the entire default theme before replacement. |

Theme namespaces drive APIs for colors, fonts, text sizes, font weights, tracking, leading, spacing, radii, shadows, inset shadows, drop shadows, blur, perspective, aspect ratios, easing, and animation. Breakpoint tokens create responsive variants; container tokens create container variants and size utilities.

### Animation ownership

Place a keyframe inside `@theme` beside its `--animate-*` token when it should be emitted only if that animation is used. Put `@keyframes` outside `@theme` when it must always exist.

```css
@theme {
  --animate-fade-in: fade-in 300ms ease-out;

  @keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
  }
}
```

### Source detection controls

```css
@source not "./src/components/legacy";
@source inline("{hover:,}bg-red-{50,{100..900..100},950}");
@source not inline("container");
```

- `@source not` excludes paths from candidate scanning.
- `@source inline()` generates literal candidates and supports brace-expanded lists, ranges, and variants.
- `@source not inline()` suppresses a candidate even if project scanning finds it.

### Build-time functions

```css
.card {
  color: --alpha(var(--color-lime-300) / 50%);
  margin: --spacing(4);
}
```

`--alpha()` compiles opacity changes to `color-mix()`. `--spacing()` multiplies the base spacing token and works inside arbitrary calculations.

## Common Utility Changes

### Values and gradients

Grid counts and spacing-based utilities accept bare values outside a configured scale:

```html
<div class="grid grid-cols-15 w-17 pr-29"></div>
```

Linear, radial, and conic gradients share `from-*`, `via-*`, and `to-*` stops:

```html
<div class="bg-linear-to-r/oklch from-indigo-500 to-pink-500"></div>
<div class="bg-conic/[in_hsl_longer_hue] from-red-600 to-red-600"></div>
<div class="bg-radial-[at_25%_25%] from-white to-zinc-900 to-75%"></div>
```

### Shadows and masks

```html
<h1 class="text-shadow-lg text-shadow-sky-300">Title</h1>
<h2 class="text-shadow-lg/30">Subtitle</h2>
<svg class="drop-shadow-xl drop-shadow-cyan-500/50">...</svg>
<img class="mask-b-from-50% mask-radial-[50%_90%] mask-radial-from-80%" src="photo.jpg" />
```

- Text shadows range from `text-shadow-2xs` through `text-shadow-lg`; size and color compose.
- Drop-shadow size and color are separate; color accepts an opacity modifier.
- Linear, radial, and conic mask utilities compose on one element.

### Wrapping and alignment

| Utility | Use |
|---|---|
| `wrap-break-word` | Break long words and URLs when necessary. |
| `wrap-anywhere` | Include mid-word breaks in intrinsic sizing; useful in flex layouts without `min-w-0`. |
| `items-baseline-last` | Align flex or grid children by their last text baseline. |
| `self-baseline-last` | Apply last-baseline alignment to one item. |
| `justify-center-safe` | Fall back to start alignment when centering would overflow. |

Safe alignment is available across flex and grid alignment properties by appending `-safe` to the alignment value.

### Logical properties and scrollbars

Prefer logical families for writing-mode-aware layouts:

- Spacing and borders: `pbs-*`, `pbe-*`, `mbs-*`, `mbe-*`, `scroll-pbs-*`, `scroll-pbe-*`, `scroll-mbs-*`, `scroll-mbe-*`, `border-bs-*`, and `border-be-*`.
- Sizing: `inline-*`, `block-*`, `min-inline-*`, `max-inline-*`, `min-block-*`, and `max-block-*`.
- Positioning: `inset-s-*`, `inset-e-*`, `inset-bs-*`, and `inset-be-*`.

Scrollbar utilities separate width, colors, and reserved gutter space:

```html
<div class="scrollbar-thin scrollbar-thumb-sky-700/60 scrollbar-track-sky-100 scrollbar-gutter-stable overflow-auto"></div>
```

## Variant Quick Reference

| Variant | Meaning |
|---|---|
| `data-current:` | Match a present boolean data attribute without bracket syntax. |
| `not-hover:` | Negate a state; `not-*` also works with media and support conditions. |
| `in-focus:` | React to a matching ancestor without requiring a `group` class. |
| `open:` | Match open disclosures and the `:popover-open` state. |
| `pointer-fine:` / `pointer-coarse:` | Test the primary pointing device. |
| `any-pointer-fine:` / `any-pointer-coarse:` | Test all available pointing devices. |
| `details-content:` | Target the content container generated by `<details>`. |
| `inverted-colors:` | Match an operating-system inverted-color mode. |
| `noscript:` | Apply CSS while JavaScript is disabled. |
| `user-valid:` / `user-invalid:` | Validate after user interaction instead of on initial render. |

```html
<button class="p-2 pointer-coarse:p-4">Select</button>
<input required class="border user-valid:border-green-500 user-invalid:border-red-500" />
<div class="hidden noscript:block">Please enable JavaScript.</div>
```

In authored CSS, a colon stacks conditions while a comma applies one block to alternatives:

```css
.button {
  @variant hover:focus { background: var(--color-sky-600); }
  @variant active, disabled { opacity: 50%; }
}
```

## Integration Choices

- Use `@reference` in component styles or CSS modules to expose theme values, custom utilities, and variants without duplicating the referenced stylesheet.
- Use `@tailwindcss/vite` with Vite projects, including Vite 8.
- Use `@tailwindcss/webpack` to run Tailwind directly as a webpack loader instead of routing through PostCSS.
- `prettier-plugin-tailwindcss` can sort classes while removing duplicate classes and unnecessary whitespace.
- Tailwind Plus plain-HTML UI blocks include their accessible interactive behavior without a framework requirement.

## Before You Finish

- Confirm tokens that should create utilities live in `@theme`, not only in `:root`.
- Check migrated gradients and logical positioning for renamed classes.
- Keep `@source inline()` inputs explicit and use exclusions narrowly.
- Choose primary-pointer or any-pointer variants based on the actual interaction requirement.
- Use higher-level typography utilities such as `tabular-nums` before reaching for `font-features-*`.
- Open the topic references before changing configuration or writing compatibility-sensitive utilities.
