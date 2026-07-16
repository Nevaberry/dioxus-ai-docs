# AuthKit for Next.js

## Contents

- [App Router setup](#app-router-setup)
- [Cookies](#cookies)
- [Callbacks and deployment overrides](#callbacks-and-deployment-overrides)
- [Proxy and middleware](#proxy-and-middleware)
- [Composable responses and cache safety](#composable-responses-and-cache-safety)
- [Server and client authentication](#server-and-client-authentication)
- [Session and access-token refresh](#session-and-access-token-refresh)
- [Eager authentication](#eager-authentication)
- [API keys and custom sessions](#api-keys-and-custom-sessions)
- [PKCE and callback CSRF checks](#pkce-and-callback-csrf-checks)

## App Router setup

`@workos-inc/authkit-nextjs` targets the App Router. Configure:

- a client ID;
- an API key;
- a public redirect URI; and
- a session-cookie password containing at least 32 characters.

Implement the callback as an App Router route handler:

```ts
// app/callback/route.ts
import { handleAuth } from '@workos-inc/authkit-nextjs';

export const GET = handleAuth({ returnPathname: '/dashboard' });
```

Configure a default Logout URI in the dashboard before using sign-out.

## Cookies

The session cookie defaults to:

| Setting | Default | Override |
| --- | --- | --- |
| Name | `wos-session` | `WORKOS_COOKIE_NAME` |
| SameSite | `Lax` | `WORKOS_COOKIE_SAMESITE` |
| Maximum age | 400 days | `WORKOS_COOKIE_MAX_AGE` |
| Domain | current host | `WORKOS_COOKIE_DOMAIN` |

`SameSite=None` forces a secure cookie. To share sessions across applications,
set `WORKOS_COOKIE_DOMAIN` and use the same cookie password in every
participating application.

## Callbacks and deployment overrides

`handleAuth` accepts `returnPathname`, `baseURL`, `onSuccess`, and
`onError`. A successful callback supplies:

- the user, access token, and refresh token;
- the impersonator and upstream OAuth tokens;
- the organization ID;
- the authentication method; and
- opaque string `state`.

`authenticationMethod` is present only on initial login. Set `baseURL` when a
container's request host differs from its public host. For dynamic deployments,
set the proxy or middleware `redirectUri` option to override the environment
redirect URI.

## Proxy and middleware

Use a root-level `proxy.ts` and `authkitProxy` with Next.js 16 or newer:

```ts
import { authkitProxy } from '@workos-inc/authkit-nextjs';

export default authkitProxy();
export const config = { matcher: ['/', '/admin/:path*'] };
```

Use `middleware.ts` and `authkitMiddleware` with Next.js 15 or earlier.
Exclude static paths such as `/_next/static`, `/_next/image`, and
`favicon.ico` from broad matchers.

To protect every matched route except explicit public paths:

```ts
import { authkitProxy } from '@workos-inc/authkit-nextjs';

export default authkitProxy({
  middlewareAuth: {
    enabled: true,
    unauthenticatedPaths: ['/', '/about'],
  },
  signUpPaths: ['/account/sign-up'],
});
```

`unauthenticatedPaths` uses Next.js matcher-style globs. `signUpPaths`
independently marks protected paths that should redirect with the sign-up screen
hint.

## Composable responses and cache safety

For custom proxy logic, `authkit(request)` returns `session`, internal
`headers`, and `authorizationUrl`. Pass every response through:

```ts
handleAuthkitHeaders(request, headers, options)
```

The helper:

- propagates server authentication data without leaking internal headers;
- normalizes relative redirects;
- uses status 303 for POST and PUT redirects;
- strips injected `x-workos-*` values; and
- safely merges cookie and cache headers.

For rewrites, use `partitionAuthkitHeaders` with `applyResponseHeaders`.
Authenticated contexts receive private/no-cache directives, while public
requests retain their normal caching behavior.

## Server and client authentication

Use `withAuth()` in server components. It returns the authenticated state,
access token, and active feature flags.

In client components, import `AuthKitProvider` and `useAuth` from
`@workos-inc/authkit-nextjs/components`. Both server and client auth readers
accept `ensureSignedIn: true`. When passing server-provided `initialAuth` to
the provider, omit the access token.

## Session and access-token refresh

`refreshSession` refreshes server-side user, role, and permission data and can
switch organization context. On the client, call:

```ts
await refreshAuth({ organizationId });
```

`useAccessToken` refreshes before expiry, exposes manual refresh with loading
and error state, and stays synchronized with `refreshAuth`. When calling
`authkit` directly, observe refreshes through `onSessionRefreshSuccess` and
`onSessionRefreshError`.

## Eager authentication

`eagerAuth: true` makes the access token available on the initial client render
through a 30-second cookie. The cookie is created only for initial page loads,
not API or prefetch requests, and the client immediately consumes and deletes it.

Use `useAccessToken().getAccessToken()` when a service cannot wait for the
normal asynchronous fetch. Accept the brief JavaScript exposure and apply normal
XSS protections.

## API keys and custom sessions

`validateApiKey()` parses the request's Bearer header and validates an AuthKit
API key for a public endpoint.

For a self-hosted or custom authentication flow, call
`saveSession(session, requestOrUrl)` after direct User Management
authentication. Store the access token, refresh token, user, and optional
impersonator in the encrypted session cookie.

## PKCE and callback CSRF checks

AuthKit Next.js v3 always uses PKCE and sealed OAuth state. Remove
`WORKOS_ENABLE_PKCE`.

The short-lived `wos-auth-verifier` cookie must match callback `state`. The
former URL-state-only fallback is unavailable. Handle missing cookies as
`Auth cookie missing` and mismatched state as `OAuth state mismatch`.
