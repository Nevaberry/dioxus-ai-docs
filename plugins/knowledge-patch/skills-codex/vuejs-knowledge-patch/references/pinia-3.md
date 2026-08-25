# Pinia 3 and 4

## Pinia 3 package requirements

### Require TypeScript 4.5 or newer (since 3.0.0)

Pinia 3 declarations use TypeScript's native `Awaited` type. Projects that
compile those declarations therefore need TypeScript 4.5 or newer.

### Account for ESM package metadata (since 3.0.0)

Pinia 3 declares `"type": "module"` while continuing to ship CommonJS
distribution files. Do not mistake the metadata change for removal of its CJS
distribution.

### Supply Devtools for IIFE builds (since 3.0.0)

The standalone IIFE build no longer bundles Vue Devtools because of its size.
Include Devtools separately in IIFE workflows that rely on it.

## Pinia 4 migration

### Move consumers to ESM and install Devtools (since 4.0.3)

Pinia 4 is ESM-only and uses `@vue/devtools-api` v8, which must be installed
alongside Pinia. Move CommonJS-only tooling to an ESM-capable path first.

```sh
pnpm add pinia@^4 @vue/devtools-api@^8
```

### Treat `storeToRefs()` as a selective conversion (since 4.0.3)

`storeToRefs()` no longer fails when a store exposes nullish values. It omits
those entries and diagnoses properties that cannot be converted. Code must not
assume every enumerable store key appears in the returned refs.

### Use the public injection key (since 4.0.3)

Use the exported `piniaSymbol` for custom integrations instead of depending on
an internal injection key.

```ts
import { piniaSymbol } from 'pinia'
```

## Hydration behavior

### Preserve `skipHydrate()` on non-plain objects (since 4.0.3)

`shouldHydrate()` respects a `skipHydrate()` marker on non-plain objects. Mark
client-only objects explicitly when their server state must not be applied.

```ts
import { skipHydrate } from 'pinia'

const localCache = skipHydrate(new Map<string, string>())
```

### Replace collection contents during hydration (since 4.0.3)

Hydrating reactive `Set` or `Map` state replaces the existing collection
contents with incoming state rather than unioning both collections. Verify any
logic that previously expected local and server entries to merge.

## Nuxt compatibility

`@pinia/nuxt` 1.0.2 explicitly supports Nuxt 5. Use that release when moving a
Pinia-backed application to Nuxt 5 (since 4.0.3).
