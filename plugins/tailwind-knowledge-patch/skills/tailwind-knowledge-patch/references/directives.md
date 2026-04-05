# Directives

## `@utility`

Register custom utilities that work with all Tailwind variants (hover, dark, responsive, etc.):

```css
@utility tab-4 {
  tab-size: 4;
}
/* Usage: hover:tab-4, sm:tab-4, dark:tab-4 */
```

## `@custom-variant`

Define custom variants in CSS:

```css
@custom-variant theme-midnight (&:where([data-theme="midnight"] *));
/* Usage: theme-midnight:bg-black theme-midnight:text-white */
```

## `@variant`

Apply a Tailwind variant within custom CSS (useful in component styles):

```css
.my-element {
  background: white;
  @variant dark {
    background: black;
  }
}
```

## `@reference`

Import theme/utilities for `@apply` in Vue/Svelte `<style>` blocks without duplicating CSS output:

```html
<style>
  @reference "../../app.css";
  h1 {
    @apply text-2xl font-bold;
  }
</style>
```

Without `@reference`, using `@apply` in scoped styles would fail because the utilities aren't defined in that scope.

## `@source`

Add content paths that are excluded by auto-detection:

```css
@source "../node_modules/@my-company/ui-lib";
```

### `@source not`

Exclude paths from scanning:

```css
@source not "./src/legacy";
```

### `@source inline()`

Safelist specific classes. Supports brace expansion for generating combinations:

```css
/* Safelist specific utilities */
@source inline("bg-red-500 text-white");

/* Brace expansion for bulk safelisting */
@source inline("{hover:,}bg-red-{50,{100..900..100},950}");

/* Exclude specific utilities */
@source not inline("container");
```

Note: `safelist` from v3 config is not supported in v4. Use `@source inline()` instead.

## v3 Compatibility

### `@config`

Load a legacy JavaScript config file:

```css
@config "../../tailwind.config.js";
```

### `@plugin`

Load a legacy JavaScript plugin:

```css
@plugin "@tailwindcss/typography";
```

### Not Supported in v4

- `corePlugins` — no equivalent
- `safelist` — use `@source inline()` instead
- `separator` — no equivalent
