# Frontend resources

## Web3 authentication

The frontend `Clerk` object provides wallet flows for MetaMask, Coinbase Wallet,
OKX Wallet, Base, and Solana, plus generic `authenticateWithWeb3()`. Solana
requires `walletName`. Sign-up-capable calls can include `unsafeMetadata` and
`legalAccepted`.

```ts
await clerk.authenticateWithWeb3({
  strategy: 'web3_solana_signature',
  walletName,
  redirectUrl: '/dashboard',
})
```

## Raw Google One Tap

Pass a custom Google Identity Services credential to
`authenticateWithGoogleOneTap()`, which returns a `SignIn` or `SignUp` resource.
Complete routing with `handleGoogleOneTapCallback()`.

```ts
const attempt = await clerk.authenticateWithGoogleOneTap({ token })
await clerk.handleGoogleOneTapCallback(attempt, {
  signInUrl: '/sign-in', signUpUrl: '/sign-up',
})
```

## Cross-device email links

`handleEmailLinkVerification()` recognizes `__clerk_status` values `verified`,
`failed`, `expired`, and `client_mismatch`. Success on another device may create
the `__clerk_created_session` session without adding it to the initiating
client's `Client.sessions`; handle `onVerifiedOnOtherDevice`.

```ts
await clerk.handleEmailLinkVerification({
  redirectUrlComplete,
  redirectUrl,
  onVerifiedOnOtherDevice: showCrossDeviceSuccess,
})
```

## Enterprise SSO email linking

`EmailAddress.createEnterpriseSSOLinkFlow()` returns separate start and cancel
functions. It sends a link and polls for completion; custom UI must cancel
polling during cleanup.

```ts
const { startEnterpriseSSOLinkFlow, cancelEnterpriseSSOLinkFlow } =
  emailAddress.createEnterpriseSSOLinkFlow()
await startEnterpriseSSOLinkFlow({ redirectUrl })
```

## Frontend API keys

`clerk.apiKeys` lists, creates, and revokes user- or Organization-owned keys.
Without `subject`, it prefers the Active Organization and falls back to the
current User. Only the `create()` response contains the secret; capture it
immediately.

```ts
const key = await clerk.apiKeys.create({
  name: 'Automation', secondsUntilExpiration: 3600,
})
await clerk.apiKeys.revoke({ apiKeyID: key.id })
```

## Session-token cache and Organization claims

`Session.getToken()` caches one-minute tokens and retries transient failures,
eventually throwing `ClerkOfflineError` when offline. `skipCache` forces a
server call. `organizationId` creates claims for another Organization without
changing the Active Organization.

```ts
const token = await session.getToken({ organizationId, skipCache: true })
```

## User refresh and unsafe metadata

`User.reload()` fetches current user data and forces session-token refresh.
`User.update({ unsafeMetadata })` replaces the entire object; explicitly retain
existing keys.

```ts
await user.update({
  unsafeMetadata: { ...user.unsafeMetadata, ...patch },
})
await user.reload()
```

## Multi-session behavior

`useSessionList()` lists sessions registered on the current client device.
`User.getSessions()` fetches every active session for that user and caches the
network result after its first call. Bare `clerk.signOut()` signs the active
user out of every session in a multi-session app; pass `sessionId` to target
one.

```ts
await clerk.signOut({ sessionId })
```

## Resource subscriptions

`Clerk.addListener()` emits `client`, `session`, `user`, and `organization`
immediately and on changes. Pass `skipInitialEmit` to receive only future
changes. Invoke the returned unsubscribe function during cleanup.

```ts
const unsubscribe = clerk.addListener(handleResources, {
  skipInitialEmit: true,
})
```

## Safari-safe session activation

For custom navigation in `setActive()`, wrap the target with `decorateUrl()`.
It may return an absolute Clerk URL to refresh Safari's ITP-limited `__client`
cookie; use full-page navigation for an absolute URL and client routing for a
relative one.

```ts
await clerk.setActive({
  session,
  navigate: ({ decorateUrl }) => {
    const url = decorateUrl('/dashboard')
    return url.startsWith('http') ? window.location.assign(url) : router.push(url)
  },
})
```

## Agent-created sessions

When `Session.actor.type` is `agent`, `Session.agent` exposes the agent and Agent
Task behind the session, distinguishing it from ordinary impersonation.
