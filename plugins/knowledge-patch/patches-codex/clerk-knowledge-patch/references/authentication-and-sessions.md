# Authentication and sessions

## Understand factor persistence and limits

Disabling password authentication applies only to new users; existing users can
still sign in with passwords. SMS begins with only the United States and Canada
enabled. Passkeys can be created only after sign-up, cannot be used as MFA, and
are limited to 10 per account.

## Request and refresh social-provider scopes

Use `additionalOAuthScopes` on `<UserProfile />` or under
`<UserButton userProfileProps>` to prompt an existing user to reconnect a
provider. Provider access tokens are available only on the server. Clerk tries
to refresh provider access and refresh tokens only when
`getUserOauthAccessToken()` is called; it does not refresh them proactively.

```tsx
<UserProfile additionalOAuthScopes={{ github: ['qux'] }} />
```

```ts
const result = await client.users.getUserOauthAccessToken(userId, 'github')
const token = result.data[0].token
```

## Place bot protection only in supported flows

Cloudflare challenges are unsupported in non-browser environments such as Expo
and Chrome extensions, where bot protection must be disabled. A custom browser
sign-up flow must render the challenge mount whenever bot protection is enabled:

```html
<div id="clerk-captcha"></div>
```

## Apply restriction matching precisely

- Enabling an empty allowlist blocks all sign-ups.
- An allowlist match wins if the same identifier is also blocklisted.
- Blocking one email also blocks its `+`, `#`, and `=` subaddresses.
- A rule such as `*@*.clerk.dev` covers subdomains.
- The separate subaddress restriction recognizes Gmail dot variants of an
  existing account.

## Link enterprise identifiers carefully

SAML requires an exact email-domain match unless subdomains are enabled on an
eTLD+1 connection. Additional identifiers are off by default for SAML and OIDC;
EASIE permits only one identifier.

IdP email addresses count as verified. A matching verified Clerk address links
automatically. A matching unverified address is verified and linked if
verification is not required; otherwise Clerk creates a separate user.

## Handle EASIE deprovisioning

EASIE supports Google Workspace and Microsoft Entra ID. Development can use
shared credentials; production requires custom credentials. Before issuing a
new session token, Clerk checks provider deprovisioning with up to a 10-minute
delay. Detection revokes existing sessions and makes new-token requests return
HTTP 401.

## Account for SCIM Directory Sync lifecycle

The beta Directory Sync feature is configured per SAML or OIDC enterprise
connection. SCIM 2.0 creates, updates, disables, and deletes Clerk users. A SCIM
disable or delete immediately revokes sessions, and synchronized fields become
read-only in Clerk. This integration does not support group sync or custom
attribute mapping.

## Operate Clerk as an OAuth/OIDC provider

An instance can publish OAuth 2.0 and OIDC endpoints:

- discovery: `/.well-known/oauth-authorization-server`
- user info: `/oauth/userinfo`
- token info: `/oauth/token_info`

OAuth access and OIDC ID tokens expire after one day, authorization codes after
10 minutes, and refresh tokens do not expire. Access tokens default to JWTs;
choose opaque tokens when immediate revocation is required.

An OAuth client secret is displayed once and cannot be fetched later. Dynamic
client registration publishes an unauthenticated registration endpoint and
forces the consent screen on. Available scopes are `profile`, `email`,
`public_metadata`, `private_metadata`, and `openid`; custom scopes are not
available. Public clients may exchange authorization codes without a secret and
should use PKCE.

## Use Client ID Metadata Documents for public clients

Beta Client ID Metadata Documents let a public OAuth or MCP client use an HTTPS
metadata-document URL as its `client_id`. Clerk fetches the document to validate
client identity and redirect URIs, avoiding a pre-issued ID, secret, or Dynamic
Client Registration.

After support enables the workspace beta, CIMD settings can pre-approve URL
identities and scopes, admit or block unknown clients, inspect fetch health,
refresh saved metadata, advertise CIMD in authorization-server metadata, and
optionally require every client to be registered. This item is from batch
`2026-07-31-2026-08-17`.

## Enforce reverification

Server code checks factor age with `auth.has()`, returns the corresponding
reverification error, and client code wrapped in `useReverification()` presents
the modal and retries.

```ts
const { has } = await auth.protect()
if (!has({ reverification: 'strict' })) {
  return reverificationError('strict')
}
const protectedAction = useReverification(myAction)
```

Password, email code, phone code, TOTP, and backup codes can satisfy
reverification. A requested second-factor or multi-factor level silently
downgrades to first-factor verification when the user has no second factor.

## Decode session-token version 2 claims

Session-token version 1 was deprecated on April 14, 2025. Version 2 adds `v`,
plan `pla`, feature list `fea`, session status `sts`, and a compact `o` object
only when an Organization is active.

```json
{
  "v": 2,
  "fea": "o:dashboard,o:teams",
  "sts": "pending",
  "o": { "rol": "admin", "per": "manage,read", "fpm": "3,2" }
}
```

Within `o.fpm`, each comma-separated integer aligns to the same-position
feature in `fea` and is a least-significant-bit-first permission mask over
`o.per`. SDKs supporting Backend API version `2025-04-10` decode it
automatically.

## Build enumeration-safe sign-in-or-up

`signIn.create({ identifier, signUpIfMissing: true })` verifies an identifier
before disclosing whether the account exists. When verification returns
`sign_up_if_missing_transfer`, create sign-up with `transfer: true` to retain the
verified identifier.

```ts
const { error } = await signIn.emailCode.verifyCode({ code })
if (error?.errors[0]?.code === 'sign_up_if_missing_transfer') {
  await signUp.create({ transfer: true })
}
```

This supports email, phone, and Web3 identifiers for public sign-up instances.
It excludes password, username, restricted, and waitlist flows.

## Route pending sessions to tasks

Organization selection, a forced-password reset, or required-MFA setup may
leave a session `pending`. Pending sessions are treated as signed out by
default: IDs are null and protected routes reject them. Prebuilt flows include
task components; custom flows must inspect `session.currentTask` after
finalization.

```ts
await signIn.finalize({
  navigate: ({ session }) => {
    if (session?.currentTask) return router.push('/session-tasks')
  },
})
const state = await auth({ treatPendingAsSignedOut: false })
```

Opt into pending identity with `treatPendingAsSignedOut: false` only in code
that deliberately handles the task.

## Enroll trusted devices for biometric sign-in

Expo, iOS, and Android SDKs can enroll the current device for a signed-in user,
then authenticate that user with Face ID, Touch ID, or Android biometrics. The
device-bound private key remains local. Prebuilt auth and profile views can show
enrollment, sign-in, and current-device controls.

Custom clients use `useTrustedDevices()` on Expo,
`Clerk.shared.trustedDevices` on iOS, and `Clerk.trustedDevices` on Android.

```ts
import { useTrustedDevices } from '@clerk/expo'

const { enroll } = useTrustedDevices()
await enroll()
```
