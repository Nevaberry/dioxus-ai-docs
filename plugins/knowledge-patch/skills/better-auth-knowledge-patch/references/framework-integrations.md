# Framework and Runtime Integrations

## SvelteKit

The SvelteKit cookie helper no longer obtains request state implicitly (since `1.3.0`). Pass `getRequestEvent` directly; configurations that depend on build state also pass `building` as required by their helper form.

```ts
import { sveltekitCookies } from "better-auth/svelte-kit";
import { getRequestEvent } from "$app/server";

plugins: [sveltekitCookies(getRequestEvent)]
```

## TanStack Start

The React Start helper was replaced by the TanStack Start package path and helper name:

```ts
import { tanstackStartCookies } from "better-auth/tanstack-start";

plugins: [tanstackStartCookies()]
```

## Convex

`@convex-dev/better-auth` runs the auth database and endpoints in a Convex component. Put secrets in Convex environment variables; the frontend needs both `.cloud` and `.site` deployment URLs.

Create auth with the component's context-bound adapter, register it with the Convex HTTP router, and generate the schema from that config:

```sh
npx auth generate --config ./convex/betterAuth/auth.ts --output ./convex/betterAuth/schema.ts
```

```ts
const createAuthOptions = (ctx: GenericCtx<DataModel>) => ({
  baseURL: process.env.SITE_URL,
  database: authComponent.adapter(ctx),
  plugins: [convex({ authConfig })],
}) satisfies BetterAuthOptions;

const createAuth = (ctx: GenericCtx<DataModel>) =>
  betterAuth(createAuthOptions(ctx));
authComponent.registerRoutes(http, createAuth);
```

`convexBetterAuthNextJs()` supplies the Next.js proxy, token, authenticated-fetch, and SSR-preload helpers.

## Electron

`@better-auth/electron` handles system-browser OAuth, custom-protocol callbacks, code exchange, and cookie storage. Configure a matching server plugin and desktop client protocol, then call `requestAuth()`.

```ts
import { electron } from "@better-auth/electron";
import { electronClient } from "@better-auth/electron/client";

plugins: [electron()];
const client = createAuthClient({
  plugins: [electronClient({ protocol: "com.example.myapp" })],
});
await client.requestAuth();
```

The web client also needs `electronProxyClient`; its protocol, callback path, and client ID must match desktop and server configuration. Put the scheme in `trustedOrigins` as `com.example.app:/`.

Keep the auth client and cookies in the main process. Run `authClient.setupMain()` and renderer `setupRenderer()` before app readiness. On the web sign-in page, call `ensureElectronRedirect()` and forward its PKCE/state query. When a deep link fails, call `requestAuth()` before exchanging the 32-character fallback code through `authenticate`.

```ts
electronProxyClient({ protocol: { scheme: "com.example.app" } });
authClient.setupMain();
setupRenderer();
```

## Expo

Pair the server's `expo()` plugin and app-scheme trusted origin with `expoClient` backed by secure storage. Relative OAuth callbacks become deep links, while native social sign-in resolves without navigation.

```ts
const authClient = createAuthClient({
  baseURL: "https://api.example.com",
  plugins: [expoClient({ scheme: "myapp", storage: SecureStore })],
});
```

Requests outside the auth client must send `authClient.getCookie()` explicitly and set `credentials: "omit"`:

```ts
await fetch("https://api.example.com/private", {
  headers: { Cookie: authClient.getCookie() },
  credentials: "omit",
});
```

Development-only `exp://` wildcard origins must not be used in production. Projects using `useSession` polling must install `expo-network`:

```sh
npx expo install expo-network
```

## Express

Express 4 uses `/api/auth/*`; Express 5 requires a named wildcard such as `/api/auth/*splat`. Mount `toNodeHandler(auth)` before `express.json()`. Pre-parsing an auth request can leave client calls permanently pending.

```ts
app.all("/api/auth/*splat", toNodeHandler(auth));
app.use(express.json());
```

## Encore

Mount Better Auth as an exposed `api.raw()` catch-all bridged by `toNodeHandler`. For protected endpoints, a gateway `authHandler` reconstructs Web `Headers` from typed `Authorization` and `Cookie` headers, calls `auth.api.getSession()`, and exposes the identity through `getAuthData()`.

```ts
export const authEndpoint = api.raw(
  { expose: true, path: "/api/auth/*path", method: "*" },
  toNodeHandler(auth),
);
```

## Lynx

Use the dedicated `better-auth/lynx` client, not the React client. It exposes reactive session state through `useSession()` and `$store.session`; pass selective keys for narrower rerenders.

```ts
import { createAuthClient } from "better-auth/lynx";

const authClient = createAuthClient({ baseURL: "https://api.example.com" });
const session = useStore(authClient.$store.session, {
  keys: ["user.name", "user.email"],
});
```

## NestJS

The community `@thallesp/nestjs-better-auth` module requires Nest's body parser to be disabled and installs its auth guard globally. Routes are protected unless marked `@AllowAnonymous()`; `@OptionalAuth()` permits no session, and `@Session()` injects one when present.

```ts
const app = await NestFactory.create(AppModule, { bodyParser: false });

@Module({ imports: [AuthModule.forRoot({ auth })] })
class AppModule {}
```

## Next.js

Direct `auth.api` sign-in or sign-up calls in Server Actions do not set browser cookies unless `nextCookies()` is the final auth plugin.

```ts
export const auth = betterAuth({
  plugins: [otherPlugin(), nextCookies()],
});
```

In Next.js 16, protection middleware moves to `proxy.ts`. Cookie helpers support optimistic redirects only; protected pages and actions must validate the complete server session.

## Waku

Waku Server Actions do not propagate cookies returned by direct `auth.api` calls. Add a final after-hook that stores `Set-Cookie` in request context, then have middleware append it after `next()`.

```ts
const wakuCookies = () => ({
  id: "waku-cookies",
  hooks: { after: [{
    matcher: () => true,
    handler: createAuthMiddleware(async (ctx) => {
      if ("_flag" in ctx && ctx._flag === "router") return;
      const headers = ctx.context.responseHeaders;
      if (headers instanceof Headers) {
        getContextData().betterAuthSetCookie = headers.get("set-cookie");
      }
    }),
  }] },
}) satisfies BetterAuthPlugin;

await next();
const cookie = getContextData().betterAuthSetCookie;
if (cookie) c.header("set-cookie", cookie, { append: true });
```

Middleware must not redirect Waku's `.txt` React Server Component requests. `getSessionCookie()` checks only for cookie existence and is not authorization.

## Cloudflare Workers

Enable AsyncLocalStorage through `nodejs_compat` with compatibility date `2024-09-23`, or use the narrower `nodejs_als` flag. The CLI supports Workers virtual-module imports.

```toml
compatibility_flags = ["nodejs_compat"]
compatibility_date = "2024-09-23"
```
