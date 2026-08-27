# Project Setup and Styling

## Stack boundary and Tailwind v4 upgrade

The CLI can initialize Tailwind v4 and React 19 projects. Existing Tailwind v3
and React 18 applications, including components subsequently added to them,
remain on that stack until an explicit upgrade. Check Tailwind v4 browser
compatibility before upgrading and run `@tailwindcss/upgrade@next` to perform
the mechanical migration.

## Tailwind v4 variable layout

Place `:root` and `.dark` outside `@layer base`. Variables hold complete color
expressions, and `@theme inline` maps them directly without another color
function. New palettes use OKLCH. Chart configuration likewise uses the complete
variable, for example `color: "var(--chart-1)"`.

```css
:root {
  --background: hsl(0 0% 100%);
}

.dark {
  --background: hsl(0 0% 3.9%);
}

@theme inline {
  --color-background: var(--background);
}
```

## Animation dependency

`tailwindcss-animate` is deprecated. Remove it and its `@plugin` directive,
install `tw-animate-css` as a development dependency, and import the replacement
from global CSS:

```css
@import "tw-animate-css";
```

## Dark-mode palette refresh

The March 2025 palette refresh applies automatically to projects created on
Tailwind v4, not to projects upgraded from v3. To opt an upgraded project in:

1. Commit local component changes.
2. Overwrite the installed components.
3. Replace the dark variables in `globals.css` with the new OKLCH values.
4. Review the diff and reapply intentional customizations.

```sh
pnpm dlx shadcn@latest add --all --overwrite
```

## Interactive project creation

`npx shadcn create` creates a customized Next.js, Vite, TanStack Start, or v0
setup. It prompts for the component library, icons, base color, theme, fonts,
and visual style. The five supplied styles are:

- Vega: classic.
- Nova: reduced spacing.
- Maia: soft and rounded.
- Lyra: boxy and sharp.
- Mira: compact and dense.

Styles rewrite component code, including fonts, spacing, structure, and
libraries; they are not merely color themes.

## Full-project initialization

`init` scaffolds Next.js, Vite, TanStack Start, React Router, Astro, or Laravel;
`create` is an alias. `--name` creates a named project, `--monorepo` creates a
workspace, and `--base` selects Base UI, Radix, or Aria primitives.

```sh
pnpm dlx shadcn@latest init --name dashboard --template astro --base radix
pnpm dlx shadcn@latest init --template next --monorepo
```

## Preset codes

A portable preset packages colors, theme, icon library, fonts, and radius.
`init --preset` scaffolds with it or switches an existing application and
reconfigures that application's components.

```sh
pnpm dlx shadcn@latest init --preset a1Dg5eFl
```

`apply` updates an existing project and can restrict the change to `theme` or
`font` without reinstalling UI components. `preset decode` inspects a code;
`preset resolve` reconstructs the current project's preset; `preset info` is an
alias for `preset resolve`. Both inspection commands support JSON output.

```sh
pnpm dlx shadcn@latest apply a2r6bw --only theme
pnpm dlx shadcn@latest preset decode a2r6bw --json
pnpm dlx shadcn@latest preset resolve --json
```

## Registry-delivered design systems and fonts

A `registry:base` item can install a complete design system containing
components, dependencies, CSS variables, fonts, and configuration. A
`registry:font` item is independently installable and declares its provider,
import, CSS variable, and subsets.

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry-item.json",
  "name": "font-inter",
  "type": "registry:font",
  "font": {
    "family": "'Inter Variable', sans-serif",
    "provider": "google",
    "import": "Inter",
    "variable": "--font-sans",
    "subsets": ["latin"]
  }
}
```

## Shared Tailwind CSS and ejection

New initialization imports `shadcn/tailwind.css` for shared Tailwind v4
variants, utilities, and animations. `shadcn eject` irreversibly inlines that
CSS and removes the `shadcn` dependency. After ejection, later CLI changes to
the shared stylesheet no longer arrive automatically.
