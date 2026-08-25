# Architecture and deployment

## Choose the integration layer

Every application enables the hosted Account Portal by default. Choose the
layer according to the amount of control required:

| Layer | Customization boundary |
| --- | --- |
| Account Portal | Dashboard options only |
| Embedded prebuilt components | CSS, but not HTML or flow order |
| Beta Clerk Elements | Custom HTML and CSS; Clerk still owns flow order |
| Custom API flow | Full authentication-logic control |

## Account Portal URLs and returns

Production portal pages live at `https://accounts.<your-domain>.com`, including
`/sign-in`, `/sign-up`, `/user`, `/organization`, and `/create-organization`.
A direct link needs `redirect_url`, because a directly opened portal page has
no application return target. `email_address`, `phone_number`, `username`,
`first_name`, and `last_name` can prefill fields.

```text
https://accounts.example.com/sign-in?redirect_url=https://example.com/dashboard&email_address=user@example.com
```

## Frontend API discovery and API boundaries

The publishable key identifies the application's Frontend API (FAPI). Removing
`pk_test_` or `pk_live_` reveals a base64 value containing the FAPI hostname and
a trailing `$` delimiter:

```ts
const encoded = publishableKey.replace(/^pk_(?:test|live)_/, '')
atob(encoded) // "example.accounts.dev$"
```

FAPI serves a user's own flows and resources. Multi-user instance
administration belongs to the secret-key Backend API; direct FAPI integration
is discouraged, while direct Backend API use is reasonable. The separate
Platform API manages workspace resources such as applications, domains, and
application transfers.

## Production cookies and token renewal

Production authentication uses a long-lived `__client` JWT on the FAPI domain
as the source of truth. It is `HttpOnly`, `SameSite=Lax`, and contains a client
ID plus a rotating anti-fixation token. The browser SDK derives a separate
60-second `__session` JWT, stores it on the application's exact domain with
`SameSite=Lax` and without `HttpOnly`, and renews it every 50 seconds through
`/client/sessions/<id>/tokens`.

The session cookie is intentionally not shared across subdomains. Send the
token as `Authorization: Bearer ...` to an API on another subdomain.

## Server-rendered handshake

An expired server-rendered session token produces a `handshake` state and a 307
redirect through FAPI's `/v1/client/handshake`. The browser presents its
`__client` cookie; the returned payload directs the server SDK to set or clear
`__session`, and any replacement JWT is verified before authentication
succeeds. The payload travels in the URL in development and a cookie in
production.

## Component routing

`<SignUp />`, `<SignIn />`, `<UserProfile />`, `<CreateOrganization />`, and
`<OrganizationProfile />` support `path` and `hash` routing. Path routing is the
default for Next.js, TanStack React Start, and React Router; other SDKs default
to hash routing. The same child step may therefore be
`/sign-up/verify-email-address` or `/sign-up#verify-email-address`.

## Tenant topology

Clerk Organizations provide a shared-user-pool B2B topology: one account can
join several Organizations with a different Role in each. Store the
Organization ID on application records and enforce it on every tenant query.
Clerk does not provide isolated per-customer user pools, domains, branding,
authentication policy, and limits within one platform application.

## Development, staging, and previews

Development instances:

- Are capped at 100 users and cannot transfer user data to production.
- May use shared social-provider credentials.
- Use the development-only `__clerk_db_jwt`; application code must not depend
  on that object.

Clerk supplies Development and Production instances, not a separate staging
tier. A typical staging environment uses another application and domain with
that application's Production instance, and settings must be mirrored manually.

A preview sharing production users and settings must use production keys on a
subdomain of the same root domain. Provider-owned preview domains such as
`*.vercel.app` use development keys. A completely independent preview backed by
another Clerk application needs another root domain, not just another
production subdomain.

## Environment controls and redirects

- `CLERK_JWT_KEY` enables networkless session verification.
- Next.js uses a 128-bit pseudorandom `CLERK_ENCRYPTION_KEY` to propagate
  dynamic `clerkMiddleware()` keys.
- `CLERK_FAPI` and `CLERK_PROXY_URL` override FAPI routing.
- `CLERK_JS_URL` and `CLERK_JS_VERSION` control the hot-loaded browser SDK;
  browser-visible Next.js and Vite forms use `NEXT_PUBLIC_` and `VITE_`
  prefixes.

`CLERK_JS` is deprecated; use `CLERK_JS_URL`. Old
`*_AFTER_SIGN_IN_URL` and `*_AFTER_SIGN_UP_URL` variables are also deprecated;
fallback and force redirect settings take precedence.

## Astro endpoint behavior

Astro endpoints call `locals.auth()` synchronously, fetch the Backend User with
`await locals.currentUser()`, and obtain the Backend API with
`clerkClient(context)`. Never serialize the complete user because it contains
`privateMetadata`.

```ts
export async function GET({ locals }) {
  const { isAuthenticated, userId } = locals.auth()
  if (!isAuthenticated) return new Response('Unauthorized', { status: 401 })
  return new Response(JSON.stringify({ userId }))
}
```

## Next.js rendering boundaries

Calling server-side `auth()` makes the entire route dynamic. Client `useAuth()`
stays statically rendered by default. For authenticated data on first render,
scope `<ClerkProvider dynamic>` to the smallest useful layout, optionally
inside `<Suspense>` for partial prerendering.

## TypeScript authorization augmentation

Augment application-specific claims, metadata, Roles, and Permissions through
global interfaces such as `CustomJwtSessionClaims` and `ClerkAuthorization`.
Custom Permissions merge with system types, but a custom `role` union replaces
the default `org:admin | org:member` union; retain those values explicitly if
the application uses them.

```ts
export {}
declare global {
  interface ClerkAuthorization {
    role: 'org:admin' | 'org:member' | 'org:teacher'
    permission: 'org:quiz:grade'
  }
}
```

## Dashboard workspace roles

Hobby and Pro workspaces have Owner and Viewer. Business also has Admin,
Developer, and Support. Admin can manage instances, billing, secrets, users,
and impersonation but cannot delete or transfer applications. Developer can
change configuration and keys and impersonate only in development. Support can
impersonate and manage restrictions without configuration access. Viewer
cannot read users or billing.

## Application ownership transfers

A transfer preserves keys, settings, domains, and operation; only ownership
changes. An application with a paid subscription can move only to a workspace
that already has active billing information.
