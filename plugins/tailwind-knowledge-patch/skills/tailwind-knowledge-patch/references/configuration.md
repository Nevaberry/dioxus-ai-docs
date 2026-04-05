# Configuration

## `@theme` Block

v4 replaces `tailwind.config.js` with `@theme {}` in CSS. Theme variables use namespaced CSS custom properties that map directly to utilities:

```css
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.72 0.11 221);
  --font-display: "Satoshi", sans-serif;
  --breakpoint-3xl: 120rem;
  --ease-snappy: cubic-bezier(0.2, 0, 0, 1);
}
```

### Namespace Reference

| Namespace | Creates |
|-----------|---------|
| `--color-*` | Color utilities (`bg-red-500`, `text-sky-300`, etc.) |
| `--font-*` | Font family (`font-sans`) |
| `--text-*` | Font **size** (`text-xl`) — not text color |
| `--font-weight-*` | Font weight (`font-bold`) |
| `--tracking-*` | Letter spacing |
| `--leading-*` | Line height |
| `--breakpoint-*` | Responsive variants (`sm:`, `md:`) |
| `--container-*` | Container query variants (`@sm:`) + max-width sizing |
| `--spacing-*` | Spacing/sizing (`px-4`, `w-16`, `max-h-*`) |
| `--radius-*` | Border radius (`rounded-sm`) |
| `--shadow-*` / `--inset-shadow-*` | Box shadow / inset shadow |
| `--ease-*` | Transition timing |
| `--animate-*` | Animations |
| `--blur-*` / `--drop-shadow-*` / `--perspective-*` / `--aspect-*` | Filters, perspective, aspect ratio |

### Clearing Defaults

Clear one namespace: `--color-*: initial`
Clear all defaults: `--*: initial`

## `@theme inline`

Inlines variable values into utilities instead of referencing the theme variable. Required when referencing other CSS variables to avoid scoping issues:

```css
@theme inline {
  --font-sans: var(--font-inter);
}
/* Generates: .font-sans { font-family: var(--font-inter); } */
/* Without inline, would generate: .font-sans { font-family: var(--font-sans); } — circular */
```

## `@theme static`

Generates all CSS variables even if unused. Normally Tailwind only emits variables that are actually referenced by utilities in your HTML:

```css
@theme static {
  --color-brand-light: oklch(0.85 0.08 221);
  --color-brand-dark: oklch(0.55 0.14 221);
}
```

## Keyframes Inside `@theme`

Define `@keyframes` within `@theme` alongside `--animate-*` variables to keep animations co-located:

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

## Build-Time Functions

CSS functions that resolve at build time:

```css
.my-element {
  color: --alpha(var(--color-lime-300) / 50%);    /* → color-mix() */
  margin: --spacing(4);                            /* → calc(var(--spacing) * 4) */
}
```

`--spacing()` also works in arbitrary values: `py-[calc(--spacing(4)-1px)]`
