# AuthKit for React

Use this reference for browser-side provider configuration, hosted sign-in,
authentication state, organization switching, token refresh, and redirects.

## Configure the provider

Initialize `@workos-inc/authkit-react` with a public client ID, a redirect URI
registered in the dashboard, and the application's allowed origin.

Set `AuthKitProvider.apiHostname` to an owned Authentication API domain in
production. `devMode` stores tokens in local storage; it turns on automatically
only for `localhost` and `127.0.0.1`.

## Provide a login endpoint

Externally initiated sign-in and impersonation flows require a dashboard
sign-in endpoint such as `/login`. That route must call `signIn()` to start the
hosted OAuth flow.

## Read authentication state

`useAuth()` exposes:

- the current user and organization;
- `role`, `roles`, permissions, and feature flags;
- the impersonator and authentication method;
- token-aware `getAccessToken` and synchronous `getUser`;
- URL-only `getSignInUrl` and `getSignUpUrl`; and
- `switchToOrganization({ organizationId, signInOpts? })`.

Sign-in and sign-up options accept state, organization, login hint, invitation
token, and screen hint.

## Redirect state

React auth state may be an object and is recovered in `onRedirectCallback`.
This differs from the Next.js helper, whose callback state is an opaque string.

## Refresh and inspect tokens

Use `onRefresh`, `onRefreshFailure`, `onBeforeAutoRefresh`, and
`refreshBufferInterval` to control renewal. `getClaims(token)` decodes access
token claims. Calling `getAccessToken()` while signed out throws
`LoginRequiredError`; handle that error explicitly.
