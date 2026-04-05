# Better Auth Infrastructure (Paid)

`@better-auth/infra` is a **paid managed service** — separate from core Better Auth. Provides hosted dashboard, audit logs, security/abuse protection, and transactional email/SMS. Requires an API key from the Better Auth Infrastructure dashboard.

## dash() Plugin — Dashboard & Audit Logs

```ts
import { dash, dashClient } from "@better-auth/infra";

export const auth = betterAuth({
  plugins: [
    dash({
      apiKey: process.env.BETTER_AUTH_API_KEY,
      activityTracking: {
        enabled: true,
        updateInterval: 300000, // ms between lastActiveAt updates (default: 5min)
      },
    }),
  ],
});

export const authClient = createAuthClient({
  plugins: [dashClient()],
});
```

Activity tracking adds a `lastActiveAt: date` field to the user schema.

Audit logs are collected automatically:

```ts
const logs = await authClient.dash.getAuditLogs({
  session: session.data,
  limit: 50,
  offset: 0,
  eventType: "user_signed_in",
  organizationId: "org_123",
});
```

## sentinel() Plugin — Security & Abuse Protection

```ts
import { sentinel, sentinelClient } from "@better-auth/infra";

export const auth = betterAuth({
  plugins: [
    sentinel({
      apiKey: process.env.BETTER_AUTH_API_KEY,
      security: {
        credentialStuffing: {
          enabled: true,
          thresholds: { challenge: 3, block: 5 },
          windowSeconds: 3600,
          cooldownSeconds: 900,
        },
        impossibleTravel: { enabled: true, maxSpeedKmh: 1000, action: "challenge" },
        geoBlocking: { allowList: ["US", "CA", "GB"], action: "block" },
        botBlocking: { action: "challenge" },
        suspiciousIpBlocking: { action: "block" },
        velocity: {
          enabled: true,
          thresholds: { challenge: 10, block: 20 },
          maxSignupsPerVisitor: 5,
          maxPasswordResetsPerIp: 10,
          maxSignInsPerIp: 50,
          windowSeconds: 3600,
          action: "challenge",
        },
        freeTrialAbuse: { enabled: true, maxAccountsPerVisitor: 3, action: "block" },
        compromisedPassword: { enabled: true, action: "block", minBreachCount: 1 },
        emailValidation: { enabled: true, strictness: "medium", action: "block" },
        staleUsers: {
          enabled: true,
          staleDays: 90,
          action: "log",
          notifyUser: true,
          notifyAdmin: true,
          adminEmail: "admin@yourapp.com",
        },
        challengeDifficulty: 18,
      },
    }),
  ],
});

export const authClient = createAuthClient({
  plugins: [sentinelClient({ autoSolveChallenge: true })],
});
```

`SecurityAction` type: `"log" | "challenge" | "block"`. Start with `"log"` to understand traffic, then escalate.

When action is `"challenge"`, sentinel issues a Proof-of-Work challenge. The `sentinelClient` auto-solves it (sends solution via `X-PoW-Solution` header, fingerprint via `X-Visitor-ID` header).

## Email Service

```ts
import { sendEmail, createEmailSender } from "@better-auth/infra";

await sendEmail({
  template: "verify-email",
  to: "user@example.com",
  variables: {
    verificationUrl: "https://app.com/verify?token=abc",
    userEmail: "user@example.com",
    userName: "John",
    appName: "Your App",
  },
});

// Reusable sender
const emailSender = createEmailSender({
  apiKey: process.env.BETTER_AUTH_API_KEY,
  apiUrl: process.env.BETTER_AUTH_API_URL,
});
```

Available templates: `verify-email`, `reset-password`, `change-email`, `sign-in-otp`, `verify-email-otp`, `reset-password-otp`, `magic-link`, `two-factor`, `invitation`, `application-invite`, `delete-account`, `stale-account-user`, `stale-account-admin`.

Integration with Better Auth config:

```ts
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    async sendResetPassword({ user, url }) {
      await sendEmail({ template: "reset-password", to: user.email, variables: { resetLink: url, userEmail: user.email } });
    },
  },
  emailVerification: {
    sendOnSignUp: true,
    async sendVerificationEmail({ user, url }) {
      await sendEmail({ template: "verify-email", to: user.email, variables: { verificationUrl: url, userEmail: user.email } });
    },
  },
});
```

## SMS Service

```ts
import { sendSMS, createSMSSender } from "@better-auth/infra";

await sendSMS({
  to: "+14155551234", // E.164 format required
  code: "123456",
  template: "phone-verification", // or "two-factor", "sign-in-otp", or omit for generic
});

const smsSender = createSMSSender({ apiKey: process.env.BETTER_AUTH_API_KEY });
await smsSender.send({ to: "+14155551234", code: "123456", template: "two-factor" });
```

Both email and SMS services require Pro plan or above. Returns `{ success: boolean, messageId?: string, error?: string }`.
