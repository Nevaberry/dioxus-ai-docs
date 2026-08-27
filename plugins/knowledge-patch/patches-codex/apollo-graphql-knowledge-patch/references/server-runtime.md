# Apollo Server Runtime and Integrations

## Runtime and integration migration

### Runtime and GraphQL.js minimums (server-v5-migration)

Apollo Server 5 requires Node.js 20.0.0+ and `graphql` 16.11.0+. Upgrade both
first. Prefer Node.js 24+ when outbound requests must use an HTTP proxy.

### ES2023 compilation target (5.0.0)

Published Apollo Server 5 JavaScript targets ES2023 rather than ES2020; all
downstream tooling must support its syntax and built-ins.

### Express integration packages (server-v5-migration)

Express middleware is no longer exported from `@apollo/server/express4`.
Install `@as-integrations/express4` or `@as-integrations/express5` and import
`expressMiddleware` there. These packages also work with Apollo Server 4, so
this can be staged before the major upgrade.

### Standalone server no longer embeds Express (server-v5-migration)

`startStandaloneServer` uses Node's HTTP server directly. Code depending on
Express details such as `x-powered-by`, dynamic `etag`, or Express request APIs
must move to an explicit Express integration.

### Reporting and callback plugins use Node.js `fetch` (server-v5-migration)

Usage reporting, schema reporting, and subscription callback plugins default to
built-in `fetch`, so `global-agent` no longer affects them. On Node.js 24+, set
`NODE_USE_ENV_PROXY=1` and use `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY`. On
Node.js 20/22, configure Undici's `EnvHttpProxyAgent` as global dispatcher.
Rename `GLOBAL_AGENT_HTTP_PROXY`, `GLOBAL_AGENT_HTTPS_PROXY`, and
`GLOBAL_AGENT_NO_PROXY` to their standard counterparts.

To preserve old behavior, install `node-fetch@2` and explicitly supply its
fetcher to every enabled reporting/callback plugin, including plugins previously
enabled implicitly through environment variables.

### Integration test suites no longer assume DOM globals (server-v5-migration)

`@apollo/server-integration-testsuite` does not compile with ambient DOM types.
Integration projects that need them must add `"dom"` to their own `tsconfig.json`
`lib` setting.

### Landing-page `precomputedNonce` removed (server-v5-migration)

Delete the deprecated and unsafe `precomputedNonce` landing-page option. It has
no replacement; the compatibility issue it addressed was fixed separately.

## Request validation and security

### Variable coercion errors default to HTTP 400 (server-v5-migration)

`status400ForVariableCoercionErrors` defaults to true, restoring HTTP 400 for
invalid variables. Set it false only for temporary compatibility; the option is
intended for future removal.

### Configurable execution coercion limit (5.3.0)

Set `executionOptions.maxCoercionErrors` in `ApolloServer` to cap execution
coercion errors.

```js
new ApolloServer({ executionOptions: { maxCoercionErrors: 50 } });
```

### Configurable validation error limit (5.3.0)

Set `validationOptions.maxErrors` to cap GraphQL validation errors.

### Standalone request-body encodings are restricted (5.4.0)

`startStandaloneServer` accepts only UTF-8, UTF-16 LE/BE, or UTF-32 LE/BE
bodies. Other encodings return HTTP 415, closing a denial-of-service path. Other
integrations are unaffected.

### Standalone GET request content-type hardening (5.5.0)

`@apollo/server/standalone` rejects GraphQL GET requests whose `Content-Type` is
not `application/json` with optional parameters; missing `Content-Type` remains
allowed. Default CSRF prevention still requires a non-empty
`X-Apollo-Operation-Name` or `Apollo-Require-Preflight` for a headerless request.
This matters especially for cookie or HTTP Basic authentication.

## Incremental delivery protocols

### Incremental delivery remains pinned to one GraphQL.js alpha (server-v5-migration)

Initial Server 5 `@defer` and `@stream` delivery works only with exactly
`graphql@17.0.0-alpha.2` and `Accept: multipart/mixed; deferSpec=20220824`.
GraphQL.js 16, newer alphas, and a later stable 17 release do not enable it for
that server release.

### Incremental delivery moves to GraphQL.js alpha 9 (5.1.0)

Server 5.1 supports `@defer`/`@stream` with `graphql@17.0.0-alpha.9` and the v0.2
protocol selected by `Accept: multipart/mixed; incrementalSpec=v0.2`.
GraphQL.js 16 remains supported without incremental delivery;
`graphql@17.0.0-alpha.2` users must upgrade. Legacy header support requires
`@yaacovcr/transform`; without it the
request errors. Old unsuffixed result types gain an `Alpha2` suffix, while new
`Alpha9` types include completed and pending results.

### Legacy incremental execution must be configured explicitly (5.2.0)

Installing `@yaacovcr/transform` alone no longer enables the legacy
`deferSpec=20220824` protocol. Pass its `legacyExecuteIncrementally` function as
`legacyExperimentalExecuteIncrementally` to `ApolloServer`; otherwise legacy
accept headers return an error.
