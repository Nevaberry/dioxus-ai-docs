---
name: clerk-knowledge-patch
description: Clerk
license: MIT
version: 1.0.0
metadata:
  author: Nevaberry
---

# Clerk Knowledge Patch

Use this guide when implementing, upgrading, or debugging Clerk authentication, authorization, Organizations, Billing, SDKs, components, or deployment architecture. Start with the migration notes below, then open the topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Architecture and deployment](references/architecture-and-deployment.md) | Account Portal, FAPI, cookies, handshake, environments, routing, Astro, Next.js, Dashboard roles, Platform API |
| [Authentication and sessions](references/authentication-and-sessions.md) | Factors, SSO, OAuth/OIDC, passkeys, pending sessions, reverification, JWT claims, restrictions |
| [Billing](references/billing.md) | Plans, Features, Subscriptions, trials, checkout, hooks, administration |
| [Components](references/components.md) | Sign-in-or-up, Waitlist, Google One Tap, Show, loading controls, redirects, Billing drawers |
| [Core 3 migration](references/core-3-migration.md) | Signal API, Expo native UI and hooks, attempt errors, MFA, transfer handling |
| [Customization](references/customization.md) | Appearance, themes, Tailwind, iOS theming, localization, templates, Elements, profile extensions |
| [Frontend resources](references/frontend-resources.md) | Browser API keys, Web3, email links, token cache, user refresh, listeners, multi-session behavior |
| [Go Backend SDK](references/go-backend-sdk.md) | v2 setup, clients, middleware, resources, JWTs, roles, machines, settings |
| [Integrations and webhooks](references/integrations-and-webhooks.md) | Svix webhooks, Inngest, framework middleware, MCP, FAPI proxies, satellites, Chrome extensions |
| [JavaScript Backend SDK](references/javascript-backend-sdk.md) | Request authentication, Next.js token types, user migration, metadata, JWT templates, API keys |
| [Organizations and enterprise](references/organizations-and-enterprise.md) | Tenant scoping, roles, permissions, role sets, invitations, Verified Domains, enterprise connections |
| [Python Backend SDK](references/python-backend-sdk.md) | Authentication, retries, API keys, agent tasks, Billing, machines, releases and breaking schemas |

## Breaking migrations and changed defaults

### Migrate custom flows to Core 3

Core 3 uses named factor methods and explicit finalization. Do not port old `attemptFirstFactor()` or `createdSessionId` activation literally.

```ts
const { signIn } = useSignIn()
await signIn.create({ identifier: email })
await signIn.password({ password })

if (signIn.status === 'complete') {
  await signIn.finalize({ navigate: () => router.push('/') })
}
```

- Email-code sign-in uses `signIn.emailCode.sendCode()` and `verifyCode()`.
- Sign-up verification lives under `signUp.verifications`.
- MFA uses the `signIn.mfa` namespace.
- Read field failures from `errors.fields`, other handled failures from `errors.global`, and unparsed failures from `errors.raw`.
- Attempt objects change identity as a flow advances; include the attempt object in React dependency arrays.
- Use `clerk.setActive()` for an `existingSession`; use an attempt's `finalize()` for a newly completed attempt.

### Treat pending sessions as unauthenticated by default

Organization selection, forced-password reset, or required-MFA setup can leave a session `pending`. IDs are normally null and protected routes reject it. After finalization, inspect `session.currentTask` and route to the task UI. Use `treatPendingAsSignedOut: false` only on code that intentionally handles pending identity.

### Update request-authentication checks

JavaScript `authenticateRequest()` reports `isAuthenticated`; `isSignedIn` is deprecated. The result can be `signed-in`, `signed-out`, or `handshake`, exposes `tokenType`, and converts through `toAuth()`.

```ts
const state = await client.authenticateRequest(request, {
  authorizedParties: ['https://app.example.com'],
})
if (!state.isAuthenticated) return new Response('Unauthorized', { status: 401 })
```

Next.js `auth()` accepts session tokens by default. Explicitly set `acceptsToken` for API keys, OAuth tokens, or mixed machine routes, and branch on `tokenType` and scopes.

### Account for SDK and prop migrations

- Python 5.x generated schemas can change incompatibly even in patch or minor releases. Pin exact versions and inspect request and response changes; 6.0.0 changes `users.update()` and `organizations.update()` inputs.
- Go v2 requires Go 1.24+ and imports from `github.com/clerk/clerk-sdk-go/v2`.
- `<SignOutButton>` takes `redirectUrl` and `sessionId` directly; `signOutOptions` is deprecated.
- Move `<UserButton>` sign-out destinations to `<ClerkProvider>`; only `afterSwitchSessionUrl` remains local to the button.
- `satelliteAutoSync` defaults to `false`. Set it explicitly when automatic synchronization is required.
- Use `CLERK_JS_URL`, not deprecated `CLERK_JS`; replace old after-sign-in/up environment variables with fallback or force redirect settings.
- Replace `sessions.verifySession()` with full-request authentication or direct JWT validation.
- Import Chrome extension background clients from `@clerk/chrome-extension/client` with `background: true`.
- Move enterprise administration from `/saml_connections` to `/v1/enterprise_connections`.

### Rename appearance variables

Prepare for removal of these deprecated names:

| Old | Current |
| --- | --- |
| `colorText` | `colorForeground` |
| `colorTextOnPrimaryBackground` | `colorPrimaryForeground` |
| `colorTextSecondary` | `colorMutedForeground` |
| `spacingUnit` | `spacing` |
| `colorInputText` | `colorInputForeground` |
| `colorInputBackground` | `colorInput` |

## Authentication quick reference

