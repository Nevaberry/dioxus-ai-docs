# Apollo Server Runtime, HTTP, and Execution

Use this reference when upgrading Apollo Server, selecting an integration, configuring incremental execution, or hardening standalone HTTP handling.

## Server 5 migration

### Runtime and GraphQL.js minimums

For the server-v5-migration, require Node.js 20.0.0+ and `graphql` 16.11.0+. Prefer Node.js 24+ when outgoing requests must use an HTTP proxy.

### Express integration packages

For the server-v5-migration, Express middleware is no longer exported from `@apollo/server/express4`. Install `@as-integrations/express4` or `@as-integrations/express5` to match Express. These integrations also work with Server 4, so migrate them first.

```ts
import { expressMiddleware } from '@as-integrations/express4';
```

### Reporting and callback plugins use Node.js `fetch`

For the server-v5-migration, usage reporting, schema reporting, and subscription callback plugins default to Node's built-in `fetch`; `global-agent` no longer affects them. On Node 24+, remove `global-agent`, set `NODE_USE_ENV_PROXY=1`, and rename `GLOBAL_AGENT_HTTP_PROXY`, `GLOBAL_AGENT_HTTPS_PROXY`, and `GLOBAL_AGENT_NO_PROXY` to `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY`. On Node 20/22, install Undici's `EnvHttpProxyAgent` as global dispatcher.

To keep old behavior, install `node-fetch@2` and pass it as `fetcher` to every enabled reporting/callback plugin, including plugins previously enabled implicitly through environment variables.

### Variable coercion errors default to HTTP 400

For the server-v5-migration, `status400ForVariableCoercionErrors` defaults to `true`. Invalid variable values therefore return 400. `false` temporarily restores the Server 4 default but is intended for removal.

### Standalone server no longer embeds Express

For the server-v5-migration, `startStandaloneServer` uses Node's HTTP server directly. Express-specific behavior such as `x-powered-by`, dynamic `etag`, and access to Express request APIs disappears; use an explicit Express integration when needed.

### Incremental delivery remains pinned to one GraphQL.js alpha

For the server-v5-migration, the initial Server 5 release enables `@defer`/`@stream` only with exactly `graphql@17.0.0-alpha.2` and `Accept: multipart/mixed; deferSpec=20220824`. GraphQL.js 16, later v17 alphas, and the eventual stable v17 do not enable it in that release.

### Landing-page `precomputedNonce` removed

For the server-v5-migration, delete the unsafe deprecated `precomputedNonce` option. The Cloudflare Workers issue it addressed was fixed without a fixed nonce.

### Integration test suites no longer assume DOM globals

For the server-v5-migration, `@apollo/server-integration-testsuite` no longer compiles with DOM globals. Integration-library test projects that require them must add `"dom"` to `compilerOptions.lib` in their `tsconfig.json`.

### ES2023 compilation target

Since 5.0.0, Server is compiled to ES2023 instead of ES2020. Consumers and tooling must support ES2023 syntax and built-ins.

## Incremental execution protocols

### Incremental delivery moves to GraphQL.js alpha 9

Since 5.1.0, `@defer` and `@stream` incremental delivery uses `graphql@17.0.0-alpha.9` and protocol v0.2 selected with `Accept: multipart/mixed; incrementalSpec=v0.2`. `graphql@16` remains supported without incremental delivery; `graphql@17.0.0-alpha.2` deployments must upgrade. Alpha.9 result types use an `Alpha9` suffix and add completed/pending types; old unsuffixed types are renamed with `Alpha2`.

Legacy `multipart/mixed; deferSpec=20220824` support in 5.1.0 requires `@yaacovcr/transform`; without it, that header receives an error.

### Legacy incremental execution must be configured explicitly

Since 5.2.0, installing `@yaacovcr/transform` is insufficient for `multipart/mixed; deferSpec=20220824`. Pass its compatibility executor explicitly:

```ts
import { legacyExecuteIncrementally } from '@yaacovcr/transform';

const server = new ApolloServer({
  legacyExperimentalExecuteIncrementally: legacyExecuteIncrementally,
});
```

## Execution limits

### Configurable execution coercion limit

Since 5.3.0, configure GraphQL execution coercion limits through `executionOptions.maxCoercionErrors` on `ApolloServer`.

### Configurable validation error limit

Since 5.3.0, configure validation limits through `validationOptions.maxErrors` on `ApolloServer`.

## Standalone HTTP hardening

### Standalone request-body encodings are restricted

Since 5.4.0, `startStandaloneServer` accepts only UTF-8, UTF-16 LE/BE, and UTF-32 LE/BE request bodies. Other charsets return `415 Unsupported Media Type`. Other integrations are unaffected.

### Standalone GET request content-type hardening

Since 5.5.0, `@apollo/server/standalone` rejects GraphQL GET requests carrying a `Content-Type` other than `application/json` with optional parameters, returning 415. No `Content-Type` remains allowed, but default CSRF protection still requires a non-empty `X-Apollo-Operation-Name` or `Apollo-Require-Preflight`. This matters especially with cookie or HTTP Basic authentication.
