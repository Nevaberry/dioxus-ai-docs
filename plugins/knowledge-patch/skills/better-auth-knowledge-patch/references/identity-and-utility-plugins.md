# Identity and Utility Plugins

## Two-factor authentication

`twoFactor.enable` only stages enrollment: it returns the TOTP URI and backup codes, while `twoFactorEnabled` remains false until TOTP verification unless `skipVerificationOnEnable` is set. `allowPasswordless` removes the password requirement only for users without a credential account.

Server-side sign-in continuations must forward returned cookies into the next two-factor call:

```ts
const { headers: responseHeaders, response } = await auth.api.signInEmail({
  returnHeaders: true,
  body: { email, password },
});
if ("twoFactorRedirect" in response) {
  // Forward responseHeaders cookies into the following auth.api 2FA call.
}
```

TOTP verification accepts the immediately previous and next periods, each 30 seconds by default. Backup codes are single-use; regeneration invalidates all old codes. A trusted device bypasses 2FA for 30 days, and every successful sign-in refreshes that window. Trust duration is enforced by the server.

## Passkeys

The passkey plugin lives in `@better-auth/passkey`. Conditional autofill requires `webauthn` as the last `autocomplete` token and an `autoFill` sign-in initiated only after conditional-mediation support is confirmed.

```html
<input name="username" autocomplete="username webauthn">
```

```ts
if (await PublicKeyCredential.isConditionalMediationAvailable?.()) {
  void authClient.signIn.passkey({ autoFill: true });
}
```

Passkey register/sign-in ignores fetch option `throw: true`; inspect the returned data object's error.

Passkey-first onboarding can register without an existing session. Set `registration.requireSession: false` and securely validate the supplied context before resolving or creating a user. Registration and authentication options accept server-defined WebAuthn extensions such as `credProps`.

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

## Magic links

Magic-link sign-in creates an unknown user unless `disableSignUp` is true. It redirects to `/` without a callback. Calling verification manually with no callback returns the session instead. Links expire after 300 seconds by default, and stored tokens default to plain text. `allowedAttempts` can bound failed verification attempts.

## Email OTP

Email OTP defaults to three verification attempts and invalidates the OTP when the limit is reached. Resending rotates the code by default. `resendStrategy: "reuse"` extends and resends a recoverable code, but hashed storage falls back to rotation and exhausted codes are always replaced.

```ts
emailOTP({
  resendStrategy: "reuse",
  storeOTP: "encrypted",
  sendVerificationOTP,
})
```

Email OTP also supports change-email and richer sign-in fields.

## Phone numbers

With `requireVerification`, password sign-in for an unverified phone returns `401 PHONE_NUMBER_NOT_VERIFIED` and automatically sends an OTP. Internal OTPs expire after 300 seconds and permit three attempts before deletion and a 403 response. Verification creates a session unless `disableSession` is passed. Phone-only signup requires `signUpOnVerification.getTempEmail`.

```ts
phoneNumber({
  sendOTP,
  requireVerification: true,
  signUpOnVerification: {
    getTempEmail: (phone) => `${phone}@example.invalid`,
  },
})
```

The plugin supports custom OTP verification and additional sign-up fields supplied during phone verification.

## Anonymous accounts

When an anonymous user signs in or signs up another way, `onLinkAccount` is the application-data migration boundary and receives both identities. The anonymous user row is deleted after linking by default. Move carts and other owned data in the hook before relying on the new account.

```ts
anonymous({
  onLinkAccount: async ({ anonymousUser, newUser }) =>
    moveOwnedData(anonymousUser.id, newUser.id),
})
```

The plugin can also delete anonymous users according to its deletion option.

## Admin roles

Defining a custom `admin` or `user` role replaces that role's built-in permissions. Merge `defaultStatements` and `adminAc.statements` to retain them, and pass the same access controller and roles to server and client plugins.

`checkRolePermission` synchronously checks a role definition, not the signed-in user. Use client `hasPermission` or server `userHasPermission` for user authorization. The admin plugin can optionally assign passwords when it creates users.

```ts
const ac = createAccessControl({
  ...defaultStatements,
  project: ["create"],
} as const);
const adminRole = ac.newRole({
  ...adminAc.statements,
  project: ["create"],
});
```

## Bearer authentication

The bearer plugin exposes the session token in `set-auth-token`. That value—not a JWT plugin token—belongs in `Authorization: Bearer ...` and is resolved by `getSession`. `requireSignature` defaults to false; enable it when unsigned bearer session tokens are unacceptable.

