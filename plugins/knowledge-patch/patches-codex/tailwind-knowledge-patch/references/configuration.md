# Configuration and Theming

## CSS-first theme variables

The CSS-first configuration APIs here are recorded in the `4.0.0-configuration` batch.

Variables in a top-level `@theme` block do two jobs: they emit CSS custom properties and create matching utilities or variants. An ordinary `:root` custom property remains usable as CSS, but it does not create a Tailwind API.

```css
@import "tailwindcss";

@theme {
  --color-mint-500: oklch(0.72 0.11 178);
  --breakpoint-3xl: 120rem;
}
```

The namespaces and the APIs they control include:

- `--color-*` for color utilities.
- `--font-*`, `--text-*`, `--font-weight-*`, `--tracking-*`, and `--leading-*` for typography.
- `--spacing-*` for spacing and related sizing.
- `--radius-*`, `--shadow-*`, `--inset-shadow-*`, and `--drop-shadow-*` for shape and shadows.
- `--blur-*`, `--perspective-*`, `--aspect-*`, and `--ease-*` for effects and behavior.
- `--animate-*` for animation utilities.
- `--breakpoint-*` for responsive variants.
- `--container-*` for container variants and size utilities.

### Removing defaults

Assign `initial` to a wildcard namespace to remove its default tokens and generated utilities. Use the global wildcard when replacing the entire default theme.

```css
@theme {
  --color-*: initial;
  --color-brand: #3f3cbb;
}

@theme {
  --*: initial;
  --spacing: 0.25rem;
}
```

### Inline and static output

Use `@theme inline` when one token references another variable and the generated utility should contain that referenced value rather than the token name. Normal theme blocks emit used variables; `@theme static` emits every variable in the block.

```css
@theme inline {
  --font-sans: var(--font-inter);
}

@theme static {
  --color-primary: var(--color-red-500);
}
```

### Animation keyframe ownership

Keyframes nested inside `@theme` beside an `--animate-*` token are emitted only when the animation token is used. Put `@keyframes` outside `@theme` if it must always be present in the output.

```css
@theme {
  --animate-fade-in: fade-in 0.3s ease-out;

  @keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
  }
}
```

## Source detection controls

Source controls from `4.1.0` can exclude scanned paths, force literal candidates, or suppress candidates that scanning finds.

```css
@import "tailwindcss";
@source not "./src/components/legacy";
@source inline("{hover:,}bg-red-{50,{100..900..100},950}");
@source not inline("container");
```

- `@source not` prevents selected paths from being scanned.
- `@source inline()` forces literal candidates into generated CSS. Brace expansion supports lists, numeric ranges, and variants.
- `@source not inline()` suppresses a candidate even if a project file contains it.

Keep inline inputs explicit and exclusions narrow so source controls do not hide expected CSS.

## Build-time functions

`--alpha()` changes a color's opacity and compiles to `color-mix()`. `--spacing()` multiplies the theme's base spacing value and can be nested inside arbitrary calculations.

```css
.card {
  color: --alpha(var(--color-lime-300) / 50%);
  margin: --spacing(4);
  width: calc(100% - --spacing(2));
}
```

As recorded in `4.3.3`, `--spacing(0)` compiles to `0px`, not unitless `0`. This preserves its `<length>` type inside `calc()` expressions.

```css
.panel {
  width: calc(100% - --spacing(0));
}
```

## Legacy JavaScript configuration bridge

Use `@config` to load a v3 JavaScript configuration and `@plugin` to load a package or local legacy plugin.

```css
@config "../../tailwind.config.js";
@plugin "@tailwindcss/typography";
```

CSS settings merge with legacy definitions when possible and otherwise win. The legacy `corePlugins`, `safelist`, and `separator` options are unsupported. Replace safelisting with `@source inline()`.

## Defaults in functional utilities

Functional `@utility` definitions can pass `--default(...)` inside `--value(...)` or `--modifier(...)`. This allows the bare utility and explicitly valued forms to share one definition. This form is recorded in `4.3.0`.

```css
@utility tab-* {
  tab-size: --value(integer, --default(4));
}
```

Here `tab` uses the default value while explicitly valued candidates use their supplied integer.
