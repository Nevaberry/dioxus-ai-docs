# Pinia Package and Runtime

## Pinia 3 package requirements

Pinia 3 declarations use TypeScript's native `Awaited`, so projects compiling
them need TypeScript 4.5 or newer (since 3.0.0).

The Pinia 3 package declares `"type": "module"` but still provides CommonJS
distribution files for CJS consumers. Its standalone IIFE build no longer
bundles Vue Devtools because of size; include Devtools separately if an IIFE
workflow needs it.

## Move to Pinia 4

Pinia 4 is ESM-only and uses `@vue/devtools-api` v8, which is now a separate
required installation (since 4.0.3). CommonJS-only tools must move to an
ESM-capable path before upgrading.

```sh
pnpm add pinia@^4 @vue/devtools-api@^8
```

Vue Router allows Pinia 4 starting in Vue Router 5.2.0.

## Store refs and public integration

### Handle omitted nullish values in `storeToRefs()`

`storeToRefs()` no longer fails when a store exposes `null` or `undefined`
(since 4.0.3). It omits those entries and diagnoses values that cannot be
converted. Do not assume every enumerable store property has a corresponding
entry in the returned object.

### Use the public injection symbol

Pinia exports `piniaSymbol` for integrations that need its injection key
(since 4.0.3). Do not depend on an internal key.

```ts
import { piniaSymbol } from 'pinia'
```

## Hydration behavior

`shouldHydrate()` honors `skipHydrate()` on non-plain objects (since 4.0.3).
Mark local state that must not be replaced:

```ts
import { skipHydrate } from 'pinia'

const localCache = skipHydrate(new Map<string, string>())
```

When reactive `Set` or `Map` state is hydrated, Pinia replaces the existing
collection contents with incoming state rather than unioning the two. Test
collection hydration where client-local values previously survived by merge.

## Nuxt compatibility

`@pinia/nuxt` 1.0.2 explicitly supports Nuxt 5. Use that release or newer
compatible guidance when migrating a Pinia-backed application to Nuxt 5.
