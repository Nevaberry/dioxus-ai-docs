# Registry Consumption

## Namespaced Registries

The CLI addresses decentralized registry items as `@registry/name`. Define a
namespace in `components.json` with a URL template containing `{name}`.
Registry items can declare namespaced `registryDependencies` from one or more
registries, and the CLI resolves them automatically.

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

## Namespace and Request-template Constraints

A namespace starts and ends with an alphanumeric character. Between those
characters it may contain alphanumerics, hyphens, or underscores. A registry
URL must contain `{name}` and may contain `{style}` for the project's selected
style. Object-form entries may add `params`. Environment expansion works in
URLs, headers, and parameters, including shell-style defaults such as
`${REGISTRY_VERSION:-v2}`.

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

## Private Registry Authentication

An object registry entry accepts `url` and `headers` with environment-variable
interpolation. Supported authentication patterns include basic auth, bearer
tokens, API-key query parameters, and arbitrary headers. If a variable is
missing, the CLI names it; supply it through `.env` or `.env.local`.

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

An authenticated backend can return a JSON `message` with a `401` or `403`.
The CLI displays that message, allowing the backend to explain a missing token,
expired subscription, or resource-specific restriction.

```ts
return NextResponse.json(
  { error: "Forbidden", message: "This component requires Design team access." },
  { status: 403 }
)
```

## Registry Discovery Commands

Inspect one item with `view`, query items with `search`, or enumerate a
registry with `list`.

```sh
pnpm dlx shadcn view @acme/auth-system
pnpm dlx shadcn search @tweakcn -q "dark"
pnpm dlx shadcn list @acme
```

## Intentional Cross-registry Overrides

Registry dependencies install before the item that declares them. Resolution
deep-merges Tailwind settings, CSS variables, CSS, environment variables, and
similar configuration. For duplicate target file paths, the last resolved
file wins. A custom item can therefore depend on a third-party item and
replace only selected files or settings.

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

## GitHub and Local Registry Dependencies

`registryDependencies` may name GitHub items or local item JSON files. Pin
every GitHub dependency with its own tag or full commit SHA because references
are not inherited. Bare names still mean built-in items, so dependencies from
the same GitHub repository need the full address.

```json
{
  "registryDependencies": [
    "acme/ui/button#v1.2.0",
    "./editor.json"
  ]
}
```

## Alias-relative File Targets

A target may begin with `@components/`, `@ui/`, `@lib/`, or `@hooks/`; these
resolve against the consumer's `components.json` directories independently of
its import prefix. `@utils/` is unsupported because that alias denotes a file.
The target may differ from the file's declared type and is required for
`registry:page` and `registry:file`.

```json
{
  "path": "registry/new-york/example/format-date.ts",
  "type": "registry:ui",
  "target": "@lib/format-date.ts"
}
```

## Current CLI Registry Resolution

The following behavior is from batch `4.16.1-4.18.0`.

### Path-segmented Build Output

From 4.16.1, `shadcn build` creates nested output directories for item names
with path segments, such as `extension/foo`, instead of failing with `ENOENT`.

### Dynamic Search Parameters and Titles

Registry search parameters are forwarded to backends, enabling server-side
search in dynamic registries. `searchRegistries` results include item titles,
and fuzzy matching considers those titles.

### SOCKS Registry Proxies

The registry HTTP stack accepts SOCKS4 and SOCKS5 through `ALL_PROXY` or
`all_proxy` when the value has a `socks*://` URL. A non-SOCKS `ALL_PROXY` is
ignored. HTTP and HTTPS proxying continues to use `HTTP_PROXY`, `HTTPS_PROXY`,
and `NO_PROXY`.

```sh
ALL_PROXY=socks5://127.0.0.1:1080 pnpm dlx shadcn@latest add button
```

### Merged Package and Component Registries

From 4.18.0, declarations in top-level `package.json` and `components.json`
are merged. If `components.json` is absent, the CLI can add registries to
`package.json`. The `add`, `search`, `view`, and `init` commands resolve that
configuration in memory without copying it into `components.json`.

```json
{
  "registries": {
    "@acme": "https://acme.example/r/{name}.json"
  }
}
```
