# Architecture and deployment

## Choose the integration tier

Every application enables hosted Account Portal by default. Portal pages can be
customized only through Dashboard settings. Embedded prebuilt components allow
CSS customization but do not expose their HTML or authentication-flow order.
The beta Clerk Elements layer permits custom HTML and CSS for sign-in and
sign-up while retaining control of flow order. Only an API-built custom flow
controls the authentication logic itself.

## Link to Account Portal correctly

Production portal pages are under `https://accounts.<your-domain>.com`, with
paths including `/sign-in`, `/sign-up`, `/user`, `/organization`, and
`/create-organization`. Add `redirect_url` to direct links because a directly
opened portal page has no application return target. The query parameters
`email_address`, `phone_number`, `username`, `first_name`, and `last_name`
prefill corresponding fields.

```text
https://accounts.example.com/sign-in?redirect_url=https://example.com/dashboard&email_address=user@example.com
```

## Keep Frontend and Backend APIs in their lanes

Each application has a dedicated Frontend API (FAPI). Its hostname is encoded
in the publishable key after `pk_test_` or `pk_live_` and before a trailing `$`:

```ts
const encoded = publishableKey.replace(/^pk_(?:test|live)_/, '')
atob(encoded) // "example.accounts.dev$"
```

FAPI handles the current user's flows and resources. Administrative multi-user
work belongs to the secret-key Backend API. Direct FAPI integration is
discouraged, while direct Backend API calls are a supported option.

The Platform API is a separate server-side surface for workspace resources such
as Clerk applications, domains, and application transfers. Do not treat those
operations as session-scoped FAPI calls or ordinary instance-resource Backend
API calls.

## Understand production cookie topology

Production authentication uses two different JWTs:

- `__client` is long-lived, `HttpOnly`, and `SameSite=Lax` on the FAPI domain.
  It is the source of truth and contains a client ID plus a rotating
  anti-fixation token.
- `__session` lasts 60 seconds, is `SameSite=Lax`, is not `HttpOnly`, and lives
  on the exact application domain. The frontend SDK renews it every 50 seconds
  through `/client/sessions/<id>/tokens`.

`__session` deliberately does not span subdomains. Send its value as a bearer
token when an API is on another subdomain.

## Preserve the server-rendered handshake

An expired token during server rendering produces an authentication state of
`handshake` and a 307 redirect through FAPI's `/v1/client/handshake`. The browser
presents `__client`; the response tells the server SDK to set or clear
`__session`. The payload is carried in the URL during development and in a
cookie in production. Verify any replacement JWT before treating the request
as signed in.

Adapters and proxies must preserve Clerk's context headers so the handshake can
complete.

## Set component routing deliberately

`<SignUp />`, `<SignIn />`, `<UserProfile />`, `<CreateOrganization />`, and
`<OrganizationProfile />` support `path` and `hash` routing. Path routing is the
default in Next.js, TanStack React Start, and React Router; other SDKs default to
hash routing. The same nested step may therefore be
`/sign-up/verify-email-address` or `/sign-up#verify-email-address`.

## Use the supported tenant topology

Organizations implement a shared-user-pool B2B topology. One account may belong
to several Organizations and hold a different role in each. Persist the
Organization ID on application records and apply it to every tenant query.
Clerk does not provide isolated user pools, domains, branding, policies, and
limits for every platform customer.

## Separate development, staging, and preview environments

Development instances:

- are capped at 100 users;
- cannot transfer users to production;
- may use shared social credentials; and
- use the development-only `__clerk_db_jwt` instead of production client-token
  architecture. Application code must not depend on that object.

Clerk provides Development and Production instances only. Staging normally
uses a separate application and domain, usually that application's Production
instance, with settings mirrored manually.

A preview sharing production users and settings must use production keys on a
subdomain of the same root domain. Provider-owned preview domains such as
`*.vercel.app` can use only development keys. A fully independent preview backed
by another Clerk application needs a different root domain, not another
subdomain of the production root.

## Configure advanced environment controls

- `CLERK_JWT_KEY` enables networkless session-token verification.
- Next.js uses a 128-bit pseudorandom `CLERK_ENCRYPTION_KEY` to propagate
  dynamic `clerkMiddleware()` keys.
- `CLERK_FAPI` and `CLERK_PROXY_URL` override FAPI routing.
- `CLERK_JS_URL` and `CLERK_JS_VERSION` select the hot-loaded browser SDK.
  Browser-visible Next.js and Vite settings use `NEXT_PUBLIC_` and `VITE_`
  prefixes respectively.

`CLERK_JS` is deprecated; use `CLERK_JS_URL`. Old
`*_AFTER_SIGN_IN_URL`/`*_AFTER_SIGN_UP_URL` settings are also deprecated, and
fallback or force redirect settings take priority.

## Use Astro endpoint locals safely

Astro endpoints obtain request authentication synchronously from
`locals.auth()`, fetch the Backend User with `await locals.currentUser()`, and
create a Backend API client with `clerkClient(context)`.

```ts
export async function GET({ locals }) {
  const { isAuthenticated, userId } = locals.auth()
  if (!isAuthenticated) return new Response('Unauthorized', { status: 401 })
  return new Response(JSON.stringify({ userId }))
}
```

Do not serialize the complete result of `currentUser()` because it contains
`privateMetadata`.

## Control Next.js rendering boundaries

Calling server-side `auth()` makes the entire route dynamic. Client `useAuth()`
remains statically rendered by default. To expose client auth data on the first
render, place `<ClerkProvider dynamic>` at the smallest useful layout, optionally
within `<Suspense>` for partial prerendering, instead of making the root provider
dynamic.

## Augment TypeScript authorization types

Application claims, metadata, roles, and permissions are typed through global
interfaces such as `CustomJwtSessionClaims` and `ClerkAuthorization`. Custom
permissions merge with system permissions, but declaring a custom `role` union
replaces the defaults. Retain `org:admin` and `org:member` explicitly when the
application still uses them.

```ts
export {}
declare global {
  interface ClerkAuthorization {
    role: 'org:admin' | 'org:member' | 'org:teacher'
    permission: 'org:quiz:grade'
  }
}
```

## Respect Dashboard workspace roles

Hobby and Pro workspaces expose Owner and Viewer. Business also has Admin,
Developer, and Support:

- Admin manages instances, billing, secrets, users, and impersonation, but
  cannot delete or transfer applications.
- Developer changes configuration and API keys and may impersonate only in
  development.
- Support impersonates and manages restrictions without configuration access.
- Viewer cannot read users or billing.

## Transfer application ownership safely

Moving an application between workspaces preserves operation, keys, settings,
and domains; only ownership changes. An application with a paid subscription
can move only to a workspace that already has active billing information.
