# Identity and Utility Plugins

## Two-factor authentication

`twoFactor.enable` stages enrollment: it returns the TOTP URI and backup codes, but `twoFactorEnabled` remains false until TOTP verification unless `skipVerificationOnEnable` is set. `allowPasswordless` removes the password requirement only for users with no credential account.

Server-side continuation must forward cookies returned by the original sign-in into the 2FA call:

```ts
const { headers: responseHeaders, response } = await auth.api.signInEmail({
  returnHeaders: true,
  body: { email, password },
});
if ("twoFactorRedirect" in response) {
  // Forward responseHeaders into the following auth.api 2FA request.
}
```

TOTP verification accepts the immediately previous and next periods, each 30 seconds by default. Backup codes are single-use and regeneration invalidates all old codes. Trusted devices bypass 2FA for 30 days, refreshing that window after successful sign-in; trust duration is server-enforced.

## Passkeys

The plugin is imported from `@better-auth/passkey` (since 1.4.0). Registration can run without a session for passkey-first onboarding (since 1.6.0), but the supplied context must be securely validated before resolving or creating the user.

```ts
passkey({
  registration: {
    requireSession: false,
    resolveUser: async ({ ctx, context }) => {
      await validateRegistrationContext(context, ctx);
      return { id: "user-id", name: "user@example.com" };
    },
  },
})
```

Registration and authentication options accept server-defined WebAuthn extensions such as `credProps`.

Conditional UI requires `webauthn` as the final autocomplete token and an `autoFill` sign-in after checking conditional-mediation support. Passkey registration/sign-in ignore fetch option `throw: true`; inspect the returned data error.

```html
<input name="username" autocomplete="username webauthn">
```

## Magic links and email OTP

Magic-link sign-in creates an unknown user unless `disableSignUp` is true, and redirects to `/` when no callback is provided. Calling verification manually without a callback returns the session. Links last 300 seconds by default, tokens are plaintext by default, and `allowedAttempts` can cap verification.

Email OTP allows three verification attempts by default and invalidates the code after that. Resends rotate by default. `resendStrategy: "reuse"` extends a recoverable code, but hashed storage forces rotation and exhausted codes are always replaced. Email OTP also supports change-email and richer sign-in fields.

```ts
emailOTP({
  resendStrategy: "reuse",
  storeOTP: "encrypted",
  sendVerificationOTP,
})
```

## Phone authentication

With `requireVerification`, password sign-in for an unverified phone returns `401 PHONE_NUMBER_NOT_VERIFIED` and sends an OTP. Internal codes last 300 seconds and allow three attempts before deletion and a 403. Verification creates a session unless `disableSession` is passed. Phone-only signup needs `signUpOnVerification.getTempEmail`; additional signup fields and custom OTP verification are supported.

```ts
phoneNumber({
  sendOTP,
  requireVerification: true,
  signUpOnVerification: {
    getTempEmail: (phone) => `${phone}@example.invalid`,
  },
})
```

## Anonymous account conversion

When an anonymous user signs in or registers another way, `onLinkAccount` receives both identities and is the data-migration boundary. Move carts or other owned data there. The anonymous user is deleted by default after linking; the plugin also supports optional anonymous-user deletion behavior.

## SIWE and last-login tracking

`siwe()` provides Sign-In with Ethereum through the built-in plugin set (since 1.3.0). Last-login-method tracking recognizes both SIWE and passkeys.

## Bearer authentication

The bearer value is the session token in `set-auth-token`, not a JWT-plugin token. Send it in `Authorization: Bearer ...`; `getSession` resolves it. `requireSignature` defaults to false.

```ts
plugins: [bearer({ requireSignature: true })]
```

## JWT service tokens and JWKS

The JWT plugin bridges service tokens; it is not session authentication. Tokens default to the full user payload, a 15-minute lifetime, and `baseURL` as issuer and audience. Alternate signing algorithms are supported (since 1.3.0). Scheduled JWKS rotation keeps old keys through a grace period:

```ts
jwt({
  jwks: {
    rotationInterval: 60 * 60 * 24 * 30,
    gracePeriod: 60 * 60 * 24 * 30,
  },
})
```

When using OAuth Provider, disable the JWT plugin's parallel `/token` route and its `set-auth-jwt` session header:

```ts
disabledPaths: ["/token"],
plugins: [jwt({ disableSettingJwtHeader: true })],
```

## Multi-session

The multi-session plugin keeps an extra browser cookie and permits five account sessions per device by default. Switching/revoking requires the target token. Ordinary `signOut` revokes every session tracked by this plugin, not just the active account.

## API keys

The plugin/client are `@better-auth/api-key` and `@better-auth/api-key/client` (since 1.5-guide). It supports multiple named configurations, required key names through `requireName`, asynchronous `verifyKey`, organization ownership with `references: "organization"`, and optional secondary storage.

```ts
apiKey([
  { configId: "user-keys", prefix: "usr_" },
  { configId: "org-keys", prefix: "org_", references: "organization" },
])
```

The schema renames `userId` to `referenceId` and adds `configId`; returned keys expose `references`. Server `updateApiKey` needs `userId` or request headers. Mock sessions require `enableSessionForAPIKeys` and work only for user-owned keys. Configure `apiKeyHeaders` and let `getSession` validate once; explicitly verifying first consumes accounting twice.

Organization-owned keys require organization membership and the relevant `apiKey` create/read/update/delete permission. Owners have all four; other roles require explicit grants. `verifyApiKey({ permissions })` requires every requested permission.

With `storage: "secondary-storage"` and `fallbackToDatabase: true`, reads check secondary storage and warm it from the database, while writes hit both. Expiring entries receive TTLs. Every get/update/delete/verify operation needs the right `configId` when configurations use different backends.

Each validation consumes the rate limit and optional `remaining` budget. Zero disables and removes the key; refill resets to `refillAmount`, not an increment. `deferUpdates` sends counter, timestamp, and budget writes to the global background handler, making accounting optimistic and eventually consistent.

```ts
apiKey({ deferUpdates: true }) // requires advanced.backgroundTasks.handler
```

## Admin roles

Custom `admin` or `user` roles replace built-in permissions. Merge `defaultStatements` and `adminAc.statements` to retain them, and pass the same controller/roles to server and client. `checkRolePermission` checks a role definition synchronously; use `hasPermission` or server `userHasPermission` for a signed-in user.

## Captcha

Captcha protects only POST and defaults to `/sign-up/email`, `/sign-in/email`, and `/request-password-reset`; setting `endpoints` replaces the list. Clients send proof in `x-captcha-response`. The server detects the remote IP and does not trust a client-supplied IP header.

## Google One Tap

One Tap hard-redirects to `/` after success unless `callbackURL` changes it or `onSuccess` handles navigation. Dismissal retries exponentially, by default five times from a one-second base delay. `onPromptNotification` is the alternate-UI fallback. Button mode is also available.

## One-time cross-domain sessions

The one-time-token plugin issues a token bound to the current session and returns that session exactly once on verification. Lifetime defaults to three minutes. Client generation and plaintext database storage are defaults; sensitive deployments can require server generation and hashing.

```ts
oneTimeToken({ disableClientRequest: true, storeToken: "hashed" })
```

## Other plugin additions

The default API error page can be restyled or replaced. The `AuthClient` type helper and automatic server-side client-IP detection are available. Social providers include Paybin and Polar (since 1.4.0). The admin plugin can optionally create users with passwords; organization membership limits may be functions.
