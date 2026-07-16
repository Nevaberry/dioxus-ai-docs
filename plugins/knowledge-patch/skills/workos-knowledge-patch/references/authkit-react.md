# AuthKit for React

## Provider configuration

Initialize `@workos-inc/authkit-react` with:

- a public client ID;
- a dashboard-configured redirect URI; and
- the application's allowed origin.

Set `AuthKitProvider.apiHostname` to an owned Authentication API domain in
production. `devMode` stores tokens in local storage; it is enabled
automatically only on `localhost` and `127.0.0.1`.

Externally initiated and impersonation flows require a dashboard sign-in
endpoint such as `/login`. That route must call `signIn()` to begin the
hosted OAuth flow.

## Authentication state

`useAuth()` exposes:

- the current user and organization;
- `role`, `roles`, permissions, and feature flags;
- the impersonator and authentication method;
- token-aware `getAccessToken`;
- synchronous `getUser`;
- URL-only `getSignInUrl` and `getSignUpUrl`; and
- `switchToOrganization({ organizationId, signInOpts? })`.

Sign-in and sign-up options support state, organization, login hint, invitation
token, and screen hint.

## Redirect state and organization switching

React authentication state may be an object. Recover it in
`onRedirectCallback`. This differs from the opaque string state accepted by
the Next.js callback helper.

Use `switchToOrganization` to change the active organization and optionally
provide sign-in options for the transition.

## Refresh and token handling

Use provider hooks `onRefresh`, `onRefreshFailure`, and
`onBeforeAutoRefresh` to control renewal behavior. Set
`refreshBufferInterval` to control how early renewal begins.

Decode access-token claims with `getClaims(token)`. When signed out,
`getAccessToken()` throws `LoginRequiredError`; handle that typed error
rather than treating the result as an empty token.
