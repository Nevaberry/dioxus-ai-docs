# CLI Workflows and Migrations

## Registry discovery

Use `view` to inspect an item before installation, `search` to query registry
items, and `list` to enumerate a registry.

```sh
pnpm dlx shadcn view @acme/auth-system
pnpm dlx shadcn search @tweakcn -q "dark"
pnpm dlx shadcn list @acme
```

## Project MCP server

Initialize the project MCP server with one command. It uses all registries in
the project's configuration, including multiple registries in one project.

```sh
pnpm dlx shadcn@latest mcp init
```

## Preflight component changes

The `add` command supports `--dry-run`, `--diff`, and `--view` to expose changes
before files are written. `--diff` compares an installed primitive with the
registry update and is the preferred starting point when local customization
must be merged.

```sh
pnpm dlx shadcn@latest add button --dry-run
pnpm dlx shadcn@latest add button --diff
pnpm dlx shadcn@latest add button --view
```

## Project-aware context

`info` reports the framework and version, CSS-variable setup, installed
components, and component resources. `docs` returns documentation, examples,
and primitive API references for a component and accepts an explicit base. Both
commands can emit JSON.

```sh
pnpm dlx shadcn@latest info --json
pnpm dlx shadcn@latest docs combobox --base radix --json
```

## Built-in migrations

### Icon libraries

`migrate icons` rewrites imports and JSX, installs the destination library, and
updates `components.json`. A path or glob scopes the rewrite but does not update
that configuration. Unmatched icons stay in place and are reported.

```sh
pnpm dlx shadcn@latest migrate icons --from lucide --to phosphor --yes
```

### Right-to-left support

`migrate rtl` enables RTL, changes physical CSS utilities to logical forms, and
adds directional variants where required.

```sh
pnpm dlx shadcn@latest migrate rtl "src/components/ui/**"
```

### Unified Radix package

`migrate radix` changes imports to the unified `radix-ui` package. Remove unused
individual primitive packages after verifying the migration.

```sh
pnpm dlx shadcn@latest migrate radix
```

## Source registry validation

Validate a root source registry, all includes, item schemas, duplicate names,
include rules, and local file paths without building first. The validator
reports all actionable errors in one run.

```sh
pnpm dlx shadcn registry validate
```

## Shared CSS ejection

`eject` irreversibly copies the contents of `shadcn/tailwind.css` into the
project and removes the `shadcn` dependency. Later CLI updates to shared
variants, utilities, and animations will no longer apply automatically.

```sh
pnpm dlx shadcn@latest eject
```
