# Core Authentication

## Email/password sign-up behavior

`signUp` accepts `rememberMe`. Email sign-in and sign-up also accept form data.

`emailAndPassword.onExistingUserSignUp` runs when registration targets an existing address, but only while protected responses are active through `requireEmailVerification: true` or `autoSignIn: false`. Use it to notify the existing owner without changing the indistinguishable client response.

```ts
emailAndPassword: {
  enabled: true,
  autoSignIn: false,
  onExistingUserSignUp: async ({ user }) => {
    void notifyExistingUser(user.email);
  },
}
```

Enumeration-safe synthetic users now include plugin-defined fields. Do not branch client behavior on protected registration results.

## Email verification

`emailVerification.sendOnSignIn` sends a verification email when an unverified user attempts to sign in. `afterEmailVerification` is the post-verification lifecycle hook and replaces removed `onEmailVerification`.

```ts
emailVerification: {
  sendOnSignIn: true,
  sendVerificationEmail: async ({ user, url }) => sendEmail(user.email, url),
  afterEmailVerification: async (user) => recordVerification(user.id),
}
```

## Password checks and resets

The server-side `verifyPassword` endpoint verifies the current user's password without beginning a new sign-in. Use it before sensitive account operations.

`authClient.requestPasswordReset` replaces `authClient.forgotPassword`. The removed `/forget-password/email-otp` endpoint must be replaced by the standard password-reset flow.

## Email changes

`user.changeEmail.sendChangeEmailConfirmation` can require confirmation at the current address before sending verification to the new address. The old change-flow `sendChangeEmailVerification` callback is removed; new-address verification uses `emailVerification.sendVerificationEmail`.

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

The `/change-email` endpoint always returns `{ status: true }` and simulates token creation when needed. Treat the response as acceptance of the request, not proof that the target address exists or changed.

## Account linking

Account linking can proceed when the provider account has no email address. Social-link email matching is case-insensitive, and trusted providers can be resolved dynamically.

Request incremental Google permissions for an already-linked account with `linkSocial`. The completed OAuth flow updates the stored account scopes and access token.

```ts
await authClient.linkSocial({
  provider: "google",
  scopes: ["https://www.googleapis.com/auth/drive.file"],
});
```

## Social providers

Built-in provider keys include Notion, Slack, Linear, Faceit, Railway, Polar, and Paybin. Social provider configuration may be asynchronous.

### Apple web and native identifiers

Apple must be a trusted origin. If `clientId` is a web Service ID but a native ID token has the app bundle ID as its audience, configure `appBundleIdentifier` or token validation fails.

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

`socialProviders.discord.permissions` sets the Discord bot permission bitfield. Discord uses it only when the OAuth request also includes the `bot` scope.

```ts
socialProviders: {
  discord: {
    clientId: process.env.DISCORD_CLIENT_ID!,
    clientSecret: process.env.DISCORD_CLIENT_SECRET!,
    permissions: 2048 | 16384,
  },
}
```

## Username sign-in

The username plugin supports availability checks and custom normalization. `signInUsername` accepts `callbackURL`.

By default, canonical `username` is lowercased while the pre-normalized value is preserved in `displayUsername`. Both validators run before normalization unless `validationOrder` says otherwise. Disable `/is-username-available` when exposing availability would permit enumeration.

```ts
betterAuth({
  disabledPaths: ["/is-username-available"],
  plugins: [username({
    validationOrder: { username: "post-normalization" },
  })],
})
```

## Account deletion

User deletion is disabled by default. Once enabled, deletion must be authorized by a valid password, a fresh session, or configured email verification for passwordless users. A custom verification page completes deletion by passing its token to `deleteUser`.

```ts
user: {
  deleteUser: {
    enabled: true,
    sendDeleteAccountVerification: async ({ user, url }) =>
      void sendEmail(user.email, url),
  },
}
```

## Account-info endpoint

The account-info endpoint is `GET /account-info` and receives `query`, not the old `POST` body shape.

```ts
await auth.api.accountInfo({ query: { /* parameters */ } });
```
