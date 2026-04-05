---
name: clerk-knowledge-patch
description: "Clerk changes since training cutoff (latest: 1.0.0) — Core 3 SDK, <Show> component, Clerk Elements, billing APIs, machine auth, Go/Python SDKs. Load before working with Clerk."
version: "1.0.0"
license: MIT
metadata:
  author: Nevaberry
---

# Clerk Knowledge Patch

Claude's baseline knowledge covers Clerk through Core 2 (`@clerk/nextjs` v5, `@clerk/clerk-react`). This patch adds Core 3 changes (`@clerk/nextjs` v6+, `@clerk/react` v1+), Go SDK v2, Python backend SDK, and new features through early 2025.

## Index

| Topic | Reference | Key Content |
|-------|-----------|-------------|
| Components | [references/components.md](references/components.md) | `<Show>` (replaces SignedIn/SignedOut), UserAvatar, Waitlist, billing components, UserButton menu customization, UNSAFE_PortalProvider |
| Authentication Flows | [references/authentication-flows.md](references/authentication-flows.md) | Core 3 custom flow API (method chaining), reverification, session tasks, signUpIfMissing, Errors\<T\> type, session token v2 claims |
| Middleware & Backend | [references/middleware-backend.md](references/middleware-backend.md) | `isAuthenticated`, async `clerkClient()`, machine token auth, Frontend API proxy, dynamic keys, organizationSyncOptions |
| Organizations & Permissions | [references/organizations.md](references/organizations.md) | Role Sets, system permissions, org slug URL patterns |
| Clerk Elements | [references/clerk-elements.md](references/clerk-elements.md) | Headless UI primitives (`@clerk/elements`), sign-in/sign-up anatomy, shadcn/ui CLI |
| Billing | [references/billing.md](references/billing.md) | Custom checkout (useCheckout + PaymentElement), billing hooks, backend/client-side billing APIs, B2B billing, free trials |
| Go SDK v2 | [references/go-sdk.md](references/go-sdk.md) | Package structure, sub-package imports, HTTP middleware, JWT verification, reverification, testing patterns |
| Python SDK | [references/python-sdk.md](references/python-sdk.md) | `clerk-backend-api` package, `_async` suffix convention, request authentication |
| Integrations & Utilities | [references/integrations-utilities.md](references/integrations-utilities.md) | MCP tools, OAuth provider (IdP), TanStack Start, React Router, Astro, Chrome Extension, getToken, ClerkOfflineError, Web3, enterprise_sso |

## Core 3 Migration Essentials

### Package Rename

```bash
# React SDK renamed
npm install @clerk/react # was @clerk/clerk-react
# Next.js unchanged
npm install @clerk/nextjs # still @clerk/nextjs (now v6+)
```

### `<Show>` Replaces `<SignedIn>` / `<SignedOut>`

```tsx
import { Show, SignInButton, UserButton } from '@clerk/react'

<Show when="signed-in">
  <UserButton />
</Show>
<Show when="signed-out">
  <SignInButton />
</Show>

// Authorization checks
<Show when={{ permission: 'org:invoices:create' }} fallback={<p>No access</p>}>
  <InvoiceForm />
</Show>
<Show when={{ feature: 'premium_access' }} fallback={<p>Upgrade</p>}>
  <PremiumFeature />
</Show>
<Show when={(has) => has({ role: 'org:admin' }) || has({ role: 'org:billing_manager' })}>
  <SettingsPage />
</Show>
```

Full `when` type: `'signed-in' | 'signed-out' | { feature: string } | { permission: string } | { plan: string } | { role: string } | (has) => boolean`

### Key API Changes Quick Reference

| Core 2 | Core 3 | Notes |
|--------|--------|-------|
| `<SignedIn>` / `<SignedOut>` | `<Show when="signed-in">` | Unified control component |
| `@clerk/clerk-react` | `@clerk/react` | Package rename |
| `if (!userId)` | `if (!isAuthenticated)` | `auth()` returns `isAuthenticated` boolean |
| `const client = clerkClient` | `const client = await clerkClient()` | Now async function |
| `signUp.create()` → `prepareVerification()` → `attemptVerification()` → `setActive()` | `signUp.password()` → `verifications.sendEmailCode()` → `verifications.verifyEmailCode()` → `finalize()` | Method chaining API |
| `clerkJSVariant: 'headless'` | `prefetchUI={false}` | On ClerkProvider |
| `saml` strategy | `enterprise_sso` | Supports both SAML + OIDC |
| `user.samlAccounts` | `user.enterpriseAccounts` | Property rename |
| `clerkClient.samlConnections` | `clerkClient.enterpriseConnections` | Backend rename |

### `ClerkProvider` Auto-detects Key

```tsx
// No publishableKey prop needed — reads from env vars automatically:
// NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY (Next.js)
// VITE_CLERK_PUBLISHABLE_KEY (Vite)
// CLERK_PUBLISHABLE_KEY (general)
<ClerkProvider>
  <App />
</ClerkProvider>
```

### Auth Pattern (Server-side)

```tsx
import { auth } from '@clerk/nextjs/server'

// Core 3 pattern
const { isAuthenticated, userId, redirectToSignIn } = await auth()
if (!isAuthenticated) return redirectToSignIn()

// clerkClient is now async
const client = await clerkClient()
const user = await client.users.getUser(userId)
```

