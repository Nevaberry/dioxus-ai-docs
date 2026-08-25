# Framework Integrations

## Node integration renames (9.0.0-guide)

`processThreadBreadcrumbIntegration` is renamed to
`childProcessIntegration`, and its integration name changes from
`ProcessAndThreadBreadcrumbs` to `ChildProcess`.

`vercelAIIntegration` keeps its factory name, but its integration name changes
from `vercelAI` to `VercelAI`. Update integration-name filters as well as
factory calls when applicable.

## Prisma

The bundled `prismaIntegration` instrumentation targets Prisma 6 and no longer
supports Prisma 5. Prisma 6 does not require the `tracing` preview feature.

To instrument another Prisma version, install matching
`@prisma/instrumentation`, pass its `PrismaInstrumentation` instance through
`prismaInstrumentation`, and retain `previewFeatures = ["tracing"]` when a
pre-v6 Prisma release requires it.

```js
Sentry.init({
  integrations: [
    Sentry.prismaIntegration({
      prismaInstrumentation: new PrismaInstrumentation(),
    }),
  ],
});
```

## NestJS

The Node SDK's `nestIntegration` and `setupNestErrorHandler` are removed. Use
`@sentry/nestjs` and make these replacements:

| Removed | Replacement |
| --- | --- |
| `@WithSentry` | `@SentryExceptionCaptured` |
| Generic or GraphQL global filters | `SentryGlobalFilter` |
| `SentryService` | Remove |
| `SentryTracingInterceptor` | Remove |

`SentryGlobalFilter` also supports WebSocket errors (since 10.68.0).

## React Router and Remix

Generic React helpers `wrapUseRoutes` and `wrapCreateBrowserRouter` are
removed. Import the explicit `V6` or `V7` variant matching the application's
React Router major.

React Router now uses its instrumentation API by default (10.68.0). Custom
instrumentation should not assume the older path is automatically selected.

Remix removes `autoInstrumentRemix` and always behaves as though it were
`true`. Its source-map upload behavior is documented in the build reference.

## Vue, Nuxt, and Pinia

Configure Vue component tracing under
`vueIntegration({ tracingOptions: ... })`, including in Nuxt. Update spans are
off unless `"update"` is included in `tracingOptions.hooks`.

```js
Sentry.init({
  integrations: [
    Sentry.vueIntegration({
      tracingOptions: {
        trackComponents: true,
        hooks: ["mount", "update", "unmount"],
      },
    }),
  ],
});
```

Pinia `stateTransformer` callbacks receive the combined state keyed by store
ID. Remove the obsolete `logErrors` option: the Vue handler always propagates
to a user handler or rethrows.

Since 9.0.0, the Nuxt module has an `enabled` switch. Its `SourceMapsOptions`
also supports `silent`, `errorHandler`, and `release`.

## SolidStart

`sentrySolidStartVite` is no longer exported. Wrap the SolidStart config with
`withSentry` and pass build-time options as its second argument:

```ts
export default defineConfig(withSentry(solidStartConfig, sentryBuildOptions));
```

SolidStart defaults server setup to `--import` and supports
`autoInjectServerSentry`, including the
`autoInjectServerSentry: "experimental_dynamic-import"` mode (9.0.0).

## SvelteKit

`fetchProxyScriptNonce` is removed. Use a CSP script hash or disable fetch
proxy script injection. Since 9.0.0, SvelteKit injects that script only for
versions below 2.16.0.

## Astro and Fastify

Astro 5 request routes and client-side routes are parameterized; the request
route is constructed at runtime (10.0.0).

`fastifyIntegration` accepts `shouldHandleError` so the integration's error
handler can select captured errors:

```js
Sentry.init({
  integrations: [
    Sentry.fastifyIntegration({
      shouldHandleError: (error) => shouldReport(error),
    }),
  ],
});
```

## Browser and Node additions

The browser SDK includes a Statsig integration, and the Node SDK captures
exceptions from `worker_threads` (since 9.0.0).

## Modern server framework data controls

The Elysia, Hono, Nitro, and TanStack Start SDKs accept `dataCollection`
options for automatic request enrichment. Disable default user information
and all request-body collection explicitly when those fields must stay inside
the application:

```js
Sentry.init({ dataCollection: { userInfo: false, httpBodies: [] } });
```

