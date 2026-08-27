# Modern server framework integrations

## Request data-collection controls

The `modern-server-frameworks` Elysia, Hono, Nitro, and TanStack Start SDKs
accept `dataCollection` options for automatic request enrichment. Explicitly
disable default user information and all HTTP request bodies when they must not
leave the application:

```js
Sentry.init({
  dataCollection: { userInfo: false, httpBodies: [] },
});
```

## Elysia

The alpha `@sentry/elysia` SDK supports Elysia 1.4+ on Bun and Node.js 18+
through `@elysiajs/node`. It instruments Elysia natively without
`@elysiajs/opentelemetry`.

Initialize Sentry before constructing the application and wrap the application
before adding routes. The global error hook captures 5xx responses by default;
`shouldHandleError` replaces that policy.

```ts
Sentry.init({ dsn });
const app = Sentry.withElysia(new Elysia(), {
  shouldHandleError: ({ set }) => set.status === 500 || set.status === 503,
}).get("/", () => "ok");
```

## Hono runtime packages

`@sentry/hono` supports Hono 4+ on Cloudflare Workers, Node.js, Bun, and Deno.
It replaces deprecated `@hono/sentry` and `toucan-js`.

Install the same-version runtime peer:

| Runtime | Peer package | Middleware import |
| --- | --- | --- |
| Cloudflare Workers | `@sentry/cloudflare` | `@sentry/hono/cloudflare` |
| Node.js | `@sentry/node` | `@sentry/hono/node` |
| Bun | `@sentry/bun` | `@sentry/hono/bun` |
| Deno | `@sentry/deno` | `@sentry/hono/deno` |

Add the middleware early. Cloudflare additionally requires `nodejs_compat` and
can derive SDK options from Worker bindings:

```ts
import { sentry } from "@sentry/hono/cloudflare";

const app = new Hono<{ Bindings: { SENTRY_DSN: string } }>();
app.use(sentry(app, env => ({ dsn: env.SENTRY_DSN })));
```

On Node.js, preload a file that imports and initializes `@sentry/hono/node`,
then call `app.use(sentry(app))` without options. The middleware captures
exceptions reaching Hono's `onError`, excluding 3xx and 4xx errors by default.
Use `shouldHandleError` to customize selection.

## Nitro build setup

The beta `@sentry/nitro` SDK requires Nitro `3.0.260415-beta` or newer and
Node.js 18.19+. Wrap the Nitro config with `withSentryConfig`, initialize Sentry
in a root `instrument.mjs`, and preload it with `--import` for development,
preview, and production.

```ts
export default withSentryConfig(defineNitroConfig({}), {
  org: "my-org",
  project: "my-project",
  authToken: process.env.SENTRY_AUTH_TOKEN,
});
// NODE_OPTIONS='--import ./instrument.mjs' nitro dev
```

The wrapper registers the module, enables Nitro tracing channels, and by default
uploads hidden source maps before deleting them. It respects an explicit
`sourcemap` setting.

## Nitro runtime behavior

The SDK re-exports `@sentry/node`. It captures unhandled route and middleware
errors through Nitro's `error` hook and skips 3xx/4xx `HTTPError` instances. Set
`enableNitroErrorHandler: false` to disable that hook.

Request tracing uses `h3.request` and `srvx.request`, records parameterized
routes and middleware spans, and exposes `sentry-trace` and `baggage` through
`Server-Timing`, allowing browser pageload traces to link to the server trace.

## TanStack Start client and build setup

The beta `@sentry/tanstackstart-react` SDK targets TanStack Start 1.0 RC. Import
a client initializer first in `src/client.tsx`. Add
`tanstackRouterBrowserTracingIntegration(router)` only when
`!router.isServer`.

Place `sentryTanstackStart()` last in the Vite plugin list. It manages
production source-map upload and tracing middleware:

```ts
export default defineConfig({
  plugins: [
    tanstackStart(),
    sentryTanstackStart({ org, project, authToken }),
  ],
});
```

Wrap an explicit server entry fetch handler with `wrapFetchWithSentry`.

## TanStack Start server instrumentation and errors

For complete server instrumentation, preload a root `instrument.server.mjs`
with `--import` and copy it into the deployed build output. Importing it directly
from `src/server.ts` is a limited fallback: it instruments only native Node.js
APIs and does not work on Cloudflare.

Request and server-function errors require `sentryGlobalRequestMiddleware` and
`sentryGlobalFunctionMiddleware` first in their respective arrays. SSR rendering
exceptions still require manual capture.

## TanStack Start event tunneling

Set `sentryTanstackStart({ tunnelRoute: true })` to create an opaque same-origin
tunnel route for each development session and production build. The plugin
automatically configures the client to use it, avoiding common ad-blocker and
firewall drops without a hand-written route.
