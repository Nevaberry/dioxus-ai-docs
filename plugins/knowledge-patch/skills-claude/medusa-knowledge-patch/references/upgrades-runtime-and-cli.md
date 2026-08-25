# Upgrades, runtime, configuration, and CLI

## CLI, builds, and scaffolding

### Monorepo scaffolding for new applications (since 2.14.0)

`create-medusa-app` and `medusa new` now scaffold a `dtc-starter`-based monorepo with separate backend and storefront packages. The former `medusa-starter-default` and Next.js Starter Storefront repositories are deprecated in favor of this layout.

```sh
yarn dlx create-medusa-app@latest my-medusa-store
```

### Package-manager-aware project creation (since 2.13.0)

`create-medusa-app` now uses the package manager that launched it, including pnpm, and accepts `--use-npm`, `--use-yarn`, or `--use-pnpm` to override that choice.

```sh
pnpm dlx create-medusa-app@latest
```

### Production CLI defaults and environment loading (since 2.5.0)

When `NODE_ENV` is unset, `medusa start` now defaults it to `production`. The CLI also always loads `.env` alongside the environment-specific file, and a failed `medusa build` now exits with a failure status so CI can detect the error.

## Dependencies and runtime compatibility

### Core dependencies are bundled behind the framework (since 2.11.0)

Medusa now installs non-Medusa core dependencies internally through `@medusajs/deps`. Upgrades must remove direct dependencies on MikroORM, Awilix, and `pg` (including the MikroORM CLI), reinstall, and rewrite explicit imports to `@medusajs/framework/mikro-orm/<subpath>`, `@medusajs/framework/awilix`, and `@medusajs/framework/pg`; supported OpenTelemetry imports likewise move under `@medusajs/framework/opentelemetry/<subpath>`.

### Framework-owned Zod imports (since 2.13.0)

Zod is now a dependency and export of `@medusajs/framework`, which makes it available under strict package-manager isolation. Custom code should migrate direct imports to the framework export; a codemod is provided for the rewrite:

```ts
import { z } from "@medusajs/framework/zod"
```

```sh
npx medusa codemod replace-zod-imports
```

### MikroORM 6 dependency upgrade (since 2.4.0)

Medusa 2.4 upgrades its MikroORM dependency from version 5 to 6. User projects do not need other changes for MikroORM's breaking APIs, but must upgrade all runtime packages and the CLI to `6.4.3` alongside Medusa and refresh the lock file.

```json
{
  "dependencies": {
    "@mikro-orm/core": "6.4.3",
    "@mikro-orm/knex": "6.4.3",
    "@mikro-orm/migrations": "6.4.3",
    "@mikro-orm/postgresql": "6.4.3"
  },
  "devDependencies": {
    "@mikro-orm/cli": "6.4.3"
  }
}
```

### Next.js storefronts are incompatible with Node.js 25 (since 2.13.0)

Medusa's Next.js storefronts are not compatible with Node.js 25 in this release, so their runtime must use another supported Node.js version.

### Zod 4.2 migration for custom code (since 2.14.0)

Medusa now uses Zod 4. Backends that directly install Zod must upgrade it to `4.2.0`, and custom validators, routes, modules, workflows, plugins, and Admin extensions must migrate their Zod 3 usage before upgrading.

```sh
yarn add zod@4.2.0
```

Notable rewrites include `invalid_type_error`/`required_error` and `errorMap` to `error`, `.format()`/`.flatten()` to `z.treeifyError`, string-format methods such as `z.string().email()` to top-level functions such as `z.email()`, `.strict()`/`.passthrough()` to `z.strictObject()`/`z.looseObject()`, `z.nativeEnum()` to `z.enum()`, and one-argument `z.record(value)` to `z.record(z.string(), value)`.

## Migrations and retention

### One-time cross-module data migration scripts (since 2.3.0)

Medusa now discovers default-exported files under `src/migration-scripts` in projects, plugins, and core, and runs them automatically during `medusa db:migrate`. They have dependency-container access for cross-module changes; execution is tracked in `script_migrations` under a table lock, and a script is skipped on future runs only after it succeeds.

## Runtime services and configuration

### Custom logger configuration (since 2.10.0)

The default logger can now be replaced with a class that implements Medusa's `Logger` interface:

```ts
// medusa-config.ts
import { MyCustomLogger } from "./custom-logger"

export default defineConfig({
  logger: MyCustomLogger,
})
```

### Default Redis retry strategy (since 2.3.0)

Redis connections now have a default retry strategy rather than requiring every project to supply one explicitly.

### Health checks in every running mode (since 2.2.0)

Medusa now provides a health endpoint in every running mode, allowing deployment probes to use the built-in health check regardless of how the server is started.

### Preview caching module and cached Query graphs (since 2.11.0)

The early-preview Caching Module adds provider-backed caching with strategy-generated keys and tags; mutations through module service methods emit events that invalidate matching tagged entries. Enable the feature flag, register the Redis provider, and opt individual Query graphs into caching:

```ts
module.exports = defineConfig({
  modules: [{
    resolve: "@medusajs/medusa/caching",
    options: {
      providers: [{
        id: "caching-redis",
        resolve: "@medusajs/caching-redis",
        options: { redisUrl: process.env.REDIS_URL },
      }],
    },
  }],
  featureFlags: { caching: true },
})

const { data } = await query.graph({
  entity: "product",
  filters: { id: "prod_1234" },
  options: { cache: { enable: true } },
})
```

Enabling caching also integrates it into cart operations for regions, promotion codes, variant price sets, variants, shipping options, sales channels, and customers. The earlier `@medusajs/cache`, `@medusajs/cache-redis`, and `@medusajs/cache-inmemory` modules are deprecated.
