# Framework Integrations

## Next.js: nextCookies Plugin

Server actions can't set cookies natively. The `nextCookies` plugin auto-sets cookies:

```ts
import { nextCookies } from "better-auth/next-js";
export const auth = betterAuth({
  plugins: [nextCookies()], // MUST be last plugin in array
});

// Now server actions can call auth.api directly:
"use server";
const signIn = async () => {
  await auth.api.signInEmail({
    body: { email: "user@email.com", password: "password" },
  });
};
```

## Next.js 16 Proxy (Replaces Middleware)

Next.js 16 renames "middleware" to "proxy". Rename `middleware.ts` → `proxy.ts`, function `middleware` → `proxy`:

```ts
// proxy.ts (Next.js 16+)
import { getSessionCookie, getCookieCache } from "better-auth/cookies";
export async function proxy(request: NextRequest) {
  const sessionCookie = getSessionCookie(request);
  const session = await getCookieCache(request);
  if (!sessionCookie) {
    return NextResponse.redirect(new URL("/sign-in", request.url));
  }
  return NextResponse.next();
}
export const config = { matcher: ["/dashboard"] };
```

Migration codemod: `npx @next/codemod@canary middleware-to-proxy .`

## getSessionCookie & getCookieCache Helpers

For middleware/proxy cookie checks without DB calls:

```ts
import { getSessionCookie, getCookieCache } from "better-auth/cookies";

// Cookie existence only (not secure, for optimistic redirects):
const sessionCookie = getSessionCookie(request);
// With custom name/prefix:
const sessionCookie = getSessionCookie(request, {
  cookieName: "my_session_cookie",
  cookiePrefix: "my_prefix",
});

// Decode cached session from cookie (validates HMAC signature):
const session = await getCookieCache(request);
```

## SvelteKit

### Handler

`svelteKitHandler` requires the `building` param from `$app/environment`:

```ts
import { svelteKitHandler } from "better-auth/svelte-kit";
import { building } from '$app/environment';

export async function handle({ event, resolve }) {
  return svelteKitHandler({ event, resolve, auth, building });
}
```

### sveltekitCookies Plugin (SvelteKit 2.20.0+)

Auto-sets cookies in form actions and server functions:

```ts
import { sveltekitCookies } from "better-auth/svelte-kit";
import { getRequestEvent } from "$app/server";
export const auth = betterAuth({
  plugins: [sveltekitCookies(getRequestEvent)], // MUST be last plugin
});
```

## TanStack Start

Requires a special cookie plugin:

```ts
import { tanstackStartCookies } from "better-auth/tanstack-start";
// For Solid: "better-auth/tanstack-start/solid"
export const auth = betterAuth({
  plugins: [tanstackStartCookies()] // must be LAST plugin in array
});
```

## Expo

### getCookie for Manual Requests

```ts
const cookies = authClient.getCookie();
const response = await fetch("http://localhost:8081/api/data", {
  headers: { Cookie: cookies },
  credentials: "omit",
});
```

### Native idToken Sign-In

Google, Apple, Facebook only — verify provider token server-side:

```ts
await authClient.signIn.social({
  provider: "google",
  idToken: { token: "...", nonce: "..." },
  callbackURL: "/dashboard",
});
```

### cookiePrefix

Accepts an array for multi-system setups:

```ts
expoClient({ storage: SecureStore, cookiePrefix: ["better-auth", "my-app"] })
```

## Express v5

Changed wildcard syntax — use `/{*any}` instead of `/*`:

```ts
app.all('/api/auth/{*any}', toNodeHandler(auth));
```

## Expo API Route

```ts
// app/api/auth/[...all]+api.ts
import { auth } from '@/lib/server/auth';
const handler = auth.handler;
export { handler as GET, handler as POST };
```

## fromNodeHeaders Utility

Converts Node.js `IncomingHttpHeaders` to web `Headers`:

```ts
import { fromNodeHeaders } from "better-auth/node";
app.get("/api/me", async (req, res) => {
  const session = await auth.api.getSession({
    headers: fromNodeHeaders(req.headers),
  });
  return res.json(session);
});
```

## Elysia: mount + macro Pattern

```ts
const betterAuthPlugin = new Elysia({ name: "better-auth" })
  .mount(auth.handler)
  .macro({
    auth: {
      async resolve({ status, request: { headers } }) {
        const session = await auth.api.getSession({ headers });
        if (!session) return status(401);
        return { user: session.user, session: session.session };
      },
    },
  });

const app = new Elysia()
  .use(betterAuthPlugin)
  .get("/user", ({ user }) => user, { auth: true })
  .listen(3000);
```

## NestJS: @thallesp/nestjs-better-auth

