# Configuration and Theming

Use this reference for CSS-first configuration, design tokens, candidate discovery, and custom functional utilities.

## Theme variables create framework APIs

In `4.0.0-configuration`, variables in a top-level `@theme` block both emit CSS custom properties and create the matching utilities or variants. Ordinary variables declared only in `:root` remain CSS variables and do not create framework APIs.

```css
@import "tailwindcss";

@theme {
  --color-mint-500: oklch(0.72 0.11 178);
  --breakpoint-3xl: 120rem;
}
```

The recognized namespaces include:

- `--color-*`, `--font-*`, `--text-*`, `--font-weight-*`, `--tracking-*`, and `--leading-*`
- `--spacing-*`, `--radius-*`, `--shadow-*`, `--inset-shadow-*`, and `--drop-shadow-*`
- `--blur-*`, `--perspective-*`, `--aspect-*`, `--ease-*`, and `--animate-*`
- `--breakpoint-*` for responsive variants
- `--container-*` for container variants and size utilities

## Remove default theme values

Assign `initial` to a wildcard namespace to remove that namespace's defaults and generated utilities. Use `--*: initial` to discard the entire default theme before defining a replacement.

```css
@theme {
  --color-*: initial;
  --color-brand: #3f3cbb;
}
```

## Inline references or force unconditional output

Use `@theme inline` when a token references another variable and the generated utility should contain the referenced value rather than the token name. Tailwind normally emits only used theme variables; use `@theme static` to emit every variable in the block.

```css
@theme inline { --font-sans: var(--font-inter); }
@theme static { --color-primary: var(--color-red-500); }
```

## Control animation keyframe ownership

Keyframes nested in `@theme` beside an `--animate-*` token are emitted only when that token is used. Put `@keyframes` outside `@theme` when it must always be present.

```css
@theme {
  --animate-fade-in: fade-in 0.3s ease-out;

  @keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
  }
}
```

## Use build-time color and spacing functions

`--alpha()` changes a color's opacity and compiles to `color-mix()`. `--spacing()` multiplies the base spacing value and can appear in arbitrary-value calculations.

```css
.card {
  color: --alpha(var(--color-lime-300) / 50%);
  margin: --spacing(4);
}
```

Since `4.3.3`, `--spacing(0)` compiles to `0px`, not unitless `0`, so it retains the `<length>` type inside `calc()` expressions.

```css
.panel { width: calc(100% - --spacing(0)); }
```

## Bridge legacy configuration selectively

`@config` loads a v3 JavaScript configuration, while `@plugin` loads a package or local legacy plugin. CSS-defined settings merge with legacy definitions where possible and otherwise take precedence.

```css
@config "../../tailwind.config.js";
@plugin "@tailwindcss/typography";
```

The legacy `corePlugins`, `safelist`, and `separator` options are unsupported. Replace safelisting with `@source inline()`.

## Control candidate discovery

Source controls introduced in `4.1.0` can exclude scanned paths, add literal candidates, or suppress specific candidates.

```css
@import "tailwindcss";
@source not "./src/components/legacy";
@source inline("{hover:,}bg-red-{50,{100..900..100},950}");
@source not inline("container");
```

- `@source not` prevents selected paths from being scanned.
- `@source inline()` supports brace expansion for candidate lists, numeric ranges, and variants.
- `@source not inline()` suppresses a candidate even when source scanning detects it.

Keep forced candidates literal and exclusions narrow so the generated stylesheet remains predictable.

## Give functional utilities a bare default

In the `4.3.0` batch, functional `@utility` definitions can pass `--default(...)` inside `--value(...)` or `--modifier(...)`. This lets the bare utility and explicitly valued forms share one definition.

```css
@utility tab-* {
  tab-size: --value(integer, --default(4));
}
```
