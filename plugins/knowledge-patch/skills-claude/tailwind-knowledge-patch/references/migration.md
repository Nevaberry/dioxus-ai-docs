# Migration and Compatibility

Use this reference when moving from legacy configuration or class names, or when older browsers and platform-specific rendering matter.

## Start from the CSS-first entry point

Tailwind 4 configuration starts by importing the framework and declaring framework tokens in CSS:

```css
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.68 0.14 250);
}
```

Tokens intended to create utilities or variants must live in a top-level `@theme`. A custom property declared only in `:root` does not create a Tailwind API. See [Configuration and Theming](configuration.md) for theme block modes and namespaces.

## Retire unsupported legacy options

The `4.0.0-configuration` bridge supports `@config` for a v3 JavaScript config and `@plugin` for legacy plugins, but these JavaScript configuration options are not supported:

- `corePlugins`
- `safelist`
- `separator`

Replace `safelist` with explicit `@source inline()` candidates. Let CSS-defined settings take precedence when a legacy and CSS definition cannot merge.

## Rename gradient utilities

In `4.0.0`, linear gradients moved from `bg-gradient-*` to `bg-linear-*`.

```html
<!-- Before -->
<div class="bg-gradient-to-r from-indigo-500 to-pink-500"></div>

<!-- Current -->
<div class="bg-linear-to-r from-indigo-500 to-pink-500"></div>
```

An angle may be the direct value, as in `bg-linear-45`. Gradients interpolate in OKLAB by default; append `/srgb`, `/oklch`, or another supported explicit modifier only when the design requires that interpolation behavior.

## Replace deprecated logical positioning names

The logical-property families described in the `4.3.0` batch deprecate `start-*` and `end-*` in favor of:

| Deprecated | Replacement | Logical side |
|---|---|---|
| `start-*` | `inset-s-*` | Inline start |
| `end-*` | `inset-e-*` | Inline end |

Use `inset-bs-*` and `inset-be-*` for block start and block end. Review bidirectional and vertical-writing layouts after replacing physical or deprecated positioning classes.

## Understand older-browser fallbacks

The `4.1.0` fallbacks cover:

- `oklab` colors
- colors with opacity modifiers
- registered-custom-property features used by shadows, transforms, and gradients in older Safari and Firefox

Explicit gradient interpolation still falls back to the browser's default interpolation when the requested mode is unsupported. The full-fidelity target remains modern browsers such as Safari 16.4 and later, so verify appearance in older supported browsers rather than assuming the fallback is visually identical.

## Keep nesting behavior consistent across pipelines

As of `4.3.3`, Tailwind handles CSS nesting when Lightning CSS does not run, including in `@tailwindcss/browser` and Tailwind Play.

```css
.card {
  &:hover { color: red; }
}
```

When comparing development and production output, account for any additional nesting or prefixing transforms that only one pipeline applies.

## Preserve Windows CJK font selection

The default sans stack in `4.3.3` uses explicit platform fonts instead of `system-ui` and `ui-sans-serif`. This allows CJK text on Windows to choose a font according to the page's `lang` attribute.

Keep accurate document or subtree language attributes, and re-check font rendering before overriding the default stack with a system-only shorthand.
