# Core 3 migration

## SDK requirements and native Expo UI

`@clerk/expo` 3.1 requires Expo SDK 53 or newer. Its Expo config plugin installs
the native iOS and Android SDKs used by the SwiftUI and Jetpack Compose exports
from `@clerk/expo/native`.

```tsx
import { AuthView, UserButton, UserProfileView } from '@clerk/expo/native'

<AuthView mode="signInOrUp" />
```

- `AuthView` renders native sign-in, sign-up, or combined UI and synchronizes
  the resulting session to JavaScript.
- `UserButton` fills its parent and opens the native profile modal.
- `UserProfileView` embeds profile management inline.

Native Google sign-in uses `ASAuthorization` on iOS and Credential Manager on
Android rather than browser OAuth. Once Google credentials are configured in
the Dashboard, the config plugin supplies the native integration without an
extra package.

In `@clerk/expo` 3.1.5, set the config plugin's `appleSignIn` option to `false`
when Apple Sign-In is unused so the entitlement is not added:

```json
{
  "expo": {
    "plugins": [["@clerk/expo", { "appleSignIn": false }]]
  }
}
```

## Replace first-factor attempts with named methods

The Signal API replaces `signIn.attemptFirstFactor()` with factor-specific
methods and replaces activation via `signIn.createdSessionId` with
`signIn.finalize()`.

```ts
const { signIn } = useSignIn()
await signIn.create({ identifier: email })
await signIn.password({ password })
// Email-code flows use signIn.emailCode.sendCode().
if (signIn.status === 'complete') {
  await signIn.finalize({ navigate: () => router.push('/') })
}
```

Errors are values on the attempt: use paths such as
`errors.fields.identifier?.message` rather than making `try`/`catch` the normal
control flow. `errors.fields` holds field failures, `errors.global` holds other
handled failures, and `errors.raw` holds unparsed failures. A `ClerkError.code`
is stable for branching and `longMessage` is user-facing; `message` is not a
stable developer contract.

`SignInFuture` and `SignUpFuture` objects change identity as the attempt
advances. Include the attempt object itself in React hook dependency arrays.

## Sign-up verification and MFA

The custom-flow surface requires `@clerk/react` 6, `@clerk/nextjs` 7,
`@clerk/expo` 3, `@clerk/react-router` 3, or
`@clerk/tanstack-react-start` 0.26. Sign-up verification is under
`signUp.verifications`:

```ts
await signUp.password({ emailAddress, password })
await signUp.verifications.sendEmailCode()
await signUp.verifications.verifyEmailCode({ code })
```

For `needs_second_factor`, use `signIn.mfa.sendPhoneCode()` and
`verifyPhoneCode()`, `verifyTOTP()`, or `verifyBackupCode()` before finalizing.

## SSO redirects, transfers, and activation

Start browser OAuth with
`signIn.sso({ strategy, redirectUrl, redirectCallbackUrl })`. The callback must
resolve incomplete or misdirected sign-in and sign-up attempts.

- If `signIn.isTransferable`, call `signUp.create({ transfer: true })`.
- Transfer in the other direction with `signIn.create({ transfer: true })`.
- Activate an `existingSession` with `clerk.setActive()`, not an attempt's
  `finalize()`.
- Use `finalize()` for a newly completed attempt.

## Native state hooks

`@clerk/expo` exposes:

- `useUserProfileModal()` for `presentUserProfile` and `isAvailable`.
- `useNativeSession()` for `isSignedIn`, `sessionId`, `user`, and `refresh()`.
- `useNativeAuthEvents()` for native `signedIn` and `signedOut` events.

## Legacy Client Trust

The legacy `SignIn` object can enter `needs_client_trust` on an untrusted device.
At that point `clientTrustState` is populated and the flow must establish trust
with a second-factor verification. This legacy object is scheduled for removal
in favor of `SignInFuture`.
