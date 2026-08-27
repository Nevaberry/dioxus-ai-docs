# Migration and Compatibility

## Rename linear gradient utilities

The `4.0.0` linear-gradient family uses `bg-linear-*` instead of `bg-gradient-*`. Update directional classes such as `bg-gradient-to-r` to `bg-linear-to-r`. Angles can be supplied directly as values.

```html
<div class="bg-linear-45 from-indigo-500 via-purple-500 to-pink-500"></div>
```

Unmodified gradients interpolate in OKLAB. Add a color-space modifier such as `/srgb` or `/oklch` only when a particular interpolation space is required.

## Replace deprecated logical positioning names

The logical-property families recorded in `4.3.0` deprecate `start-*` and `end-*` positioning classes. Replace them with `inset-s-*` and `inset-e-*` respectively.

| Deprecated | Replacement | Axis edge |
|---|---|---|
| `start-*` | `inset-s-*` | Inline start |
| `end-*` | `inset-e-*` | Inline end |

Use `inset-bs-*` and `inset-be-*` for block-start and block-end positioning. Review mixed physical and logical positioning carefully under right-to-left and vertical writing modes.

## Remove unsupported legacy options

`@config` can bridge a v3 JavaScript configuration, but the `corePlugins`, `safelist`, and `separator` options are not supported. Move framework tokens and configuration into CSS, and replace safelisting with explicit `@source inline()` candidates.

```css
@source inline("{hover:,focus:,}bg-brand");
```

CSS definitions merge with legacy definitions where possible and otherwise take precedence.

## Older-browser fallbacks

The `4.1.0` behavior adds fallbacks for:

- `oklab` colors.
- Opacity-modified colors.
- Registered-custom-property features used by shadows, transforms, and gradients in older Safari and Firefox.

Explicit gradient interpolation falls back to the browser default when the requested color-space syntax is unsupported. Full-fidelity rendering still targets modern browsers such as Safari 16.4 and later, so test important gradients and effects in older targets.

## Windows CJK font selection

As recorded in `4.3.3`, the default sans stack uses explicit platform fonts instead of `system-ui` and `ui-sans-serif`. This allows CJK text on Windows to follow the page's `lang` attribute. Preserve correct language metadata on the document when relying on platform CJK font selection.