### Core 3 sign-in-or-up without enumeration

Use `signIn.create({ identifier, signUpIfMissing: true })`. Verification returns `sign_up_if_missing_transfer` for a new account, after which `signUp.create({ transfer: true })` preserves the verified identifier. This excludes password, username, restricted, and waitlist flows.

### Reverification

Server code checks `auth.has({ reverification: preset })` and returns `reverificationError(preset)`; client code wraps the operation with `useReverification()`. If the user lacks a second factor, a requested second- or multi-factor level downgrades to first-factor verification. Native Expo must provide `onNeedsReverification`; the prebuilt modal is web-only.

### Session-token claims

Current session tokens include `v`, `pla`, `fea`, `sts`, and an `o` object only when an Organization is active. Keep custom claims below 1.2 KB so the complete cookie stays below browser limits. Use `CLERK_JWT_KEY` or a supplied `jwtKey` for networkless verification.

### OAuth and machine tokens

- Clerk can expose OAuth/OIDC discovery, token, user-info, and token-info endpoints.
- Dynamic client registration is public and forces the consent screen on.
- API routes must opt into `oauth_token`; API-key routes must opt into `api_key`.
- M2M creation supports locally verifiable JWTs or immediately revocable opaque tokens.
- A custom JWT template is independent of a session and cannot include session-bound `sid`, `v`, `pla`, or `fea`.

## Framework and deployment quick reference

### Next.js

Calling server-side `auth()` makes the route dynamic. Client `useAuth()` remains static by default; scope `<ClerkProvider dynamic>` narrowly, optionally under `<Suspense>`. Built-in FAPI proxying is available through `clerkMiddleware()` or App Router proxy handlers.

### Astro

Endpoints use synchronous `locals.auth()`, `await locals.currentUser()`, and `clerkClient(context)`. Never serialize the complete Backend User because it contains `privateMetadata`. Match `isStatic` on Clerk controls to whether the page is prerendered.

### Production sessions

The long-lived `__client` JWT on the FAPI domain is distinct from the one-minute `__session` JWT on the exact application domain. Cross-subdomain APIs should receive the session token in `Authorization`. An expired server-rendered token can trigger a 307 FAPI handshake; preserve Clerk's context headers through adapters and proxies.

### Environment topology

Development instances have a 100-user cap and cannot transfer users to production. Staging normally needs a separate application and domain. A preview sharing production identity must use production keys on a subdomain of the same root domain; provider-owned preview domains use development keys.

## Organizations and authorization quick reference

- Store the Organization ID on tenant-owned records and verify it on every query.
- Active Organization is tab-local, but the shared cookie can reflect another active tab. Fetch a token in the current tab and send it as a bearer token for tenant-scoped background work.
- An unknown or unauthorized slug leaves the prior Organization active. Compare route `slug` with authenticated `orgSlug` before reading tenant data.
- System Permissions are not session claims. Use equivalent Custom Permissions for server-side `has()` checks.
- A Custom Permission succeeds only while the active Organization Plan includes its corresponding Feature.
- Role Set changes propagate to assigned Organizations; switching or deleting sets requires explicit Role remapping.
- Organization collection hooks fetch nothing unless each collection is requested.

## Billing quick reference

Clerk Billing objects are separate from Stripe Billing objects. The service is USD-only and has no native refunds, tax/VAT calculation, 3D Secure confirmation, or merchant-of-record service. Authorize entitlements with `has()` or `<Show>`, not display hooks.

For custom checkout, call `start()`, `confirm()`, then `finalize()` to synchronize identity state. New cards require `<PaymentElementProvider>` and `<PaymentElement />`; existing cards pass `paymentMethodId`. Billing buttons must be inside `<Show when="signed-in">`, and Organization checkout also requires an Active Organization.

## UI and customization quick reference

- `<Show>` accepts roles, permissions, features, plans, or a callback, but it only hides client content; repeat sensitive checks on the server.
- `<GoogleOneTap>` needs custom Google credentials and does not return provider access tokens.
- Embedded `<Waitlist />` needs Waitlist mode plus `waitlistUrl`.
- Global appearance supports `theme`, `options`, `variables`, `elements`, `captcha`, and `cssLayerName`; direct component appearance wins for one instance.
- For Tailwind v4, place Clerk in an earlier cascade layer than `utilities`.
- Stable DOM hooks are the human-readable `cl-*` classes before the lock marker; remove `cl-` when using an `appearance.elements` key.
- Hosted Account Portal pages allow Dashboard customization only; prebuilt components allow CSS changes; Elements allows custom HTML/CSS but still owns flow order; only API-built flows control authentication logic.

## Native Expo quick reference

`@clerk/expo` 3.1 requires Expo SDK 53+. Its config plugin installs native iOS and Android dependencies. `AuthView`, `UserButton`, and `UserProfileView` come from `@clerk/expo/native`; native Google sign-in uses platform-native APIs. Set the plugin's `appleSignIn` option to `false` when the entitlement is not needed.

Use `useUserProfileModal()`, `useNativeSession()`, and `useNativeAuthEvents()` for native state. Cloudflare bot protection is unsupported in Expo and must be disabled there.

## Before shipping

1. Confirm the accepted token types and authorized parties for every backend route.
2. Enforce tenant and entitlement checks on the server, even when UI controls hide content.
3. Handle handshake, pending-session, and reverification states explicitly.
4. Check redirect URLs, Account Portal return targets, proxy headers, and satellite origins.
5. Capture API-key secrets and OAuth client secrets at creation; they are not generally retrievable later.
6. Recheck SDK-specific deprecations and schema changes in the relevant reference.