```ts
plugins: [bearer({ requireSignature: true })]
const token = ctx.response.headers.get("set-auth-token");
await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
```

## JWT service tokens

The JWT plugin is a service-token bridge, not session authentication. Tokens default to the complete user payload, 15-minute expiry, and `baseURL` as issuer and audience. JWKS supports alternate algorithms and scheduled key rotation with a grace period.

```ts
jwt({
  jwks: {
    rotationInterval: 60 * 60 * 24 * 30,
    gracePeriod: 60 * 60 * 24 * 30,
  },
})
```

When using OAuth Provider, disable both JWT's `/token` endpoint and the `set-auth-jwt` session header so parallel protocol endpoints are not exposed.

```ts
betterAuth({
  disabledPaths: ["/token"],
  plugins: [jwt({ disableSettingJwtHeader: true })],
})
```

## Multi-session cookies

The multi-session plugin maintains an additional browser cookie and allows five account sessions per device by default. Switching or revoking needs the target session token. Ordinary `signOut` revokes every session tracked by the plugin, not only the active account.

## Sign-In with Ethereum

SIWE is built in as the `siwe` plugin. Last-login-method tracking recognizes SIWE and passkeys.

```ts
import { siwe } from "better-auth/plugins";

plugins: [siwe()]
```

## API keys

The API-key server/client packages are `@better-auth/api-key` and `@better-auth/api-key/client`. `requireName` can require a key name and `verifyKey` may be asynchronous. Mock sessions are disabled by default and must be enabled explicitly.

Multiple named configurations are supported. Organization-owned keys use `references: "organization"`. The migration renames `ApiKey.userId` to `referenceId`, adds `configId` with default `"default"`, and returns `references` as the owner type. `defaultPermissions` receives `referenceId`; server-side `updateApiKey` needs at least `userId` or request headers.

```ts
apiKey([
  { configId: "user-keys", prefix: "usr_" },
  { configId: "org-keys", prefix: "org_", references: "organization" },
])

await auth.api.createApiKey({
  body: { configId: "org-keys", organizationId: "org_123" },
});
```

The plugin can use configured secondary storage. With `fallbackToDatabase: true`, reads check secondary storage then warm it from the database, while writes go to both. Expiring keys receive a secondary-store TTL. Every get, update, delete, and verify operation must carry the correct `configId` when configurations use different backends.

```ts
apiKey({ storage: "secondary-storage", fallbackToDatabase: true })
```

Session mocking works only for user-owned keys. Configure API-key headers so `getSession` validates and rate-limits once; manually calling `verifyApiKey` before `getSession` increments usage twice.

```ts
apiKey({
  enableSessionForAPIKeys: true,
  apiKeyHeaders: ["x-api-key", "x-service-key"],
})
```

Every validation consumes the rate limit and optional `remaining` budget. At zero, the key is disabled and removed. Refill resets `remaining` to `refillAmount`, rather than adding. `deferUpdates` sends counter, timestamp, and budget writes through the global background handler, making accounting optimistic and eventually consistent.

```ts
apiKey({ deferUpdates: true }) // requires advanced.backgroundTasks.handler
```

## Captcha

Captcha protects only POST requests. Its defaults are `/sign-up/email`, `/sign-in/email`, and `/request-password-reset`; supplying `endpoints` replaces the list. Clients send proof in `x-captcha-response`. The server detects remote IP and does not trust a client IP header.

## Google One Tap

One Tap hard-redirects to `/` after success unless `callbackURL` changes the target or an `onSuccess` fetch callback navigates without reload. Dismissed prompts retry with exponential backoff: five attempts from a one-second base delay by default. Use `onPromptNotification` to show alternate UI. Button mode is available.

## One-time tokens

The one-time-token plugin attaches a token to the current session and returns that session once on verification. Lifetime defaults to three minutes. Client generation is enabled and database storage is plain text by default; sensitive deployments can require server generation and hashing.

```ts
oneTimeToken({ disableClientRequest: true, storeToken: "hashed" })
```

## Internationalized errors

`@better-auth/i18n` provides type-checked translations and can detect locale from headers, cookies, or sessions. Error responses contain a machine-readable `code`; `defineErrorCodes()` returns `{ code, message }` values accepted by `APIError.from()`.

```ts
i18n({
  defaultLocale: "en",
  detection: ["header", "cookie"],
  translations: {
    en: { USER_NOT_FOUND: "User not found" },
    fr: { USER_NOT_FOUND: "Utilisateur introuvable" },
  },
})
```
