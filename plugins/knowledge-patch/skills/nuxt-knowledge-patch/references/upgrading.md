# Upgrading and compatibility

Use this reference for major-version boundaries, changed defaults, removed options, dependency shifts, and migration commands. Verify the application, Nitro, builder, and module majors separately.

## Contents

- [Major boundaries and source layout](#major-boundaries-and-source-layout)
- [Upgrade commands and support channels](#upgrade-commands-and-support-channels)
- [Compatibility controls and changed defaults](#compatibility-controls-and-changed-defaults)
- [Dependency and builder migrations](#dependency-and-builder-migrations)
- [API and type migrations](#api-and-type-migrations)

## Major boundaries and source layout

### Adopt the `app/` source directory deliberately (4.0.0)

New Nuxt 4 projects place Vue application code under `app/` by default. Keep `content/`, `public/`, `server/`, `shared/`, and `nuxt.config.ts` at the project root.

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

Nuxt detects the established Nuxt 3 layout, so migration to `app/` is optional for an existing project.

### Treat Nuxt and Nitro majors independently (4.0-platform-guide)

Nuxt 4 initially continues to use Nitro 2; Nitro 3 integration is associated with the Nuxt 5 direction rather than the Nuxt 4 launch. Do not infer the Nitro major from the Nuxt major. The platform guide originally announced Nuxt 3 maintenance through the end of 2025 and estimated Nuxt 4 support through mid-2026; the Nuxt 3 date was revised later as described below.

### Use context-specific TypeScript projects (4.0.0)

Nuxt 4 generates separate TypeScript projects for application, server, `shared/`, and builder/configuration code while retaining one root `tsconfig.json`. This stronger separation can expose cross-context imports and type errors hidden by the former single project.

### Account for path-prefixed component names (3.14.0)

With v4 compatibility defaults, `components/App/Header.vue` is named `<AppHeader>`, not `<Header>`. Update name-based `<KeepAlive>` include/exclude rules and code that inspects component names.

## Upgrade commands and support channels

### Align related dependencies and apply the migration recipe (4.0.0)

Use the deduplicating upgrade command to align Nuxt packages and the lockfile. Run the migration recipe when moving to Nuxt 4, then review its changes because it cannot automate every project-specific migration.

```sh
npx nuxt upgrade --dedupe
npx codemod@latest nuxt/4/migration-recipe
```

### Stay on the Nuxt 3 channel explicitly (3.20.0)

Prevent a Nuxt 3 maintenance upgrade from moving to a newer major:

```sh
npx nuxt upgrade --dedupe --channel=v3
```

If the installed CLI does not recognize `--channel`, invoke `npx nuxi@latest` for the initial upgrade.

### Opt into nightly packages intentionally (3.19.0)

Use `npx nuxt upgrade --nightly` only when the task calls for testing nightly packages.

### Apply the revised Nuxt 3 support date (3.21.0)

Nuxt 3 security updates and critical bug fixes continue through July 31, 2026, superseding the earlier January 31 date and the platform guide's original end-of-2025 plan.

## Compatibility controls and changed defaults

### Remove stabilized experimental options (3.12.0)

Remove these obsolete options:

- `experimental.treeshakeClientOnly`: client-only tree-shaking remains enabled.
- `experimental.configSchema`: config schemas remain enabled.
- `experimental.polyfillVueUseHead`: replace the old behavior with a user plugin if needed.
- `experimental.respectNoSSRHeader`: replace the old behavior with server middleware if needed.

`scanPageMeta` is enabled by default.

### Expect narrower style inlining under v4 defaults (3.15.0)

Nuxt limits default style inlining to styles originating in Vue components when v4 defaults are active. Verify critical CSS behavior if the application relied on other styles being inlined.

### Enforce declared module compatibility (3.17.0)

Nuxt 3 can turn incompatible module declarations into errors with:

```ts
export default defineNuxtConfig({
  experimental: { enforceModuleCompatibility: true },
})
```

This enforcement becomes the default in Nuxt 4.

### Treat compatibility version 5 as a preview (4.2.0)

`future.compatibilityVersion: 5` opts into the first Nuxt 5 breaking behavior and subsequent v5 changes as they land, potentially including Nitro 3 integration. Use it for testing, not as a stable compatibility target.

```ts
export default defineNuxtConfig({
  future: { compatibilityVersion: 5 },
})
```

## Dependency and builder migrations

### Verify Vite 6 consumers (3.15.0)

Nuxt 3.15 upgrades to Vite 6. Most applications need no direct changes, but plugins or dependencies coupled to a specific Vite major require compatibility checks.

### Audit ESM-only transitive dependencies (3.16.0)

Nuxt 3.16 upgrades `db0` to 0.3 and moves `ohash`, `untyped`, `c12`, `pathe`, and `cookie-es` to ESM-only majors. It also adopts `unenv` v2, `unimport` v4, esbuild 0.25, and chokidar 4. Check modules that import or depend on those versions directly, especially CommonJS modules.

### Stop using deprecated Vite extension hooks (3.20.0)

The Vite `extend`, `extendConfig`, and `configResolved` hooks are deprecated. Avoid adding new dependencies on them in modules or builders and migrate existing integrations to supported hooks.

### Remove the Nuxt 2 compatibility assumption from Kit modules (4.0.0)

`@nuxt/kit` no longer supports Nuxt 2. Module authors that still target Nuxt 2 must split compatibility or retain an older Kit line.

### Remove a redundant router package after the router upgrade (4.4.0)

Nuxt uses Vue Router v5 and no longer depends on `unplugin-vue-router`. The change should be transparent for most projects; remove a direct `unplugin-vue-router` dependency when it was present only for Nuxt routing.

## API and type migrations

### Import `mergeModels` explicitly (4.2.0)

Nuxt no longer auto-imports Vue's `mergeModels`; add an explicit import wherever it is used.

### Prefer Web API error names (3.21.0)

`statusCode` and `statusMessage` still work but are deprecated ahead of Nuxt 5. Prefer `status` and `statusText`; `NuxtError` exposes getters under the new names.

```ts
throw createError({ status: 404, statusText: 'Not Found' })
```

### Treat `NuxtError` as a standard error (4.3.0)

`NuxtError` extends the standard `Error` type, so generic error utilities can preserve `message`, `stack`, and other standard properties without adapters.
