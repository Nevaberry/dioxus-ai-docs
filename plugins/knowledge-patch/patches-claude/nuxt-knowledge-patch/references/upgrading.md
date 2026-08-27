# Upgrading and compatibility

## Choose the intended release channel

For a Nuxt 3 application, stay on the v3 channel while deduplicating related packages (3.20.0):

```sh
npx nuxt upgrade --dedupe --channel=v3
```

If the installed CLI does not recognize `--channel`, run `npx nuxi@latest` for the first upgrade. Nuxt 3 security and critical-fix support was extended through July 31, 2026 (3.21.0). Use `npx nuxt upgrade --nightly` only when deliberately testing nightly packages (3.19.0).

For a Nuxt 4 migration, align dependencies and the lockfile, then optionally run the migration recipe (4.0.0):

```sh
npx nuxt upgrade --dedupe
npx codemod@latest nuxt/4/migration-recipe
```

The codemod covers common changes, not every application-specific migration. `npm create nuxt` is the lightweight single-file initializer for new projects (3.16.0).

## Keep Nuxt and Nitro majors independent

Nuxt 4 did not initially adopt Nitro 3; the dependency-major change was planned with Nuxt 5. Do not infer Nitro's major from Nuxt's major (4.0-platform-guide). That platform guide estimated Nuxt 4 maintenance through mid-2026; treat the date as a planning snapshot and verify the applicable support policy. The `future.compatibilityVersion: 5` switch opts into the first Nuxt 5 break and later v5 changes as they arrive, potentially including Nitro 3. Use it for experiments, not as a fixed migration target (4.2.0).

```ts
export default defineNuxtConfig({
  future: { compatibilityVersion: 5 },
})
```

## Nuxt 4 source layout

New Nuxt 4 projects default application code to `app/`; `content/`, `public/`, `server/`, `shared/`, and `nuxt.config.ts` remain at the project root. Nuxt detects existing Nuxt 3 layouts, so moving directories is optional unless the migration explicitly adopts the new structure (4.0.0).

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

Compatibility version 4 also changes component naming: `components/App/Header.vue` is named `AppHeader`, not `Header`, which matters to name-based `<KeepAlive>` filters (3.14.0). Under v4 defaults, automatic style inlining is limited to styles originating in Vue components (3.15.0).

## TypeScript compatibility shifts

Nuxt uses TypeScript `bundler` module resolution so subpath imports match its resolver. Packages with incomplete export metadata may need the temporary `future.typescriptBundlerResolution: false` escape hatch (3.10.0). With local TypeScript 5.4, generated configuration uses `module: preserve` (3.12.0).

Nuxt 4 creates separate application, server, shared, and builder/configuration TypeScript projects behind the root `tsconfig.json`; this can reveal invalid cross-context imports and previously hidden errors (4.0.0). Current Nuxt 4 also exposes `typescript.nodeTsConfig` and `typescript.sharedTsConfig` for independent overrides (release-catalogs).

Vue type augmentation now targets `vue`, not `@vue/runtime-core` (3.13.0). If a dependency still augments the legacy target, bridge it temporarily from a root declaration file:

```ts
import type {
  ComponentCustomOptions as LegacyOptions,
  ComponentCustomProperties as LegacyProperties,
} from 'vue'

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties extends LegacyProperties {}
  interface ComponentCustomOptions extends LegacyOptions {}
}
```

## Removed experimental settings

The `experimental.treeshakeClientOnly`, `experimental.configSchema`, `experimental.polyfillVueUseHead`, and `experimental.respectNoSSRHeader` options were removed (3.12.0). Client-only tree shaking and configuration schemas remain enabled. Re-create the two formerly disabled behaviors with a user plugin or server middleware when needed. Page-meta scanning became enabled by default.

Do not keep removed settings as documentation: deleting inert configuration makes the active compatibility behavior clear.

## Dependency and API migrations

- Nuxt 3.15 moved to Vite 6; check plugins and dependencies that pin a Vite major (3.15.0).
- Nuxt 3.16 moved `db0` to 0.3 and `ohash`, `untyped`, `c12`, `pathe`, and `cookie-es` to ESM-only majors. It also adopted `unenv` v2, `unimport` v4, esbuild 0.25, and chokidar 4; audit modules coupled to these transitive packages (3.16.0).
- Import head composables from Nuxt auto-imports or `#app/composables/head`; direct `@unhead/vue` imports can lose Nuxt async context after the Unhead v2 integration (3.16.0).
- Import Vue's `mergeModels` explicitly because Nuxt no longer auto-imports it (4.2.0).
- Avoid new use of deprecated Vite `extend`, `extendConfig`, and `configResolved` hooks in module and builder integrations (3.20.0).
- Prefer Web API names `status` and `statusText`; `statusCode` and `statusMessage` still work but are deprecated, and `NuxtError` exposes getters for the new names (3.21.0).
- Nuxt uses Vue Router v5 and no longer depends on `unplugin-vue-router`; direct users can remove that dependency (4.4.0).
- Nuxt Kit no longer supports Nuxt 2, so modules that still target Nuxt 2 need a separate compatible Kit line (4.0.0).

## Compatibility enforcement and diagnostics

Consumers can opt into errors for modules whose declared compatibility requirements do not match; this became the Nuxt 4 default (3.17.0). Development diagnostics also became stricter: rootless server components, the reserved `runtimeConfig.app` namespace, core auto-import preset overrides, and multiple `definePageMeta` calls are reported. Use one page-meta call per file.

Install `@nuxt/docs` when a tool needs the raw Markdown and YAML documentation sources rather than scraping the documentation site (3.17.0).

After an upgrade, regenerate types and verify initial SSR, client navigation, the selected builder, and the real deployment preset.
