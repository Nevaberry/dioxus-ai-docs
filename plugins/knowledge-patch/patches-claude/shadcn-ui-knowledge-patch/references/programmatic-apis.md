# Programmatic APIs

## API Migration

Existing `components.json` files and installed components remain compatible,
but direct API consumers should replace `fetchRegistry` with `getRegistry` and
`resolveRegistryTree` with `resolveRegistryItems`. Registry schemas now come
from the `shadcn/schema` public subpath.

```ts
import { registryItemSchema } from "shadcn/schema"
```

## Public API Boundary and Registry Configuration

Only documented subpath imports are stable APIs; CLI command internals are not
public. `getRegistriesConfig(cwd)` reads `components.json`, or falls back to
top-level `registries` in `package.json`.

Registry fetches use process-lifetime resolved-URL caching by default and
deduplicate concurrent in-flight requests. Disable caching for servers and
watchers that require fresh registry reads.

```ts
const config = await getRegistriesConfig(process.cwd())
const items = await getRegistryItems(["@acme/button"], {
  config,
  useCache: false,
})
```

## Non-interactive Installation

`addRegistryItems` writes files and applies dependencies, environment
variables, CSS, and Tailwind configuration without prompting. It throws rather
than exiting and skips existing files unless `overwrite` is enabled.

The function does not load project configuration. Pass a resolved configuration
containing aliases and `resolvedPaths`. A registries-only configuration is
sufficient only for universal `registry:item` or `registry:file` payloads whose
files provide explicit targets.

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

## Typed Registry Failures

Registry functions throw subclasses of `RegistryError` rather than terminating
the process. Branch on `RegistryErrorCode` or specific classes for missing
items, authentication, fetch failures, configuration, local files, parsing,
validation, invalid namespaces, and missing environment variables.

```ts
try {
  await getRegistry("@unknown")
} catch (error) {
  if (error instanceof RegistryNotFoundError) {
    // Recover from an unknown registry.
  }
}
```

## Programmatic Preset Codes

`encodePreset` accepts a partial preset, fills omitted values from
`DEFAULT_PRESET_CONFIG`, and returns a version-prefixed URL-safe code.
`decodePreset` returns the full defaulted configuration, or `null` for a
missing or invalid code. `shadcn/preset` also exports validators, random-preset
helpers, Base62 helpers, and the `PRESET_*` option constants used by theme
tooling.

```ts
import { decodePreset, encodePreset } from "shadcn/preset"

const code = encodePreset({ style: "vega", theme: "blue", radius: "large" })
const preset = decodePreset(code)
```
