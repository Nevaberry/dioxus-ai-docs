# Identity and Utility Plugins

## Sign-In with Ethereum

The built-in `siwe` plugin provides Sign-In with Ethereum. Last-login-method tracking recognizes SIWE and passkeys.

```ts
import { siwe } from "better-auth/plugins";

plugins: [siwe()]
```

## Passkeys

The passkey plugin lives in `@better-auth/passkey`. Conditional autofill requires `webauthn` as the last `autocomplete` token and an `autoFill` sign-in started only after conditional-mediation support is confirmed. Registration and sign-in do not honor fetch option `throw: true`; inspect the returned data object's error.

```html
<input name="username" autocomplete="username webauthn">
```

```ts
if (await PublicKeyCredential.isConditionalMediationAvailable?.()) {
  void authClient.signIn.passkey({ autoFill: true });
}
```

Passkey-first onboarding may register without an existing session. Set `registration.requireSession: false` and securely authenticate the supplied context before resolving or creating the user. Registration and authentication options accept server-defined WebAuthn extensions such as `credProps`.

```ts
import { passkey } from "@better-auth/passkey";

plugins: [passkey({
  registration: {
    requireSession: false,
    resolveUser: async ({ ctx, context }) => {
      await validateRegistrationContext(context, ctx);
      return { id: "user-id", name: "user@example.com" };
    },
  },
})]
```

## Two-factor authentication

`twoFactor.enable` stages enrollment: it returns the TOTP URI and backup codes, but `twoFactorEnabled` remains false until TOTP verification unless `skipVerificationOnEnable` is set. `allowPasswordless` removes the password requirement only for users without a credential account.

Server-side continuations must forward cookies returned by sign-in into the subsequent two-factor call.

```ts
const { headers: responseHeaders, response } = await auth.api.signInEmail({
  returnHeaders: true,
  body: { email, password },
});
if ("twoFactorRedirect" in response) {
  // Forward responseHeaders cookies into the next auth.api 2FA call.
}
```

TOTP accepts the immediately previous and next periods, each 30 seconds by default. Backup codes are single-use; regeneration invalidates all previous codes. Trusted devices bypass 2FA for 30 days, with the window refreshed after each successful sign-in. Trust duration is enforced server-side.

## Magic links

Magic-link sign-in creates an unknown user unless `disableSignUp` is true. Without a callback it redirects to `/`; manually calling verification without a callback returns the session. Links expire after 300 seconds by default, stored tokens default to plain text, and `allowedAttempts` can limit verification attempts.

## Email OTP

Email OTPs allow three verification attempts by default and become invalid after exhaustion. Resends normally rotate the code. `resendStrategy: "reuse"` extends and resends a recoverable code, but hashed storage falls back to rotation and exhausted codes are always replaced.

```ts
emailOTP({
  resendStrategy: "reuse",
  storeOTP: "encrypted",
  sendVerificationOTP,
})
```

Email OTP also supports change-email and richer sign-in fields.

## Phone authentication

The phone plugin supports custom OTP verification and additional sign-up fields. With `requireVerification`, password sign-in for an unverified phone returns `401 PHONE_NUMBER_NOT_VERIFIED` and sends an OTP. Internal OTPs expire after 300 seconds and allow three attempts before deletion and a 403 response.

Verification creates a session unless `disableSession` is passed. Phone-only sign-up requires `signUpOnVerification.getTempEmail`.

```ts
phoneNumber({
  sendOTP,
  requireVerification: true,
  signUpOnVerification: {
    getTempEmail: (phone) => `${phone}@example.invalid`,
  },
})
```

## Anonymous-account conversion

When an anonymous user signs in or signs up through another method, `onLinkAccount` is the application-data migration boundary and receives both identities. The anonymous user is deleted by default after linking; move carts and other owned data inside this hook. The plugin can also opt into deleting anonymous users explicitly.

```ts
anonymous({
  onLinkAccount: async ({ anonymousUser, newUser }) =>
    moveOwnedData(anonymousUser.id, newUser.id),
})
```

## Bearer sessions

The bearer plugin returns the session token in `set-auth-token`. Use that value—not a JWT-plugin token—in `Authorization: Bearer ...`; `getSession` resolves it. `requireSignature` defaults to false.

