# Frontend resources

## Authenticate with Web3 wallets

The frontend `Clerk` object supports MetaMask, Coinbase Wallet, OKX Wallet,
Base, and Solana flows, plus the generic `authenticateWithWeb3()` entry point.
Solana requires `walletName`. Sign-up-capable calls may include
`unsafeMetadata` and `legalAccepted`.

```ts
await clerk.authenticateWithWeb3({
  strategy: 'web3_solana_signature',
  walletName,
  redirectUrl: '/dashboard',
})
```

## Complete raw Google One Tap

A custom Google Identity Services UI can pass its credential token to
`authenticateWithGoogleOneTap()`. The result is a `SignIn` or `SignUp`
resource; route it with `handleGoogleOneTapCallback()`.

```ts
const attempt = await clerk.authenticateWithGoogleOneTap({ token })
await clerk.handleGoogleOneTapCallback(attempt, {
  signInUrl: '/sign-in',
  signUpUrl: '/sign-up',
})
```

## Handle cross-device email links

`handleEmailLinkVerification()` recognizes `__clerk_status` values including
`verified`, `failed`, `expired`, and `client_mismatch`. A link completed on a
different device may create the session named by `__clerk_created_session`
without adding it to the initiating client's `Client.sessions`. Handle that
outcome with `onVerifiedOnOtherDevice`.

```ts
await clerk.handleEmailLinkVerification({
  redirectUrlComplete,
  redirectUrl,
  onVerifiedOnOtherDevice: showCrossDeviceSuccess,
})
```

## Link an EmailAddress through Enterprise SSO

An `EmailAddress` can email an Enterprise SSO link and poll for completion.
`createEnterpriseSSOLinkFlow()` returns independent start and cancel functions;
cancel when custom UI unmounts or abandons the flow.

```ts
const { startEnterpriseSSOLinkFlow, cancelEnterpriseSSOLinkFlow } =
  emailAddress.createEnterpriseSSOLinkFlow()
await startEnterpriseSSOLinkFlow({ redirectUrl })
```

## Manage frontend API keys

`clerk.apiKeys` lists, creates, and revokes user- or Organization-owned keys.
Without `subject`, it chooses the Active Organization before the current User.
Only the `create()` response includes the secret, so capture it immediately.

```ts
const key = await clerk.apiKeys.create({
  name: 'Automation',
  secondsUntilExpiration: 3600,
})
await clerk.apiKeys.revoke({ apiKeyID: key.id })
```

## Control the session-token cache and Organization claims

`Session.getToken()` caches one-minute tokens and retries transient failures;
after retries, offline operation throws `ClerkOfflineError`. `skipCache` forces
a server call. `organizationId` creates claims for a selected Organization
without changing the session's Active Organization.

```ts
const token = await session.getToken({
  organizationId,
  skipCache: true,
})
```

## Refresh user data and replace unsafe metadata safely

`User.reload()` fetches the current user and forces a session-token refresh so
new claims are not delayed until the normal token cycle.

`User.update({ unsafeMetadata })` replaces the complete unsafe-metadata object;
merge existing keys in the caller when applying a partial change.

```ts
await user.update({
  unsafeMetadata: { ...user.unsafeMetadata, ...patch },
})
await user.reload()
```

## Build custom and native reverification

`factorVerificationAge` is `[firstFactorAge, secondFactorAge]` in minutes. A
custom UI starts with `Session.startVerification()` and follows with the
matching prepare and attempt methods.

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
await session.attemptFirstFactorVerification({
  strategy: 'email_code',
  code,
})
```

Expo's prebuilt reverification modal works on web only. Native mobile code must
call `useReverification(..., { onNeedsReverification })` and eventually invoke
the callback's `complete` or `cancel`.

## Distinguish device sessions from all user sessions

`useSessionList()` returns sessions registered on the current client device.
`User.getSessions()` fetches every active session for that user and caches its
network result after the first call.

In a multi-session application, bare `clerk.signOut()` signs the active user out
of every session. Pass `sessionId` to sign out one session only.

```ts
await clerk.signOut({ sessionId })
```

## Subscribe to resource changes

`Clerk.addListener()` emits `client`, `session`, `user`, and `organization`
immediately by default and whenever they change. Use `skipInitialEmit` when only
future changes matter, and invoke the returned unsubscribe function on cleanup.

```ts
const unsubscribe = clerk.addListener(handleResources, {
  skipInitialEmit: true,
})
```

## Activate sessions safely in Safari

When `setActive()` uses custom navigation, wrap the target in `decorateUrl()`.
The result can be an absolute Clerk URL used to refresh Safari's ITP-limited
`__client` cookie. Use full-page navigation for an absolute result and client
routing otherwise.

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

## Identify an Agent Task session

When `Session.actor.type` is `agent`, `Session.agent` exposes the agent and
Agent Task behind the session. Use it to distinguish an agent-created session
from ordinary impersonation.
