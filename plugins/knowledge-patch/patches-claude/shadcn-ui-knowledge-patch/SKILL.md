---
name: shadcn-ui-knowledge-patch
description: shadcn/ui
version: "4.16.0"
license: MIT
metadata:
  author: Nevaberry
---


# shadcn/ui Knowledge Patch

Use this skill when a task involves shadcn/ui project setup, component bases,
Tailwind v4 migration, presets, registries, or the public programmatic APIs.
Inspect the project before changing it because generated component source is
owned by the application and can contain local customizations.

## Working Method

1. Read `components.json` and `package.json` to identify the framework,
   component base, style, aliases, registries, and installed CLI package.
2. Use `shadcn info --json` when the CLI is available to confirm the detected
   framework, CSS-variable configuration, installed components, and resources.
3. Inspect local component source and commit local changes before an overwrite,
   migration, preset application, or base conversion.
4. Preview registry changes with `add --view`, `--dry-run`, or `--diff`.
5. Make the smallest scoped change, then typecheck and build the application.
6. Treat documented subpath exports as the public programmatic surface; do not
   import CLI command internals.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Upgrade and Styling](references/upgrade-and-styling.md) | Tailwind v4, React 19 wrappers, defaults, animations, dark palette |
| [Projects, CLI, and Presets](references/projects-cli-and-presets.md) | Initialization, presets, inspection, migrations, MCP, eject |
| [Component Bases and Content](references/component-bases-and-content.md) | Base UI, Radix, React Aria, Toast, chat helpers, Typeset |
| [Registry Consumption](references/registry-consumption.md) | Namespaces, authentication, discovery, dependencies, proxies |
| [Registry Authoring](references/registry-authoring.md) | Composition, validation, GitHub sources, schema payloads, dynamic routes |
| [Programmatic APIs](references/programmatic-apis.md) | Stable imports, caching, installation, errors, presets |

## Breaking Changes and Deprecations

### Preserve the Existing Stack Until an Explicit Upgrade

The CLI can initialize Tailwind v4 and React 19 projects, but adding components
to an existing Tailwind v3 or React 18 application does not upgrade it. Check
Tailwind v4 browser compatibility and run the upgrade codemod only as part of
an intentional migration.

```sh
npx @tailwindcss/upgrade@next
```

### Update Tailwind v4 Theme Variables

Keep `:root` and `.dark` outside `@layer base`. Store complete color values in
CSS variables, then map them directly through `@theme inline`; do not wrap a
variable in another color function. New palettes use OKLCH, and chart colors
should reference complete variables such as `var(--chart-1)`.

```css
:root {
  --background: oklch(1 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
}

@theme inline {
  --color-background: var(--background);
}
```

### Use React 19 Component Shapes

Updated components use `React.ComponentProps`-typed functions instead of
`React.forwardRef`. Pass `ref` with the remaining props, add `data-slot` to
each primitive, and remove obsolete `displayName` assignments.

```tsx
function AccordionItem({
  className,
  ...props
}: React.ComponentProps<typeof AccordionPrimitive.Item>) {
  return (
    <AccordionPrimitive.Item
      data-slot="accordion-item"
      className={cn("border-b last:border-b-0", className)}
      {...props}
    />
  )
}
```

### Replace Deprecated Defaults

- Prefer `sonner` over the legacy toast component where that deprecation
  applies. Base UI's newer Toast is a distinct supported component.
- New projects use the `new-york` style; the old `default` style is deprecated.
- Buttons retain the browser's default cursor.
- Replace `tailwindcss-animate` and its `@plugin` directive with the
  `tw-animate-css` development dependency and a global CSS import.

```css
@import "tw-animate-css";
```

### Pin the Component Base in Automation

New projects default to Base UI. CI and non-interactive scripts that require
Radix must select it explicitly. Registry authors that must pin a base should
ship a `registry:base` item.

```sh
pnpm dlx shadcn init -b radix
```

### Treat Ejection as Irreversible

New initialization imports `shadcn/tailwind.css` for shared Tailwind v4
variants, utilities, and animations. `eject` inlines that CSS and removes the
`shadcn` dependency, so later shared-stylesheet updates no longer apply.

## Safe CLI Operations

### Inspect Before Adding

```sh
pnpm dlx shadcn@latest info --json
pnpm dlx shadcn@latest docs combobox --base radix --json
pnpm dlx shadcn@latest add button --view
pnpm dlx shadcn@latest add button --dry-run
pnpm dlx shadcn@latest add button --diff
```

Use `--diff` when an installed primitive has local edits. Use `docs` with an
explicit base when primitive behavior matters.

### Initialize a Project Explicitly

`init` scaffolds Next.js, Vite, TanStack Start, React Router, Astro, or Laravel;
`create` is an alias. Use `--name` for a new project, `--monorepo` for a
workspace, and `--base` for Base UI, Radix, or Aria.

```sh
pnpm dlx shadcn@latest init --name dashboard --template astro --base radix
pnpm dlx shadcn@latest init --template next --monorepo
```

### Apply Presets Deliberately

A preset code packages colors, theme, icons, fonts, and radius. `init --preset`
can scaffold or reconfigure an app; `apply --only theme` and `--only font`
avoid reinstalling UI components. Decode or resolve a preset before applying
it when reviewing an unfamiliar code.

```sh
pnpm dlx shadcn@latest preset decode a2r6bw --json
pnpm dlx shadcn@latest preset resolve --json
pnpm dlx shadcn@latest apply a2r6bw --only theme
```

## Registry Decision Guide

### Consume a Namespaced Registry

Define a `{name}` URL template under `registries`, then use `@namespace/item`.
Object entries can supply headers and parameters with environment expansion.

```json
{
  "registries": {
    "@private": {
      "url": "https://registry.company.com/{name}.json",
      "headers": {
        "Authorization": "Bearer ${REGISTRY_TOKEN}"
      }
    }
  }
}
```

Use `view`, `search`, and `list` to inspect remote items. Registry dependencies
can cross namespaces; dependency payloads are installed before the dependent
item, which can intentionally override selected files and merged settings.

### Author and Validate from Source

A root `registry.json` may compose other registries with `include`. Validate
the source directly so schema, duplicate-name, include, and local-path errors
are reported together.

```sh
pnpm dlx shadcn registry validate
```

Public GitHub repositories with a root registry can be consumed as
`username/repo/item`; a generated registry build or hosted registry server is
not required.

### Use Public APIs for Automation

Migrate direct consumers from `fetchRegistry` to `getRegistry` and from
`resolveRegistryTree` to `resolveRegistryItems`. Import schemas from
`shadcn/schema`, registry loaders from `shadcn/registry`, and preset helpers
from `shadcn/preset`. Programmatic installers throw typed errors instead of
exiting, so handle `RegistryError` subclasses at the integration boundary.

## Base and Component Selection

- Base UI and Radix retain the shadcn/ui component abstraction and local import
  paths, while their underlying primitives differ.
- React Aria has its own isolated registry and supports Vega, Nova, Maia, Lyra,
  Mira, Luma, Rhea, and Sera without modifying installed Base UI or Radix code.
- Progressive Radix-to-Base-UI migration can keep both bases temporarily;
  typecheck and build each component conversion and review behavioral changes.
- Base UI Toast supports actions, status types, promises, stacking, and swipe
  dismissal.
- `shadcn/typeset` provides theme-aware, streaming-safe prose styling through
  a `typeset` class and context-specific CSS variables.

Consult the topic references before implementing any of these paths; they
contain the exact commands, configuration constraints, and API caveats.
