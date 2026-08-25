# Authentication, runtime, and query

## Authentication

### Per-request OAuth callback URLs (2.2.0)

OAuth authentication requests may include `callback_url`, allowing different
actors or login pages to choose different return destinations. The flow also
carries OAuth `state`:

```http
POST /customer/auth/github
Content-Type: application/json

{"callback_url":"https://example.com/customer/github/callback"}
```

### OAuth callback validation requires all query parameters (2.2.0)

Third-party callback handling must forward every query parameter returned by
the provider, not only `code`; this includes `state` and `error`. If the Auth
Module definition is overridden in `medusa-config.ts`, add the Cache Module
dependency because OAuth state is stored there temporarily:

```ts
{
  resolve: "@medusajs/medusa/auth",
  dependencies: [Modules.CACHE, ContainerRegistrationKeys.LOGGER],
  options: { providers: [/* ... */] },
}
```

### Authentication JWT user metadata (2.11.0)

JWTs issued by authentication routes include `user_metadata`, exposing
identity-associated custom data in token claims.

## Server runtime and routing

### Health checks in every running mode (2.2.0)

Medusa provides a health endpoint in every running mode. Deployment probes can
use the built-in health check regardless of how the server starts.

### Default Redis retry strategy (2.3.0)

Redis connections have a default retry strategy; projects do not need to
supply one explicitly in every case.

### Deterministic API route and middleware loading (2.6.0)

The rebuilt loader registers global middleware, route middleware, and then API
routes. Within middleware groups, core runs first, registered plugins run in
registration order, and the application runs last. Matchers are ordered
wildcard, regex, static, then dynamic.

A middleware definition without HTTP methods is global; one with methods is
route middleware. Custom middleware extends rather than replaces the existing
stack. Application route overrides still take precedence over plugin and core
routes in this release, though that override behavior is planned for removal.

### Custom logger configuration (2.10.0)

Replace the default logger with a class implementing Medusa's `Logger`
interface:

```ts
// medusa-config.ts
import { MyCustomLogger } from "./custom-logger"

export default defineConfig({
  logger: MyCustomLogger,
})
```

## Cross-module Index queries

### Experimental cross-module index queries (2.8.0)

The experimental `@medusajs/index` module ingests Products, Product Variants,
Prices, and Sales Channels into a central structure for cross-module filtering.
Install and register it, enable the feature flag, and apply migrations before
starting the server:

```sh
yarn add @medusajs/index
```

```ts
// medusa-config.ts
modules: [{ resolve: "@medusajs/index", options: {} }]
```

```dotenv
MEDUSA_FF_INDEX_ENGINE=true
```

```sh
npx medusa db:migrate
```

Query it through `query.index`. To include a custom linked model, put that
model's property names in `filterable` on its side of the link definition:

```ts
const { data, metadata } = await query.index({
  entity: "product",
  fields: ["id", "title", "brand.*"],
  filters: { brand: { name: "Hermes" } },
})
```

The result count in `metadata` is a PostgreSQL planner estimate, not an exact
`COUNT(*)`, and can be inaccurate for small data sets. The module is
experimental and its API is subject to change.

### Logical operators in Index filters (2.9.0)

Index filters accept nested `$and` and `$or` arrays. This release also restores
indexing of custom-module entities after a regression:

```ts
const { data: products } = await query.index({
  entity: "product",
  filters: {
    $and: [
      { status: "published" },
      { $or: [{ brand: { name: { $ilike: "%adidas%" } } }] },
    ],
  },
})
```

### Negation operators in Index filters (2.10.0)

Index filters support `$nin` and `$not` in addition to the logical operators.

## Query graph caching

### Preview caching module and cached Query graphs (2.11.0)

The early-preview Caching Module provides provider-backed caching with
strategy-generated keys and tags. Mutations through module service methods
emit events that invalidate matching tagged entries. Enable the feature flag,
register the Redis provider, and opt individual Query graphs into caching:

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

Enabling caching integrates it into cart operations for regions, promotion
codes, variant price sets, variants, shipping options, sales channels, and
customers. The earlier `@medusajs/cache`, `@medusajs/cache-redis`, and
`@medusajs/cache-inmemory` modules are deprecated.
