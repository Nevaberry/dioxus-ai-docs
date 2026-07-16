# Configuration and Theming

Use this reference for CSS-first theme definition, source detection, legacy bridges, and custom utility authoring.

## Theme Variables Create Framework APIs

These theme behaviors are recorded in source batch `4.0.0-configuration`.

A variable in a top-level `@theme` block does two jobs: it emits a CSS custom property and creates the utility or variant associated with its namespace. Defining the same variable only in `:root` makes it available to CSS but does not extend Tailwind's API.

```css
@import "tailwindcss";

@theme {
  --color-mint-500: oklch(0.72 0.11 178);
  --breakpoint-3xl: 120rem;
}
```

The main namespaces are:

| Namespace | Generated API |
|---|---|
| `--color-*` | Color utilities |
| `--font-*` | Font-family utilities |
| `--text-*` | Font-size utilities |
| `--font-weight-*` | Font-weight utilities |
| `--tracking-*` | Letter-spacing utilities |
| `--leading-*` | Line-height utilities |
| `--spacing-*` | Spacing and sizing utilities |
| `--radius-*` | Border-radius utilities |
| `--shadow-*` | Box-shadow utilities |
| `--inset-shadow-*` | Inset-shadow utilities |
| `--drop-shadow-*` | Filter drop-shadow utilities |
| `--blur-*` | Blur utilities |
| `--perspective-*` | Perspective utilities |
| `--aspect-*` | Aspect-ratio utilities |
| `--ease-*` | Transition timing utilities |
| `--animate-*` | Animation utilities |
| `--breakpoint-*` | Responsive variants |
| `--container-*` | Container variants and size utilities |

## Remove or Replace Defaults

Set a wildcard namespace to `initial` to remove its defaults and the utilities those defaults would generate. Set the global wildcard when building a theme entirely from scratch.

```css
@theme {
  --color-*: initial;
  --color-brand: #3f3cbb;
}
```

```css
@theme {
  --*: initial;
  --color-brand: oklch(0.55 0.18 265);
}
```

## Inline and Static Theme Output

Use `inline` when one token refers to another variable. Generated utilities then contain the referenced value instead of referring to the theme token by name.

```css
@theme inline {
  --font-sans: var(--font-inter);
}
```

Tailwind normally emits only theme variables that are used. Use `static` when every variable in a block must be present in the output regardless of utility usage.

```css
@theme static {
  --color-primary: var(--color-red-500);
}
```

## Theme-Owned Animation Keyframes

Keyframes nested in `@theme` alongside an `--animate-*` token are emitted only when the animation token is used.

```css
@theme {
  --animate-fade-in: fade-in 0.3s ease-out;

  @keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
  }
}
```

Move `@keyframes` outside `@theme` when the rule must always be emitted, including when animation is invoked without the corresponding theme utility.

## Build-Time Color and Spacing Functions

`--alpha()` changes a color's opacity and compiles to `color-mix()`. `--spacing()` multiplies the base theme spacing value and can participate in arbitrary-value calculations.

```css
.card {
  color: --alpha(var(--color-lime-300) / 50%);
  margin: --spacing(4);
  padding-inline: calc(--spacing(3) + 1px);
}
```

## Source Detection

The source controls in this section come from source batch `4.1.0`.

### Exclude Paths

`@source not` prevents selected paths from being scanned for class candidates.

```css
@import "tailwindcss";
@source not "./src/components/legacy";
```

### Add Literal Candidates

`@source inline()` forces literal candidates into generated CSS. Its brace expansion supports lists, numeric ranges, steps, and variant prefixes.

```css
@source inline("{hover:,}bg-red-{50,{100..900..100},950}");
```

This generates the base and hover forms for the listed red shades. Prefer explicit ranges over attempting to generate candidates dynamically at runtime.

### Suppress Candidates

`@source not inline()` prevents a candidate from being generated even when it is found in project files.

```css
@source not inline("container");
```

## Legacy Configuration Bridge

`@config` loads a JavaScript configuration file, and `@plugin` loads a package or local legacy plugin.

```css
@config "../../tailwind.config.js";
@plugin "@tailwindcss/typography";
```

CSS-defined settings merge with legacy definitions where possible. When the two forms cannot be merged, the CSS definition wins. The legacy `corePlugins`, `safelist`, and `separator` options are not supported; replace safelisting with `@source inline()`.

## Defaults in Functional Utilities

Functional utility defaults are recorded in source batch `4.3.0`.

Pass `--default(...)` inside `--value(...)` or `--modifier(...)` so the bare utility and explicitly valued forms share one definition.

```css
@utility tab-* {
  tab-size: --value(integer, --default(4));
}
```

Here `tab` uses `4`, while an explicitly valued class can supply another integer through the same functional definition. The same default mechanism is available for modifiers.
