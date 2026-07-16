# Frontend resources

## Web3 authentication

The frontend `Clerk` object provides wallet flows for MetaMask, Coinbase Wallet, OKX Wallet, Base, and Solana, plus generic `authenticateWithWeb3()`.

Solana requires `walletName`. Sign-up-capable calls can include `unsafeMetadata` and `legalAccepted`.

```ts
await clerk.authenticateWithWeb3({
  strategy: 'web3_solana_signature',
  walletName,
  redirectUrl: '/dashboard',
})
```

## Raw Google One Tap

A custom Google Identity Services UI can pass its credential to `authenticateWithGoogleOneTap()`. The call returns a `SignIn` or `SignUp` resource; complete routing with `handleGoogleOneTapCallback()`.

```ts
const attempt = await clerk.authenticateWithGoogleOneTap({ token })
await clerk.handleGoogleOneTapCallback(attempt, {
  signInUrl: '/sign-in',
  signUpUrl: '/sign-up',
})
```

This is separate from `<GoogleOneTap />`, which does not return Google provider tokens.

## Cross-device email links

`handleEmailLinkVerification()` understands `__clerk_status` values including `verified`, `failed`, `expired`, and `client_mismatch`.

A successful link opened on a different device may create the session named by `__clerk_created_session`; that session is absent from the initiating client's `Client.sessions`. Handle that outcome with `onVerifiedOnOtherDevice`.

```ts
await clerk.handleEmailLinkVerification({
  redirectUrlComplete,
  redirectUrl,
  onVerifiedOnOtherDevice: showCrossDeviceSuccess,
})
```

## Enterprise SSO email linking

An `EmailAddress` can email an enterprise SSO link and poll for completion. `createEnterpriseSSOLinkFlow()` returns independent start and cancellation functions, allowing custom UI to stop polling during cleanup.

```ts
const {
  startEnterpriseSSOLinkFlow,
  cancelEnterpriseSSOLinkFlow,
} = emailAddress.createEnterpriseSSOLinkFlow()

await startEnterpriseSSOLinkFlow({ redirectUrl })
```

## Frontend API-key lifecycle

`clerk.apiKeys` lists, creates, and revokes user- or Organization-owned API keys.

When `subject` is omitted, the Active Organization takes precedence over the current User. Only the `create()` response contains the secret, so capture and display it immediately.

```ts
const key = await clerk.apiKeys.create({
  name: 'Automation',
  secondsUntilExpiration: 3600,
})

await clerk.apiKeys.revoke({ apiKeyID: key.id })
```

## Session-token cache and Organization claims

`Session.getToken()` caches one-minute tokens and retries transient failures. If the client remains offline, it eventually throws `ClerkOfflineError`.

- `skipCache` forces a server request.
- `organizationId` creates claims for the selected Organization without changing the session's Active Organization.

```ts
const token = await session.getToken({
  organizationId,
  skipCache: true,
})
```

## Refresh user data and claims

`User.reload()` fetches the current user and forces a session-token refresh, so changed claims do not wait for the normal token cycle.

`User.update({ unsafeMetadata })` replaces the entire unsafe-metadata object rather than merging. Copy existing keys explicitly when applying a patch.

```ts
await user.update({
  unsafeMetadata: {
    ...user.unsafeMetadata,
    ...patch,
  },
})
await user.reload()
```

## Custom reverification

`factorVerificationAge` is `[firstFactorAge, secondFactorAge]` in minutes. Build a custom flow with `Session.startVerification()` followed by the matching prepare and attempt methods.

```ts
const verification = await session.startVerification({
  level: 'first_factor',
})
const email = verification.supportedFirstFactors?.find(
  (factor) => factor.strategy === 'email_code',
)
if (!email) throw new Error('Email code is unavailable')

await session.prepareFirstFactorVerification({
  strategy: 'email_code',
  emailAddressId: email.emailAddressId,
})
await session.attemptFirstFactorVerification({
  strategy: 'email_code',
  code,
})
```

Expo's prebuilt reverification modal works only on web. Native mobile uses `useReverification(..., { onNeedsReverification })` and calls the provided `complete` or `cancel` callback.

## Multi-session scope

`useSessionList()` returns sessions registered on the current client device. `User.getSessions()` fetches every active session for that user and caches the network result after its first call.

In a multi-session application, `clerk.signOut()` without arguments signs the active user out of all sessions. Pass `sessionId` to sign out only one session.

```ts
await clerk.signOut({ sessionId })
```

## Resource subscriptions

`Clerk.addListener()` emits `client`, `session`, `user`, and `organization` immediately by default and again whenever they change.

Set `skipInitialEmit` when only future updates matter. Always call the returned unsubscribe function during cleanup.

```ts
const unsubscribe = clerk.addListener(handleResources, {
  skipInitialEmit: true,
})
```

## Safari-safe session activation

When `setActive()` uses custom navigation, wrap the destination with `decorateUrl()`. It can return an absolute Clerk URL to refresh Safari's ITP-limited `__client` cookie. Use full-page navigation for an absolute URL and client routing otherwise.

```ts
await clerk.setActive({
  session,
  navigate: ({ decorateUrl }) => {
    const url = decorateUrl('/dashboard')
    return url.startsWith('http')
      ? window.location.assign(url)
      : router.push(url)
  },
})
```

## Agent-task sessions

When `Session.actor.type === 'agent'`, `Session.agent` exposes the agent and Agent Task that created the session. This distinguishes an agent-created session from ordinary impersonation.
