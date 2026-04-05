---
name: workos-knowledge-patch
description: "WorkOS changes since training cutoff (latest: Node SDK v8.10, AuthKit Next.js v3) -- AuthKit proxy/middleware, PKCE, createWorkOS factory, client components, React SPA auth. Load before working with WorkOS."
version: "8.10"
license: MIT
metadata:
  author: Nevaberry
---

## Index

| Topic | Reference | Key features |
|---|---|---|
| AuthKit Next.js | [references/authkit-nextjs.md](references/authkit-nextjs.md) | Proxy/middleware, composable auth, client hooks, session management, eager auth, API key validation |
| AuthKit React (SPA) | [references/authkit-react.md](references/authkit-react.md) | Provider setup, sign-in endpoint, multi-org switching, feature flags, token refresh lifecycle |
| Node SDK v8 | [references/node-sdk-v8.md](references/node-sdk-v8.md) | PKCE auth, createWorkOS factory, Cloudflare Workers, breaking changes from v7 |
| Python & Go SDKs | [references/sdk-python-go.md](references/sdk-python-go.md) | WorkOSClient (Python), AsyncWorkOSClient, per-package Go SDK |

---

## Quick Reference

### AuthKit Next.js -- Proxy vs Middleware

| Next.js version | File | Export |
|---|---|---|
| 16+ | `proxy.ts` | `authkitProxy()` |
| <=15 | `middleware.ts` | `authkitMiddleware()` |

For composable proxy/middleware, use `authkit()` + `handleAuthkitHeaders()`:

```ts
import { authkit, handleAuthkitHeaders } from '@workos-inc/authkit-nextjs';

export default async function proxy(request: NextRequest) {
  const { session, headers, authorizationUrl } = await authkit(request);
  if (!session.user && authorizationUrl) {
    return handleAuthkitHeaders(request, headers, { redirect: authorizationUrl });
  }
  return handleAuthkitHeaders(request, headers);
}
```

For rewrites, use `partitionAuthkitHeaders()` + `applyResponseHeaders()` instead.

### Custom State Through Auth Flow

Pass custom data through OAuth via `state` parameter:

```ts
const signInUrl = await getSignInUrl({
  state: JSON.stringify({ teamId: 'team_123', referrer: 'homepage' }),
});

export const GET = handleAuth({
  onSuccess: async ({ user, state }) => {
    const data = state ? JSON.parse(state) : null;
  },
});
```

### Session Refresh Callbacks

```ts
const { session, headers } = await authkit(request, {
  onSessionRefreshSuccess: async ({ accessToken, user, impersonator }) => { /* ... */ },
  onSessionRefreshError: async ({ error, request }) => { /* ... */ },
});
```

### AuthKit Client Components

All client-side imports use the `/components` subpath:

```tsx
import { AuthKitProvider, Impersonation } from '@workos-inc/authkit-nextjs/components';
import { useAuth, useAccessToken } from '@workos-inc/authkit-nextjs/components';
```

### Node SDK v8 -- Client Types

```ts
import { createWorkOS } from '@workos-inc/node';

// Public client (PKCE only, no server APIs)
const pub = createWorkOS({ clientId: 'client_123' });

// Confidential client (full API access)
const srv = createWorkOS({ apiKey: 'sk_...', clientId: 'client_123' });
```

For Cloudflare Workers: `import { WorkOS } from '@workos-inc/node/worker';`

### PKCE Authentication (Public Clients)

```ts
const workos = new WorkOS({ clientId: 'client_123' }); // no apiKey

const { url, state, codeVerifier } =
  await workos.userManagement.getAuthorizationUrlWithPKCE({
    redirectUri: 'myapp://callback',
    provider: 'authkit',
  });

// After callback:
const { accessToken, refreshToken, user } =
  await workos.userManagement.authenticateWithCode({
    code: authCode,
    codeVerifier, // required for PKCE
  });
```

### Key Breaking Changes (v7 to v8)

| Area | Change |
|---|---|
| Runtime | Node.js 20+ required (was 16+) |
| SSO | `getAuthorizationUrl` options: discriminated union -- specify one of `connection`, `organization`, `provider` |
| Directory Sync | User fields (`emails`, `username`, `jobTitle`) moved to `customAttributes` |
| MFA | `verifyFactor()` renamed to `verifyChallenge()` |
| Vault | All `*Secret()` methods renamed to `*Object()` |
| PKCE | Always enabled in AuthKit v3 -- remove `WORKOS_ENABLE_PKCE` env var |

### User Management Renames (v7 to v8)

| v7 | v8 |
|---|---|
| `sendMagicAuthCode()` | `createMagicAuth()` |
| `sendPasswordResetEmail()` | `createPasswordReset()` |
| `refreshAndSealSessionData()` | `loadSealedSession()` then `session.refresh()` |

### AuthKit React (SPA) Essentials

Wrap app in `AuthKitProvider` with `clientId`. Set `apiHostname` for custom auth domains in production.

```tsx
import { useAuth } from '@workos-inc/authkit-react';
const { user, signIn, signOut, role, roles, featureFlags, permissions } = useAuth();

// Multi-org switching
const { switchToOrganization } = useAuth();
await switchToOrganization({ organizationId: 'org_123' });
```

Token refresh control: `onBeforeAutoRefresh: () => boolean`, `onRefreshFailure: ({ signIn }) => void`, `refreshBufferInterval: number`.

### Python & Go SDK Patterns

```python
# Python -- uses WorkOSClient, not WorkOS
from workos import WorkOSClient

client = WorkOSClient(api_key="sk_1234", client_id="client_1234")

# Async
from workos import AsyncWorkOSClient

async_client = AsyncWorkOSClient(api_key="sk_1234", client_id="client_1234")
```

```go
// Go v6 -- per-package configuration, no unified client
import "github.com/workos/workos-go/v6/pkg/sso"
sso.Configure("<API_KEY>", "<CLIENT_ID>")
```

---

## Reference Files

| File | Contents |
|---|---|
| [authkit-nextjs.md](references/authkit-nextjs.md) | Proxy migration, composable middleware, client hooks, useAccessToken, session callbacks, eager auth, validateApiKey, saveSession |
| [authkit-react.md](references/authkit-react.md) | SPA provider, sign-in endpoint, multi-org, feature flags, getClaims, token refresh, URL helpers |
| [node-sdk-v8.md](references/node-sdk-v8.md) | PKCE auth, createWorkOS factory, Cloudflare Workers, all breaking changes v7 to v8, post-v8 additions |
| [sdk-python-go.md](references/sdk-python-go.md) | Python WorkOSClient/AsyncWorkOSClient, Go per-package SDK pattern |