```ts
// main.ts — disable body parser (required)
const app = await NestFactory.create(AppModule, { bodyParser: false });

// app.module.ts
@Module({ imports: [AuthModule.forRoot({ auth })] })
export class AppModule {}

// controllers — AuthGuard is global by default
@Controller("users")
export class UserController {
  @Get("me")
  getProfile(@Session() session: UserSession) { return session.user; }

  @Get("public")
  @AllowAnonymous()
  getPublic() { return { message: "public" }; }

  @Get("optional")
  @OptionalAuth()
  getOptional(@Session() session: UserSession) { return { authenticated: !!session }; }
}
```

## Encore

```ts
export const authHandler = api.raw(
  { expose: true, path: "/api/auth/*path", method: "*" },
  toNodeHandler(auth),
);

const handler = authHandler(async (params: AuthParams): Promise<AuthData> => {
  const headers = new Headers();
  if (params.cookie) headers.set("Cookie", params.cookie);
  const session = await auth.api.getSession({ headers });
  if (!session?.user) throw APIError.unauthenticated("invalid session");
  return { userID: session.user.id, email: session.user.email };
});
export const gateway = new Gateway({ authHandler: handler });
```

## Convex

Community-maintained `@convex-dev/better-auth`. Better Auth runs inside Convex functions:

```ts
// convex/betterAuth/auth.ts
import { createClient } from "@convex-dev/better-auth";
export const authComponent = createClient<DataModel, typeof schema>(
  components.betterAuth,
  { local: { schema }, verbose: false },
);
export const createAuthOptions = (ctx: GenericCtx<DataModel>) => ({
  baseURL: process.env.SITE_URL,
  secret: process.env.BETTER_AUTH_SECRET,
  database: authComponent.adapter(ctx),
  plugins: [convex({ authConfig })],
});

// convex/http.ts
authComponent.registerRoutes(http, createAuth);

// lib/auth-server.ts — Next.js helpers
import { convexBetterAuthNextJs } from "@convex-dev/better-auth/nextjs";
export const { handler, preloadAuthQuery, isAuthenticated, getToken } =
  convexBetterAuthNextJs({
    convexUrl: process.env.NEXT_PUBLIC_CONVEX_URL!,
    convexSiteUrl: process.env.NEXT_PUBLIC_CONVEX_SITE_URL!,
  });

// Schema generation: npx auth generate --config ./convex/betterAuth/auth.ts --output ./convex/betterAuth/schema.ts
```

## Electron (`@better-auth/electron`)

Three-part architecture: server plugin, web proxy client, Electron client. Uses PKCE + deep links:

```ts
// Server
import { electron } from "@better-auth/electron";
export const auth = betterAuth({
  plugins: [electron()],
  trustedOrigins: ["com.example.app:/"],
});

// Web client: proxy plugin redirects back to Electron app
import { electronProxyClient } from "@better-auth/electron/proxy";
const authClient = createAuthClient({
  plugins: [electronProxyClient({ protocol: { scheme: "com.example.app" } })],
});

// Electron main process client
import { electronClient } from "@better-auth/electron/client";
const authClient = createAuthClient({
  plugins: [electronClient({
    signInURL: "https://app.example.com/sign-in",
    protocol: { scheme: "com.example.app" },
    storage: storage(), // from @better-auth/electron/storage
  })],
});

// Main process setup (before app ready):
authClient.setupMain();

// Preload script:
import { setupRenderer } from "@better-auth/electron/preload";
setupRenderer();

// Renderer process:
window.requestAuth();
window.requestAuth({ provider: "google" });
window.onAuthenticated((user) => { /* ... */ });
window.signOut();
```

Type inference for IPC bridges:

```ts
declare global {
  type Bridges = typeof authClient.$Infer.Bridges;
  interface Window extends Bridges {}
}
```

## Lynx Client

Cross-platform framework client with nanostores and selective key watching:

```ts
import { createAuthClient } from "better-auth/lynx";
const authClient = createAuthClient({ baseURL: "http://localhost:3000" });

const session = useStore(authClient.$store.session, {
  keys: ["user.name", "user.email"],
});
```

## Waku: Custom wakuCookies Plugin

Waku needs a manual cookie plugin using `getContextData()`:

```ts
import { getContextData, getContext } from "waku/server";

function wakuCookies() {
  return {
    id: "waku-cookies",
    hooks: {
      after: [{
        matcher: () => true,
        handler: createAuthMiddleware(async (ctx) => {
          const setCookie = ctx.context.responseHeaders?.get("set-cookie");
          if (setCookie) {
            getContextData().betterAuthSetCookie = setCookie;
          }
        }),
      }],
    },
  } satisfies BetterAuthPlugin;
}

// Session dedup per request:
export function getSession(): Promise<Session | null> {
  const contextData = getContextData();
  if (contextData.sessionPromise) return contextData.sessionPromise;
  const promise = auth.api.getSession({ headers: new Headers(getContext().req.headers) });
  contextData.sessionPromise = promise;
  return promise;
}
```
