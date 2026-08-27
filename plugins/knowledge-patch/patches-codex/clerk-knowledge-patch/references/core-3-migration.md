# Core 3 migration

## Migrate attempt methods and finalization

The Core 3 Signal API replaces broad first-factor calls with named factor
methods. Replace `signIn.attemptFirstFactor()` and activation through
`signIn.createdSessionId` with the factor namespace and `signIn.finalize()`.

```ts
const { signIn } = useSignIn()
await signIn.create({ identifier: email })
await signIn.password({ password })
// Email-code flows use signIn.emailCode.sendCode().
if (signIn.status === 'complete') {
  await signIn.finalize({ navigate: () => router.push('/') })
}
```

Use paths such as `errors.fields.identifier?.message` for field failures rather
than depending on `try`/`catch` alone.

## Track attempt identity and error channels

`useSignIn()` and `useSignUp()` return `SignInFuture` and `SignUpFuture`
attempts. An attempt's identity changes as the flow advances, so include the
attempt object itself in React dependency arrays.

Errors are separated into field-specific `fields`, non-field `global` errors,
and unparsed `raw` errors. Branch on a `ClerkError.code`, show its user-facing
`longMessage`, and do not treat the developer-facing `message` as stable.

The legacy `SignIn` can enter `needs_client_trust` on a new device. Its
`clientTrustState` then describes the second-factor trust flow. This legacy
object is scheduled for replacement by `SignInFuture`.

## Move sign-up verification and MFA to namespaces

Core 3 custom flows require `@clerk/react` 6, `@clerk/nextjs` 7,
`@clerk/expo` 3, `@clerk/react-router` 3, or
`@clerk/tanstack-react-start` 0.26. Sign-up verification is under
`signUp.verifications`:

```ts
await signUp.password({ emailAddress, password })
await signUp.verifications.sendEmailCode()
await signUp.verifications.verifyEmailCode({ code })
```

For `needs_second_factor`, use `signIn.mfa.sendPhoneCode()` followed by
`verifyPhoneCode()`, `verifyTOTP()`, or `verifyBackupCode()`, then finalize.

## Handle SSO transfers explicitly

Start browser OAuth with
`signIn.sso({ strategy, redirectUrl, redirectCallbackUrl })`. The callback must
resolve incomplete or misdirected sign-in and sign-up attempts. Transfer a
sign-in attempt through `signUp.create({ transfer: true })` when
`signIn.isTransferable`; transfer the reverse direction with
`signIn.create({ transfer: true })`.

An `existingSession` is not a newly completed attempt. Activate it through
`clerk.setActive()`, not either attempt's `finalize()`.

## Upgrade Expo native integration

`@clerk/expo` 3.1 requires Expo SDK 53 or newer. Its config plugin installs the
native iOS and Android SDKs behind SwiftUI and Jetpack Compose components from
`@clerk/expo/native`:

```tsx
import { AuthView, UserButton, UserProfileView } from '@clerk/expo/native'

<AuthView mode="signInOrUp" />
```

- `AuthView` renders sign-in, sign-up, or combined native UI and synchronizes
  the resulting session to JavaScript.
- `UserButton` fills its parent and opens the native profile modal.
- `UserProfileView` embeds profile management inline.

Native Google Sign-In uses `ASAuthorization` on iOS and Credential Manager on
Android. The config plugin integrates the native module, so no extra package is
needed after Dashboard Google OAuth credentials are configured.

## Use Expo native state hooks

- `useUserProfileModal()` returns `presentUserProfile` and `isAvailable`.
- `useNativeSession()` exposes `isSignedIn`, `sessionId`, `user`, and
  `refresh()`.
- `useNativeAuthEvents()` observes native `signedIn` and `signedOut` events.

## Disable an unused Apple Sign-In entitlement

`@clerk/expo` 3.1.5 adds the config-plugin option `appleSignIn`. Set it to
`false` when the application does not use Apple Sign-In so the plugin does not
add the entitlement unconditionally.

```json
{
  "expo": {
    "plugins": [["@clerk/expo", { "appleSignIn": false }]]
  }
}
```

## Apply current provider behavior

X/Twitter sign-in now returns the user's email instead of forcing a separate
manual email step. Development instances can enable the connection without
additional provider configuration.

## Choose an M2M token format

M2M creation accepts `tokenFormat: 'jwt'`. Verify JWT-format tokens locally
with the instance public key. Opaque tokens continue to use server-side
verification and support immediate revocation.

```ts
const created = await clerkClient.m2m.createToken({ tokenFormat: 'jwt' })
const verified = await clerkClient.m2m.verify({ token: created.token })
```

## Initialize Chrome extension clients

Non-React extension pages create a client from
`@clerk/chrome-extension/client`; allow the extension redirect protocol when
loading popups or side panels.

```ts
import { createClerkClient } from '@clerk/chrome-extension/client'

const clerk = createClerkClient({ publishableKey })
await clerk.load({ allowedRedirectProtocols: ['chrome-extension:'] })
```

The same entry point supports service workers through `background: true`.
`@clerk/chrome-extension/background` is deprecated.

```ts
const clerk = await createClerkClient({ publishableKey, background: true })
const token = clerk.session ? await clerk.session.getToken() : null
```
