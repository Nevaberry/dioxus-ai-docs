# JavaScript Backend SDK

## Treat API keys as a supported tenant credential

Clerk includes multi-tenant API-key functionality for SaaS applications. API
key authentication can therefore share Clerk's identity and authorization
architecture instead of requiring an unrelated credential system.

## Authenticate complete requests

`authenticateRequest()` now reports success through `isAuthenticated`;
`isSignedIn` is deprecated. Its state is `signed-in`, `signed-out`, or
`handshake`, exposes the accepted `tokenType`, and converts to the session- or
machine-shaped `Auth` object through `toAuth()`.

```ts
const client = createClerkClient({
  publishableKey: process.env.CLERK_PUBLISHABLE_KEY,
  secretKey: process.env.CLERK_SECRET_KEY,
})
const state = await client.authenticateRequest(request, {
  authorizedParties: ['https://app.example.com'],
})
```

Provide `jwtKey` for networkless verification instead of relying on
`secretKey`. Custom adapters and reverse proxies must retain authentication
context headers: `Authorization`, `Accept`, `Host`, `Origin`, `Referer`,
`Sec-Fetch-Dest`, `User-Agent`, `X-Forwarded-Host`, and `X-Forwarded-Proto` or
`CloudFront-Forwarded-Proto`.

## Accept token types explicitly in Next.js

Next.js `auth()` accepts one or more values in `acceptsToken` and defaults to
session tokens. API keys and OAuth tokens are rejected unless enabled.
Machine-authenticated results expose `tokenType`, scopes, identity, and claims.

```ts
const state = await auth({
  acceptsToken: ['session_token', 'api_key'],
})
if (!state.isAuthenticated) {
  return new Response('Unauthorized', { status: 401 })
}
if (
  state.tokenType === 'api_key' &&
  !state.scopes?.includes('write:users')
) {
  return new Response('Insufficient scope', { status: 401 })
}
```

For non-document requests, failed machine authentication through
`auth.protect()` returns 401; a failed session-token check returns 404. Protect
a route group with `auth.protect({ token: 'api_key' })`, or `token: 'any'` when
all configured token types are valid.

## Use built-in Next.js FAPI proxying

Enable a Frontend API proxy in `clerkMiddleware()`. A custom proxy path must be
included in the Next.js matcher.

```ts
export default clerkMiddleware({
  frontendApiProxy: {
    enabled: true,
    path: '/custom-clerk-proxy',
  },
})
export const config = {
  matcher: ['/(api|trpc|custom-clerk-proxy)(.*)'],
}
```

App Router can export the `GET`, `POST`, `PUT`, `DELETE`, and `PATCH` handlers
from `createFrontendApiProxyHandlers()`, or call
`clerkFrontendApiProxy(request)` inside individual handlers.

## Combine user-list include and exclude filters

`getUserList()` accepts up to 100 values for each identifier filter. Prefix
`userId`, `externalId`, or `organizationId` values with `+` to require them and
`-` to exclude them. `query` separately performs partial matching across
identifiers and names.

```ts
const users = await client.users.getUserList({
  organizationId: ['+org_required', '-org_excluded'],
  userId: ['-user_test'],
})
```

## Import users and configure self-service

`createUser()` can import password digest and hasher, TOTP secret, backup codes,
original `createdAt`, and `legalAcceptedAt`. Password and legal-check bypasses
are for migrations only. `updateUser()` independently controls self-deletion
and Organization creation. `createOrganizationsLimit: 0` means unlimited.

```ts
const user = await client.users.createUser({
  emailAddress: ['migrated@example.com'],
  passwordDigest: digest,
  passwordHasher: 'bcrypt',
  createdAt: new Date('2020-01-01T00:00:00Z'),
})
await client.users.updateUser(user.id, {
  deleteSelfEnabled: false,
  createOrganizationEnabled: true,
  createOrganizationsLimit: 0,
})
```

## Choose replacement or deep merge for metadata

Metadata supplied to `updateUser()` replaces the existing object.
`updateUserMetadata()` performs a deep merge, retaining nested keys. A `null`
value removes the corresponding key at any depth.

```ts
await client.users.updateUserMetadata(userId, {
  publicMetadata: {
    profile: { timezone: 'UTC' },
    obsoleteKey: null,
  },
})
```

## Replace deprecated session verification

`clerkClient.sessions.verifySession(sessionId, token)` is deprecated.
Authenticate the complete request with `authenticateRequest()` or directly
validate JWT signature and claims.

## Keep session claims and JWT templates distinct

Keep custom session-token claims below 1.2 KB so the whole cookie remains under
the browser's approximate 4 KB limit. Fetch large metadata separately.

Custom JWT templates create session-independent tokens. They include `azp`,
`exp`, `iat`, `iss`, `jti`, `nbf`, and `sub`, but cannot include session-bound
`sid`, `v`, `pla`, or `fea`. Use a customized session token for those claims.

A whole-value shortcode retains its JSON type; interpolation yields a string.
Nested metadata uses dot notation, and `||` returns the first operand that is
neither `null` nor `false`.

```json
{
  "metadata": "{{user.public_metadata}}",
  "display_name": "{{user.full_name || 'Unknown'}}"
}
```

Generate a template token through `getToken({ template: 'service' })`. This is
a network request and counts against Backend API rate limits.
