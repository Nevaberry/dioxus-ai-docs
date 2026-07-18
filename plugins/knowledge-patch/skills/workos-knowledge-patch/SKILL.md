---
name: workos-knowledge-patch
description: WorkOS
license: MIT
version: "8.10"
metadata:
  author: Nevaberry
---

# WorkOS Knowledge Patch

Use this skill when implementing, upgrading, or reviewing a WorkOS integration.
Start with the migration hazards below, then load only the references relevant to
the product surface and language in use.

## Reference index

| Reference | Topics |
| --- | --- |
| [node-sdk-migrations.md](references/node-sdk-migrations.md) | Node.js runtime requirements, v9/v10 breaking contracts, events, errors, pagination, webhooks, Vault, Radar, Connect |
| [authkit-nextjs.md](references/authkit-nextjs.md) | App Router setup, cookies, callbacks, proxy and middleware, response headers, caching, sessions, access tokens, PKCE |
| [authkit-react.md](references/authkit-react.md) | Browser provider configuration, redirects, auth state, organization switching, refresh hooks, token helpers |
| [api-and-sdk-contracts.md](references/api-and-sdk-contracts.md) | Public-client PKCE, Python async client, Go v6 packages, published OpenAPI contract |
| [authentication-and-sessions.md](references/authentication-and-sessions.md) | Identity data, AuthKit customization, applications, sessions, invitations, email lifecycle, OAuth configuration |
| [authorization-and-features.md](references/authorization-and-features.md) | Authorization resources, roles, group assignments, permissions, multi-role provisioning, Feature Flags |
| [sso-directory-and-widgets.md](references/sso-directory-and-widgets.md) | SSO lifecycle and providers, Directory Sync, identity-provider attributes, domains, embedded widgets |
| [platform-products.md](references/platform-products.md) | Connect, MCP, CLI, Pipes, Radar, Vault BYOK, Audit Logs, API keys, email delivery, analytics, Stripe |

## Triage the integration

1. Identify the SDK language, package version, framework, and WorkOS products in use.
2. Apply breaking migrations before adding features.
3. Load the matching topic references from the index.
4. Preserve raw payloads, security state, and internal response headers exactly as
   required by the selected framework.
5. Confirm dashboard-side settings such as redirect URIs, logout URIs, allowed
   origins, domains, providers, and authentication endpoints.

## Breaking changes and deprecations

### Migrate Node SDK v9

- Run on Node.js 22.11 or newer; v9 no longer supports Node.js 20.
- Replace the removed legacy FGA package with authorization resources and role
  APIs. The FGA package was deprecated in v8.4 and removed in v9.
- Rename client access from `portal` to `adminPortal`.
- Keep the established Authorization method names. v9.1.1 reverted generated
  method renames and corrected the endpoint used by
  `listEffectivePermissionsByExternalId`.

### Migrate Node SDK v10

- Treat `Group.createdAt` and `Group.updatedAt` as `Date` values, not strings.
- Construct webhooks with the WorkOS client:

```ts
const webhooks = new Webhooks(workos);
```

- Remove `search` from calls to `listResources`.
- Consume `vault.listObjects` as an auto-paginatable collection of object
  summaries. Generated key and object response fields are camel-cased.

### Update event handling

- Handle API-key deletion as `api_key.revoked`, not `api_key.deleted`.
- Accept typed organization-role, permission, feature-flag, Vault, group, and
  domain-verification-failure events.
- Handle `vault.byok_key.verification_completed`.
- Read `resourceTypeSlug` from deserialized role events.

### Enforce AuthKit Next.js v3 state checks

- Remove `WORKOS_ENABLE_PKCE`; PKCE and sealed OAuth state are always enabled.
- Preserve the short-lived `wos-auth-verifier` cookie through the callback.
- Treat a missing verifier cookie as `Auth cookie missing` and a state mismatch
  as `OAuth state mismatch`; do not restore the URL-state-only fallback.

### Select the Next.js request hook

- On Next.js 16 or newer, define root-level `proxy.ts` with `authkitProxy`.
- On earlier Next.js releases, define `middleware.ts` with
  `authkitMiddleware`.
- Exclude static paths such as `/_next/static`, `/_next/image`, and
  `favicon.ico` from broad matchers.

## AuthKit Next.js quick reference

### Configure the App Router flow

Provide a client ID, API key, public redirect URI, and a session-cookie password
of at least 32 characters. Implement the callback as an App Router route handler:

