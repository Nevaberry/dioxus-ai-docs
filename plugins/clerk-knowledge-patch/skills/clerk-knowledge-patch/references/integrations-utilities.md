# Integrations & Utilities

## Clerk as OAuth Provider (IdP)

Clerk can act as an OAuth 2.0 / OIDC Identity Provider, letting users sign into third-party apps with their Clerk credentials. Configure OAuth applications in the Clerk Dashboard under **OAuth applications**.

### Verifying OAuth Tokens (Resource Server)

```ts
// Next.js — use acceptsToken to verify OAuth access tokens
import { auth } from '@clerk/nextjs/server'

export async function GET() {
  // acceptsToken tells Clerk to verify the OAuth access token instead of session token
  const { userId } = await auth({ acceptsToken: 'oauth-token' })
  // ... or with auth.protect():
  // const { userId } = await auth.protect({ acceptsToken: 'oauth-token' })
}
```

SDKs auto-handle both JWT and opaque token formats. Manual verification via REST API:

```bash
curl https://api.clerk.com/oauth_applications/access_tokens/verify \
  -X POST -H 'Authorization: Bearer <CLERK_SECRET_KEY>' \
  -H 'Content-Type: application/json' \
  -d '{ "access_token": "<OAUTH_TOKEN>" }'
```

## Building MCP Servers with `@clerk/mcp-tools`

Clerk provides `@clerk/mcp-tools` for building MCP servers that use Clerk as the OAuth authorization provider. Requires enabling **Dynamic client registration** in the Clerk Dashboard under OAuth applications.

### Next.js App Router

```bash
npm install mcp-handler @clerk/mcp-tools
```

```ts
// app/[transport]/route.ts — [transport] supports /mcp (Streamable HTTP) and /sse
import { verifyClerkToken } from '@clerk/mcp-tools/next'
import { createMcpHandler, withMcpAuth } from 'mcp-handler'
import { auth, clerkClient } from '@clerk/nextjs/server'

const clerk = await clerkClient()

const handler = createMcpHandler((server) => {
  server.tool('get-user-data', 'Gets authenticated user data', {}, async (_, { authInfo }) => {
    const userId = authInfo!.extra!.userId! as string
    const userData = await clerk.users.getUser(userId)
    return { content: [{ type: 'text', text: JSON.stringify(userData) }] }
  })
})

const authHandler = withMcpAuth(
  handler,
  async (_, token) => {
    const clerkAuth = await auth({ acceptsToken: 'oauth_token' })
    return verifyClerkToken(clerkAuth, token)
  },
  { required: true, resourceMetadataPath: '/.well-known/oauth-protected-resource/mcp' },
)

export { authHandler as GET, authHandler as POST }
```

### Express

```bash
npm install @modelcontextprotocol/sdk @clerk/mcp-tools cors
```

```ts
import { clerkClient, clerkMiddleware } from '@clerk/express'
import { mcpAuthClerk, protectedResourceHandlerClerk, streamableHttpHandler } from '@clerk/mcp-tools/express'
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'

const app = express()
app.use(cors({ exposedHeaders: ['WWW-Authenticate'] }))
app.use(clerkMiddleware())
app.use(express.json())

const server = new McpServer({ name: 'my-server', version: '0.0.1' })
server.tool('get-user-data', 'Gets user data', {}, async (_, { authInfo }) => {
  const userId = authInfo!.extra!.userId! as string
  const userData = await clerkClient.users.getUser(userId)
  return { content: [{ type: 'text', text: JSON.stringify(userData) }] }
})

app.post('/mcp', mcpAuthClerk, streamableHttpHandler(server))
app.get('/.well-known/oauth-protected-resource/mcp', protectedResourceHandlerClerk({ scopes_supported: ['email', 'profile'] }))
app.get('/.well-known/oauth-authorization-server', authServerMetadataHandlerClerk)
```

### Required Metadata Endpoints (MCP Spec Compliance)

```ts
// Next.js: app/.well-known/oauth-authorization-server/route.ts
import { authServerMetadataHandlerClerk, metadataCorsOptionsRequestHandler } from '@clerk/mcp-tools/next'
const handler = authServerMetadataHandlerClerk()
const corsHandler = metadataCorsOptionsRequestHandler()
export { handler as GET, corsHandler as OPTIONS }

// Next.js: app/.well-known/oauth-protected-resource/mcp/route.ts
import { protectedResourceHandlerClerk, metadataCorsOptionsRequestHandler } from '@clerk/mcp-tools/next'
const handler = protectedResourceHandlerClerk({ scopes_supported: ['profile', 'email'] })
const corsHandler = metadataCorsOptionsRequestHandler()
export { handler as GET, corsHandler as OPTIONS }
```

Ensure `.well-known` paths are excluded from `clerkMiddleware()` route protection.

## TanStack Start Middleware

```ts
// src/start.ts
import { clerkMiddleware } from '@clerk/tanstack-react-start/server'

export const startInstance = createStart(() => ({
  requestMiddleware: [clerkMiddleware()],
}))
```

## React Router Middleware

```ts
// react-router.config.ts
export default { future: { v8_middleware: true } } satisfies Config

// app/root.tsx
import { clerkMiddleware } from '@clerk/react-router/server'
import type { Route } from './+types/root'
export const middleware: Route.MiddlewareFunction[] = [clerkMiddleware()]
```

