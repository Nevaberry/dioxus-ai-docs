# JavaScript Backend SDK

## Create a backend client

```ts
import { createClerkClient } from '@clerk/backend'

const client = createClerkClient({
  publishableKey: process.env.CLERK_PUBLISHABLE_KEY,
  secretKey: process.env.CLERK_SECRET_KEY,
})
```

Supply `jwtKey` when session-token verification must avoid a network request.

## Authenticate complete requests

`authenticateRequest()` reports `isAuthenticated`; `isSignedIn` is deprecated. The request state distinguishes `signed-in`, `signed-out`, and `handshake`, exposes the accepted `tokenType`, and converts to the session- or machine-shaped `Auth` object through `toAuth()`.

```ts
const state = await client.authenticateRequest(request, {
  authorizedParties: ['https://app.example.com'],
})

if (!state.isAuthenticated) {
  return new Response('Unauthorized', { status: 401 })
}
```

Reverse proxies and custom adapters must preserve authentication context, including:

- `Authorization`
- `Accept`
- `Host`
- `Origin`
- `Referer`
- `Sec-Fetch-Dest`
- `User-Agent`
- `X-Forwarded-Host`
- `X-Forwarded-Proto`, or `CloudFront-Forwarded-Proto`

## Token-aware Next.js routes

Next.js `auth()` defaults to session tokens. API keys and OAuth tokens are rejected unless enabled through `acceptsToken`.

```ts
const state = await auth({
  acceptsToken: ['session_token', 'api_key'],
})

if (!state.isAuthenticated) return new Response('Unauthorized', { status: 401 })
if (state.tokenType === 'api_key' && !state.scopes?.includes('write:users')) {
  return new Response('Insufficient scope', { status: 401 })
}
```

Machine results expose `tokenType`, scopes, identity, and claims. On non-document requests, `auth.protect()` returns HTTP 401 for failed machine authentication and HTTP 404 for a failed session-token check.

Protect a route group with `auth.protect({ token: 'api_key' })`, or use `token: 'any'` when every supported valid token type is acceptable.

## Built-in Next.js FAPI proxy

`clerkMiddleware()` can proxy FAPI. A custom proxy path must also appear in the Next.js matcher.

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

App Router code can export the `GET`, `POST`, `PUT`, `DELETE`, and `PATCH` handlers returned by `createFrontendApiProxyHandlers()`, or call `clerkFrontendApiProxy(request)` from individual handlers.

## User listing filters

`getUserList()` accepts at most 100 values per identifier filter. Prefix entries in `userId`, `externalId`, or `organizationId` with `+` to require them and `-` to exclude them. `query` separately performs partial matching across identifiers and names.

```ts
const users = await client.users.getUserList({
  organizationId: ['+org_required', '-org_excluded'],
  userId: ['-user_test'],
})
```

## User migration inputs

`createUser()` can import:

- A password digest and hasher.
- A TOTP secret.
- Backup codes.
- Original `createdAt` and `legalAcceptedAt` timestamps.

Password- and legal-check bypasses are intended only for migrations.

```ts
const user = await client.users.createUser({
  emailAddress: ['migrated@example.com'],
  passwordDigest: digest,
  passwordHasher: 'bcrypt',
  createdAt: new Date('2020-01-01T00:00:00Z'),
})
```

`updateUser()` also controls whether the user can delete themselves or create Organizations. `createOrganizationsLimit: 0` means unlimited creation.

```ts
await client.users.updateUser(user.id, {
  deleteSelfEnabled: false,
  createOrganizationEnabled: true,
  createOrganizationsLimit: 0,
})
```

## Metadata replacement and merge

Metadata supplied to `updateUser()` replaces the existing object. `updateUserMetadata()` deep-merges instead, retaining nested keys; a `null` value removes a key at any depth.

```ts
await client.users.updateUserMetadata(userId, {
  publicMetadata: {
    profile: { timezone: 'UTC' },
    obsoleteKey: null,
  },
})
```

## Session verification deprecation

`clerkClient.sessions.verifySession(sessionId, token)` is deprecated. Authenticate the complete request with `authenticateRequest()` or validate the JWT signature and claims.

## Session claims and custom JWT templates

Keep custom session-token claims below 1.2 KB; the complete cookie must remain under the browser's roughly 4 KB limit. Fetch large metadata separately.

Custom JWT templates create tokens independent of a session. They automatically include `azp`, `exp`, `iat`, `iss`, `jti`, `nbf`, and `sub`, but cannot include session-bound `sid`, `v`, `pla`, or `fea`. Customize the session token when those claims are needed.

A whole-value shortcode preserves its JSON type. Interpolation produces a string. Nested metadata uses dot notation, and `||` chooses the first operand that is neither `null` nor `false`.

```json
{
  "metadata": "{{user.public_metadata}}",
  "display_name": "{{user.full_name || 'Unknown'}}"
}
```

Generate the token with `getToken({ template: 'service' })`. This makes a network request and counts against Backend API rate limits.

## Machine-to-machine token formats

M2M creation accepts `tokenFormat: 'jwt'`. Verify that format locally through `clerkClient.m2m.verify()` and the instance public key. The opaque format uses server-side verification and supports immediate revocation.

```ts
const m2mToken = await clerkClient.m2m.createToken({
  tokenFormat: 'jwt',
})
const verified = await clerkClient.m2m.verify({ token: m2mToken.token })
```

## Multi-tenant API keys

Clerk supports API keys as a first-class multi-tenant SaaS credential. Route authentication must explicitly accept `api_key`, validate its subject, and enforce scopes rather than treating the key as a session token.
