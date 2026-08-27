# Framework and Runtime Integrations

## Convex

`@convex-dev/better-auth` runs the auth database and endpoints inside Convex. Put secrets in Convex environment variables; the frontend needs both the `.cloud` and `.site` deployment URLs. Build auth with the component's context-bound adapter, register it on the Convex HTTP router, and generate its schema with:

```sh
npx auth generate --config ./convex/betterAuth/auth.ts --output ./convex/betterAuth/schema.ts
```

`convexBetterAuthNextJs()` supplies Next.js proxy, token, authenticated-fetch, and SSR-preload helpers.

## Electron

`@better-auth/electron` supplies the system-browser OAuth flow, custom-protocol callback, code exchange, and cookie storage (since 1.5-guide). Configure matching protocol values on the server plugin, desktop client, and `electronProxyClient`; include the callback path, client ID, and a trusted origin such as `com.example.app:/`.

Keep the auth client and cookies in the main process. Run `authClient.setupMain()` and renderer `setupRenderer()` before app readiness. On the web sign-in page, call `ensureElectronRedirect()` while forwarding PKCE/state parameters. After a failed deep link, call `requestAuth()` before passing the 32-character fallback code to `authenticate`.

## Expo

Pair the server `expo()` plugin and app-scheme trusted origin with `expoClient` backed by secure storage. Relative OAuth callbacks become deep links; native social sign-in resolves without navigating. Requests outside the auth client must send `getCookie()` explicitly with `credentials: "omit"`. Development `exp://` wildcard origins are unsafe for production.

```ts
await fetch("https://api.example.com/private", {
  headers: { Cookie: authClient.getCookie() },
  credentials: "omit",
});
```

Projects using `useSession` network polling must install `expo-network` (since 1.4.0).

## Express

Express 4 uses `/api/auth/*`; Express 5 needs a named wildcard such as `/api/auth/*splat`. Mount `toNodeHandler(auth)` before `express.json()`; pre-parsing auth requests can leave client calls pending indefinitely.

```ts
app.all("/api/auth/*splat", toNodeHandler(auth));
app.use(express.json());
```

## Encore

Mount Better Auth in an exposed `api.raw()` catch-all bridged by `toNodeHandler`. Protected endpoints use a gateway `authHandler` that rebuilds Web `Headers` from typed Authorization/Cookie headers, calls `auth.api.getSession()`, and exposes identity through `getAuthData()`.

## Lynx

Use the dedicated `better-auth/lynx` client. It provides `useSession()` and the `$store.session` nanostore, including selective key watching for narrower rerenders.

```ts
const session = useStore(authClient.$store.session, {
  keys: ["user.name", "user.email"],
});
```

## NestJS

The community `@thallesp/nestjs-better-auth` module requires Nest's body parser to be disabled and registers a global guard. Routes are protected unless decorated with `@AllowAnonymous()`; `@OptionalAuth()` allows a missing session, and `@Session()` injects the session.

## Next.js

When Server Actions directly invoke sign-in/sign-up through `auth.api`, place `nextCookies()` last or returned cookies will not reach the browser. Next.js 16 moves protection middleware to `proxy.ts`. Cookie helpers support optimistic redirects only; protected pages/actions must validate the full server session.

## SvelteKit and TanStack Start

The SvelteKit helper requires `getRequestEvent` as an explicit argument (breaking since 1.3.0):

```ts
import { sveltekitCookies } from "better-auth/svelte-kit";
import { getRequestEvent } from "$app/server";

plugins: [sveltekitCookies(getRequestEvent)]
```

React Start's old helper was replaced by:

```ts
import { tanstackStartCookies } from "better-auth/tanstack-start";
plugins: [tanstackStartCookies()]
```

## Cloudflare Workers

Enable AsyncLocalStorage with `nodejs_compat` and compatibility date `2024-09-23`, or with `nodejs_als`, before constructing auth. The CLI supports Workers virtual-module imports.

## Waku

Direct `auth.api` calls in Waku Server Actions do not propagate response cookies. Put a final custom after-hook on auth to save `Set-Cookie` in request context, then append it in Waku middleware after `next()`. Ignore router-internal hook invocations, append rather than overwrite multiple cookies, and never redirect Waku's `.txt` React Server Component requests. `getSessionCookie()` is an existence check, not authorization.
