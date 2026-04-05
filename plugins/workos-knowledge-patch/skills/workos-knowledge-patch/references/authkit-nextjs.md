# AuthKit Next.js Integration

## Next.js 16+ Proxy Migration

Next.js 16+ renames middleware to "proxy". AuthKit provides `authkitProxy` alongside `authkitMiddleware`:

```ts
// proxy.ts (Next.js 16+)
import { authkitProxy } from '@workos-inc/authkit-nextjs';
export default authkitProxy();
export const config = { matcher: ['/', '/admin'] };

// middleware.ts (Next.js <=15) -- unchanged
import { authkitMiddleware } from '@workos-inc/authkit-nextjs';
export default authkitMiddleware();
```

## Composable Proxy/Middleware

For combining AuthKit with other logic (rate limiting, redirects), use `authkit()` + `handleAuthkitHeaders()`:

```ts
import { NextRequest } from 'next/server';
import { authkit, handleAuthkitHeaders } from '@workos-inc/authkit-nextjs';

export default async function proxy(request: NextRequest) {
  const { session, headers, authorizationUrl } = await authkit(request);

  if (request.nextUrl.pathname.startsWith('/app') && !session.user && authorizationUrl) {
    return handleAuthkitHeaders(request, headers, { redirect: authorizationUrl });
  }
  return handleAuthkitHeaders(request, headers);
}
```

Always use `handleAuthkitHeaders()` -- it strips internal `x-workos-*` headers from browser responses and handles `Set-Cookie`/`Cache-Control` correctly.

### Rewrites

For rewrites, use `partitionAuthkitHeaders()` + `applyResponseHeaders()`:

```ts
import { authkit, partitionAuthkitHeaders, applyResponseHeaders } from '@workos-inc/authkit-nextjs';
const { headers } = await authkit(request);
const { requestHeaders, responseHeaders } = partitionAuthkitHeaders(request, headers);
const response = NextResponse.rewrite(url, { request: { headers: requestHeaders } });
applyResponseHeaders(response, responseHeaders);
```

## Client Component Imports

Client-side hooks and components use the `/components` subpath:

```tsx
import { AuthKitProvider, Impersonation } from '@workos-inc/authkit-nextjs/components';
import { useAuth } from '@workos-inc/authkit-nextjs/components';
import { useAccessToken } from '@workos-inc/authkit-nextjs/components';
```

## useAccessToken Hook

Client-side hook for direct JWT access with automatic refresh:

```tsx
'use client';
import { useAccessToken } from '@workos-inc/authkit-nextjs/components';

function ApiClient() {
  const { accessToken, loading, error, refresh } = useAccessToken();
  // accessToken: string | undefined, refresh(): Promise<string | undefined>
}
```

## AuthKitProvider Optimization

Pass server-side auth data to avoid a server action call on mount:

```tsx
const auth = await withAuth();
const { accessToken, ...initialAuth } = auth; // strip token from client data
<AuthKitProvider initialAuth={initialAuth}>{children}</AuthKitProvider>
```

## handleAuth onSuccess Callback

The `onSuccess` callback receives: `{ user, accessToken, refreshToken, impersonator?, oauthTokens?, authenticationMethod?, organizationId?, state? }`. `authenticationMethod` is only available during initial login, not refreshes.

## Custom State Through Auth Flow

Pass custom data through OAuth via `state` parameter:

```ts
const signInUrl = await getSignInUrl({
  state: JSON.stringify({ teamId: 'team_123', referrer: 'homepage' }),
});

export const GET = handleAuth({
  onSuccess: async ({ user, state }) => {
    const data = state ? JSON.parse(state) : null;
  },
});
```

## Session Refresh Callbacks

Monitor session refreshes in proxy/middleware:

```ts
const { session, headers } = await authkit(request, {
  onSessionRefreshSuccess: async ({ accessToken, user, impersonator }) => { /* ... */ },
  onSessionRefreshError: async ({ error, request }) => { /* ... */ },
});
```

## Eager Auth

`eagerAuth: true` in proxy/middleware stores access token in a 30-second cookie for synchronous client-side access (needed by third-party services that validate tokens with WorkOS directly).

## validateApiKey

Validates Bearer auth API keys in route handlers:

```ts
import { validateApiKey } from '@workos-inc/authkit-nextjs';
const { apiKey } = await validateApiKey();
```

## saveSession (Advanced)

For custom auth flows (email verification, token exchange), manually save a session:

```ts
import { saveSession, getWorkOS } from '@workos-inc/authkit-nextjs';
const authResponse = await getWorkOS().userManagement.authenticateWithEmailVerification({
  clientId, code,
});
await saveSession({
  accessToken: authResponse.accessToken,
  refreshToken: authResponse.refreshToken,
  user: authResponse.user,
}, req);
```

## getWorkOS()

Direct access to the underlying WorkOS SDK client:

```ts
import { getWorkOS } from '@workos-inc/authkit-nextjs';
const workos = getWorkOS();
const orgs = await workos.organizations.listOrganizations({ limit: 10 });
```

## PKCE Always Enabled (v3)

PKCE is now always on in v3. Remove `WORKOS_ENABLE_PKCE` env var. The `wos-auth-verifier` cookie must survive the auth round-trip -- if a CDN strips `Set-Cookie` on redirects, you'll get "Auth cookie missing" errors.
