# JavaScript Backend SDK

## Authenticate complete requests

`authenticateRequest()` reports `isAuthenticated`; `isSignedIn` is deprecated.
The state distinguishes `signed-in`, `signed-out`, and `handshake`, exposes
`tokenType`, and converts to a session- or machine-shaped `Auth` via `toAuth()`.

```ts
const client = createClerkClient({
  publishableKey: process.env.CLERK_PUBLISHABLE_KEY,
  secretKey: process.env.CLERK_SECRET_KEY,
})
const state = await client.authenticateRequest(request, {
  authorizedParties: ['https://app.example.com'],
})
```

Supplying `jwtKey` instead of depending on `secretKey` makes verification
networkless. Adapters and reverse proxies must preserve `Authorization`,
`Accept`, `Host`, `Origin`, `Referer`, `Sec-Fetch-Dest`, `User-Agent`,
`X-Forwarded-Host`, and `X-Forwarded-Proto` or
`CloudFront-Forwarded-Proto`.

## Token-aware Next.js routes

Next.js `auth()` defaults to session tokens. Set `acceptsToken` for API keys,
OAuth tokens, or mixed routes. Machine results expose `tokenType`, `scopes`,
identity, and claims. On non-document requests, `auth.protect()` returns HTTP
401 for failed machine authentication and 404 for failed session checks.

```ts
const state = await auth({ acceptsToken: ['session_token', 'api_key'] })
if (!state.isAuthenticated) return new Response('Unauthorized', { status: 401 })
if (state.tokenType === 'api_key' && !state.scopes?.includes('write:users')) {
  return new Response('Insufficient scope', { status: 401 })
}
```

Use `auth.protect({ token: 'api_key' })` for an API-key route group or
`token: 'any'` when every supported valid token type is acceptable.

## Built-in Next.js FAPI proxy

`clerkMiddleware()` can proxy FAPI. A custom proxy path must also appear in the
Next.js matcher. App Router can export `GET`, `POST`, `PUT`, `DELETE`, and
`PATCH` from `createFrontendApiProxyHandlers()` or call
`clerkFrontendApiProxy(request)` in individual handlers.

```ts
export default clerkMiddleware({
  frontendApiProxy: { enabled: true, path: '/custom-clerk-proxy' },
})
export const config = { matcher: ['/(api|trpc|custom-clerk-proxy)(.*)'] }
```

## Multi-tenant API keys

Clerk API keys support multi-tenant SaaS authentication. Treat them as a
first-class Clerk credential type and explicitly enable `api_key` acceptance on
routes that consume them.

## Machine-to-machine token formats

M2M creation accepts `tokenFormat: 'jwt'`; verify that format locally with
`clerkClient.m2m.verify()` and the instance public key. Opaque tokens retain
server-side verification and immediate revocation.

```ts
const m2mToken = await clerkClient.m2m.createToken({ tokenFormat: 'jwt' })
const verified = await clerkClient.m2m.verify({ token: m2mToken.token })
```

## User list filters

`getUserList()` accepts up to 100 values per identifier filter. Prefix `userId`,
`externalId`, or `organizationId` values with `+` to require or `-` to exclude.
`query` separately does partial matching over identifiers and names.

```ts
const users = await client.users.getUserList({
  organizationId: ['+org_required', '-org_excluded'],
  userId: ['-user_test'],
})
```

## User migration and self-service controls

`createUser()` can import password digest and hasher, TOTP secret, backup codes,
original `createdAt`, and `legalAcceptedAt`. Password and legal bypasses are for
migrations. `updateUser()` separately controls self-deletion and Organization
creation; `createOrganizationsLimit: 0` means unlimited.

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

## Metadata semantics

Metadata passed to `updateUser()` replaces the existing object.
`updateUserMetadata()` deep-merges instead, retaining nested keys and deleting
any key set to `null`.

```ts
await client.users.updateUserMetadata(userId, {
  publicMetadata: { profile: { timezone: 'UTC' }, obsoleteKey: null },
})
```

## Deprecated session verification

`clerkClient.sessions.verifySession(sessionId, token)` is deprecated. Use
`authenticateRequest()` on the complete request or perform full JWT signature
and claim validation.

## Session claims and JWT templates

Keep custom session claims below 1.2 KB so the full cookie remains below the
browser's roughly 4 KB limit. Fetch large metadata separately.

Custom JWT templates produce session-independent tokens. They include `azp`,
`exp`, `iat`, `iss`, `jti`, `nbf`, and `sub`, but cannot include session-bound
`sid`, `v`, `pla`, or `fea`. A whole-value shortcode preserves JSON type;
interpolation returns a string; dot notation reads nested metadata; `||`
selects the first operand that is neither `null` nor `false`.

```json
{
  "metadata": "{{user.public_metadata}}",
  "display_name": "{{user.full_name || 'Unknown'}}"
}
```

`getToken({ template: 'service' })` makes a network request and counts against
Backend API rate limits.
