# AuthKit for Next.js

Use this reference for App Router integration, cookies, callbacks, proxy or
middleware behavior, route protection, session refresh, and client token state.

## App Router setup

`@workos-inc/authkit-nextjs` targets the App Router. Configure a client ID, API
key, public redirect URI, and session-cookie password of at least 32
characters. Define the callback as a route handler:

```ts
// app/callback/route.ts
import { handleAuth } from '@workos-inc/authkit-nextjs';

export const GET = handleAuth({ returnPathname: '/dashboard' });
```

Signing out requires a default Logout URI in the WorkOS dashboard.

## Cookie configuration

The encrypted session cookie defaults to:

- name `wos-session`;
- `SameSite=Lax`; and
- a 400-day maximum age.

Override these with `WORKOS_COOKIE_NAME`, `WORKOS_COOKIE_MAX_AGE`,
`WORKOS_COOKIE_DOMAIN`, and `WORKOS_COOKIE_SAMESITE`. `SameSite=None` forces a
secure cookie. Apps sharing sessions through `WORKOS_COOKIE_DOMAIN` must also
use the same cookie password.

## Callback data and deployment overrides

`handleAuth` accepts `returnPathname`, `baseURL`, `onSuccess`, and `onError`.
Successful callbacks receive the user, access and refresh tokens, impersonator,
upstream OAuth tokens, organization ID, authentication method, and opaque
string `state`. `authenticationMethod` is present only at initial login.

Set `baseURL` when the request host visible inside a container or reverse proxy
differs from the public host. A proxy or middleware `redirectUri` option can
override the environment value for dynamic deployments.

## Next.js 16 proxy migration

Next.js 16 or newer uses root-level `proxy.ts` and `authkitProxy`. Next.js 15 or
earlier uses `middleware.ts` and `authkitMiddleware`.

```ts
import { authkitProxy } from '@workos-inc/authkit-nextjs';

export default authkitProxy();
export const config = { matcher: ['/', '/admin/:path*'] };
```

Exclude static assets such as `/_next/static`, `/_next/image`, and
`favicon.ico` from broad matchers.

## Compose custom proxy responses safely

`authkit(request)` returns `session`, internal `headers`, and
`authorizationUrl`. Pass every resulting response through
`handleAuthkitHeaders(request, headers, options)`. The helper:

- propagates server authentication state without leaking internal values;
- normalizes relative redirects;
- uses HTTP 303 for redirects after POST or PUT;
- strips injected `x-workos-*` request values; and
- merges safe cookie and cache headers.

For rewrites, partition the internal values with `partitionAuthkitHeaders`, then
apply them with `applyResponseHeaders`. Authenticated contexts receive private
or no-cache directives without disabling caching for public requests.

## Protect routes at the proxy

Enable `middlewareAuth.enabled` to require authentication for every matched
path except entries in `unauthenticatedPaths`, which uses Next.js matcher-style
globs. `signUpPaths` independently marks protected paths that should redirect
with the sign-up screen hint.

```ts
import { authkitProxy } from '@workos-inc/authkit-nextjs';

export default authkitProxy({
  middlewareAuth: { enabled: true, unauthenticatedPaths: ['/', '/about'] },
  signUpPaths: ['/account/sign-up'],
});
```

## Server and client authentication

Server components call `withAuth()`. Client components import
`AuthKitProvider` and `useAuth` from
`@workos-inc/authkit-nextjs/components`. Both auth readers accept
`ensureSignedIn: true`; `withAuth` also returns the access token and active
feature flags.

When hydrating the provider with server `initialAuth`, omit the access token so
it is not serialized into client state.

## Refresh sessions and tokens

`refreshSession` updates server-side user, role, and permission data and can
switch organization context. Client code calls
`refreshAuth({ organizationId })`. `useAccessToken` refreshes before expiry,
supports explicit refresh with loading and error state, and stays synchronized
with `refreshAuth`.

Code calling `authkit` directly can observe refreshes with
`onSessionRefreshSuccess` and `onSessionRefreshError`.

## Eager client authentication

Set `eagerAuth: true` only when the access token must exist on initial client
render. It places the token in a 30-second cookie only for initial page loads,
not API or prefetch requests. Client JavaScript immediately consumes and
deletes it. Use `useAccessToken().getAccessToken()` for services that cannot
wait for normal asynchronous token retrieval, and account for the brief
JavaScript exposure with standard XSS defenses.

## API keys and custom sessions

`validateApiKey()` parses the Bearer header and validates an AuthKit API key for
public endpoints. For a self-hosted or custom authentication flow,
`saveSession(session, requestOrUrl)` stores an access token, refresh token,
user, and optional impersonator in the encrypted cookie after direct User
Management authentication.

## PKCE and CSRF callback behavior

AuthKit Next.js v3 always uses PKCE and sealed OAuth state. Remove
`WORKOS_ENABLE_PKCE`. The short-lived `wos-auth-verifier` cookie must match the
callback `state`; the URL-state-only fallback no longer exists. A missing cookie
fails with `Auth cookie missing`, while a mismatch fails with
`OAuth state mismatch`.
