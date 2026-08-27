---
name: workos-knowledge-patch
description: WorkOS
version: "8.10"
license: MIT
metadata:
  author: Nevaberry
---


# WorkOS Knowledge Patch

Use this skill when implementing, upgrading, or reviewing a WorkOS integration.
Start with migration hazards, then load only the references relevant to the SDK,
framework, and WorkOS products in use.

## Reference index

| Reference | Topics |
| --- | --- |
| [node-sdk-migrations.md](references/node-sdk-migrations.md) | Node runtime and v9/v10 migrations, events, errors, pagination, webhooks, Vault, Radar, Connect, Agents, retries |
| [authkit-nextjs.md](references/authkit-nextjs.md) | App Router, callbacks, cookies, proxy or middleware, response headers, caching, sessions, access tokens, PKCE |
| [authkit-react.md](references/authkit-react.md) | Browser provider setup, redirects, auth state, organization switching, refresh hooks, token helpers |
| [api-and-sdk-contracts.md](references/api-and-sdk-contracts.md) | Public-client PKCE, Python async client, Go v6 packages, OpenAPI contract |
| [authentication-and-sessions.md](references/authentication-and-sessions.md) | Identity data, AuthKit customization, applications, sessions, invitations, email lifecycle, OAuth, Radar |
| [authorization-and-features.md](references/authorization-and-features.md) | Roles, authorization resources, group assignments, permissions, multi-role provisioning, Feature Flags |
| [sso-directory-and-widgets.md](references/sso-directory-and-widgets.md) | SSO lifecycle and providers, Directory Sync, identity-provider attributes, domains, embedded widgets |
| [platform-products.md](references/platform-products.md) | Connect, MCP, CLI, Pipes, Vault BYOK, Audit Logs, API keys, email delivery, analytics, Stripe |

## Triage the integration

1. Identify the SDK language and version, framework version, and WorkOS products.
2. Apply breaking migrations before adding features.
3. Load the topic references that match the integration surface.
4. Preserve raw payloads, OAuth security state, and internal response headers as
   required by the framework.
5. Verify dashboard-side settings: redirect and logout URIs, allowed origins,
   domains, providers, sign-in endpoints, cookie sharing, and OAuth scopes.

## Breaking changes and deprecations

### Migrate Node SDK v9

- Run Node.js 22.11 or newer; v9 no longer supports Node.js 20.
- Replace the removed legacy FGA package with authorization resources and role
  APIs. FGA was deprecated in v8.4 and removed in v9.
- Rename client access from `portal` to `adminPortal`.
- Keep the established Authorization method names. v9.1.1 reverted generated
  renames and fixed the endpoint for `listEffectivePermissionsByExternalId`.

### Migrate Node SDK v10

- Treat `Group.createdAt` and `Group.updatedAt` as `Date`, not strings.
- Construct webhooks from the WorkOS client: `new Webhooks(workos)`.
- Remove `search` from `listResources` calls.
- Consume `vault.listObjects` as an auto-paginatable collection of object
  summaries; generated key and object response fields are camel-cased.

### Update event handling

- Handle API-key deletion as `api_key.revoked`, not `api_key.deleted`.
- Accept typed events for organization roles and permissions, feature flags,
  Vault, groups, and domain-verification failures.
- Handle `vault.byok_key.verification_completed`.
- Read `resourceTypeSlug` from deserialized organization-role events.

### Enforce AuthKit Next.js v3 state checks

- Remove `WORKOS_ENABLE_PKCE`; PKCE and sealed OAuth state are always enabled.
- Preserve the short-lived `wos-auth-verifier` cookie through the callback.
- Treat a missing verifier as `Auth cookie missing` and a mismatch as
  `OAuth state mismatch`; do not restore the removed URL-state-only fallback.

### Select the Next.js request hook

- For Next.js 16 or newer, define root-level `proxy.ts` with `authkitProxy`.
- For earlier Next.js versions, define `middleware.ts` with `authkitMiddleware`.
- Exclude `/_next/static`, `/_next/image`, and `favicon.ico` from broad matchers.

## Recent Node SDK contracts

For SDK changes identified by batch `10.10.0`:

- Action contexts expose the authentication method.
- Agents can link a claim attempt to an external user, read agent
  registrations, and validate credentials; API-key validation returns the agent
  registration ID.
