# Authentication and sessions

## Authentication-option persistence and passkeys

Disabling password authentication affects only new users; existing users retain
password sign-in. SMS begins with only the United States and Canada enabled.
Passkeys can be created only after sign-up, cannot be an MFA factor, and are
limited to 10 per account.

## Trusted-device biometric authentication

Trusted-device support from batch `2026-07-31-2026-08-17` lets Expo, iOS, and
Android enroll a signed-in user's current device and later authenticate through
Face ID, Touch ID, or Android biometrics. The device-bound private key stays on
the device. Prebuilt authentication and profile views can expose enrollment,
sign-in, and current-device controls. Custom integrations use
`useTrustedDevices()` on Expo, `Clerk.shared.trustedDevices` on iOS, and
`Clerk.trustedDevices` on Android.

```ts
import { useTrustedDevices } from '@clerk/expo'
const { enroll } = useTrustedDevices()
await enroll()
```

## Social providers and token refresh

X/Twitter sign-in now supplies the user's email rather than requiring a manual
email step. Development instances can enable the connection without separate
provider configuration.

Use `additionalOAuthScopes` on `<UserProfile />` or inside
`<UserButton userProfileProps>` to prompt an existing user to reconnect with
more scopes. Provider access tokens are server-only. Clerk attempts to refresh
access and refresh tokens only when `getUserOauthAccessToken()` is called; it
does not refresh proactively.

```tsx
<UserProfile additionalOAuthScopes={{ github: ['qux'] }} />
```

## Bot protection

Cloudflare challenges are unsupported in non-browser environments such as Expo
and Chrome extensions; disable bot protection there. A custom browser sign-up
flow must render `<div id="clerk-captcha" />` whenever bot protection is enabled.

## Restriction matching

- An enabled empty allowlist blocks every sign-up.
- An allowlist match wins when an identifier is also blocklisted.
- Blocking an email also blocks its `+`, `#`, and `=` subaddresses.
- `*@*.clerk.dev` matches subdomains.
- The separate subaddress restriction detects Gmail dot variants of an
  existing account.

## Enterprise identifiers and account linking

SAML requires an exact email-domain match unless subdomains are enabled on an
eTLD+1 connection. Additional identifiers are off by default for SAML and OIDC;
EASIE permits only one identifier. IdP email addresses count as verified. A
matching verified Clerk address links automatically. A matching unverified
address is verified and linked when verification is not required; otherwise a
separate user is created.

## EASIE deprovisioning

EASIE supports Google Workspace and Microsoft Entra ID, with shared credentials
in development and required custom credentials in production. Before minting a
new session token, Clerk checks provider deprovisioning with up to a ten-minute
delay. Detection revokes existing sessions and makes new-token requests return
HTTP 401.

## Directory Sync lifecycle

The beta Directory Sync feature is configured per SAML or OIDC enterprise
connection and uses SCIM 2.0 to create, update, disable, and delete users. A
SCIM disable or delete immediately revokes sessions. Synced fields are
read-only in Clerk. Group sync and custom attribute mapping are unsupported in
this SCIM flow.

## Clerk as an OAuth/OIDC provider

An instance publishes OAuth discovery at
`/.well-known/oauth-authorization-server`, user information at
`/oauth/userinfo`, and token information at `/oauth/token_info`. OAuth access
and OIDC ID tokens expire after one day, authorization codes after ten minutes,
and refresh tokens do not expire. Access tokens default to JWTs but may be
opaque for immediate revocation.

OAuth client secrets are shown once. Dynamic client registration exposes a
public unauthenticated registration endpoint and forces the consent screen on.
Available scopes are `profile`, `email`, `public_metadata`, `private_metadata`,
and `openid`; custom scopes are unavailable. Public clients can exchange codes
without a secret and should use PKCE.

Client ID Metadata Documents let a beta-enabled public OAuth or MCP client use
an HTTPS metadata-document URL as `client_id`. Clerk fetches it to validate the
client and redirect URIs, avoiding a pre-issued ID, secret, or dynamic
registration. Dashboard settings can preapprove URL identities and scopes,
allow or block unknown clients, inspect fetch health, refresh saved metadata,
advertise CIMD in authorization-server metadata, and require preregistration.

## Reverification

Server code checks factor age with `auth.has()` and returns a matching
reverification error. Client code wrapped by `useReverification()` presents the
modal and retries. Password, email code, phone code, TOTP, and backup codes are
supported. A requested second- or multi-factor level downgrades to first-factor
verification if the user has no second factor.

```ts
const { has } = await auth.protect()
if (!has({ reverification: 'strict' })) return reverificationError('strict')
const protectedAction = useReverification(myAction)
```

`factorVerificationAge` is `[firstFactorAge, secondFactorAge]` in minutes. Raw
flows call `Session.startVerification({ level: 'first_factor' })`, select a
strategy from `supportedFirstFactors`, and invoke the matching prepare and
attempt methods. For email code, pass the factor's `emailAddressId` to
`prepareFirstFactorVerification()`, then submit `code` with
`attemptFirstFactorVerification()`. Expo's prebuilt modal is web-only; native
mobile must pass `onNeedsReverification` to `useReverification()` and invoke
its `complete` or `cancel` callback.

## Session-token version 2

Version 1 was deprecated on April 14, 2025. Version 2 adds `v`, Plan `pla`,
Feature list `fea`, session status `sts`, and a compact `o` object only when an
Organization is active. In `o.fpm`, each comma-separated integer aligns with
the same-position Feature in `fea` and encodes a least-significant-bit-first
Permission mask over `o.per`. SDKs supporting API version `2025-04-10` decode
this automatically.

```json
{ "v": 2, "fea": "o:dashboard,o:teams", "sts": "pending",
  "o": { "rol": "admin", "per": "manage,read", "fpm": "3,2" } }
```

## Enumeration-safe sign-in-or-up

`signIn.create({ identifier, signUpIfMissing: true })` verifies before revealing
whether an account exists. For a missing account, verification returns
`sign_up_if_missing_transfer`; call `signUp.create({ transfer: true })` to keep
the verified identifier. This works with email, phone, or Web3 on public-sign-up
instances, but excludes passwords, usernames, restricted mode, and waitlist.

The embedded `<SignIn />` combined flow also supports strict enumeration
protection without another prop. The instance must use Open access, cannot use
username identifiers, and cannot begin with password; disable password or
prefer OTP. Development reports the invalid password-preferred combination as
`sign_up_if_missing_password_preferred`. Account Portal does not support this
combined flow.

## Pending sessions and session tasks

Organization selection, forced-password reset, or required-MFA enrollment can
leave a session `pending`. Pending sessions are signed-out by default: IDs are
null and protected routes reject them. Prebuilt flows embed task components;
custom flows must inspect `session.currentTask` after finalization. Set
`treatPendingAsSignedOut: false` only in code intentionally handling pending
identity.

```ts
await signIn.finalize({ navigate: ({ session }) => {
  if (session?.currentTask) return router.push('/session-tasks')
} })
const state = await auth({ treatPendingAsSignedOut: false })
```
