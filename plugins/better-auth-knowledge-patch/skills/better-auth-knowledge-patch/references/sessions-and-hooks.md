# Sessions, Hooks & Background Tasks

## Cookie Cache Strategies

Three encoding strategies for session cookie cache:

```ts
export const auth = betterAuth({
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
      strategy: "compact", // default, smallest size, base64url+HMAC-SHA256
      // strategy: "jwt",  // standard JWT (HS256), interoperable, readable
      // strategy: "jwe",  // encrypted (A256CBC-HS512), largest, most secure
    },
  },
});
// Bypass cache for sensitive operations:
await authClient.getSession({ query: { disableCookieCache: true } });
```

## Stateless Session Management

Run without a database — most plugins still require one:

```ts
export const auth = betterAuth({
  // No database config → auto-enables stateless mode. Or configure manually:
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 7 * 24 * 60 * 60,
      strategy: "jwe",
      refreshCache: true, // auto-refresh at 80% of maxAge without DB query
      // refreshCache: { updateAge: 60 }, // custom: refresh when 60s remain
      version: "2", // change to invalidate all stateless sessions on redeploy
    },
    deferSessionRefresh: true, // GET becomes read-only (returns needsRefresh: true), client auto-POSTs to refresh — useful for read-replica DB setups
  },
  account: { storeStateStrategy: "cookie", storeAccountCookie: true },
});
```

## customSession Plugin

```ts
import { customSession, customSessionClient } from "better-auth/plugins";
export const auth = betterAuth({
  plugins: [
    customSession(async ({ user, session }, ctx) => {
      const roles = await findRoles(session.userId);
      return { roles, user: { ...user, displayName: user.name.toUpperCase() }, session };
    }),
    // To infer plugin-added fields, extract options first:
    // customSession(callback, options) — pass BetterAuthOptions as 2nd arg
    // 3rd arg: { shouldMutateListDeviceSessionsEndpoint: true }
  ],
});
// Client:
const authClient = createAuthClient({ plugins: [customSessionClient<typeof auth>()] });
```

Caveat: session caching (cookie/secondary) does NOT include custom fields — the function runs every fetch.

## Update Session Endpoint

New `/update-session` endpoint for updating custom additional session fields on the fly:

```ts
await authClient.updateSession({
  theme: "dark",
  language: "en",
});
```

## Hooks with createAuthMiddleware

Before/after hooks for customizing endpoint behavior without writing a plugin:

```ts
import { createAuthMiddleware } from "better-auth"; // or "better-auth/api"
export const auth = betterAuth({
  hooks: {
    before: createAuthMiddleware(async (ctx) => {
      // ctx.path, ctx.body, ctx.headers, ctx.query, ctx.request
      // Return early: throw new APIError("BAD_REQUEST", { message: "..." })
      // Redirect: throw ctx.redirect("/somewhere")
      // JSON response: return ctx.json({ message: "..." })
      // Modify context: return { context: { ...ctx, body: { ...ctx.body, name: "Modified" } } }
    }),
    after: createAuthMiddleware(async (ctx) => {
      // ctx.context.newSession — newly created session (after hooks only)
      // ctx.context.returned — response from the endpoint
      // ctx.context.responseHeaders — headers set by prior hooks
      // ctx.context.authCookies.sessionToken.name — predefined cookie names
      // ctx.context.secret, ctx.context.password.hash/verify
      // ctx.context.runInBackground(promise) — fire-and-forget after response
      // ctx.context.runInBackgroundOrAwait(promise) — defers if handler configured
      // ctx.setCookie / ctx.getCookie / ctx.setSignedCookie / ctx.getSignedCookie
    }),
  },
});
```

## Database Hooks (databaseHooks)

Separate from endpoint hooks — run on DB operations for user/session/account:

```ts
export const auth = betterAuth({
  databaseHooks: {
    user: {
      create: {
        before: async (user, ctx) => {
          // Return { data: modifiedUser } to modify, return false to abort
          // Throw APIError to abort with error
          return { data: { ...user, firstName: user.name.split(" ")[0] } };
        },
        after: async (user) => { /* e.g. create Stripe customer */ },
      },
      update: {
        before: async (data, ctx) => {
          // ctx.context.session available in update hooks
          return { data };
        },
      },
      delete: {
        before: async (user, ctx) => false, // return false to abort deletion
        after: async (user) => { /* cleanup */ },
      },
    },
    session: { delete: { before: async (session) => true } },
    account: { create: { before: (account) => {
      // Token encryption pattern:
      if (account.accessToken) account.accessToken = encrypt(account.accessToken);
      return { data: account };
    }}},
  },
});
```

## Secondary Storage (Redis)

```ts
import { redisStorage } from "@better-auth/redis-storage";
export const auth = betterAuth({
  secondaryStorage: redisStorage({ client: new Redis(), keyPrefix: "better-auth:" }),
  session: {
    storeSessionInDatabase: true, // keep sessions in DB even with secondary storage
    preserveSessionInDatabase: true, // don't delete revoked sessions from DB
  },
});
```

Interface: `{ get(key): Promise<unknown>, set(key, value, ttl?): Promise<void>, delete(key): Promise<void> }`

## Background Tasks for Serverless

Defer non-critical work to run after the response:

```ts
export const auth = betterAuth({
  advanced: {
    backgroundTasks: { handler: waitUntil }, // platform's waitUntil function
  },
  hooks: {
    after: createAuthMiddleware(async (ctx) => {
      if (ctx.path === "/sign-up/email") {
        ctx.context.runInBackground(logSignUp(ctx.context.newSession?.user.id));
        // or ctx.context.runInBackgroundOrAwait() — awaits if no handler configured
      }
    }),
  },
});
```