- User API-key methods are available, and `ApiKey.owner` includes a user variant
  and `organizationId`.
- `CookieSession.refresh()` distinguishes retryable transient failures from
  terminal failures.
- Listed `AuthenticationFactor` values may omit `totp`.
- The HTTP client supports configurable automatic retries.
- Pipes supports API-key installation and Data Integration operations and models.
- DELETE calls preserve query parameters supplied through `{ query: ... }`.

## AuthKit Next.js quick reference

### Configure the App Router flow

Provide a client ID, API key, public redirect URI, and session-cookie password
of at least 32 characters. Create the callback as an App Router route handler:

```ts
// app/callback/route.ts
import { handleAuth } from '@workos-inc/authkit-nextjs';

export const GET = handleAuth({ returnPathname: '/dashboard' });
```

Set a default Logout URI in the WorkOS dashboard before relying on sign-out.
Use `baseURL` when an internal request host differs from the public host.

### Preserve proxy response semantics

For custom proxy logic, call `authkit(request)` and pass every response through
`handleAuthkitHeaders(request, headers, options)`. For rewrites, use
`partitionAuthkitHeaders` and `applyResponseHeaders`. Never expose or forward
injected `x-workos-*` request values.

Enable route protection with `middlewareAuth.enabled`; put public routes in
`unauthenticatedPaths`, and use `signUpPaths` for protected routes that should
show the sign-up screen.

### Read and refresh authentication

- Use `withAuth()` in server components.
- Import `AuthKitProvider` and `useAuth` from
  `@workos-inc/authkit-nextjs/components` in client components.
- Pass `ensureSignedIn: true` where authentication is mandatory.
- Remove the access token from server `initialAuth` before passing it to the
  provider.
- Use `refreshSession` on the server and
  `refreshAuth({ organizationId })` on the client.
- Use `useAccessToken` for expiry-aware access, manual refresh, and refresh state.

Use `eagerAuth: true` only when the initial client render needs an access token.
It transfers the token in a 30-second initial-page-load-only cookie that client
JavaScript consumes and deletes, so maintain normal XSS defenses.

## AuthKit React quick reference

Configure `AuthKitProvider` with the public client ID, dashboard redirect URI,
and allowed application origin. In production, set `apiHostname` to an owned
Authentication API domain. Treat `devMode` as local-development token storage;
it is automatic only on `localhost` and `127.0.0.1`.

Use `useAuth()` for user and organization state, roles, permissions, feature
flags, impersonator, authentication method, token access, and organization
switching. Catch `LoginRequiredError` when `getAccessToken()` is called while
signed out.

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

Confidential clients may use the same flow with an API key; exchange then sends
both the client secret and verifier.

## Authorization quick reference

- Model scoped access with authorization resources and resource-scoped custom
  roles. Supply `resource_type_slug` when creating an organization role.
- Pass `role_slug` on invitations.
- Filter assignment lists with `resource` and `role_slug`.
- Inspect assignment `source` to distinguish direct grants from group grants.
- Expect memberships to hold multiple roles provisioned by AuthKit, SSO, or
  Directory Sync.
- Use the Feature Flags runtime client for local evaluation when a network
  request per evaluation is undesirable.

## Webhook and data-integrity checklist

- Verify signatures against raw request bytes; do not decode, normalize, or
  reserialize the payload first.
- Preserve SSO context on authentication events.
- Preserve `verification_prefix` on organization domains.
- Expect server and authentication errors to retain typed data.
- Use exported `ConflictException.code` and the complete
  `isAuthenticationErrorData` guard.
- Treat the normalized identity-provider value as `GitHubOAuth`, not
  `GithubOAuth`.

## Product selection quick reference

- Use AuthKit for hosted user authentication, including MCP authorization.
- Use Standalone OAuth for a server that retains its existing authentication.
- Use Connect for delegated application authorization and organization choice.
- Use Pipes for end-user third-party connections or a deployable MCP server with
  time-limited connection access.
- Use Radar for signup risk controls and SMS challenges.
- Use Vault BYOK with AWS KMS or Azure Key Vault for customer-managed keys.

## Final verification

Before shipping, verify runtime compatibility, dashboard configuration,
callback cookies and state, redirect behavior, session refresh, raw-body webhook
verification, pagination shapes, retry behavior, and exact event names.
