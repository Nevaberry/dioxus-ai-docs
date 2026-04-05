---
name: tailwind-knowledge-patch
description: "Tailwind CSS v4.x changes since training cutoff (latest: 4.1) — CSS-first @theme configuration, new directives (@utility, @custom-variant, @variant, @reference, @source), gradient/mask/text-shadow utilities, container queries built-in. Load before working with Tailwind CSS v4."
license: MIT
metadata:
  author: Nevaberry
  version: "4.1"
---

Claude's baseline knowledge covers Tailwind CSS through v3.x. This patch covers v4.0 and v4.1.

## Quick Reference

### CSS-First Configuration

v4 replaces `tailwind.config.js` with `@theme {}` in CSS. Theme variables use namespaced CSS custom properties:

| Namespace | Creates | Example |
|-----------|---------|---------|
| `--color-*` | Color utilities | `bg-red-500`, `text-sky-300` |
| `--font-*` | Font family | `font-sans` |
| `--text-*` | Font **size** (not color) | `text-xl` |
| `--font-weight-*` | Font weight | `font-bold` |
| `--tracking-*` | Letter spacing | `tracking-tight` |
| `--leading-*` | Line height | `leading-snug` |
| `--breakpoint-*` | Responsive variants | `sm:`, `md:` |
| `--container-*` | Container query variants | `@sm:`, `@md:` |
| `--spacing-*` | Spacing/sizing | `px-4`, `w-16`, `max-h-*` |
| `--radius-*` | Border radius | `rounded-sm` |
| `--shadow-*` / `--inset-shadow-*` | Box/inset shadow | `shadow-lg` |
| `--ease-*` | Transition timing | `ease-in-out` |
| `--animate-*` | Animations | `animate-spin` |
| `--blur-*` / `--drop-shadow-*` / `--perspective-*` / `--aspect-*` | Filters, etc. | `blur-md` |

```css
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.72 0.11 221);
  --font-display: "Satoshi", sans-serif;
  --breakpoint-3xl: 120rem;
  --ease-snappy: cubic-bezier(0.2, 0, 0, 1);
}
```

See `references/configuration.md` for `@theme inline`, `@theme static`, keyframes in theme, clearing defaults, and build-time functions.

### Directives

| Directive | Purpose | Example |
|-----------|---------|---------|
| `@utility` | Custom utility with variant support | `@utility tab-4 { tab-size: 4; }` |
| `@custom-variant` | Custom variant in CSS | `@custom-variant theme-dark (&:where([data-theme="dark"] *));` |
| `@variant` | Apply variant in custom CSS | `@variant dark { background: black; }` |
| `@reference` | Import theme for `@apply` without output | `@reference "../../app.css";` |
| `@source` | Add content paths for scanning | `@source "../node_modules/@my-company/ui-lib";` |
| `@source not` | Exclude paths from scanning | `@source not "./src/legacy";` |
| `@config` | Load legacy JS config (v3 compat) | `@config "../../tailwind.config.js";` |
| `@plugin` | Load legacy JS plugin (v3 compat) | `@plugin "@tailwindcss/typography";` |

See `references/directives.md` for full syntax, `@source inline()` with brace expansion, and v3 compatibility notes.

### New Utilities (v4.0-4.1)

| Utility | What it does |
|---------|-------------|
| `bg-linear-*` | Linear gradients (replaces `bg-gradient-*`) |
| `bg-linear-45` | Gradient with angle |
| `bg-linear-to-r/oklch` | Gradient with interpolation modifier |
| `bg-conic/*`, `bg-radial-[*]` | Conic and radial gradients |
| `@container` + `@sm:` | Built-in container queries (no plugin) |
| `@min-md:@max-xl:` | Container query ranges |
| `text-shadow-{2xs,xs,sm,md,lg}` | Text shadow sizes |
| `text-shadow-<color>` | Text shadow color |
| `text-shadow-lg/50` | Text shadow with opacity |
| `mask-{t,r,b,l}-from-*` | Directional linear masks |
| `mask-radial-from-*` | Radial masks |
| `wrap-break-word` | Break long words to prevent overflow |
| `wrap-anywhere` | Mid-word breaks for intrinsic sizing |
| `drop-shadow-<color>` | Colored drop shadows |
| `items-baseline-last` | Align to last text baseline |
| `justify-center-safe` | Safe alignment (falls back on overflow) |

See `references/utilities.md` for full examples and composable mask patterns.

### New Variants (v4.1)

| Variant | Target |
|---------|--------|
| `pointer-fine` / `pointer-coarse` | Primary input device precision |
| `any-pointer-fine` / `any-pointer-coarse` | Any connected input device |
| `details-content` | Content of `<details>` element |
| `inverted-colors` | OS inverted colors mode |
| `noscript` | JavaScript disabled |
| `user-valid` / `user-invalid` | Form validation after user interaction |

## Critical Examples

### Minimal v4 Setup

```css
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.72 0.11 221);
  --font-display: "Satoshi", sans-serif;
}
```

### Custom Utility + Variant

```css
@utility tab-4 {
  tab-size: 4;
}

@custom-variant theme-midnight (&:where([data-theme="midnight"] *));
/* Usage: theme-midnight:tab-4 */
```

### Custom Animation

```css
@theme {
  --animate-fade-in: fade-in 0.3s ease-out;
  @keyframes fade-in {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
}
```

### Gradients with Interpolation

```html
<!-- Angle-based gradient -->
<div class="bg-linear-45 from-indigo-500 to-pink-500">
  <!-- oklch interpolation for vibrant transitions -->
  <div class="bg-linear-to-r/oklch from-indigo-500 to-teal-400">
    <!-- Radial with position -->
    <div class="bg-radial-[at_25%_25%] from-white to-zinc-900"></div>
  </div>
</div>
```

### Container Queries

```html
<div class="@container">
  <div class="grid-cols-1 @sm:grid-cols-3 @max-md:grid-cols-1"></div>
</div>
```

### Composable Masks

```html
<div class="mask-b-from-50% mask-radial-from-80% bg-[url(/img/photo.jpg)]"></div>
```

### Text Shadow

```html
<button class="text-sky-950 text-shadow-2xs text-shadow-sky-300">Embossed</button>
```

### Vue/Svelte Scoped Styles

```html
<style>
  @reference "../../app.css";
  h1 {
    @apply text-2xl font-bold;
  }
</style>
```

### Build-Time Functions

```css
.element {
  color: --alpha(var(--color-lime-300) / 50%);
  margin: --spacing(4);
}
```

## Reference Files

| File | Contents |
|------|----------|
| `references/configuration.md` | `@theme` options (inline, static), keyframes, clearing defaults, build-time functions |
| `references/directives.md` | `@utility`, `@custom-variant`, `@variant`, `@reference`, `@source`, v3 compat |
| `references/utilities.md` | Gradients, container queries, text shadows, masks, overflow-wrap, drop shadows, alignment |
