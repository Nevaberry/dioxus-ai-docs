# Migration and Compatibility

Use this reference when upgrading an existing project or deciding whether a compatibility fallback preserves the intended result.

## Move Configuration Into CSS

The configuration transition is documented in source batch `4.0.0-configuration`.

The primary configuration surface is CSS. Import Tailwind and define framework tokens in `@theme`:

```css
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.62 0.16 252);
}
```

Use `@config` to load an existing JavaScript configuration and `@plugin` to load legacy plugins while migrating. CSS and legacy definitions merge where possible; CSS wins when they cannot be merged.

Three JavaScript configuration options have no legacy bridge:

| Legacy option | Migration |
|---|---|
| `corePlugins` | Remove it; this option is unsupported. |
| `safelist` | Express literal candidates with `@source inline()`. |
| `separator` | Remove it; this option is unsupported. |

Do not move custom properties mechanically from `:root` and expect new utilities. Only appropriately named variables in a top-level `@theme` block generate matching framework APIs.

## Rename Linear Gradient Utilities

The gradient migration comes from source batch `4.0.0`.

Linear gradient utilities use `bg-linear-*` rather than `bg-gradient-*`:

```html
<!-- Before -->
<div class="bg-gradient-to-r from-indigo-500 to-pink-500"></div>

<!-- After -->
<div class="bg-linear-to-r from-indigo-500 to-pink-500"></div>
```

Angles can be supplied directly as utility values:

```html
<div class="bg-linear-45 from-indigo-500 via-purple-500 to-pink-500"></div>
```

## Review Gradient Color Interpolation

Gradients interpolate in OKLAB by default. Add a color-space modifier when a design depends on another interpolation mode:

```html
<div class="bg-linear-to-r/srgb from-indigo-500 to-teal-400"></div>
<div class="bg-linear-to-r/oklch from-indigo-500 to-teal-400"></div>
```

The modifier works with linear, radial, and conic gradient families. In browsers that do not support explicit interpolation, the declaration falls back to the browser's default interpolation behavior, so compare the fallback visually instead of assuming identical colors.

## Understand Older-Browser Fallbacks

Compatibility fallbacks are documented in source batch `4.1.0`.

Fallback output covers:

- `oklab` colors;
- colors with opacity modifiers;
- registered-custom-property behavior used by shadows;
- registered-custom-property behavior used by transforms;
- registered-custom-property behavior used by gradients.

These fallbacks improve rendering in older Safari and Firefox releases. Full-fidelity output still targets modern browser capabilities such as Safari 16.4 and later. Explicit gradient interpolation falls back to the browser default when that syntax is unavailable.

Test the actual utilities a project uses: a valid fallback can be visually different from the modern declaration, especially for interpolation and color mixing.

## Replace Deprecated Logical Positioning

Logical-property migration is represented by source batch `4.3.0` and belongs to the 4.2 utility set.

Replace the deprecated `start-*` and `end-*` positioning utilities:

| Deprecated | Replacement | CSS axis |
|---|---|---|
| `start-*` | `inset-s-*` | Inline start |
| `end-*` | `inset-e-*` | Inline end |

Related logical positioning utilities include `inset-bs-*` and `inset-be-*` for block start and block end. Prefer these logical forms when the layout must follow writing direction.

## Migration Checklist

- Replace `bg-gradient-*` with `bg-linear-*` and inspect interpolation-sensitive designs.
- Move API-producing tokens into top-level `@theme` blocks.
- Replace a legacy safelist with explicit `@source inline()` candidates.
- Remove unsupported `corePlugins` and `separator` settings.
- Replace `start-*` and `end-*` with `inset-s-*` and `inset-e-*`.
- Test opacity colors, transforms, shadows, and gradients in the oldest supported browsers.
- Keep `@config` and `@plugin` only where the legacy bridge is still needed.
