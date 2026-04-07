# Configuration

## `@source not` — Exclude Paths (4.1)

Exclude specific paths from Tailwind's automatic class scanning. Useful for preventing legacy or third-party code from polluting the generated CSS:

```css
@source not "./src/components/legacy";
@source not "./node_modules/some-lib";
```

## `@source inline()` — Safelist Replacement (4.1)

`@source inline()` replaces the v3 `safelist` configuration. It force-generates specific utility classes using brace expansion syntax.

### Brace Expansion Syntax

Supports shell-like brace expansion for generating multiple class patterns:

```css
/* Generate bg-red-50, bg-red-100, ..., bg-red-900, bg-red-950 */
/* Also generates hover: variants of each */
@source inline("{hover:,}bg-red-{50,{100..900..100},950}");
```

### Preventing Class Generation

Combine with `not` to prevent specific classes from being generated:

```css
@source not inline("container");
```

### Common Patterns

```css
/* Dynamic color classes from CMS/database */
@source inline("bg-{red,blue,green}-{100,500,900}");

/* All text sizes with responsive variants */
@source inline("{sm:,md:,lg:,}text-{xs,sm,base,lg,xl,2xl}");

/* Status badge colors */
@source inline("bg-{green,yellow,red}-{100,500} text-{green,yellow,red}-{700,900}");
```
