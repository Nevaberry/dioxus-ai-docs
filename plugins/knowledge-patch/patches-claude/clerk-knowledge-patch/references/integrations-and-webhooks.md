# Integrations and webhooks

## Verify webhook delivery

Clerk sends Svix-signed public `POST` requests without Clerk authentication
state. Keep the route public and trust it only after `verifyWebhook()` succeeds.
Store the endpoint secret as `CLERK_WEBHOOK_SIGNING_SECRET`. A `2xx` stops
delivery; `4xx`, `5xx`, or no response triggers retries. Replay failed or
missing deliveries from the Dashboard.

```ts
import { verifyWebhook } from '@clerk/nextjs/webhooks'

export async function POST(request: NextRequest) {
  const event = await verifyWebhook(request)
  if (event.type === 'user.created') await upsertUser(event.data)
  return new Response(null, { status: 204 })
}
```

Use the integration's `/webhooks` export for Astro, Express, Fastify, Nuxt,
React Router, or TanStack React Start. Express must expose the raw body with
`express.raw({ type: 'application/json' })`. Narrow `event.type` before reading
event-specific fields.

## Inngest transformation

The Dashboard Inngest template creates a webhook in Inngest's production
environment and maps Clerk event names into the `clerk/` namespace. The original
`data` remains `event.data`; several functions may consume one event.

```ts
const syncUser = inngest.createFunction(
  { id: 'sync-user-from-clerk' },
  { event: 'clerk/user.created' },
  async ({ event }) => database.users.upsert(event.data),
)
```

## Framework middleware

React Router framework mode requires the v8 middleware future flag, then
exports `clerkMiddleware()` from the root route. TanStack Start registers its
middleware in `src/start.ts` through
`createStart(() => ({ requestMiddleware: [clerkMiddleware()] }))`.

```ts
// react-router.config.ts
export default { future: { v8_middleware: true } } satisfies Config

// app/root.tsx
export const middleware: Route.MiddlewareFunction[] = [clerkMiddleware()]
```

## Clerk Skills and snippet MCP server

Clerk distributes development Skills with `npx skills add clerk/skills`. Its
separate snippet server at `https://mcp.clerk.com/mcp` uses Streamable HTTP, not
SSE, and exposes `clerk_sdk_snippet` and `list_clerk_sdk_snippets`, including
`b2b-saas`, `waitlist`, `custom-flows`, and `server-side` bundles.

## OAuth-protected application MCP servers

`@clerk/mcp-tools` connects an application's MCP server to Clerk OAuth. Most
clients need Dynamic client registration. Next.js routes should accept only
`oauth_token`, verify it with `verifyClerkToken()`, and expose the user ID to
tools as `authInfo.extra.userId`.

Publish a public protected-resource metadata route with
`protectedResourceHandlerClerk({ scopes_supported: [...] })`. Older clients may
also need a public `/.well-known/oauth-authorization-server` handler. Express
uses `mcpAuthClerk` with `streamableHttpHandler(server)`. Browser clients need
CORS to expose `WWW-Authenticate`.

## Chrome extension clients

Non-React extension pages initialize Clerk using `createClerkClient()` from
`@clerk/chrome-extension/client`. Allow the extension redirect protocol for
popup or side-panel use.

```ts
const clerk = createClerkClient({ publishableKey })
await clerk.load({ allowedRedirectProtocols: ['chrome-extension:'] })
```

The same entry point handles service workers with `background: true`; the
`@clerk/chrome-extension/background` import is deprecated.

```ts
const clerk = await createClerkClient({ publishableKey, background: true })
const token = clerk.session ? await clerk.session.getToken() : null
```

## Astro static and hybrid controls

For Astro `server` output, a prerendered page must pass `isStatic={true}` to
Clerk controls. For `hybrid` output, a page opted out of prerendering passes
`isStatic={false}` so controls read server-side `locals`. Static controls render
a `clerk-*` custom-element wrapper; put flex/grid classes on the control itself
when the wrapper must participate in layout.

## Frontend API proxy contract

Manual proxying is production-only and the proxy must share the application's
domain. Forward the body and every original header unchanged. Add the complete
proxy URL as `Clerk-Proxy-Url`, the secret as `Clerk-Secret-Key`, and the
original client IP as `X-Forwarded-For`. Enable the domain's `proxy_url` only
after the proxy is live.

Express can meet forwarding and redirect-rewrite requirements with
`clerkMiddleware({ frontendApiProxy: { enabled: true } })`. For a satellite,
configure `proxyUrl` or `CLERK_PROXY_URL`, not `domain`/`CLERK_DOMAIN`; these
configurations are mutually exclusive.

## Satellite synchronization

`satelliteAutoSync` defaults to `false` in Core 3 as of `@clerk/clerk-js` 6.3.3
and `@clerk/backend` 3.2.3. Set it to `true` explicitly when automatic sync is
required.

In the manual flow, sign-in/up occurs on the primary and satellite links must
come from `buildSignInUrl()` or `buildSignUpUrl()`. These add
`__clerk_synced=false`, which triggers import on return; hard-coded primary URLs
omit the trigger. The primary `<ClerkProvider>` must list all satellites in
`allowedRedirectOrigins`.

Server-rendered multi-domain applications are supported for Next.js, TanStack
Start, and Nuxt. Other React integrations must avoid server rendering and
hydration in this topology.
