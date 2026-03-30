# Plugin Creation API

## Server Plugin

Full server plugin with `createAuthEndpoint`, schema, hooks, middleware, rate limits:

```ts
import { createAuthEndpoint, createAuthMiddleware, sessionMiddleware, getSessionFromCtx } from "better-auth";
const myPlugin = (opts) => ({
  id: "my-plugin",
  endpoints: {
    getHello: createAuthEndpoint("/my-plugin/hello", {
      method: "GET",
      use: [sessionMiddleware], // requires valid session, adds ctx.context.session
    }, async (ctx) => {
      // ctx.context gives: options, db, adapter, internalAdapter, baseURL,
      //   secret, tables, session config, authCookie, logger, trustedOrigins,
      //   isTrustedOrigin(url, { allowRelativePaths }), createAuthCookie, generateId
      return ctx.json({ user: ctx.context.session.user.name });
    }),
  },
  schema: {
    myTable: { fields: { name: { type: "string" } } },
    user: { fields: { age: { type: "number" } } }, // extends user table, auto-inferred in types
  },
  hooks: {
    before: [{ matcher: (c) => c.path === "/sign-up/email", handler: createAuthMiddleware(async (ctx) => { /* ... */ }) }],
  },
  middlewares: [{ path: "/my-plugin/*", middleware: createAuthMiddleware(async (ctx) => { /* runs on API requests only, not direct server calls */ }) }],
  onRequest: async (request, context) => { /* return { response } to interrupt or { request } to modify */ },
  onResponse: async (response, context) => { /* return modified response */ },
  rateLimit: [{ pathMatcher: (p) => p === "/my-plugin/hello", limit: 10, window: 60 }],
  trustedOrigins: ["http://trusted.com"],
}) satisfies BetterAuthPlugin;
```

## Client Plugin

With type inference from server:

```ts
import type { BetterAuthClientPlugin, BetterFetchOption } from "better-auth";
const myPluginClient = () => ({
  id: "my-plugin",
  $InferServerPlugin: {} as ReturnType<typeof myPlugin>, // infers endpoints, paths auto-converted from kebab-case
  getActions: ($fetch) => ({
    customAction: async (data: { foo: string }, fetchOptions?: BetterFetchOption) =>
      $fetch("/custom/action", { method: "POST", body: { foo: data.foo }, ...fetchOptions }),
  }),
  getAtoms: ($fetch) => ({ myAtom: atom<null>() }), // nanostores atoms for reactive hooks
  pathMethods: { "/my-plugin/hello": "POST" }, // override inferred HTTP method
}) satisfies BetterAuthClientPlugin;
```

## v1.5 Plugin Type System

`BetterAuthPluginRegistry` for typed `getPlugin()` / `hasPlugin()`:

```ts
declare module "@better-auth/core" {
  interface BetterAuthPluginRegistry<AuthOptions, Options> {
    "my-plugin": { creator: typeof myPlugin };
  }
}
// Usage in plugin context:
const otherPlugin = ctx.getPlugin("my-plugin"); // typed return
const hasIt = ctx.hasPlugin("my-plugin"); // narrows to true
```

After hooks (`create.after`, `update.after`, `delete.after`) now run **after** transaction commits, not during. Plugin `init()` context is mutable and can inject custom values via `Record<string, unknown>` return.