## Astro Hybrid Rendering `isStatic` Prop

In Astro's `server` or `hybrid` output modes, control components need `isStatic` to switch between server-side (uses middleware locals) and client-side (uses nanostores) rendering:

```astro
---
export const prerender = true  // pre-rendered page
---
<Show when="signed-in" isStatic={true}>You are signed in!</Show>
```

When `isStatic={true}`, the component renders inside a custom element (e.g., `<clerk-signed-in>`). Apply styles directly via `class` prop on `<Show>` to fix flex alignment.

## Standalone `getToken()` Function

Top-level `getToken()` export that works outside React component trees — in axios interceptors, React Query/SWR, or vanilla JS. Automatically waits for Clerk to initialize.

```ts
import { getToken } from '@clerk/nextjs' // or @clerk/react, @clerk/vue, etc.

// Example: Axios interceptor
axios.interceptors.request.use(async (config) => {
  const token = await getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

## `ClerkOfflineError`

`getToken()` now throws `ClerkOfflineError` instead of returning `null` when offline. Previously, `null` could be misinterpreted as "user is signed out."

```ts
import { ClerkOfflineError } from '@clerk/react/errors'

try {
  const token = await session.getToken()
} catch (error) {
  if (ClerkOfflineError.is(error)) {
    // Handle offline — show offline UI, retry later
  }
  throw error
}
```

During SSR, `useAuth().getToken` is now a function (not `undefined`) that throws with code `clerk_runtime_not_browser`:

```ts
import { isClerkRuntimeError } from '@clerk/react/errors'

try {
  const token = await getToken()
} catch (error) {
  if (isClerkRuntimeError(error) && error.code === 'clerk_runtime_not_browser') {
    // Running on server — use auth() instead
  }
}
```

## `enterprise_sso` Replaces `saml` Strategy

The `saml` strategy name and `samlAccount` property are removed in Core 3:

- Strategy: `'saml'` → `'enterprise_sso'` (in Clerk Elements and custom flows)
- Property: `user.samlAccounts` → `user.enterpriseAccounts`
- Backend: `clerkClient.samlConnections` → `clerkClient.enterpriseConnections` (supports both SAML and OIDC)

## Enterprise Connections API (Unified SAML + OIDC)

The `/v1/enterprise_connections` endpoint replaces the legacy `/saml_connections` endpoint:

```ts
// Create an enterprise connection (SAML or OIDC)
const client = await clerkClient()
await client.enterpriseConnections.create({
  provider: 'saml',  // or 'oidc'
  domains: ['acme.com'],
  name: 'Acme SSO',
  organizationId: 'org_xxx',
})

// List enterprise connections (optionally filter by org)
const connections = await client.enterpriseConnections.list({
  organizationId: 'org_xxx',
})

// Update / Delete
await client.enterpriseConnections.update('ec_xxx', { name: 'Updated Name' })
await client.enterpriseConnections.delete('ec_xxx')
```

REST endpoints: `POST/GET /v1/enterprise_connections`, `GET/PATCH/DELETE /v1/enterprise_connections/{id}`.

## M2M JWT Token Format

M2M tokens can now be generated as JWTs instead of opaque tokens. JWTs enable networkless verification (no API call to Clerk), are free to verify, and have lower latency. Opaque tokens remain better for instant revocation needs.

```ts
// Create a JWT M2M token (instead of default opaque)
const m2mToken = await clerkClient.m2m.createToken({
  tokenFormat: 'jwt',
})

// Verify locally — no network request needed for JWT format
const verified = await clerkClient.m2m.verify({ token: m2mToken.token })
```

## Chrome Extension SDK — Vanilla JS Support

`@clerk/chrome-extension` now supports vanilla JavaScript (non-React) via `createClerkClient()`:

```ts
// Popup or side panel (vanilla JS)
import { createClerkClient } from '@clerk/chrome-extension/client'

const clerk = createClerkClient({
  publishableKey: process.env.CLERK_PUBLISHABLE_KEY,
})
await clerk.load({ allowedRedirectProtocols: ['chrome-extension:'] })

// Background service worker — use background: true
const clerk = await createClerkClient({
  publishableKey: process.env.CLERK_PUBLISHABLE_KEY,
  background: true,  // replaces deprecated @clerk/chrome-extension/background import
})
const token = clerk.session ? await clerk.session.getToken() : null
```

**Deprecation**: `@clerk/chrome-extension/background` import is deprecated. Use `@clerk/chrome-extension/client` with `background: true` instead.

## Solana and Base Web3 Authentication

```ts
// Solana — requires walletName parameter
await clerk.authenticateWithSolana({
  walletName: 'phantom', // required: which Solana wallet provider
  redirectUrl: '/dashboard',
  legalAccepted: true,   // optional: legal compliance acceptance
})

// Base
await clerk.authenticateWithBase({
  redirectUrl: '/dashboard',
  legalAccepted: true,
})

// Generic Web3 with Solana strategy
await signIn.authenticateWithWeb3({
  identifier: walletAddress,
  generateSignature: async ({ identifier, nonce, walletName }) => { /* sign message */ },
  strategy: 'web3_solana_signature',
  walletName: 'phantom', // required for Solana strategy
})
```
