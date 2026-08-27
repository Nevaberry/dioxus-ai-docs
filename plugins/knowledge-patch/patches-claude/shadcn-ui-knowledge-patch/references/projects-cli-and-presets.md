# Projects, CLI, and Presets

## Custom Project Creation

`npx shadcn create` interactively creates a setup for Next.js, Vite, TanStack
Start, or v0. It prompts for the component library, icon set, base color,
theme, fonts, and visual style. The supplied styles are Vega (classic), Nova
(reduced spacing), Maia (soft and rounded), Lyra (boxy and sharp), and Mira
(compact and dense). A style selection rewrites component code, including
fonts, spacing, structure, and libraries; it is not merely a color theme.

```sh
npx shadcn create
```

## Full-project Initialization

`init` supports Next.js, Vite, TanStack Start, React Router, Astro, and Laravel,
and `create` is an alias for `init`. Use `--name` to create a project,
`--monorepo` for a workspace, and `--base` to choose Base UI, Radix, or Aria.

```sh
pnpm dlx shadcn@latest init --name dashboard --template astro --base radix
pnpm dlx shadcn@latest init --template next --monorepo
```

## Project-aware Inspection

`info` reports the detected framework and version, CSS-variable setup,
installed components, and component resources. `docs` returns documentation,
examples, and primitive API references for a component; specify a base when
needed. Both commands support JSON output.

```sh
pnpm dlx shadcn@latest info --json
pnpm dlx shadcn@latest docs combobox --base radix --json
```

## Preflight Component Changes

The `add` command can expose a registry change before writing files:

```sh
pnpm dlx shadcn@latest add button --dry-run
pnpm dlx shadcn@latest add button --diff
pnpm dlx shadcn@latest add button --view
```

Use `--diff` to compare an installed primitive with its registry update before
merging local customizations.

## Portable Preset Codes

A preset code packages colors, theme, icon library, fonts, and radius.
`init --preset` can scaffold with the preset or switch an existing application
to it, reconfiguring component source as well.

```sh
pnpm dlx shadcn@latest init --preset a1Dg5eFl
```

## Applying and Inspecting Presets

`apply` changes an existing project and can limit the operation to `theme` or
`font` without reinstalling UI components. `preset decode` inspects a code.
`preset resolve` reconstructs the current project's preset, and `preset info`
is an alias for `preset resolve`. Both inspection operations support JSON.

```sh
pnpm dlx shadcn@latest apply a2r6bw --only theme
pnpm dlx shadcn@latest preset decode a2r6bw --json
pnpm dlx shadcn@latest preset resolve --json
```

## Built-in Migrations

### Icons

`migrate icons` rewrites imports and JSX, installs the target icon library,
and updates `components.json`. Supplying a path or glob scopes the rewrite but
does not update `components.json`. Unmatched icons remain in place and are
reported.

```sh
pnpm dlx shadcn@latest migrate icons --from lucide --to phosphor --yes
```

### Right-to-left Layout

`migrate rtl` enables RTL, replaces physical CSS utilities with logical forms,
and adds directional variants where required. It accepts a path or glob.

```sh
pnpm dlx shadcn@latest migrate rtl "src/components/ui/**"
```

### Unified Radix Package

`migrate radix` switches imports to the unified `radix-ui` package. After the
migration succeeds, unused individual primitive packages can be removed.

```sh
pnpm dlx shadcn@latest migrate radix
```

## Project MCP Server

Initialize the project MCP server with one command. It uses every registry in
the project's configuration and supports several registries at once.

```sh
pnpm dlx shadcn@latest mcp init
```

## CLI Skill

The installable shadcn skill supplies coding agents with Radix and Base UI
APIs, component patterns, registry workflows, and CLI usage aligned with a
project's design system.

```sh
pnpm dlx skills add shadcn/ui
```
