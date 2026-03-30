# Node SDK v8

## PKCE Authentication (Public Clients)

v8 adds PKCE for mobile/desktop/SPA apps without exposing API keys. Initialize with `clientId` only (no `apiKey`):

```ts
import { WorkOS } from '@workos-inc/node';

const workos = new WorkOS({ clientId: 'client_123' });

// Automatic PKCE (recommended)
const { url, state, codeVerifier } =
  await workos.userManagement.getAuthorizationUrlWithPKCE({
    redirectUri: 'myapp://callback',
    provider: 'authkit',
  });
// Store codeVerifier securely, redirect user to url

// After callback:
const { accessToken, refreshToken, user } =
  await workos.userManagement.authenticateWithCode({
    code: authCode,
    codeVerifier, // required for PKCE
  });
```

Manual PKCE: `workos.pkce.generate()` returns `{ codeVerifier, codeChallenge }` for use with `getAuthorizationUrl({ codeChallenge, codeChallengeMethod: 'S256' })`.

## createWorkOS() Type-Safe Factory

Compile-time enforcement of public vs confidential client capabilities:

```ts
import { createWorkOS } from '@workos-inc/node';

// Public client -- only PKCE/auth URL methods available
const pub = createWorkOS({ clientId: 'client_123' });
pub.userManagement.getAuthorizationUrlWithPKCE({ ... }); // OK
pub.userManagement.listUsers(); // TypeScript error

// Confidential client -- full API
const srv = createWorkOS({ apiKey: 'sk_...', clientId: 'client_123' });
srv.userManagement.listUsers(); // OK
```

## Cloudflare Workers

```ts
import { WorkOS } from '@workos-inc/node/worker';
```

## Breaking Changes (v7 to v8)

**Node.js 20+ required** (was 16+). ESM-first with CJS still supported via conditional exports. Deep imports removed -- use public API only.

### Directory Sync

User fields (`emails`, `username`, `jobTitle`) moved to `customAttributes`. `getPrimaryEmail()` helper removed -- use `user.customAttributes?.emails?.[0]`.

### User Management

- `sendMagicAuthCode()` renamed to `workos.userManagement.createMagicAuth()`
- `sendPasswordResetEmail()` renamed to `workos.userManagement.createPasswordReset()`
- `refreshAndSealSessionData()` replaced by `loadSealedSession()` then `session.refresh()`
- `getAuthorizationUrl`: `context` field removed (use `state`)
- `listOrganizationMemberships()` now requires `userId` or `organizationId`

### SSO

`getAuthorizationUrl` options are a **discriminated union** -- specify exactly one of `connection`, `organization`, or `provider`. `domain` field removed (use `organization`).

### MFA

`verifyFactor()` renamed to `verifyChallenge()`.

### Organizations

`allowProfilesOutsideOrganization` removed. `domains` changed to `domainData: [{ domain: 'example.com', state: 'verified' }]`. `LegacyVerified` domain state removed.

### Vault

All `*Secret()` methods renamed to `*Object()` (createObject, listObjects, readObject, etc.).

### Events

`dsync.deactivated` renamed to `dsync.deleted`. `OrganizationMembershipAdded`/`Removed` events removed.

## Post-v8.0 Additions (v8.2-v8.10)

**Authorization Resources & Roles (v8.2-v8.4)**: New `authorizationResources` module with environment roles and organization roles. FGA module deprecated in favor of Authorization Resources. `resourceTypeSlug` added to permissions and roles.

**Events (v8.3-v8.7)**: Organization role/permission events, feature flag events, vault events. `api_key.deleted` renamed to `api_key.revoked`.

**User Management (v8.8-v8.9)**: `claimNonce` parameter added to `getAuthorizationUrl`. `directoryManaged` boolean added to `OrganizationMembership`. `CookieSession` exported from package root.