```ts
plugins: [bearer({ requireSignature: true })]
const token = ctx.response.headers.get("set-auth-token");
await fetch(url, {
  headers: { Authorization: `Bearer ${token}` },
});
```

## JWT service tokens

The JWT plugin is a service-token bridge, not session authentication. Tokens default to the complete user payload, a 15-minute expiry, and `baseURL` for both issuer and audience. JWKS supports alternate algorithms and scheduled key rotation with a grace period.

```ts
plugins: [jwt({
  jwks: {
    rotationInterval: 60 * 60 * 24 * 30,
    gracePeriod: 60 * 60 * 24 * 30,
  },
})]
```

When using the OAuth provider, disable both the JWT plugin's `/token` endpoint and `set-auth-jwt` header to avoid parallel protocol endpoints.

```ts
betterAuth({
  disabledPaths: ["/token"],
  plugins: [jwt({ disableSettingJwtHeader: true })],
})
```

## Multi-session cookies

The multi-session plugin keeps an extra browser cookie and defaults to five account sessions per device. Switching or revoking needs the target session token. Ordinary `signOut` revokes every session tracked by the plugin, not just the active account.

## API keys

### Package, configurations, and ownership

Import the server and client plugins from `@better-auth/api-key` and `@better-auth/api-key/client`. Multiple named configurations may coexist. `references: "organization"` issues organization-owned keys; user-owned keys remain the default.

```ts
import { apiKey } from "@better-auth/api-key";

plugins: [apiKey([
  { configId: "user-keys", prefix: "usr_" },
  { configId: "org-keys", prefix: "org_", references: "organization" },
])]
```

`requireName` can require a creation-time key name, and `verifyKey` may be asynchronous. `defaultPermissions` receives `referenceId`. Server-side `updateApiKey` needs at least `userId` or request headers.

### API-key sessions and authorization

Mock sessions must be enabled explicitly and work only for user-owned keys. Organization-owned keys cannot impersonate one user. Configure `apiKeyHeaders` and let `getSession` validate once; calling `verifyApiKey` before `getSession` consumes the key's counters twice.

```ts
apiKey({
  enableSessionForAPIKeys: true,
  apiKeyHeaders: ["x-api-key", "x-service-key"],
})
```

Organization-owned key operations require membership plus the relevant `apiKey` `create`, `read`, `update`, or `delete` permission. Owners get all four. `verifyApiKey({ permissions })` requires every requested permission.

### Storage and accounting

Keys may live in configured secondary storage. With `fallbackToDatabase: true`, reads check secondary storage then warm it from the database, while writes target both stores. Expiring keys get a secondary-store TTL. Supply the right `configId` to every get, update, delete, or verify when configurations use different backends.

```ts
apiKey({
  storage: "secondary-storage",
  fallbackToDatabase: true,
})
```

Each validation consumes rate limits and an optional `remaining` budget. At zero, the key is disabled and removed. Refills set `remaining` to `refillAmount` rather than adding. `deferUpdates` sends counter, timestamp, and budget writes through the global background handler, making responses optimistically and eventually consistent.

```ts
apiKey({ deferUpdates: true }) // requires advanced.backgroundTasks.handler
```

## Captcha

Captcha protects POST requests only and defaults to `/sign-up/email`, `/sign-in/email`, and `/request-password-reset`; supplying `endpoints` replaces the defaults. Clients put proof in `x-captcha-response`. The server detects the remote IP rather than trusting a client-provided IP header.

## Google One Tap

One Tap redirects to `/` after success unless `callbackURL` changes the destination or an `onSuccess` fetch callback handles navigation. Dismissed prompts retry with exponential backoff, by default five attempts starting at one second. `onPromptNotification` is the fallback for alternate UI. Button mode is available.

## One-time cross-domain sessions

The one-time-token plugin attaches a token to the current session and returns that session once on verification. Default lifetime is three minutes. Client generation is enabled and database storage is plain by default, so sensitive deployments should require server generation and hash the token.

```ts
oneTimeToken({
  disableClientRequest: true,
  storeToken: "hashed",
})
```
