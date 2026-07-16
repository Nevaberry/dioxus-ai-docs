# Authentication and sessions

## Authentication option behavior

- Disabling password authentication affects only new users; existing users may continue signing in with passwords.
- SMS starts with only the United States and Canada enabled.
- Passkeys can be created only after sign-up, cannot serve as MFA, and are limited to 10 per account.
- X/Twitter sign-in now returns the user's email instead of requiring a separate email step. Development instances can enable X/Twitter without additional provider configuration.

## Social provider scopes and tokens

Prompt an existing user to reconnect a provider with additional scopes by setting `additionalOAuthScopes` on `<UserProfile />` or inside `<UserButton userProfileProps>`.

```tsx
<UserProfile additionalOAuthScopes={{ github: ['qux'] }} />
```

Provider access tokens are available only on the server. Clerk attempts a provider token refresh only when `getUserOauthAccessToken()` is called; it does not refresh proactively.

```ts
const result = await client.users.getUserOauthAccessToken(userId, 'github')
const token = result.data[0].token
```

## Bot protection

The Cloudflare challenge is unsupported outside browsers, including Expo and Chrome extensions. Disable bot protection for those applications. A custom browser sign-up flow must render the challenge mount point whenever bot protection is enabled:

```html
<div id="clerk-captcha"></div>
```

## Allowlist, blocklist, and subaddress rules

- An enabled but empty allowlist blocks every sign-up.
- An allowlist match wins when the same identifier is blocklisted.
- Blocking one email also blocks its `+`, `#`, and `=` subaddresses.
- A rule such as `*@*.clerk.dev` covers subdomains.
- The dedicated subaddress restriction also recognizes Gmail dot variants of an existing account.

## Enterprise identifiers and linking

SAML requires an exact email-domain match unless subdomains are enabled on an eTLD+1 connection. Additional identifiers are disabled by default for SAML and OIDC; EASIE permits only one identifier.

An IdP email is treated as verified:

- A matching verified Clerk address links automatically.
- A matching unverified address is verified and linked when application verification is not required.
- Otherwise Clerk creates a separate user.

An `EmailAddress` can start an Enterprise SSO email-link flow and poll for completion. Keep the returned cancellation function so custom UI can stop polling.

```ts
const { startEnterpriseSSOLinkFlow, cancelEnterpriseSSOLinkFlow } =
  emailAddress.createEnterpriseSSOLinkFlow()
await startEnterpriseSSOLinkFlow({ redirectUrl })
// call cancelEnterpriseSSOLinkFlow() during cleanup if still pending
```

## EASIE deprovisioning

EASIE supports Google Workspace and Microsoft Entra ID, using shared credentials in development and required custom credentials in production. Before issuing a new session token, Clerk checks whether the provider deprovisioned the user. Detection can take up to 10 minutes; after detection, existing sessions are revoked and token requests return HTTP 401.

## Directory Sync

Directory Sync is a beta feature configured per SAML or OIDC enterprise connection. It uses SCIM 2.0 to create, update, disable, and delete users.

- Disabling or deleting a SCIM user revokes sessions immediately.
- Synced fields become read-only in Clerk.
- Group sync and custom attribute mapping are not supported.

## Clerk as an OAuth/OIDC identity provider

An instance can expose OAuth 2.0 and OIDC identity-provider endpoints:

- Discovery: `/.well-known/oauth-authorization-server`
- Token exchange: `/oauth/token`
- User info: `/oauth/userinfo`
- Token inspection: `/oauth/token_info`

OAuth access and OIDC ID tokens expire after one day, authorization codes after 10 minutes, and refresh tokens do not expire. Access tokens default to JWTs; opaque access tokens support immediate revocation.

## OAuth application constraints

- The client secret is displayed once and cannot be retrieved later.
- Dynamic client registration exposes a public, unauthenticated registration endpoint and forces the consent screen on.
- Available scopes are `profile`, `email`, `public_metadata`, `private_metadata`, and `openid`; custom scopes are unavailable.
- Public clients may exchange codes without a client secret and should use PKCE.

OAuth application resources expose `consent_screen_enabled` and `dynamically_registered`; consent-screen behavior is configurable at creation and afterward.

## Reverification with SDK helpers

On the server, check factor age with `auth.has()` and return the matching reverification error. On the client, `useReverification()` opens the modal and retries.

```ts
const { has } = await auth.protect()
if (!has({ reverification: 'strict' })) return reverificationError('strict')

const protectedAction = useReverification(myAction)
```

Password, email code, phone code, TOTP, and backup codes can satisfy reverification. A requested second-factor or multi-factor level silently falls back to first-factor verification when the user has no second factor.

Go also provides factor-age helpers and HTTP middleware for triggering reverification.

## Raw and native reverification

`factorVerificationAge` is `[firstFactorAge, secondFactorAge]` in minutes. A custom UI starts with `Session.startVerification()`, then uses the matching prepare and attempt methods.

```ts
const verification = await session.startVerification({ level: 'first_factor' })
const email = verification.supportedFirstFactors?.find(
  (factor) => factor.strategy === 'email_code',
)
if (!email) throw new Error('Email-code reverification is unavailable')

await session.prepareFirstFactorVerification({
  strategy: 'email_code',
  emailAddressId: email.emailAddressId,
})
await session.attemptFirstFactorVerification({ strategy: 'email_code', code })
```

Expo's prebuilt reverification modal works on web only. Native mobile must pass `onNeedsReverification` to `useReverification()` and invoke the supplied `complete` or `cancel` callback.

## Session-token claim format

Session-token version 1 was deprecated on April 14, 2025. Version 2 adds:

- `v`: token version.
- `pla`: plans.
- `fea`: comma-separated features.
- `sts`: session status, including `pending`.
- `o`: compact Active Organization data, omitted when no Organization is active.

```json
{
  "v": 2,
  "fea": "o:dashboard,o:teams",
  "sts": "pending",
  "o": { "rol": "admin", "per": "manage,read", "fpm": "3,2" }
}
```

In `o.fpm`, each comma-separated integer aligns with the feature in the same position in `fea`. Each integer is a least-significant-bit-first mask over permissions in `o.per`. SDKs supporting Backend API version `2025-04-10` decode this automatically.

## JWT verification behavior

Go's `jwt.Verify` can fetch a JSON web key from `GET /v1/jwks` when none is supplied. It accepts a `jwks.Client`; cache fetched keys when reusing them. The claims API separates `RegisteredClaims`, Clerk `Claims`, and `SessionClaims`, and `jwt.Decode` exposes the key ID. Version 2 Organization claims are populated only when an Organization exists, preventing a false Organization Role.

JavaScript request authentication can use `jwtKey` for networkless verification. Environment-based integrations can use `CLERK_JWT_KEY`.

## Legacy Client Trust state

The legacy `SignIn` resource may enter `needs_client_trust` on a new device. `clientTrustState` is then present, and the flow must establish trust with a second-factor verification. This legacy resource is scheduled for removal in favor of `SignInFuture`.

## Pending sessions and session tasks

Organization selection, forced-password reset, and required-MFA enrollment can leave a session `pending`. Pending sessions are treated as signed out by default. Prebuilt flows contain task UI; custom flows must route from `session.currentTask` after finalization. Set `treatPendingAsSignedOut: false` only for code designed to process pending identity.

## Agent-created session identity

When `Session.actor.type` is `agent`, `Session.agent` identifies the agent and Agent Task behind the session. Use it to distinguish an agent-created session from ordinary user impersonation.
