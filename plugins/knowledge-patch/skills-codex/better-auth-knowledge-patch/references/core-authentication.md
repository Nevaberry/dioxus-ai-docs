# Core Authentication

## Email/password and verification

### Verification mail on sign-in

Since 1.3.0, `emailVerification.sendOnSignIn` sends a verification message when an unverified user attempts to sign in.

```ts
emailVerification: {
  sendOnSignIn: true,
  afterEmailVerification: async (user) => recordVerification(user.id),
}
```

`afterEmailVerification` is the post-verification callback. Sign-up accepts `rememberMe`, and account linking may proceed for an account that has no email address.

### Existing-user sign-up notifications

`emailAndPassword.onExistingUserSignUp` runs when registration targets an existing address, but only while enumeration-protected responses are active through `requireEmailVerification: true` or `autoSignIn: false`. It can notify the existing owner without changing the indistinguishable response.

```ts
emailAndPassword: {
  enabled: true,
  autoSignIn: false,
  onExistingUserSignUp: async ({ user }) => {
    void notifyExistingUser(user.email);
  },
}
```

### Email changes

`user.changeEmail.sendChangeEmailConfirmation` can require approval through the current address before sending verification to the new address. New-address verification uses `emailVerification.sendVerificationEmail`; the former change-flow `sendChangeEmailVerification` callback is removed.

```ts
user: {
  changeEmail: {
    enabled: true,
    sendChangeEmailConfirmation: async ({ user, newEmail, url }) =>
      sendEmail({ to: user.email, text: `Approve ${newEmail}: ${url}` }),
  },
}
```

The `/change-email` endpoint is enumeration-safe: it always returns `{ status: true }` and simulates token generation when needed. Treat that response as request acceptance, not proof that an address existed or changed.

### Current-password checks

The server-side `verifyPassword` endpoint checks the current user's password without starting a new sign-in. Use it before sensitive account operations when password proof is appropriate.

## Password reset and account information

Use `authClient.requestPasswordReset`, not the removed `forgotPassword` name. Account information is a `GET /account-info` operation and receives parameters under `query`, not a `POST` body.

```ts
await authClient.requestPasswordReset({ email });
await auth.api.accountInfo({ query: { /* parameters */ } });
```

The obsolete `/forget-password/email-otp` endpoint is gone; use the standard password-reset flow.

## Usernames

The username plugin supports availability checks and custom normalization, and `signInUsername` accepts a `callbackURL`. Canonical `username` is lowercased by default while `displayUsername` retains the pre-normalized spelling. Both validators normally run before normalization; change `validationOrder` when canonical-value validation is required.

```ts
betterAuth({
  disabledPaths: ["/is-username-available"],
  plugins: [username({
    validationOrder: { username: "post-normalization" },
  })],
});
```

Disable `/is-username-available` if publishing availability would enable enumeration.

## Social providers and account linking

### Incremental Google permissions

Call `linkSocial` with extra scopes for an already-linked Google account. A successful OAuth flow replaces the stored scopes and access token.

```ts
await authClient.linkSocial({
  provider: "google",
  scopes: ["https://www.googleapis.com/auth/drive.file"],
});
```

Social-provider configuration can be asynchronous, trusted providers can be resolved dynamically, and social-link email comparison is case-insensitive. Railway is available as a provider. The 1.3 additions were Notion, Slack, Linear, and Faceit; Polar and Paybin were added later. Last-login-method tracking recognizes SIWE and passkeys.

### Apple identifiers

Apple must be a trusted origin. If `clientId` is a web Service ID but native sign-in sends a token whose audience is the app bundle ID, configure `appBundleIdentifier` or token validation fails.

```ts
socialProviders: {
  apple: {
    clientId: process.env.APPLE_CLIENT_ID!,
    clientSecret: appleClientSecret,
    appBundleIdentifier: "com.example.app",
  },
},
trustedOrigins: ["https://appleid.apple.com"],
```

### Discord bot permissions

`socialProviders.discord.permissions` sets the bot permission bitfield. Discord applies it only when the OAuth request also includes the `bot` scope.

```ts
socialProviders: {
  discord: {
    clientId,
    clientSecret,
    permissions: 2048 | 16384,
  },
}
```

## Form and session-related auth additions

Email sign-in/sign-up accepts form data. Custom additional session fields can be changed without reauthentication through `authClient.updateSession()`. Other auth-flow facilities include read-replica-aware deferred refresh, per-request refresh skipping, and enumeration-safe synthetic users that include plugin-defined fields.

```ts
await authClient.updateSession({ theme: "dark", language: "en" });
```

## Account deletion

User deletion is disabled by default. Once enabled, authorize it with a valid password, a fresh session, or configured email verification for passwordless users. A custom verification page completes deletion by sending its token to `deleteUser`.

```ts
user: {
  deleteUser: {
    enabled: true,
    sendDeleteAccountVerification: async ({ user, url }) =>
      void sendEmail(user.email, url),
  },
}
```
