# Registry Authoring

## Registry-wide Design Systems

A `registry:base` item can install a full design-system payload: components,
dependencies, CSS variables, fonts, and configuration. Use it when a registry
must establish or pin a component base and its associated system settings.

## Font Items

Fonts are independently installable `registry:font` items. Their metadata can
specify the provider, import name, font family, CSS variable, and subsets.

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

## Composable Source Registries

A root `registry.json` may use `include` to compose items from other registry
files. Only the root supplies `name` and `homepage`. `shadcn build` resolves
the includes to a flat registry without `include` and preserves item file paths
relative to the root.

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry.json",
  "name": "acme",
  "homepage": "https://acme.com",
  "include": [
    "components/ui/registry.json",
    "hooks/registry.json"
  ]
}
```

## Validate Registry Source

Validation operates on the source registry; a build is not required first. It
checks the root, included registries, item schemas, duplicate names, include
rules, and local file paths, then reports all actionable errors in one run.

```sh
pnpm dlx shadcn registry validate
```

## Dynamic Registry Loaders

Dynamic routes can load the composed registry or a resolved item from the
`shadcn/registry` public subpath.

```ts
import { loadRegistry, loadRegistryItem } from "shadcn/registry"

const registry = await loadRegistry()
const item = await loadRegistryItem(name)
```

## GitHub Source Registries

Any public GitHub repository with a root `registry.json` can be addressed as
`username/repo/item`. The CLI reads the source registry and resolves includes,
so an author does not need to run `shadcn build`, publish generated item JSON,
or host a registry server. A `registry:item` can carry arbitrary project files,
including documentation, editor settings, agent instructions, workflows,
templates, and codemods.

```sh
pnpm dlx shadcn@latest add acme/toolkit/project-conventions
```