### Machine Token Authentication

```tsx
// Middleware — protect routes by token type
export default clerkMiddleware(async (auth, req) => {
  if (isApiRoute(req)) await auth.protect({ token: 'api_key' })
  if (isM2MRoute(req)) await auth.protect({ token: 'm2m_token' })
  if (isOAuthRoute(req)) await auth.protect({ token: 'oauth_token' })
})

// Route handler — acceptsToken parameter
const { userId } = await auth({ acceptsToken: 'oauth_token' })
```

### Standalone `getToken()`

```ts
import { getToken } from '@clerk/nextjs' // or @clerk/react, @clerk/vue

// Works outside React — in axios interceptors, React Query, vanilla JS
axios.interceptors.request.use(async (config) => {
  const token = await getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
```

Throws `ClerkOfflineError` when offline (instead of returning `null`). Import from `@clerk/react/errors`.

### Types Subpath Export

```ts
import type { UserResource, OrganizationResource } from '@clerk/react/types'
// Also: @clerk/nextjs/types, @clerk/vue/types, etc.
```

## Custom Flow API (Core 3 Summary)

Old pattern: `signUp.create()` → `prepareEmailAddressVerification()` → `attemptEmailAddressVerification()` → `setActive()`

New pattern uses method chaining:

```tsx
// Sign-up
const { signUp, errors, fetchStatus } = useSignUp()
await signUp.password({ emailAddress, password })
await signUp.verifications.sendEmailCode()
await signUp.verifications.verifyEmailCode({ code })
if (signUp.status === 'complete') await signUp.finalize({ navigate: ({ decorateUrl }) => { /* ... */ } })

// Sign-in
const { signIn, errors, fetchStatus } = useSignIn()
await signIn.create({ identifier: emailAddress })
await signIn.emailCode.sendCode()
await signIn.emailCode.verifyCode({ code })
if (signIn.status === 'complete') await signIn.finalize({ navigate: ({ decorateUrl }) => { /* ... */ } })
```

Field-level errors: `errors.fields.emailAddress`, `errors.fields.password`, `errors.fields.code`. Loading: `fetchStatus === 'fetching'`.

## Reverification (Step-up Auth)

```ts
// Server action
import { auth, reverificationError } from '@clerk/nextjs/server'
export const sensitiveAction = async () => {
  const { has } = await auth.protect()
  if (!has({ reverification: 'strict' })) return reverificationError('strict')
  // Presets: 'strict_mfa' | 'strict' (10m) | 'moderate' (1h) | 'lax'
}

// Client — wraps action, auto-shows verification modal
import { useReverification } from '@clerk/nextjs'
const perform = useReverification(sensitiveAction)
const result = await perform() // null if user cancelled
```

## Session Tasks (Pending Sessions)

Three states: `signed-in` | `pending` | `signed-out`. Pending = authenticated but tasks incomplete (choose org, reset password, setup MFA).

```tsx
import { TaskChooseOrganization, TaskResetPassword, TaskSetupMFA } from '@clerk/nextjs'

// In middleware — redirect pending users
const { isAuthenticated, sessionStatus } = await auth()
if (!isAuthenticated && sessionStatus === 'pending') {
  // redirect to /session-tasks
}

// Access pending user data
const { userId } = await auth({ treatPendingAsSignedOut: false })
```

## Billing Quick Reference

```tsx
// Components (PricingTable from main, rest from /experimental)
import { PricingTable } from '@clerk/nextjs'
import { CheckoutButton, useCheckout, usePlans, useSubscription } from '@clerk/nextjs/experimental'

<PricingTable />                                    // works signed-in or signed-out
<PricingTable for="organization" />                 // org-level plans
<CheckoutButton planId="cplan_xxx" planPeriod="month" for="user" />  // must be in <Show when="signed-in">

// Hooks (all experimental) — shared interface: { data, isLoading, hasNextPage, fetchNext, revalidate }
const { data: plans } = usePlans({ for: 'user' })
const { data: subscription } = useSubscription({ for: 'organization' })

// Backend
const client = await clerkClient()
const sub = await client.billing.getUserBillingSubscription('user_123')
await client.billing.cancelSubscriptionItem('subi_123', { endNow: true })
```

**B2B gotcha**: `has({ permission: 'org:teams:manage' })` returns false if the org's Plan doesn't include the "teams" Feature, even if the user has the permission.

## Go SDK v2 Quick Reference

```go
import "github.com/clerk/clerk-sdk-go/v2"           // was github.com/clerkinc/clerk-sdk-go
import "github.com/clerk/clerk-sdk-go/v2/user"       // sub-packages per resource
import clerkhttp "github.com/clerk/clerk-sdk-go/v2/http"

clerk.SetKey("sk_live_XXX")
// Pointer helpers: clerk.String(), clerk.Bool(), clerk.Int64()
// Header-only auth (no cookies): clerkhttp.RequireHeaderAuthorization()(handler)
// Claims: claims, ok := clerk.SessionClaimsFromContext(r.Context())
```

## Python SDK Quick Reference

```python
# Package: clerk-backend-api (NOT clerk-python)
from clerk_backend_api import Clerk

with Clerk(bearer_auth="sk_live_xxx") as clerk:
    user = clerk.users.get(user_id="user_123")
# Async uses _async suffix: await clerk.users.get_async(user_id="user_123")
```
