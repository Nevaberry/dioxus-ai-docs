# Registries and Programmatic APIs

## Namespaced registry configuration

CLI 3.0 addresses decentralized registry items as `@registry/name`. Define each
namespace in `components.json` with a URL template containing `{name}`. Registry
items may declare namespaced `registryDependencies` from one or several
registries; the CLI resolves them automatically.

```json
{
  "registries": {
    "@acme": "https://acme.com/r/{name}.json"
  }
}
```

```sh
pnpm dlx shadcn add @acme/button
```

A namespace must start and end with an alphanumeric character. Between those
characters it may contain alphanumerics, hyphens, or underscores. URLs require
`{name}` and may use `{style}` for the current project style. Object-form entries
may add `params`. The URL, headers, and parameters support environment expansion
and shell-style defaults such as `${REGISTRY_VERSION:-v2}`.

```json
{
  "registries": {
    "@themes_v2": {
      "url": "https://registry.example.com/{style}/{name}.json",
      "params": {
        "version": "${REGISTRY_VERSION:-v2}"
      }
    }
  }
}
```

## Authentication and proxies

An object registry entry accepts `url` and `headers`, including environment
interpolation. Basic authentication, bearer tokens, API-key query parameters,
and custom headers are supported. Missing variables are named in the error and
may be supplied through `.env` or `.env.local`.

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

An authenticated registry may return a JSON `message` with a `401` or `403`.
The CLI displays that message, allowing the server to explain a missing token,
expired subscription, or resource-specific restriction.

```ts
return NextResponse.json(
  { error: "Forbidden", message: "This component requires Design team access." },
  { status: 403 }
)
```

The registry HTTP stack accepts SOCKS4 and SOCKS5 proxy URLs through `ALL_PROXY`
or `all_proxy` (batch `4.16.1-4.18.0`). It ignores a non-SOCKS `ALL_PROXY` value.
HTTP and HTTPS proxies continue to use `HTTP_PROXY`, `HTTPS_PROXY`, and
`NO_PROXY`.

```sh
ALL_PROXY=socks5://127.0.0.1:1080 pnpm dlx shadcn@latest add button
```

## Configuration precedence and merging

`getRegistriesConfig(cwd)` reads `components.json`; when that file is absent,
it falls back to top-level `registries` in `package.json`. Registry declarations
from both files are merged. The CLI can add registries to `package.json` when
`components.json` is absent, and `add`, `search`, `view`, and `init` resolve them
there in memory without copying them to `components.json`.

Registry dependencies install before the dependent item. Resolution deep-merges
Tailwind configuration, CSS variables, CSS, and environment variables. For
duplicate target file paths, the last resolved file wins, allowing a custom item
to depend on a third-party item and override only selected files or config.

```json
{
  "name": "custom-button",
  "type": "registry:ui",
  "registryDependencies": ["@vendor/button"],
  "files": [
    {
      "path": "components/ui/button.tsx",
      "type": "registry:ui",
      "content": "export function Button() { return null }"
    }
  ]
}
```

## Composable source registries

A root `registry.json` may use `include` to compose items from other registry
files. Only the root must define `name` and `homepage`. `shadcn build` resolves
the includes into a flattened registry without an `include` property while
preserving item file paths relative to the root.

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

Item names with path segments such as `extension/foo` produce nested output
directories instead of an `ENOENT` failure from 4.16.1 (batch
`4.16.1-4.18.0`).

Dynamic routes can load the composed registry or one resolved item from the
stable `shadcn/registry` entry point:

```ts
import { loadRegistry, loadRegistryItem } from "shadcn/registry"

const registry = await loadRegistry()
const item = await loadRegistryItem(name)
```

## GitHub source registries and local dependencies

A public GitHub repository with a root `registry.json` is addressable as
`<username>/<repo>/<item>`. The CLI reads the source and resolves includes, so
the author does not need to run `shadcn build`, publish generated item JSON, or
host a registry server. A `registry:item` can distribute arbitrary project files
such as documentation, editor settings, agent instructions, workflows,
templates, and codemods.

```sh
pnpm dlx shadcn@latest add acme/toolkit/project-conventions
```

`registryDependencies` also accepts GitHub items and local item JSON files. Pin
each GitHub dependency with its own tag or full commit SHA because refs are not
inherited. Bare names resolve to built-in items, so same-repository dependencies
need their full GitHub address.

```json
{
  "registryDependencies": [
    "acme/ui/button#v1.2.0",
    "./editor.json"
  ]
}
```

## File targets and aliases

Targets beginning with `@components/`, `@ui/`, `@lib/`, or `@hooks/` resolve
against the consumer's `components.json` directories rather than its import
prefix. `@utils/` is unsupported because that alias denotes a file. A target may
route a file somewhere different from its declared type, and `registry:page`
and `registry:file` entries require a target.

```json
{
  "path": "registry/new-york/example/format-date.ts",
  "type": "registry:ui",
  "target": "@lib/format-date.ts"
}
```

## Stable APIs and schema migration

Direct API consumers should replace `fetchRegistry` with `getRegistry` and
`resolveRegistryTree` with `resolveRegistryItems`. Registry schemas are exported
from `shadcn/schema`. Existing `components.json` files and installed components
remain compatible. Only documented subpath imports are stable APIs; CLI command
internals are not public API.

```ts
import { registryItemSchema } from "shadcn/schema"
```

Registry fetching uses a process-lifetime, resolved-URL cache by default and
deduplicates concurrent in-flight requests. Disable caching for fresh reads in
servers or watchers.

```ts
const config = await getRegistriesConfig(process.cwd())
const items = await getRegistryItems(["@acme/button"], {
  config,
  useCache: false,
})
```

## Non-interactive installation and errors

`addRegistryItems` installs files, dependencies, environment variables, CSS,
and Tailwind configuration without prompting. It throws rather than exiting and
skips existing files unless `overwrite` is enabled. It does not load project
configuration; pass a resolved config containing aliases and `resolvedPaths`.
A registries-only config is sufficient only for universal `registry:item` or
`registry:file` payloads with explicit file targets.

```ts
const cwd = process.cwd()
const config = await getRegistriesConfig(cwd)
await addRegistryItems(["@acme/agent"], {
  cwd,
  config,
  overwrite: false,
  silent: true,
})
```

Registry functions throw `RegistryError` subclasses. Handle `RegistryErrorCode`
or the specific classes for missing items, authentication, fetches,
configuration, local files, parsing, validation, invalid namespaces, and missing
environment variables.

```ts
try {
  await getRegistry("@unknown")
} catch (error) {
  if (error instanceof RegistryNotFoundError) {
    // recover from an unknown registry
  }
}
```

## Programmatic presets

`encodePreset` accepts a partial preset, fills omitted fields from
`DEFAULT_PRESET_CONFIG`, and returns a version-prefixed URL-safe code.
`decodePreset` returns the complete defaulted configuration or `null` for a
missing or invalid code. `shadcn/preset` also exports validators, random-preset
helpers, Base62 helpers, and `PRESET_*` option constants.

```ts
import { decodePreset, encodePreset } from "shadcn/preset"

const code = encodePreset({ style: "vega", theme: "blue", radius: "large" })
const preset = decodePreset(code)
```

## Dynamic search behavior

Registry search parameters are forwarded to registry backends, allowing a
dynamic registry to execute the search server-side. `searchRegistries` results
include item titles, and fuzzy matching considers those titles. These behaviors
are recorded in batch `4.16.1-4.18.0`.
