# Middleware & Backend

## `isAuthenticated` Replaces `userId` Truthiness Checks

`auth()` now returns an `isAuthenticated` boolean:

```tsx
const { isAuthenticated, userId, redirectToSignIn } = await auth()
if (!isAuthenticated) return redirectToSignIn()
```

## `clerkClient()` is Now Async

In Next.js, `clerkClient` changed from a direct import to an async function call:

```tsx
import { clerkClient } from '@clerk/nextjs/server'

// Core 3 — must await the function
const client = await clerkClient()
const user = await client.users.getUser(userId)

// Also works inline
await clerkClient().organizations.createOrganizationDomain({
  organizationId: orgId,
  name: domain,
  enrollmentMode: 'automatic_invitation',
})
```

## Machine Token Authentication in Middleware

Routes can be protected by token type using `auth.protect({ token })`. Machine token types: `'api_key'`, `'oauth_token'`, `'m2m_token'`, `'session_token'`, or `'any'`.

```tsx
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isOAuthRoute = createRouteMatcher(['/oauth(.*)'])
const isApiKeyRoute = createRouteMatcher(['/api(.*)'])
const isM2MRoute = createRouteMatcher(['/m2m(.*)'])
const isUserRoute = createRouteMatcher(['/user(.*)'])

export default clerkMiddleware(async (auth, req) => {
  if (isOAuthRoute(req)) await auth.protect({ token: 'oauth_token' })
  if (isApiKeyRoute(req)) await auth.protect({ token: 'api_key' })
  if (isM2MRoute(req)) await auth.protect({ token: 'm2m_token' })
  if (isUserRoute(req)) await auth.protect({ token: 'session_token' })
})
```

For route handlers, use `acceptsToken` parameter:

```tsx
import { auth } from '@clerk/nextjs/server'

export async function GET() {
  const { userId } = await auth({ acceptsToken: 'oauth_token' })
  // or with protect:
  // await auth.protect({ token: 'oauth_token' })
}
```

## Machine Auth Object

When authenticating machine tokens, the Auth object has a different shape:

```ts
// Machine Auth object properties:
{
  id: 'oat_123',           // machine token ID
  tokenType: 'oauth_token', // 'api_key' | 'oauth_token' | 'm2m_token'
  subject: 'user_123',     // user or org ID associated
  name: 'My API Key',      // for api_key and m2m_token types
  claims: {},               // for api_key and m2m_token types
  scopes: ['read', 'write'],
  getToken: async () => string,
}
```

## Frontend API Proxy

Route Clerk's Frontend API requests through your own domain to avoid third-party cookie issues and ad blockers.

### Via Middleware

```tsx
export default clerkMiddleware({
  frontendApiProxy: {
    enabled: true,
    path: '/custom-clerk-proxy', // optional, defaults to /__clerk
  },
})
```

### Via App Router Route Handlers

```ts
// app/api/__clerk/[[...path]]/route.ts
import { createFrontendApiProxyHandlers } from '@clerk/nextjs/server'

// Exports GET, POST, PUT, DELETE, PATCH handlers
export const { GET, POST, PUT, DELETE, PATCH } = createFrontendApiProxyHandlers()

// Or for individual control:
import { clerkFrontendApiProxy } from '@clerk/nextjs/server'
export async function GET(request: Request) {
  return clerkFrontendApiProxy(request)
}
```

## Dynamic Keys for Multi-tenant Middleware

For multi-tenant apps with separate Clerk instances per tenant, provide keys dynamically per request:

```tsx
const tenantKeys = {
  tenant1: { publishableKey: 'pk_tenant1...', secretKey: 'sk_tenant1...' },
  tenant2: { publishableKey: 'pk_tenant2...', secretKey: 'sk_tenant2...' },
}

export default clerkMiddleware(
  (auth, req) => { /* middleware checks */ },
  (req) => {
    const tenant = getTenant(req)
    return tenantKeys[tenant]
  },
)
```

When providing a custom `secretKey`, set `CLERK_ENCRYPTION_KEY` env var (32-byte hex via `openssl rand --hex 32`). Dynamic keys are encrypted with AES and shared to server-side helpers like `auth()`.

## Backend `verify()` Method Consolidation

Machine token verification methods were renamed to a consistent `.verify()`:

```ts
const client = await clerkClient()

// API Keys: verifySecret() → verify()
await client.apiKeys.verify(secret)

// OAuth: verifyAccessToken() → verify()
await client.idpOAuthAccessToken.verify(accessToken)

// M2M: verifyToken() → verify()
await client.m2m.verify(params)
```

## API Keys Client-side API (`clerk.apiKeys`)

The `APIKeys` object on the `Clerk` instance provides programmatic management of API keys. API keys are long-lived opaque tokens for machine-to-machine access. If no `subject` is provided, methods default to the active organization (if any), then the current user.

```tsx
const clerk = useClerk()

// List API keys (paginated)
const { data } = await clerk.apiKeys.getAll({
  subject: 'org_123',  // optional — defaults to active org, then current user
  query: 'production', // optional search filter
  pageSize: 20,
})

// Create — secret is ONLY available in the create response
const newKey = await clerk.apiKeys.create({
  name: 'Production API Key',
  subject: 'org_123',                // optional
  secondsUntilExpiration: 86400 * 90, // optional, null = never expires
  description: 'For CI pipeline',     // optional
})
console.log(newKey.secret) // Store immediately — not retrievable later

// Revoke
await clerk.apiKeys.revoke({
  apiKeyID: 'ak_123',
  revocationReason: 'Compromised', // optional
})
```
