---
name: workos-knowledge-patch
description: WorkOS
version: "8.10"
license: MIT
metadata:
  author: Nevaberry
---


# WorkOS Knowledge Patch

Use this skill when implementing, upgrading, or reviewing a WorkOS
integration. Identify the SDK language and version, framework version, and
WorkOS products in use before changing code. Apply migration hazards first,
then open only the references needed for the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [Node SDK migrations and contracts](references/node-sdk-migrations.md) | Runtime requirements, v9/v10 migrations, pagination, events, errors, webhooks, Vault, request behavior |
| [AuthKit for Next.js](references/authkit-nextjs.md) | App Router setup, callbacks, cookies, proxy or middleware, response headers, sessions, tokens, PKCE |
| [AuthKit for React](references/authkit-react.md) | Provider configuration, hosted redirects, auth state, organization switching, refresh hooks, token helpers |
| [API and SDK contracts](references/api-and-sdk-contracts.md) | Public-client PKCE, Python async client, Go v6 packages, OpenAPI contract |
| [Authentication and sessions](references/authentication-and-sessions.md) | Users, identity data, applications, sessions, invitations, email, OAuth configuration, authentication methods |
| [Authorization and features](references/authorization-and-features.md) | Authorization resources, roles, assignments, permissions, groups, API keys, Feature Flags |
| [SSO, Directory Sync, domains, and widgets](references/sso-directory-and-widgets.md) | SSO lifecycle and providers, directory attributes, Entra groups, domains, embedded administration |
| [Platform products and operations](references/platform-products.md) | Connect, MCP, CLI, Pipes, Radar, Vault BYOK, Audit Logs, email delivery, analytics, Stripe, Agents |

## Triage the integration

1. Read the package manifest for the exact SDK and framework versions.
2. Inventory the WorkOS products and dashboard configuration used by the app.
3. Apply breaking migrations and removed contracts before adding features.
4. Preserve raw payloads, OAuth state, cookies, and framework-internal response
   headers exactly where the selected integration requires them.
5. Verify redirect and logout URIs, allowed origins, cookie domains,
   authentication endpoints, providers, and organization settings in the
   dashboard.

## Breaking changes and deprecations

### Migrate Node SDK v9

- Run Node.js 22.11 or newer; v9 no longer supports Node.js 20.
- Replace the removed legacy FGA package with authorization resources,
  organization roles, and role-assignment APIs. FGA was deprecated in v8.4.
- Rename client access from `portal` to `adminPortal`.
- Keep the established Authorization method names. v9.1.1 reverted generated
  renames and fixed the endpoint used by
  `listEffectivePermissionsByExternalId`.

### Migrate Node SDK v10

- Treat `Group.createdAt` and `Group.updatedAt` as `Date` objects rather than
  strings.
- Construct webhooks with the WorkOS client: `new Webhooks(workos)`.
- Remove `search` from `listResources` calls.
- Consume `vault.listObjects` as an auto-paginatable collection of object
  summaries. Generated Vault key and object fields are camel-cased.

### Enforce AuthKit Next.js v3 callback state

- Remove `WORKOS_ENABLE_PKCE`; PKCE and sealed OAuth state are always enabled.
- Preserve the short-lived `wos-auth-verifier` cookie through the callback.
- Treat a missing verifier as `Auth cookie missing` and a mismatch as
  `OAuth state mismatch`. Do not restore the removed URL-state-only fallback.

### Select the Next.js request hook

- On Next.js 16 or newer, define root-level `proxy.ts` with `authkitProxy`.
- On Next.js 15 or earlier, define `middleware.ts` with `authkitMiddleware`.
- Exclude `/_next/static`, `/_next/image`, `favicon.ico`, and other static
  paths from broad matchers.

## AuthKit Next.js quick reference

### Configure the App Router flow

Provide a client ID, API key, public redirect URI, and a session-cookie password
of at least 32 characters. Implement the callback as an App Router route
handler:

```ts
// app/callback/route.ts
import { handleAuth } from '@workos-inc/authkit-nextjs';

export const GET = handleAuth({ returnPathname: '/dashboard' });
```