```ts
// app/callback/route.ts
import { handleAuth } from '@workos-inc/authkit-nextjs';

export const GET = handleAuth({ returnPathname: '/dashboard' });
```

Set a default Logout URI in the WorkOS dashboard before relying on sign-out.
Use `handleAuth` options such as `baseURL`, `onSuccess`, and `onError` for
reverse-proxy deployments and callback control.

### Preserve proxy response semantics

When composing custom proxy logic, call `authkit(request)`, then pass every
response through `handleAuthkitHeaders(request, headers, options)`. For rewrites,
use `partitionAuthkitHeaders` and `applyResponseHeaders`. Do not expose or
forward injected `x-workos-*` request values.

Enable route protection with `middlewareAuth.enabled`; list public routes in
`unauthenticatedPaths`, and use `signUpPaths` for routes that should display
the sign-up screen.

### Read and refresh authentication

- Use `withAuth()` in server components.
- Import `AuthKitProvider` and `useAuth` from
  `@workos-inc/authkit-nextjs/components` in client components.
- Pass `ensureSignedIn: true` when authentication is mandatory.
- Remove the access token before passing server `initialAuth` to the provider.
- Use `refreshSession` on the server and
  `refreshAuth({ organizationId })` on the client.
- Use `useAccessToken` for expiry-aware token access and manual refresh state.

Use `eagerAuth: true` only when an access token must exist on the initial client
render. It transfers the token through a 30-second, initial-page-load-only cookie
that client JavaScript consumes and deletes, so apply normal XSS protections.

## AuthKit React quick reference

Configure `AuthKitProvider` with the public client ID, dashboard redirect URI,
and allowed application origin. Set `apiHostname` to an owned Authentication API
domain in production. Treat `devMode` as local development token storage; it is
automatic only on `localhost` and `127.0.0.1`.

Use `useAuth()` for the user, organization, roles, permissions, feature flags,
impersonator, authentication method, token access, and organization switching.
Catch `LoginRequiredError` when `getAccessToken()` is called while signed out.

## Public-client PKCE quick reference

Construct the Node client with only a client ID for browser, mobile, or CLI
applications. Generate the URL and verifier together, retain the verifier in
secure platform storage across restarts, and submit it during code exchange:

```ts
const workos = new WorkOS({ clientId: 'client_...' });
const { url, codeVerifier } =
  await workos.userManagement.getAuthorizationUrlWithPKCE({
    provider: 'authkit',
    redirectUri: 'myapp://callback',
    clientId: 'client_...',
  });

const tokens = await workos.userManagement.authenticateWithCode({
  code: authorizationCode,
  codeVerifier,
  clientId: 'client_...',
});
```

Confidential clients may use the same flow with an API key; the exchange then
sends both the client secret and verifier.

## Authorization quick reference

- Represent scoped access with authorization resources and resource-scoped custom
  roles. Use `resource_type_slug` when creating an organization role.
- Pass `role_slug` on invitations.
- Filter role-assignment lists by `resource` and `role_slug`.
- Inspect assignment `source` to distinguish direct grants from group grants.
- Expect memberships to hold multiple roles provisioned by AuthKit, SSO, or
  Directory Sync.
- Use the Feature Flags runtime client for local evaluation when an API request
  per evaluation is undesirable.

## Webhook and data-integrity checklist

- Verify webhook signatures against the raw request bytes. Do not decode,
  normalize, or reserialize the payload first.
- Preserve SSO context on authentication events.
- Preserve `verification_prefix` on organization domains.
- Expect server and authentication errors to retain typed data.
- Use exported `ConflictException.code` and the complete
  `isAuthenticationErrorData` guard.
- Treat the normalized identity provider value as `GitHubOAuth`, not
  `GithubOAuth`.

## Product selection quick reference

- Use AuthKit for hosted user authentication, including MCP authorization.
- Use Standalone OAuth to add OAuth to a server that keeps its existing
  authentication.
- Use Connect for delegated application authorization and organization
  selection.
- Use Pipes for end-user third-party connections or as a deployable MCP server
  that grants time-limited connection access.
- Use Radar for signup risk controls and SMS challenges.
- Use Vault BYOK with AWS KMS or Azure Key Vault for customer-managed keys.

## Final verification

Before shipping, verify runtime compatibility, dashboard configuration, callback
cookies and state, redirect behavior, session refresh, raw-body webhook
verification, pagination shapes, and the exact event names consumed by the
application.
