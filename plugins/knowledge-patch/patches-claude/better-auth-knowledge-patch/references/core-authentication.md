# Core Authentication

## Email/password and verification lifecycle

### Verification mail during sign-in

Set `emailVerification.sendOnSignIn: true` to send a verification message when an unverified user attempts to sign in (since 1.3.0). Sign-up also accepts `rememberMe`, and `afterEmailVerification` is the post-verification callback. Account linking may proceed even when the linked account has no email.

### Existing-user registration notification

`emailAndPassword.onExistingUserSignUp` runs when a registration targets an existing email, but only while enumeration-safe responses are active through `requireEmailVerification: true` or `autoSignIn: false`. Use it to notify the owner without changing the indistinguishable client response.

```ts
emailAndPassword: {
  enabled: true,
  autoSignIn: false,
  onExistingUserSignUp: async ({ user }) => {
    void notifyExistingUser(user.email);
  },
}
```

### Password and email changes

`auth.api.verifyPassword` verifies the current signed-in user's password without starting a new sign-in flow (since 1.5.0). Use it before sensitive account operations.

`/change-email` always returns `{ status: true }` and simulates token generation when needed, so its response means only that the request was accepted. To require approval at the old address, enable `user.changeEmail` and implement `sendChangeEmailConfirmation`; verification at the new address uses `emailVerification.sendVerificationEmail` (since 1.4.0).

```ts
user: {
  changeEmail: {
    enabled: true,
    sendChangeEmailConfirmation: async ({ user, newEmail, url }) => {
      await sendEmail({ to: user.email, text: `Approve ${newEmail}: ${url}` });
    },
  },
}
```

### Account deletion

Deletion is disabled by default. Once enabled, require a valid password, a fresh session, or configured email verification for a passwordless user. A custom verification page completes the operation by passing its token to `deleteUser`.

```ts
user: {
  deleteUser: {
    enabled: true,
    sendDeleteAccountVerification: async ({ user, url }) =>
      void sendEmail(user.email, url),
  },
}
```

## Social providers and account linking

### Incremental Google permissions

Call `linkSocial` with additional scopes for an already-linked Google account. The completed OAuth flow updates its stored scopes and access token.

```ts
await authClient.linkSocial({
  provider: "google",
  scopes: ["https://www.googleapis.com/auth/drive.file"],
});
```

### Apple web and native identifiers

Add `https://appleid.apple.com` to `trustedOrigins`. If `clientId` is a web Service ID but native sign-in supplies a token whose audience is the app bundle ID, set `appBundleIdentifier` or validation fails.

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

`socialProviders.discord.permissions` is the bot permission bitfield. Discord uses it only when the OAuth request also contains the `bot` scope.

```ts
socialProviders: {
  discord: {
    clientId: process.env.DISCORD_CLIENT_ID!,
    clientSecret: process.env.DISCORD_CLIENT_SECRET!,
    permissions: 2048 | 16384,
  },
}
```

### Provider additions

`socialProviders` includes Notion, Slack, Linear, and Faceit (since 1.3.0), plus Railway (since 1.5-guide). Trusted providers may be resolved dynamically, social-link email matching is case-insensitive, and async social-provider configuration is supported.

Email sign-in and sign-up accept form data. Enumeration-safe signup creates synthetic users that include plugin-defined fields, so custom plugin schemas continue to receive a shape compatible with the real user.

## Username flows

The username plugin supports availability checks, custom normalization, and a `callbackURL` on `signInUsername` (since 1.3.0). The canonical `username` is lowercased by default while `displayUsername` preserves the pre-normalized value. Validators run before normalization unless `validationOrder` says otherwise.

Disable the availability path where exposing it would permit enumeration:

```ts
betterAuth({
  disabledPaths: ["/is-username-available"],
  plugins: [username({ validationOrder: { username: "post-normalization" } })],
})
```
