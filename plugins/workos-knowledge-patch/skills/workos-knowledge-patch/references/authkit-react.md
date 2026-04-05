# AuthKit React (SPA)

## Package & Provider Setup

`@workos-inc/authkit-react` is the client-side SPA package (separate from the Next.js one). Wrap your app in `AuthKitProvider` with `clientId`. Set `apiHostname` to your custom auth domain in production (e.g. `auth.example.com`). `devMode` auto-enables on localhost/127.0.0.1 (stores tokens in localStorage).

## Sign-In Endpoint for External Flows

Register a `/login` URL as the **sign-in endpoint** in WorkOS Dashboard. External-initiated flows (admin impersonation, third-party SSO) redirect here. Your `/login` route must call `signIn()` to start OAuth:

```jsx
function LoginRoute() {
  const { signIn } = useAuth();
  useEffect(() => { signIn(); }, [signIn]);
  return <div>Redirecting...</div>;
}
```

## Multi-Organization Switching

`switchToOrganization({ organizationId })` re-authenticates with a different org context. `useAuth()` exposes both `role` (string) and `roles` (string array -- all roles in current org).

## Feature Flags & Permissions from JWT

`useAuth()` returns `featureFlags: string[]` (org-level flags) and `permissions: string[]` alongside roles. These are decoded from the access token JWT claims.

## getClaims Utility

```ts
import { getClaims } from '@workos-inc/authkit-react';
const claims = getClaims(accessToken);
// claims.sub, claims.org_id, claims.role, claims.permissions, etc.
```

## Token Refresh Lifecycle

- `onBeforeAutoRefresh: () => boolean` -- return `false` to skip automatic refresh (e.g. when app is backgrounded)
- `onRefreshFailure: ({ signIn }) => void` -- session expired, receives `signIn` to re-authenticate
- `refreshBufferInterval: number` -- seconds before expiry to trigger refresh

## URL Helpers Without Redirect

`getSignInUrl(opts?)` and `getSignUpUrl(opts?)` return the auth URL as a string without navigating. Useful for custom link elements or programmatic flows.
