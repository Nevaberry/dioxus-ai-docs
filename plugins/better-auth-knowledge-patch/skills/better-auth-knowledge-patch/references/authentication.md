# Authentication Methods

## Email Enumeration Protection with customSyntheticUser

When `requireEmailVerification: true` or `autoSignIn: false`, the sign-up endpoint returns the same `200` response for both new and existing emails (OWASP best practice). If plugins add fields to the user table, use `customSyntheticUser` to build an indistinguishable fake response:

```ts
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    customSyntheticUser: ({ coreFields, additionalFields, id }) => ({
      ...coreFields,
      role: "user",
      banned: false,
      banReason: null,
      banExpires: null,
      ...additionalFields,
      id, // must be last to match DB output order
    }),
    onExistingUserSignUp: async ({ user }, request) => {
      void sendEmail({ to: user.email, subject: "Sign-up attempt with your email" });
    },
  },
  plugins: [admin()],
});
```

The `/change-email` endpoint also returns success for already-registered emails.

## Generic OAuth Plugin (genericOAuth)

Add any OAuth2/OIDC provider without built-in support:

```ts
import { genericOAuth } from "better-auth/plugins";
import { genericOAuthClient } from "better-auth/client/plugins";

export const auth = betterAuth({
  plugins: [
    genericOAuth({
      config: [
        {
          providerId: "keycloak",
          clientId: process.env.KC_CLIENT_ID,
          clientSecret: process.env.KC_CLIENT_SECRET,
          discoveryUrl: "https://kc.example.com/realms/main/.well-known/openid-configuration",
        },
        {
          providerId: "instagram",
          clientId: process.env.IG_CLIENT_ID,
          clientSecret: process.env.IG_CLIENT_SECRET,
          authorizationUrl: "https://api.instagram.com/oauth/authorize",
          tokenUrl: "https://api.instagram.com/oauth/access_token",
          scopes: ["user_profile"],
        },
      ],
    }),
  ],
});

const authClient = createAuthClient({ plugins: [genericOAuthClient()] });
await authClient.signIn.oauth2({ providerId: "keycloak", callbackURL: "/dashboard" });
```

Pre-configured helpers: `slack()`, `auth0()`, `keycloak()`, `okta()`, `microsoftEntraId()`.

## linkSocial for Additional OAuth Scopes

Request more OAuth scopes from an already-linked provider:

```ts
await authClient.linkSocial({
  provider: "google",
  scopes: ["https://www.googleapis.com/auth/drive.file"],
});
```

Requires Better Auth v1.2.7+. Updated access token and scope stored in the account record.

## Social Sign-In Extra Callbacks

`signIn.social` supports `newUserCallbackURL` to redirect newly registered users separately from returning users, plus `errorCallbackURL` for error redirects. Also supports `idToken` or `accessToken` auth instead of redirect flow.

## Magic Link: Metadata, Token Storage & Attempt Limits

```ts
await authClient.signIn.magicLink({
  email: "user@example.com",
  callbackURL: "/dashboard",
  metadata: { inviteId: "123" }, // forwarded to sendMagicLink
});
```

Token storage: `"plain"` (default), `"hashed"`, or custom hasher. `allowedAttempts` defaults to `1` (single-use link). Storage backend controlled by global `verification` config.

## Email OTP: Change Email, Override Verification & Resend

Change email with OTP (disabled by default):

```ts
emailOTP({
  changeEmail: {
    enabled: true,
    verifyCurrentEmail: true,
  },
})
// Flow: sendVerificationOtp(currentEmail) → requestEmailChange(newEmail, currentOtp) → changeEmail(newEmail, newOtp)
```

Replace default email verification link with OTP:

```ts
emailOTP({ overrideDefaultEmailVerification: true })
```

`resendStrategy: "reuse"` resends the same OTP (extends expiry) instead of generating a new one. Falls back to `"rotate"` when OTP is hashed or attempts exhausted.