Set a default Logout URI in the WorkOS dashboard before using sign-out. For
reverse proxies or dynamic deployments, review `baseURL` and the proxy or
middleware `redirectUri` override.

### Preserve proxy response semantics

When composing custom proxy logic, call `authkit(request)`, then pass every
response through `handleAuthkitHeaders(request, headers, options)`. For
rewrites, use `partitionAuthkitHeaders` and `applyResponseHeaders`. Never expose
or forward injected `x-workos-*` request values.

Enable route protection with `middlewareAuth.enabled`; place public routes in
`unauthenticatedPaths`, and use `signUpPaths` for protected routes that should
show the sign-up screen.

### Read and refresh authentication

- Use `withAuth()` in server components.
- Import `AuthKitProvider` and `useAuth` from
  `@workos-inc/authkit-nextjs/components` in client components.
- Pass `ensureSignedIn: true` when authentication is mandatory.
- Remove the access token from server `initialAuth` before passing it to the
  provider.
- Use `refreshSession` on the server and
  `refreshAuth({ organizationId })` on the client.
- Use `useAccessToken` for expiry-aware access and explicit refresh state.

Use `eagerAuth: true` only when an access token must exist on the first client
render. It transfers the token through a 30-second, initial-page-load-only
cookie that client JavaScript consumes and deletes; apply normal XSS controls.

## AuthKit React quick reference

Configure `AuthKitProvider` with the public client ID, dashboard redirect URI,
and allowed application origin. In production, set `apiHostname` to an owned
Authentication API domain. `devMode` stores tokens in local storage and is
automatic only on `localhost` and `127.0.0.1`.

Use `useAuth()` for the user, organization, roles, permissions, feature flags,
impersonator, authentication method, tokens, and organization switching. Catch
`LoginRequiredError` when `getAccessToken()` is called while signed out.

## Public-client PKCE quick reference

Browser, mobile, and CLI applications can construct the Node client with only a
client ID. Generate the authorization URL and verifier together, retain the
verifier in secure platform storage across restarts, and supply it during code
exchange:

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

- Model scoped access with authorization resources and resource-scoped custom
  roles; pass `resource_type_slug` when creating an organization role.
- Pass `role_slug` on invitations.
- Filter assignment lists by `resource` and `role_slug`.
- Inspect assignment `source` to distinguish direct grants from group grants.
- Expect organization memberships to hold multiple roles from AuthKit, SSO, or
  Directory Sync.
- Use the Feature Flags runtime client for local evaluation when an API request
  per decision is undesirable.

## Webhook and data-integrity checklist

- Verify webhook signatures against raw request bytes. Do not decode,
  normalize, or reserialize the payload first.
- Handle API-key deletion as `api_key.revoked`, not `api_key.deleted`.
- Accept typed organization-role, permission, feature-flag, Vault, group, and
  domain-verification-failure events, including
  `vault.byok_key.verification_completed`.
- Read `resourceTypeSlug` from deserialized role events.
- Preserve SSO context on authentication events and `verification_prefix` on
  organization domains.
- Preserve typed server and authentication error data.
- Use exported `ConflictException.code` and the complete
  `isAuthenticationErrorData` guard.
- Treat the normalized provider value as `GitHubOAuth`, not `GithubOAuth`.

## Product selection quick reference

- Use AuthKit for hosted user authentication, including MCP authorization.
- Use Standalone OAuth to add OAuth while retaining an existing authentication
  system.
- Use Connect for delegated application authorization and organization
  selection.
- Use Pipes for end-user third-party connections or a deployable MCP server
  that grants time-limited connection access.
- Use Radar for signup risk controls and SMS challenges.
- Use Vault BYOK with AWS KMS or Azure Key Vault for customer-managed keys.

## Final verification

Before shipping, verify runtime compatibility, SDK response types, dashboard
configuration, callback cookies and state, redirect behavior, session refresh,
raw-body webhook verification, pagination shapes, retry behavior, and the exact
event names consumed by the application.
