# AuthKit for Next.js

## App Router setup

`@workos-inc/authkit-nextjs` targets the App Router. Configure a client ID, API
key, public redirect URI, and session-cookie password of at least 32 characters.
Implement the callback as a route handler:

```ts
// app/callback/route.ts
import { handleAuth } from '@workos-inc/authkit-nextjs';

export const GET = handleAuth({ returnPathname: '/dashboard' });
```

Configure a default Logout URI in the dashboard before using sign-out.

## Session cookie configuration

The session cookie defaults to `wos-session`, `SameSite=Lax`, and a 400-day
maximum age. Override these with `WORKOS_COOKIE_NAME`, `WORKOS_COOKIE_MAX_AGE`,
`WORKOS_COOKIE_DOMAIN`, and `WORKOS_COOKIE_SAMESITE`.

`SameSite=None` forces a secure cookie. Apps sharing a session through
`WORKOS_COOKIE_DOMAIN` must also use the same cookie password.

## Callback data and deployment overrides

`handleAuth` accepts `returnPathname`, `baseURL`, `onSuccess`, and `onError`.
Successful callbacks receive the user, access and refresh tokens, impersonator,
upstream OAuth tokens, organization ID, authentication method, and opaque string
`state`. `authenticationMethod` is present only on initial login.

Use `baseURL` when a container sees an internal host instead of the public host.
For dynamic deployments, a proxy or middleware `redirectUri` overrides the
environment value.

## Next.js request hook

Next.js 16 and newer uses a root-level `proxy.ts` with `authkitProxy`. Next.js
15 and earlier uses `middleware.ts` with `authkitMiddleware`.

```ts
import { authkitProxy } from '@workos-inc/authkit-nextjs';

export default authkitProxy();
export const config = { matcher: ['/', '/admin/:path*'] };
```

Broad matchers must exclude `/_next/static`, `/_next/image`, `favicon.ico`, and
other static assets.

## Composable proxy responses

For custom logic, `authkit(request)` returns `session`, internal `headers`, and
`authorizationUrl`. Pass every response through
`handleAuthkitHeaders(request, headers, options)`. The helper:

- propagates server authentication data without exposing internal headers;
- normalizes relative redirects;
- uses status 303 for POST and PUT redirects;
- strips injected `x-workos-*` values; and
- safely merges cookie and cache headers.

For rewrites, partition headers with `partitionAuthkitHeaders` and apply response
headers with `applyResponseHeaders`. Authenticated contexts receive private and
no-cache directives, while public requests retain normal caching.

## Route protection

Set `middlewareAuth.enabled` to authenticate every matched route except
`unauthenticatedPaths`, whose values use Next.js matcher-style globs.
`signUpPaths` independently marks protected paths that should redirect with the
sign-up screen hint.

```ts
import { authkitProxy } from '@workos-inc/authkit-nextjs';

export default authkitProxy({
  middlewareAuth: { enabled: true, unauthenticatedPaths: ['/', '/about'] },
  signUpPaths: ['/account/sign-up'],
});
```

## Server and client auth surfaces

Use `withAuth()` in server components. Client components import
`AuthKitProvider` and `useAuth` from
`@workos-inc/authkit-nextjs/components`. Both readers accept
`ensureSignedIn: true`; `withAuth()` also returns the access token and active
feature flags.

When passing server-provided `initialAuth` into `AuthKitProvider`, remove the
access token first.

## Session refresh and access tokens

`refreshSession` updates server-side user, role, and permission data and can
switch organizations. On the client, use `refreshAuth({ organizationId })`.
`useAccessToken` refreshes before expiry, supports manual refresh with loading
and error state, and stays synchronized with `refreshAuth`.

Direct `authkit` calls can observe refreshes with
`onSessionRefreshSuccess` and `onSessionRefreshError`.

## Eager client authentication

`eagerAuth: true` makes an access token available on the initial client render
by placing it in a 30-second cookie only for initial page loads—not API or
prefetch requests. Client JavaScript consumes and deletes the cookie. Use
`useAccessToken().getAccessToken()` for services that cannot wait for normal
asynchronous token retrieval, and account for the brief JavaScript exposure
with normal XSS protections.

## API-key validation and custom sessions

`validateApiKey()` parses the Bearer header and validates an AuthKit API key for
public endpoints. For custom or self-hosted authentication, call
`saveSession(session, requestOrUrl)` after direct User Management authentication
to store the access token, refresh token, user, and optional impersonator in the
encrypted session cookie.

## PKCE and CSRF state

AuthKit Next.js v3 always uses PKCE and sealed OAuth state. Remove
`WORKOS_ENABLE_PKCE`. Preserve the short-lived `wos-auth-verifier` cookie and
require it to match callback `state`; the URL-state-only fallback no longer
exists. A missing verifier fails with `Auth cookie missing`, and a mismatch
fails with `OAuth state mismatch`.
