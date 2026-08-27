# AuthKit for React

## Provider configuration

Initialize `@workos-inc/authkit-react` with a public client ID, a dashboard
redirect URI, and the application's allowed origin. Set
`AuthKitProvider.apiHostname` to an owned Authentication API domain in
production.

`devMode` stores tokens in local storage. It activates automatically only on
`localhost` and `127.0.0.1`; treat it as a local-development facility.

Externally initiated and impersonation flows need a dashboard sign-in endpoint,
such as `/login`. Its route must call `signIn()` to start the hosted OAuth flow.

## Auth state and organizations

`useAuth()` exposes:

- the current user and organization;
- `role`, `roles`, permissions, and feature flags;
- impersonator and authentication method;
- token-aware `getAccessToken` and synchronous `getUser`;
- URL-only `getSignInUrl` and `getSignUpUrl`; and
- `switchToOrganization({ organizationId, signInOpts? })`.

Sign-in and sign-up options support state, organization, login hint, invitation
token, and screen hint.

## Redirect state

React state may be an object and is recovered in `onRedirectCallback`. This
differs from the Next.js helper, whose state value is an opaque string.

## Refresh and token helpers

Use `onRefresh`, `onRefreshFailure`, `onBeforeAutoRefresh`, and
`refreshBufferInterval` to control token renewal. `getClaims(token)` decodes
access-token claims. Calling `getAccessToken()` while signed out throws
`LoginRequiredError`.
