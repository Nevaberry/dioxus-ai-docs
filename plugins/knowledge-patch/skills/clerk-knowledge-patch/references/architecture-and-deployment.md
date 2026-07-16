# Architecture and deployment

## Choose the integration tier

Every application has the hosted Account Portal enabled by default.

| Tier | Custom HTML/CSS | Control of flow order and authentication logic |
| --- | --- | --- |
| Account Portal | Dashboard options only | Clerk-owned |
| Embedded prebuilt components | CSS, but not component HTML | Clerk-owned |
| Clerk Elements | Custom HTML and CSS for sign-in/sign-up | Clerk-owned |
| Custom API flow | Application-owned | Application-owned |

Clerk Elements provides more visual control, but only a flow built from the API controls authentication logic.

## Account Portal routing

Production pages use `https://accounts.<your-domain>.com`:

- `/sign-in`
- `/sign-up`
- `/user`
- `/organization`
- `/create-organization`

A directly opened page has no application return target, so include `redirect_url`. The query parameters `email_address`, `phone_number`, `username`, `first_name`, and `last_name` prefill fields.

```text
https://accounts.example.com/sign-in?redirect_url=https://example.com/dashboard&email_address=user@example.com
```

## Frontend and Backend API boundary

Each application has a dedicated Frontend API (FAPI). Its hostname is encoded in the publishable key after `pk_test_` or `pk_live_`, in base64, with a trailing `$` delimiter.

```ts
const encoded = publishableKey.replace(/^pk_(?:test|live)_/, '')
atob(encoded) // "example.accounts.dev$"
```

FAPI handles a user's own flows and resources. Administrative operations spanning users belong to the secret-key Backend API. Direct FAPI calls are discouraged; direct Backend API use is supported when an SDK lacks an operation.

The Platform API is a separate server-side surface for workspace resources such as applications, domains, and application transfers. Do not treat these as session-scoped FAPI or ordinary instance-resource Backend API operations.

## Production token architecture

The production source of truth is a long-lived `__client` JWT on the FAPI domain. It is `HttpOnly`, `SameSite=Lax`, and contains a client ID plus a rotating anti-fixation token.

The `__session` JWT is different:

- It lasts 60 seconds.
- Browser code writes it to the application's exact domain.
- It is `SameSite=Lax` and intentionally not `HttpOnly`.
- The frontend SDK renews it every 50 seconds through `/client/sessions/<id>/tokens`.
- It is deliberately not shared across subdomains. Send it as a bearer token to an API on another subdomain.

Development uses `__clerk_db_jwt` instead of this client-token architecture. Application code must not depend on the development-only object.

## Server-rendered handshake

If server rendering sees an expired session token, Clerk classifies the request as `handshake` and issues a 307 redirect through FAPI `/v1/client/handshake`. The browser presents `__client`; the response tells the server SDK whether to set or clear `__session`.

The handshake payload travels in the URL during development and in a cookie in production. Any replacement JWT is verified before the request becomes authenticated. Reverse proxies and custom adapters must preserve Clerk's authentication context headers.

## Component routing defaults

`<SignUp />`, `<SignIn />`, `<UserProfile />`, `<CreateOrganization />`, and `<OrganizationProfile />` support `path` and `hash` routing.

- Next.js, TanStack React Start, and React Router default to path routing.
- Other SDK integrations default to hash routing.

The same nested step may therefore appear as `/sign-up/verify-email-address` or `/sign-up#verify-email-address`.

## Supported tenant topology

Organizations implement a shared user pool: an account may belong to multiple Organizations and have a different Role in each. Store the Organization ID on tenant-owned application data and filter every tenant query by it.

Clerk does not provide a platform topology in which every customer receives an isolated user pool, domain, branding, authentication policy, and limits.

## Development, staging, and previews

Development instances:

- Are capped at 100 users.
- Cannot transfer user data to production.
- May use shared social credentials.
- Use the development-only client object described above.

Clerk supplies Development and Production instances, not a separate Staging instance. Staging normally uses a separate application and domain, often with that application's Production instance; mirror settings manually.

A preview that shares production users and configuration must use production keys on another subdomain of the same root domain. Provider-owned preview domains such as `*.vercel.app` can use only development keys. A preview backed by another Clerk application requires a different root domain, not just another subdomain of the production root.

## Environment controls

- `CLERK_JWT_KEY`: verify session tokens without a network request.
- `CLERK_ENCRYPTION_KEY`: 128-bit pseudorandom key used by Next.js to propagate dynamic `clerkMiddleware()` keys.
- `CLERK_FAPI`: override FAPI routing.
- `CLERK_PROXY_URL`: select a FAPI proxy.
- `CLERK_JS_URL` and `CLERK_JS_VERSION`: control the hot-loaded browser SDK.
- Next.js and Vite expose browser values through their `NEXT_PUBLIC_` and `VITE_` variants.

`CLERK_JS` is deprecated; use `CLERK_JS_URL`. The old `*_AFTER_SIGN_IN_URL` and `*_AFTER_SIGN_UP_URL` variables are also deprecated. Fallback and force redirect variables take priority.

## Astro server boundaries

Astro endpoints read authentication synchronously from `locals.auth()`, fetch the Backend User with `await locals.currentUser()`, and obtain the Backend API client with `clerkClient(context)`.

```ts
export async function GET({ locals }) {
  const { isAuthenticated, userId } = locals.auth()
  if (!isAuthenticated) return new Response('Unauthorized', { status: 401 })
  return new Response(JSON.stringify({ userId }))
}
```

Do not serialize the complete result of `currentUser()` because it contains `privateMetadata`.

For Astro `server` output, a page that opts into prerendering with `export const prerender = true` must set `isStatic={true}` on Clerk control components. For `hybrid` output, a page that opts out with `prerender = false` must use `isStatic={false}` so controls read server-side `locals`.

Static controls emit a `clerk-*` custom-element wrapper. Put flex/grid layout classes on the Clerk control when the wrapper itself must participate in layout.

```astro
---
export const prerender = true
---
<Show when="signed-in" isStatic={true} class="flex">Signed in</Show>
```

## Next.js rendering boundaries

Calling server-side `auth()` opts the complete route into dynamic rendering. Client-side `useAuth()` remains statically rendered by default. To make auth data available on first render, scope `<ClerkProvider dynamic>` to the smallest useful layout, optionally beneath `<Suspense>` for partial prerendering; avoid making the root provider dynamic unless the entire tree needs it.

## TypeScript authorization augmentation

Application claims, metadata, Roles, and Permissions are typed through global interfaces such as `CustomJwtSessionClaims` and `ClerkAuthorization`. Custom Permissions merge with the defaults, but a custom `role` union replaces the default `org:admin | org:member` union. Retain those values explicitly when still used.

```ts
export {}
declare global {
  interface ClerkAuthorization {
    role: 'org:admin' | 'org:member' | 'org:teacher'
    permission: 'org:quiz:grade'
  }
}
```

## Dashboard workspace access

Hobby and Pro workspaces have Owner and Viewer. Business adds Admin, Developer, and Support.

- Admin can manage instances, billing, secrets, users, and impersonation, but cannot delete or transfer applications.
- Developer can change configuration and API keys and can impersonate only in development.
- Support can impersonate and manage restrictions but cannot change configuration.
- Viewer cannot read users or billing.

## Application transfers

Moving an application between workspaces preserves API keys, settings, domains, and operation; only ownership changes. An application with a paid subscription can move only to a workspace that already has active billing information.

