---
name: tailwind-knowledge-patch
description: "Tailwind CSS changes since training cutoff (latest: 4.1) — text shadows, composable masks, overflow-wrap, safe alignment, @source directives, pointer/noscript variants. Load before working with Tailwind CSS."
version: "4.1"
license: MIT
metadata:
  author: Nevaberry
---

# Tailwind CSS Knowledge Patch

Covers Tailwind CSS 4.1 (2025-04-03). Claude Opus 4.6 knows Tailwind CSS through 3.x. It is **unaware** of the features below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| New utilities | [references/utilities.md](references/utilities.md) | Text shadows, masks, overflow-wrap, colored drop shadows, alignment |
| New variants | [references/variants.md](references/variants.md) | Pointer device, `details-content`, `inverted-colors`, `noscript`, `user-valid`/`user-invalid` |
| Configuration | [references/configuration.md](references/configuration.md) | `@source not`, `@source inline()` |

---

## New Utility Classes (4.1)

### Text Shadow

| Class | Effect |
|---|---|
| `text-shadow-{2xs,xs,sm,md,lg}` | Text shadow at size |
| `text-shadow-<color>` | Shadow color |
| `text-shadow-lg/50` | Size with opacity modifier |

```html
<p class="text-shadow-md text-shadow-blue-500">Shadowed text</p>
<p class="text-shadow-lg/30">30% opacity shadow</p>
```

### Composable Mask Utilities

Direction-based linear masks and radial masks. Multiple masks compose together.

| Pattern | Purpose |
|---|---|
| `mask-{t,r,b,l}-from-<value>` | Linear mask start (direction) |
| `mask-{t,r,b,l}-to-<value>` | Linear mask end (direction) |
| `mask-radial-from-<value>` | Radial mask start |
| `mask-radial-to-<value>` | Radial mask end |
| `mask-radial-at-<position>` | Radial mask position |

```html
<div class="mask-b-from-50% bg-[url(/img/photo.jpg)]"></div>
<div class="mask-r-from-80% mask-b-from-80% mask-radial-from-70%"></div>
```

### Overflow Wrap

| Class | CSS |
|---|---|
| `wrap-break-word` | `overflow-wrap: break-word` |
| `wrap-anywhere` | `overflow-wrap: anywhere` |

Use `wrap-anywhere` inside flex containers instead of `min-w-0` hacks:

```html
<div class="flex">
  <div class="wrap-anywhere">
    <p>long.email@example.com</p>
  </div>
</div>
```

### Colored Drop Shadows

`drop-shadow-<color>` and `drop-shadow-<color>/<opacity>` to color filter drop shadows:

```html
<svg class="drop-shadow-xl drop-shadow-cyan-500/50">...</svg>
```

### Alignment

- `items-baseline-last` / `self-baseline-last` — align to the last line of text baseline in flex/grid
- Safe alignment — append `-safe` to fall back to `start` on overflow: `justify-center-safe`, `items-center-safe`, etc.

```html
<ul class="flex justify-center-safe gap-2">...</ul>
```

## New Variants (4.1)

| Variant | Purpose |
|---|---|
| `pointer-fine` | Primary pointer is fine (mouse) |
| `pointer-coarse` | Primary pointer is coarse (touch) |
| `any-pointer-fine` | Any available pointer is fine |
| `any-pointer-coarse` | Any available pointer is coarse |
| `details-content` | Targets content container of `<details>` |
| `inverted-colors` | Matches OS inverted-colors mode |
| `noscript` | Applies when JS is disabled |
| `user-valid` | Validation styling after user interaction |
| `user-invalid` | Validation styling after user interaction |

```html
<!-- Responsive touch targets -->
<label class="p-2 pointer-coarse:p-4">Option</label>

<!-- Validation after interaction (no error flash on page load) -->
<input
  type="email"
  required
  class="border user-valid:border-green-500 user-invalid:border-red-500"
/>

<!-- Progressive enhancement fallback -->
<div class="hidden noscript:block">Please enable JavaScript.</div>

<!-- Style details content -->
<details class="details-content:p-4 details-content:bg-gray-50">
  <summary>Expand</summary>
  <p>Styled content area.</p>
</details>
```

## Configuration (4.1)

### `@source not` — Exclude paths from class scanning

```css
@source not "./src/components/legacy";
```

### `@source inline()` — Safelist replacement

Force-generate classes with brace expansion:

```css
@source inline("{hover:,}bg-red-{50,{100..900..100},950}");
@source not inline("container"); /* prevent generation */
```

## Reference Files

| File | Contents |
|---|---|
| [utilities.md](references/utilities.md) | Text shadows, masks, overflow-wrap, colored drop shadows, alignment utilities |
| [variants.md](references/variants.md) | Pointer device, details-content, inverted-colors, noscript, user-valid/invalid variants |
| [configuration.md](references/configuration.md) | `@source not`, `@source inline()` directives |
