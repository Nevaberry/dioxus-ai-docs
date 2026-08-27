---
name: shadcn-ui-knowledge-patch
description: shadcn/ui
version: "4.16.0"
license: MIT
metadata:
  author: Nevaberry
---


# shadcn/ui Knowledge Patch

Use this skill when creating, upgrading, configuring, or extending a shadcn/ui
project, or when consuming its CLI and registry APIs. Inspect the project's
`components.json`, `package.json`, framework manifest, global CSS, and installed
component sources before proposing changes. shadcn/ui copies source into the
project, so local code and configuration remain authoritative.

## Reference index

| Reference | Topics |
| --- | --- |
| [Project setup and styling](references/project-setup-and-styling.md) | Tailwind v4, React 19, project creation, presets, themes, fonts, and shared CSS |
| [Components and primitive bases](references/components-and-bases.md) | Component defaults, Radix, Base UI, React Aria, Toast, Typeset, and chat helpers |
| [CLI workflows and migrations](references/cli-and-migrations.md) | Inspection, preflight, discovery, MCP, validation, and migrations |
| [Registries and programmatic APIs](references/registries-and-programmatic-apis.md) | Registry configuration, composition, authentication, dependencies, schemas, caching, and installation APIs |

## Breaking changes and deprecations

### Preserve the installed stack unless upgrading deliberately

Initialization supports Tailwind v4 and React 19, but adding components does not
silently move an existing Tailwind v3 or React 18 project to that stack. Before a
Tailwind v4 upgrade, check its browser requirements and run the upgrade codemod:

```sh
npx @tailwindcss/upgrade@next
```

Review the resulting CSS and component diffs before continuing.

### Use the current component and animation defaults

- Prefer `sonner`; `toast` is deprecated for the Radix-oriented component set.
- Prefer the `new-york` style; `default` is deprecated.
- Do not add `cursor-pointer` merely to restore the old button default.
- Replace `tailwindcss-animate` and its `@plugin` directive with the
  `tw-animate-css` development dependency and a global CSS import.

```css
@import "tw-animate-css";
```

Base UI projects also have a distinct, current `toast` implementation. Identify
the project's primitive base before treating that component name as deprecated.

### Write Tailwind v4 theme variables in their current form

Keep `:root` and `.dark` outside `@layer base`. Store the complete color value in
each variable, then map it through `@theme inline` without wrapping it in another
color function. The same rule applies to chart configuration.

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

### Use React 19 component wrappers

Prefer functions typed with `React.ComponentProps<typeof Primitive>` over
`React.forwardRef`. Pass `ref` with the other props, add a stable `data-slot` to
each primitive, and remove obsolete wrapper `displayName` assignments.

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

### Update direct API consumers

Replace `fetchRegistry` with `getRegistry` and `resolveRegistryTree` with
`resolveRegistryItems`. Import registry schemas from the stable `shadcn/schema`
subpath. Do not import CLI command internals as library APIs.

## High-value workflows

### Detect and pin the primitive base

New projects default to Base UI. Automated setups that require Radix must make
that choice explicit:

```sh
pnpm dlx shadcn init -b radix
```

The CLI detects Base UI, Radix, or React Aria and transforms both built-in and
remote-registry components for that base. Keep imports through the local
component abstraction, such as `@/components/ui/dialog`, rather than importing a
primitive solely to compensate for a guessed base.

### Inspect before writing

Use the project-aware commands before changing generated source or config:

```sh
pnpm dlx shadcn@latest info --json
pnpm dlx shadcn@latest docs combobox --base radix --json
pnpm dlx shadcn@latest add button --dry-run
pnpm dlx shadcn@latest add button --diff
pnpm dlx shadcn@latest add button --view
```

`--diff` is especially useful for reconciling an installed component with its
registry version while preserving local customization.

### Create or initialize explicitly

`init` scaffolds supported projects and `create` aliases it. Use `--name` for a
new project, `--monorepo` for a workspace, and `--base` to choose primitives.
Interactive `shadcn create` can select the component library, icon set, base
color, theme, fonts, and structural style.

```sh
pnpm dlx shadcn@latest init --name dashboard --template astro --base radix
pnpm dlx shadcn@latest init --template next --monorepo
```

### Treat presets as whole-system configuration

A preset code represents colors, theme, icons, fonts, and radius. `init
--preset` can scaffold or reconfigure a project; `apply` can restrict an update
to the theme or font. Decode an incoming code and resolve the current project
before applying changes blindly.

```sh
pnpm dlx shadcn@latest preset decode a2r6bw --json
pnpm dlx shadcn@latest preset resolve --json
pnpm dlx shadcn@latest apply a2r6bw --only theme
```

### Configure namespaced registries deliberately

Define each `@namespace` with a URL containing `{name}`. Object entries may also
carry headers and parameters with environment expansion. Registry dependencies
are resolved before their dependents; configuration is deep-merged and the last
resolved duplicate target path wins.

```json
{
  "registries": {
    "@acme": "https://acme.example/r/{name}.json"
  }
}
```

Use `view`, `search`, and `list` for discovery, and use `registry validate` on a
source registry before publishing or consuming it.

### Use stable programmatic entry points

Load project registry configuration with `getRegistriesConfig(cwd)`, then pass
that resolved config into lookup or installation calls. Disable the default
process-lifetime URL cache for watchers and long-running servers that require
fresh data.

```ts
const config = await getRegistriesConfig(process.cwd())
const items = await getRegistryItems(["@acme/button"], {
  config,
  useCache: false,
})
```

`addRegistryItems` is non-interactive, throws instead of exiting, and skips
existing files unless `overwrite` is set. Catch typed `RegistryError`
subclasses or inspect `RegistryErrorCode` at application boundaries.

## Safety checks

- Commit local component and CSS changes before overwriting or migrating them.
- Use `--dry-run`, `--diff`, or `--view` before an `add` that may replace files.
- Treat `eject` as irreversible: it inlines shared Tailwind CSS, removes the
  `shadcn` dependency, and stops automatic stylesheet updates.
- When migrating icons with a path or glob, remember that scoped rewrites do not
  update `components.json`; review unmatched icons reported by the command.
- Pin GitHub registry dependencies with their own tag or full commit SHA.
- Use `overwrite` only after confirming that local copied source is disposable.