## Elysia

The alpha `@sentry/elysia` SDK supports Elysia 1.4+ on Bun and on Node.js 18+
through `@elysiajs/node`. It instruments Elysia directly; do not add
`@elysiajs/opentelemetry` for Sentry.

Initialize Sentry before constructing the application and wrap the app before
adding routes. The global error hook captures 5xx responses by default;
`shouldHandleError` replaces that policy.

```ts
Sentry.init({ dsn });
const app = Sentry.withElysia(new Elysia(), {
  shouldHandleError: ({ set }) => set.status === 500 || set.status === 503,
}).get("/", () => "ok");
```

## Hono

`@sentry/hono` supports Hono 4+ on Cloudflare Workers, Node.js, Bun, and Deno.
It replaces deprecated `@hono/sentry` and `toucan-js` packages.

Install the same-version peer for the runtime: `@sentry/cloudflare`,
`@sentry/node`, `@sentry/bun`, or `@sentry/deno`. Import `sentry` from the
matching `@sentry/hono/<runtime>` entry point and register it early.
Cloudflare needs `nodejs_compat`; options may come from Worker bindings.

```ts
import { sentry } from "@sentry/hono/cloudflare";

const app = new Hono<{ Bindings: { SENTRY_DSN: string } }>();
app.use(sentry(app, (env) => ({ dsn: env.SENTRY_DSN })));
```

On Node.js, preload a file that imports and initializes `@sentry/hono/node`,
then call `app.use(sentry(app))` without options. The middleware captures
exceptions reaching Hono's `onError`, excluding 3xx/4xx by default; use
`shouldHandleError` to override the selection.

## Nitro

The beta `@sentry/nitro` SDK requires Nitro `3.0.260415-beta` or newer and
Node.js 18.19+. Wrap configuration with `withSentryConfig`, initialize in a
root `instrument.mjs`, and preload it with `--import` in development, preview,
and production.

```ts
export default withSentryConfig(defineNitroConfig({}), {
  org: "my-org",
  project: "my-project",
  authToken: process.env.SENTRY_AUTH_TOKEN,
});
// NODE_OPTIONS='--import ./instrument.mjs' nitro dev
```

The wrapper registers the module, enables Nitro tracing channels, and by
default uploads hidden source maps before deleting them. It respects an
explicit `sourcemap` setting.

The SDK re-exports `@sentry/node`. Its Nitro `error` hook captures unhandled
route and middleware errors but skips 3xx/4xx `HTTPError`s; set
`enableNitroErrorHandler: false` to turn off the hook.

Request tracing covers `h3.request`, `srvx.request`, parameterized routes, and
middleware spans. It exposes `sentry-trace` and `baggage` through
`Server-Timing`, enabling browser pageload traces to link to the server trace.

## TanStack Start

The beta `@sentry/tanstackstart-react` SDK targets TanStack Start 1.0 RC.
Import a client initializer first in `src/client.tsx`. Add
`tanstackRouterBrowserTracingIntegration(router)` only when
`!router.isServer`, put `sentryTanstackStart()` last in the Vite plugin list,
and wrap an explicit server entry's fetch handler with `wrapFetchWithSentry`.

```ts
export default defineConfig({
  plugins: [
    tanstackStart(),
    sentryTanstackStart({ org, project, authToken }),
  ],
});
```

The Vite plugin handles production source-map upload and tracing middleware.
For complete server instrumentation, preload root `instrument.server.mjs`
with `--import` and copy it into the deployed output.

Directly importing that file from `src/server.ts` is a limited fallback: it
instruments only native Node.js APIs and does not work on Cloudflare. Put
`sentryGlobalRequestMiddleware` and `sentryGlobalFunctionMiddleware` first in
their arrays to capture request and server-function errors. Capture SSR render
exceptions manually.

`sentryTanstackStart({ tunnelRoute: true })` generates an opaque same-origin
tunnel route per development session and production build and configures the
client to use it, reducing ad-blocker and firewall drops.

## Compatibility additions (10.69.0-10.70.0)

Core supports the stable MCP SDK v2. Solid and SolidStart support
`@solidjs/router` v1. Gatsby permits React 19 in its peer range. The SvelteKit
worker entry point exports `metrics`.
