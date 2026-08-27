# Framework and Runtime Integrations

## SvelteKit

The SvelteKit cookie helper no longer obtains build/request state implicitly. Pass `getRequestEvent` directly (the `building` value is also an explicit helper input where required).

```ts
import { sveltekitCookies } from "better-auth/svelte-kit";
import { getRequestEvent } from "$app/server";

plugins: [sveltekitCookies(getRequestEvent)]
```

## TanStack Start

Use the TanStack Start path and helper in place of the old React Start helper.

```ts
import { tanstackStartCookies } from "better-auth/tanstack-start";

plugins: [tanstackStartCookies()]
```

## Cloudflare Workers

Enable AsyncLocalStorage before constructing auth. Use `nodejs_compat` with compatibility date `2024-09-23` or the narrower `nodejs_als` flag. CLI schema/config loading understands Workers virtual-module imports.

```toml
compatibility_flags = ["nodejs_compat"]
compatibility_date = "2024-09-23"
```

## Convex

`@convex-dev/better-auth` runs the auth database and endpoints in a Convex component. Store secrets in Convex environment variables; the frontend needs both `.cloud` and `.site` deployment URLs. Build the auth factory with the context-bound component adapter, register it with the Convex HTTP router, and generate the schema from that config.

```sh
npx auth generate --config ./convex/betterAuth/auth.ts \
  --output ./convex/betterAuth/schema.ts
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

For Next.js, `convexBetterAuthNextJs()` provides proxy, token, authenticated-fetch, and SSR-preload helpers.

## Electron

`@better-auth/electron` coordinates the system-browser OAuth flow, custom-protocol callback, code exchange, and cookie storage. Configure the server plugin and an `electronClient` with the same protocol, then start with `requestAuth()`.

```ts
plugins: [electron()];

const client = createAuthClient({
  plugins: [electronClient({ protocol: "com.example.myapp" })],
});
await client.requestAuth();
```

The web side also needs `electronProxyClient`. Protocol, callback path, and client ID must match the server and desktop clients; put the scheme in `trustedOrigins` as `com.example.app:/`. Keep auth state and cookies in the main process. Call `setupMain()` and `setupRenderer()` before app readiness.

On the web sign-in page call `ensureElectronRedirect()` and preserve its PKCE/state query. For failed deep links, call `requestAuth()` before exchanging the 32-character fallback code with `authenticate`.

```ts
electronProxyClient({ protocol: { scheme: "com.example.app" } });
authClient.setupMain();
setupRenderer();
```

## Expo

Pair the server `expo()` plugin and app-scheme trusted origin with `expoClient` backed by secure storage. Relative OAuth callbacks become deep links, while native social sign-in resolves without navigation. Install `expo-network` for `useSession` polling behavior.

```sh
npx expo install expo-network
```

Requests made outside the auth client must send `getCookie()` manually and set `credentials: "omit"`. Development-only `exp://` wildcard origins are not appropriate in production.

```ts
const authClient = createAuthClient({
  baseURL: "https://api.example.com",
  plugins: [expoClient({ scheme: "myapp", storage: SecureStore })],
});

await fetch("https://api.example.com/private", {
  headers: { Cookie: authClient.getCookie() },
  credentials: "omit",
});
```

## Express

Express 4 uses `/api/auth/*`; Express 5 requires a named wildcard such as `/api/auth/*splat`. Mount `toNodeHandler(auth)` before `express.json()`. Pre-parsing auth requests can leave client calls pending forever.

```ts
app.all("/api/auth/*splat", toNodeHandler(auth));
app.use(express.json());
```

## Encore

Mount Better Auth through an exposed `api.raw()` catch-all bridged by `toNodeHandler`. For protected endpoints, a gateway `authHandler` should reconstruct Web `Headers` from typed `Authorization` and `Cookie` inputs, call `auth.api.getSession()`, and expose the identity through `getAuthData()`.

```ts
export const authEndpoint = api.raw(
  { expose: true, path: "/api/auth/*path", method: "*" },
  toNodeHandler(auth),
);
```

## Lynx

Use the dedicated `better-auth/lynx` client. It provides `useSession()` and a nanostore at `$store.session`; watch selected keys to reduce rerenders.

```ts
import { createAuthClient } from "better-auth/lynx";

const authClient = createAuthClient({ baseURL: "https://api.example.com" });
const session = useStore(authClient.$store.session, {
  keys: ["user.name", "user.email"],
});
```

## NestJS

The community `@thallesp/nestjs-better-auth` module requires Nest's body parser to be disabled and installs a global auth guard. Routes are protected by default. Mark public routes with `@AllowAnonymous()`, permit a missing session with `@OptionalAuth()`, and inject a present session with `@Session()`.

```ts
const app = await NestFactory.create(AppModule, { bodyParser: false });

@Module({ imports: [AuthModule.forRoot({ auth })] })
class AppModule {}
```

## Next.js

Direct `auth.api` sign-in/sign-up calls in Server Actions set browser cookies only when `nextCookies()` is the last plugin.

```ts
export const auth = betterAuth({
  plugins: [otherPlugin(), nextCookies()],
});
```

Next.js 16 protection middleware belongs in `proxy.ts`. Cookie-presence helpers support optimistic redirects only; protected pages and actions must validate the full server session.

## Waku

Waku Server Actions do not propagate cookies from direct `auth.api` calls. A final custom after-hook must save `Set-Cookie` into request context, and outer middleware must append it after `next()`. Do not redirect Waku's `.txt` React Server Component requests. `getSessionCookie()` checks existence only and is not authorization.

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
