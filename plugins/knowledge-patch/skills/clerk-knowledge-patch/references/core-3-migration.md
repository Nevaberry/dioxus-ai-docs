# Core 3 migration

## Package requirements

The custom-flow surface requires one of these package generations:

- `@clerk/react` 6
- `@clerk/nextjs` 7
- `@clerk/expo` 3
- `@clerk/react-router` 3
- `@clerk/tanstack-react-start` 0.26

Expo 3.1 is a major upgrade and requires Expo SDK 53 or newer. Its config plugin installs the native iOS and Android SDKs used by SwiftUI and Jetpack Compose components.

## Named factor operations

The Signal API replaces `signIn.attemptFirstFactor()` with named methods. It also replaces `setActive({ session: signIn.createdSessionId })` with `signIn.finalize()`.

```ts
const { signIn } = useSignIn()
await signIn.create({ identifier: email })
await signIn.password({ password })
// Email code: await signIn.emailCode.sendCode()
if (signIn.status === 'complete') {
  await signIn.finalize({ navigate: () => router.push('/') })
}
```

Sign-up verification is under `signUp.verifications`:

```ts
await signUp.password({ emailAddress, password })
await signUp.verifications.sendEmailCode()
await signUp.verifications.verifyEmailCode({ code })
```

For `needs_second_factor`, use `signIn.mfa.sendPhoneCode()` followed by `verifyPhoneCode()`, `verifyTOTP()`, or `verifyBackupCode()`, then finalize.

## Attempts and error channels

`useSignIn()` and `useSignUp()` expose `SignInFuture` and `SignUpFuture`. The attempt object's identity changes as the flow advances, so include it in React dependency arrays.

Errors are split into:

- `errors.fields`, such as `errors.fields.identifier?.message`.
- `errors.global` for handled failures not attached to a field.
- `errors.raw` for unparsed failures.

Branch on a `ClerkError.code`. Its `longMessage` is user-facing; its developer-oriented `message` is not a stable branch key. Do not rely on `try`/`catch` alone for field validation.

## SSO and attempt transfer

Start browser OAuth with:

```ts
await signIn.sso({ strategy, redirectUrl, redirectCallbackUrl })
```

The callback must handle incomplete or misdirected sign-in and sign-up attempts.

- If `signIn.isTransferable`, call `signUp.create({ transfer: true })`.
- Transfer the opposite direction with `signIn.create({ transfer: true })`.
- If the result is an `existingSession`, activate it through `clerk.setActive()` rather than either attempt's `finalize()`.

## Enumeration-safe sign-in-or-up

`signIn.create({ identifier, signUpIfMissing: true })` verifies the identifier before revealing whether an account exists. For a missing account, verification returns `sign_up_if_missing_transfer`; then transfer into sign-up while preserving the verified identifier.

```ts
const { error } = await signIn.emailCode.verifyCode({ code })
if (error?.errors[0]?.code === 'sign_up_if_missing_transfer') {
  await signUp.create({ transfer: true })
}
```

This flow supports email, phone, and Web3 identifiers on public-sign-up instances. It does not support passwords, usernames, restricted mode, or waitlist mode.

## Pending session tasks

Selecting an Organization, changing a forced password, or enrolling required MFA can produce an authenticated session with status `pending`. Pending sessions are treated as signed out by default: identity IDs are null and protected routes reject them.

Prebuilt flows contain task components. Custom flows must inspect `session.currentTask` after finalization and route to task UI.

```ts
await signIn.finalize({ navigate: ({ session }) => {
  if (session?.currentTask) return router.push('/session-tasks')
} })

const state = await auth({ treatPendingAsSignedOut: false })
```

Opt out of pending-as-signed-out only in code that explicitly handles the task state.

## Expo native UI

Native components come from `@clerk/expo/native`:

```tsx
import { AuthView, UserButton, UserProfileView } from '@clerk/expo/native'

<AuthView mode="signInOrUp" />
```

- `AuthView` renders native sign-in, sign-up, or combined UI and synchronizes the session to JavaScript.
- `UserButton` opens the native profile modal and fills its parent.
- `UserProfileView` embeds profile management.

Expo Google Sign-In uses `ASAuthorization` on iOS and Credential Manager on Android rather than browser OAuth. The config plugin integrates the native module; after Dashboard Google OAuth credentials are configured, no additional package is required.

Since `@clerk/expo` 3.1.5, the config plugin exposes `appleSignIn`; set it to `false` when the Apple Sign-In entitlement is unused:

```json
{
  "expo": {
    "plugins": [["@clerk/expo", { "appleSignIn": false }]]
  }
}
```

## Expo native hooks

- `useUserProfileModal()` returns `presentUserProfile` and `isAvailable`.
- `useNativeSession()` exposes `isSignedIn`, `sessionId`, `user`, and `refresh()`.
- `useNativeAuthEvents()` receives native `signedIn` and `signedOut` events.
