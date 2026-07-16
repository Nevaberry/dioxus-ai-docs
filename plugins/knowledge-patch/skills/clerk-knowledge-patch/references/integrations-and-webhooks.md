# Integrations and webhooks

## Verify Clerk webhooks

Clerk sends Svix-signed `POST` requests. A webhook carries no Clerk authentication state, so its route must remain public and trust the payload only after `verifyWebhook()` succeeds.

Store the endpoint secret as `CLERK_WEBHOOK_SIGNING_SECRET`.

```ts
import { verifyWebhook } from '@clerk/nextjs/webhooks'
import { NextRequest } from 'next/server'

export async function POST(request: NextRequest) {
  const event = await verifyWebhook(request)
  if (event.type === 'user.created') {
    await upsertUser(event.data)
  }
  return new Response(null, { status: 204 })
}
```

A `2xx` response stops delivery. A `4xx`, `5xx`, or missing response causes retries. Failed and missing messages can be replayed from the Dashboard.

Astro, Express, Fastify, Nuxt, React Router, and TanStack React Start use their integration-specific `/webhooks` export. Express must expose the unparsed body with `express.raw({ type: 'application/json' })`. Narrow `event.type` before reading event-specific fields from `event.data`.

## Self-delivered email and SMS

When Clerk delivery is disabled for a template, consume `emails.created` or `sms.created` webhooks and deliver the message. SMS content can be changed only through this self-delivery path.

## Inngest transformation

The Dashboard Inngest transformation creates a webhook in Inngest's production environment and maps Clerk event names into the `clerk/` namespace. The original webhook `data` remains `event.data`; multiple functions may consume the event independently.

```ts
const syncUser = inngest.createFunction(
  { id: 'sync-user-from-clerk' },
  { event: 'clerk/user.created' },
  async ({ event }) => database.users.upsert(event.data),
)
```

## Framework middleware registration

React Router framework mode must enable the v8 middleware future flag before Clerk middleware can be exported from the root route.

```ts
// react-router.config.ts
import type { Config } from '@react-router/dev/config'

export default {
  future: { v8_middleware: true },
} satisfies Config
```

```ts
// app/root.tsx
import { clerkMiddleware } from '@clerk/react-router/server'
import type { Route } from './+types/root'

export const middleware: Route.MiddlewareFunction[] = [clerkMiddleware()]
```

TanStack Start registers middleware in `src/start.ts` with `createStart(() => ({ requestMiddleware: [clerkMiddleware()] }))`:

```ts
createStart(() => ({
  requestMiddleware: [clerkMiddleware()],
}))
```

## Clerk Skills and snippet server

Clerk publishes reusable Skills through:

```bash
npx skills add clerk/skills
```

Its separate remote MCP snippet server is `https://mcp.clerk.com/mcp`. It uses Streamable HTTP, not SSE. Available tools are `clerk_sdk_snippet` and `list_clerk_sdk_snippets`; bundles include `b2b-saas`, `waitlist`, `custom-flows`, and `server-side`.

```json
{
  "mcpServers": {
    "clerk": { "url": "https://mcp.clerk.com/mcp" }
  }
}
```

## OAuth-protected application MCP servers

`@clerk/mcp-tools` connects an application's MCP server to Clerk's OAuth server. Most MCP clients require Dynamic client registration.

Next.js handlers should accept only `oauth_token`, validate it with `verifyClerkToken()`, and pass identity to tools through `authInfo.extra.userId`.

```ts
import { verifyClerkToken } from '@clerk/mcp-tools/next'
import { auth } from '@clerk/nextjs/server'
import { withMcpAuth } from 'mcp-handler'

const authHandler = withMcpAuth(
  handler,
  async (_, token) =>
    verifyClerkToken(
      await auth({ acceptsToken: 'oauth_token' }),
      token,
    ),
  {
    required: true,
    resourceMetadataPath: '/.well-known/oauth-protected-resource/mcp',
  },
)
```

Publish the protected-resource metadata route with `protectedResourceHandlerClerk({ scopes_supported: [...] })` and leave it public. Older clients may also require the public `/.well-known/oauth-authorization-server` handler.

Express uses `mcpAuthClerk` with `streamableHttpHandler(server)`. Browser clients require CORS that exposes the `WWW-Authenticate` response header.

## Manual FAPI proxy contract

Manual FAPI proxying works only for production instances, and the proxy must share the application's domain.

Forward:

- The body unchanged.
- Every original header unchanged.
- `Clerk-Proxy-Url` containing the complete proxy URL.
- `Clerk-Secret-Key`.
- The original client IP in `X-Forwarded-For`.

Deploy and verify the proxy before enabling its `proxy_url` on the Clerk domain.

Express can implement forwarding and Clerk redirect rewriting with `clerkMiddleware({ frontendApiProxy: { enabled: true } })`:

```ts
clerkMiddleware({
  frontendApiProxy: { enabled: true },
})
```

For a satellite proxy, set `proxyUrl` or `CLERK_PROXY_URL`, not `domain` or `CLERK_DOMAIN`. Proxy and domain configuration are mutually exclusive.

## Satellite synchronization default

In `@clerk/clerk-js` 6.3.3 and `@clerk/backend` 3.2.3, `satelliteAutoSync` correctly defaults to `false`. Omission previously behaved as `true`. Applications relying on automatic synchronization must opt in explicitly.

```tsx
<ClerkProvider satelliteAutoSync={true}>...</ClerkProvider>
```

## Manual satellite synchronization

When automatic synchronization is disabled, sign-in and sign-up run on the primary domain. Satellite links must use `buildSignInUrl()` or `buildSignUpUrl()`. These builders add `__clerk_synced=false`, which tells the satellite to import the session on return. A hard-coded primary URL omits the trigger.

```tsx
const { buildSignInUrl } = useClerk()
return <a href={buildSignInUrl()}>Sign in</a>
```

The primary `<ClerkProvider>` must list every satellite in `allowedRedirectOrigins`.

Server-rendered multi-domain applications are supported in Next.js, TanStack Start, and Nuxt. Other React integrations must avoid server rendering and hydration for this topology.

## Chrome extension clients

Non-React extension pages initialize Clerk through `createClerkClient()` from `@clerk/chrome-extension/client`. Popup and side-panel clients must allow the extension redirect protocol.

```ts
import { createClerkClient } from '@clerk/chrome-extension/client'

const clerk = createClerkClient({ publishableKey })
await clerk.load({
  allowedRedirectProtocols: ['chrome-extension:'],
})
```

The same entry point handles service workers with `background: true`. `@clerk/chrome-extension/background` is deprecated.

```ts
const clerk = await createClerkClient({
  publishableKey,
  background: true,
})
const token = clerk.session
  ? await clerk.session.getToken()
  : null
```

Cloudflare bot protection is unsupported in Chrome extensions and must be disabled.

## Astro static and server controls

For Astro `server` output, a prerendered page uses `isStatic={true}` on Clerk controls. In `hybrid` output, a dynamically rendered page uses `isStatic={false}` so controls read `locals`. Static controls emit a `clerk-*` wrapper; apply layout classes to the control when the wrapper must take part in flex or grid layout.
