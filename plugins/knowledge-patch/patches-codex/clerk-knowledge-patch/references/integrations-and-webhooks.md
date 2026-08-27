# Integrations and webhooks

## Verify every webhook before processing it

Clerk webhooks are Svix-signed `POST` requests and carry no Clerk authentication
state. Keep the route public and trust the request only after `verifyWebhook()`
succeeds. Store the endpoint secret in `CLERK_WEBHOOK_SIGNING_SECRET`.

```ts
import { verifyWebhook } from '@clerk/nextjs/webhooks'
import { NextRequest } from 'next/server'

export async function POST(request: NextRequest) {
  const event = await verifyWebhook(request)
  if (event.type === 'user.created') await upsertUser(event.data)
  return new Response(null, { status: 204 })
}
```

A `2xx` response stops delivery. A `4xx`, `5xx`, or missing response triggers
retries; failed or missing messages can be replayed from the Dashboard. Import
from the integration-specific `/webhooks` entry in Astro, Express, Fastify,
Nuxt, React Router, or TanStack React Start. Express must expose the unparsed
body with `express.raw({ type: 'application/json' })`. Narrow `event.type`
before reading event-specific fields.

## Transform events through Inngest

The Dashboard's Inngest template creates a webhook in the Inngest production
environment, renames Clerk events into the `clerk/` namespace, and retains the
original payload's `data` as `event.data`. Multiple functions may independently
consume the same event.

```ts
const syncUser = inngest.createFunction(
  { id: 'sync-user-from-clerk' },
  { event: 'clerk/user.created' },
  async ({ event }) => database.users.upsert(event.data),
)
```

## Register framework middleware

React Router framework mode requires the v8 middleware future flag before
Clerk middleware can be exported from the root route.

```ts
// react-router.config.ts
import type { Config } from '@react-router/dev/config'
export default { future: { v8_middleware: true } } satisfies Config
```

```ts
// app/root.tsx
import { clerkMiddleware } from '@clerk/react-router/server'
import type { Route } from './+types/root'
export const middleware: Route.MiddlewareFunction[] = [clerkMiddleware()]
```

TanStack Start registers `clerkMiddleware()` in `src/start.ts` through
`createStart(() => ({ requestMiddleware: [clerkMiddleware()] }))`.

## Use Clerk's Skills and snippet MCP service

Install Clerk's reusable Skills with:

```text
npx skills add clerk/skills
```

The remote snippet service is at `https://mcp.clerk.com/mcp`. It supports
Streamable HTTP, not SSE. It exposes `clerk_sdk_snippet` and
`list_clerk_sdk_snippets`, including `b2b-saas`, `waitlist`, `custom-flows`,
and `server-side` bundles.

```json
{
  "mcpServers": {
    "clerk": { "url": "https://mcp.clerk.com/mcp" }
  }
}
```

## Protect an application MCP server with OAuth

`@clerk/mcp-tools` connects an application's MCP server to Clerk's OAuth
server. Most MCP clients require Dynamic Client Registration. Next.js handlers
should accept only `oauth_token`, verify with `verifyClerkToken()`, and pass the
identity to tools through `authInfo.extra.userId`.

```ts
import { verifyClerkToken } from '@clerk/mcp-tools/next'
import { auth } from '@clerk/nextjs/server'
import { withMcpAuth } from 'mcp-handler'

const authHandler = withMcpAuth(
  handler,
  async (_, token) =>
    verifyClerkToken(await auth({ acceptsToken: 'oauth_token' }), token),
  {
    required: true,
    resourceMetadataPath: '/.well-known/oauth-protected-resource/mcp',
  },
)
```

Publish the protected-resource metadata path through
`protectedResourceHandlerClerk({ scopes_supported: [...] })` and keep it
public. Older clients may also need a public
`/.well-known/oauth-authorization-server` handler. Express uses `mcpAuthClerk`
with `streamableHttpHandler(server)`. Browser clients require CORS that exposes
`WWW-Authenticate`.

## Match Astro controls to rendering mode

In Astro `server` output, a page with `export const prerender = true` must pass
`isStatic={true}` to Clerk control components. In `hybrid` output, a page with
`prerender = false` must pass `isStatic={false}` so controls use server-side
`locals`.

```astro
---
export const prerender = true
---
<Show when="signed-in" isStatic={true} class="flex">Signed in</Show>
```

Static controls render a `clerk-*` custom-element wrapper. Put flex/grid layout
classes on the control when that wrapper must participate in layout.

## Implement a manual FAPI proxy exactly

Manual FAPI proxying works only for production instances, and the proxy must
share the application's domain. Forward the request body and all original
headers unchanged, then add:

- `Clerk-Proxy-Url`: complete proxy URL
- `Clerk-Secret-Key`: instance secret key
- `X-Forwarded-For`: original client IP

Bring the proxy live before setting its `proxy_url` on the Clerk domain.
Express can handle forwarding and redirect rewriting with
`clerkMiddleware({ frontendApiProxy: { enabled: true } })`.

For a satellite proxy, configure `proxyUrl` or `CLERK_PROXY_URL`, not `domain`
or `CLERK_DOMAIN`. Do not set both configuration families.

## Synchronize satellites after sign-in

With automatic synchronization off, sign-in and sign-up occur on the primary
domain. Generate satellite links with `buildSignInUrl()` or `buildSignUpUrl()`.
These add `__clerk_synced=false`, which triggers session import on return. A
hard-coded primary URL omits the trigger.

```tsx
const { buildSignInUrl } = useClerk()
return <a href={buildSignInUrl()}>Sign in</a>
```

The primary `<ClerkProvider>` must list all satellites in
`allowedRedirectOrigins`. Server-rendered multi-domain applications are
supported in Next.js, TanStack Start, and Nuxt. Other React integrations must
avoid server rendering and hydration for this topology.

## Set satellite auto-sync explicitly

In `@clerk/clerk-js` 6.3.3 and `@clerk/backend` 3.2.3,
`satelliteAutoSync` correctly defaults to `false` in Core 3; omission had
previously acted as `true`. Applications depending on auto-sync must enable it
after upgrade.

```tsx
<ClerkProvider satelliteAutoSync={true}>...</ClerkProvider>
```