OTP storage: `storeOTP` supports `"plain"`, `"encrypted"`, `"hashed"`, or custom `{ encrypt, decrypt }` / `{ hash }`.

## Username: Display Username & Normalization

Two fields: `username` (normalized, unique) and `displayUsername` (original casing):

```ts
username({
  usernameNormalization: (u) => u.toLowerCase().replaceAll("0", "o"),
  displayUsernameNormalization: false,
  validationOrder: {
    username: "post-normalization",
    displayUsername: "post-normalization",
  },
})
// Sign up: authClient.signUp.email({ email, password, name, username: "TestUser", displayUsername: "TestUser123" })
// Sign in: authClient.signIn.username({ username: "testuser", password })
// Check: authClient.isUsernameAvailable({ username: "test" })
```

## Anonymous: Account Linking

Anonymous users auto-link when signing in with another method:

```ts
anonymous({
  onLinkAccount: async ({ anonymousUser, newUser }) => {
    // Move cart items, preferences, etc.
  },
  generateRandomEmail: () => `guest-${crypto.randomUUID()}@example.com`,
  generateName: () => "Anonymous User",
  // emailDomainName: "example.com", // simpler alternative
})
```

Schema adds `isAnonymous: boolean` to user table. `disableDeleteAnonymousUser: true` prevents deletion endpoint.

## Phone Number: Sign-Up on Verify, Custom Verification & Password Reset

```ts
phoneNumber({
  sendOTP: ({ phoneNumber, code }, ctx) => { /* send SMS */ },
  signUpOnVerification: {
    getTempEmail: (phone) => `${phone}@my-site.com`,
    getTempName: (phone) => phone,
  },
  requireVerification: true, // block sign-in until phone verified
})
```

Custom OTP verification (e.g., Twilio Verify):

```ts
phoneNumber({
  sendOTP: ({ phoneNumber, code }, ctx) => { /* send via Twilio */ },
  verifyOTP: async ({ phoneNumber, code }, ctx) => {
    const result = await twilioClient.verify.services("SID").verificationChecks.create({ to: phoneNumber, code });
    return result.status === "approved";
  },
})
```

Password reset via phone:

```ts
await authClient.phoneNumber.requestPasswordReset({ phoneNumber: "+1234567890" });
await authClient.phoneNumber.resetPassword({ phoneNumber: "+1234567890", otp: "123456", newPassword: "new-pw" });
```

## Multi-Session

Multiple active sessions per device:

- `authClient.multiSession.listDeviceSessions()` — list all sessions
- `authClient.multiSession.setActive({ sessionToken })` — switch active
- `authClient.multiSession.revoke({ sessionToken })` — revoke one
- `signOut()` revokes all sessions
- `multiSession({ maximumSessions: 3 })` — default is 5

## Change Email

```ts
user: {
  changeEmail: {
    enabled: true,
    sendChangeEmailConfirmation: async ({ user, newEmail, url, token }, request) => {
      // Sends to CURRENT email for confirmation before verification email goes to new email
    },
    updateEmailWithoutVerification: true, // skip verification if current email unverified
  },
}
// Client: await authClient.changeEmail({ newEmail: "new@e.com", callbackURL: "/dashboard" });
```

## Delete User with Verification

```ts
user: {
  deleteUser: {
    enabled: true,
    sendDeleteAccountVerification: async ({ user, url, token }, request) => { /* send email */ },
    beforeDelete: async (user, request) => { /* throw APIError to abort */ },
    afterDelete: async (user, request) => { /* cleanup */ },
  },
}
// Client: authClient.deleteUser({ password: "pw" }) or deleteUser({ token }) or deleteUser({ callbackURL: "/bye" })
```

## Account Linking Options

```ts
account: {
  accountLinking: {
    enabled: true,
    trustedProviders: ["google"],
    allowDifferentEmails: true,
    updateUserInfoOnLink: true,
    allowUnlinkingAll: true,
  },
}
// authClient.unlinkAccount({ providerId: "google", accountId: "123" })
```
