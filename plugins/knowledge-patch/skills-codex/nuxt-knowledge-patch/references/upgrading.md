# Upgrading and compatibility

Choose migration paths, compatibility modes, dependency majors, and replacement APIs.

## Compatibility changes and replacements

### `mergeModels` is no longer auto-imported (since 4.2.0)

Nuxt no longer auto-imports Vue's `mergeModels` helper; code using it must import it explicitly.

### Context-specific TypeScript projects (since 4.0.0)

Nuxt 4 generates separate TypeScript projects for application, server, `shared/`, and builder/configuration code while the project keeps a single root `tsconfig.json`. The stronger context separation can expose type errors that the previous setup hid.

### Default `app/` source directory (since 4.0.0)

Nuxt 4 places application code under `app/` by default, while `content/`, `public/`, `server/`, and `nuxt.config.ts` remain at the project root. Existing Nuxt 3 layouts are detected and continue to work, so adopting the new structure is optional.

```text
app/
├─ assets/
├─ components/
├─ composables/
├─ layouts/
├─ middleware/
├─ pages/
├─ plugins/
├─ utils/
├─ app.vue
├─ app.config.ts
└─ error.vue
```

### Deprecated Vite hooks (since 3.20.0)

The Vite `extend`, `extendConfig`, and `configResolved` hooks are now deprecated, so module and builder integrations should avoid new dependencies on these extension points.

### Stabilized experimental configuration (since 3.12.0)

The `experimental.treeshakeClientOnly`, `experimental.configSchema`, `experimental.polyfillVueUseHead`, and `experimental.respectNoSSRHeader` options have been removed. Client-only tree-shaking and config schemas retain their enabled defaults, while the two previously disabled behaviors require a user plugin or server middleware; `scanPageMeta` is now enabled by default.

### Web API error property names (since 3.21.0)

`statusCode` and `statusMessage` remain functional but are deprecated in favor of `status` and `statusText` ahead of Nuxt 5; `NuxtError` also exposes getters with the new names.

```ts
throw createError({ status: 404, statusText: 'Not Found' })
```

## Release channels and migrations

### ESM-only dependency upgrades (since 3.16.0)

Nuxt 3.16 upgrades `db0` to 0.3 and `ohash`, `untyped`, `c12`, `pathe`, and `cookie-es` to ESM-only majors. It also brings the rewritten `unenv` v2, `unimport` v4, esbuild 0.25, and chokidar 4, so modules coupled to those dependency versions need compatibility checks.

### Extended Nuxt 3 support (since 3.21.0)

Nuxt 3 security updates and critical bug fixes continue until its revised end-of-life date of July 31, 2026, rather than January 31.

### Nightly upgrades (since 3.19.0)

The Nuxt upgrade command supports `--nightly` for updating a project against nightly packages.

```sh
npx nuxt upgrade --nightly
```

### Nuxt 2 support removed from Nuxt Kit (since 4.0.0)

`@nuxt/kit` no longer supports Nuxt 2, a breaking change for module authors whose modules still target Nuxt 2.

### Nuxt 5 compatibility preview (since 4.2.0)

`future.compatibilityVersion: 5` opts into the first Nuxt 5 breaking behavior and all later v5 changes as they land, potentially including Nitro v3 integration. Use it only for testing rather than as a bounded compatibility target.

```ts
export default defineNuxtConfig({ future: { compatibilityVersion: 5 } })
```

### Nuxt and Nitro major versions (since 4.0-platform-guide)

Nuxt 4 does not initially adopt Nitro v3; that upgrade is planned together with Nuxt 5, decoupling Nuxt majors from immediate dependency-major adoption. The announced maintenance plan keeps Nuxt 3 updated through the end of 2025 and estimates Nuxt 4 support through mid-2026.

### Staying on the Nuxt 3 release channel (since 3.20.0)

Nuxt 3 upgrades should explicitly select the v3 channel so related dependencies are deduplicated without moving the project to a newer major.

```shell
npx nuxt upgrade --dedupe --channel=v3
```

If the installed CLI is too old to support `--channel`, run `npx nuxi@latest` for the initial upgrade.

### Upgrade and migration commands (since 4.0.0)

Use the deduplicating upgrade command to align Nuxt's related dependencies and lockfile. An optional Codemod recipe automates many, but not all, Nuxt 4 migration steps.

```sh
npx nuxt upgrade --dedupe
npx codemod@latest nuxt/4/migration-recipe
```

### Vite 6 upgrade (since 3.15.0)

Nuxt 3.15 upgrades its Vite dependency to Vite 6. The change is expected to be transparent for most applications, but plugins and other dependencies that require a particular Vite major need compatibility checks.

### Vue Router v5 (since 4.4.0)

Nuxt now uses Vue Router v5 and no longer depends on `unplugin-vue-router`. The upgrade should be transparent for most applications, but projects using `unplugin-vue-router` directly can remove that dependency.
