# Infrastructure and Observability

## Automatic OpenTelemetry spans

Better Auth emits experimental OpenTelemetry spans through the `better-auth` tracer for endpoints, database operations, hooks, and middleware. Register a tracer provider before constructing the auth instance; no Better Auth option is required.

```ts
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import {
  ConsoleSpanExporter,
  SimpleSpanProcessor,
} from "@opentelemetry/sdk-trace-base";

const provider = new NodeTracerProvider({
  spanProcessors: [
    new SimpleSpanProcessor(new ConsoleSpanExporter()),
  ],
});
provider.register();
```

## Managed dashboard and activity

The paid `@better-auth/infra` package connects an auth instance to Better Auth Infrastructure through `dash()`. It supplies dashboard administration, analytics, event tracking, audit APIs, and optional activity tracking. Activity tracking adds `lastActiveAt` to the user schema, so migrate after enabling it.

```ts
export const auth = betterAuth({
  plugins: [dash({
    apiKey: process.env.BETTER_AUTH_API_KEY,
    activityTracking: {
      enabled: true,
      updateInterval: 300_000,
    },
  })],
});
```

## Audit-log queries

`dash()` records user, session, account, verification, organization, and security events without application instrumentation. Add `dashClient()` to query by event, organization, identifier, or user. Pagination defaults to 50 and caps at 100.

```ts
const authClient = createAuthClient({ plugins: [dashClient()] });
const session = await authClient.getSession();
const logs = await authClient.dash.getAuditLogs({
  session: session.data,
  eventType: "user_signed_in",
  limit: 100,
  offset: 0,
});
```

## Sentinel abuse protection

The Pro-tier `sentinel()` plugin can log, challenge, or block credential stuffing, impossible travel, trial abuse, compromised passwords, stale-account access, disallowed geographies, bots, suspicious IPs, excess velocity, and invalid email domains.

Challenge mode requires `sentinelClient()`. It supplies the `X-Visitor-ID` fingerprint and can solve proof-of-work automatically, returning the answer in `X-PoW-Solution`.

```ts
export const auth = betterAuth({
  plugins: [sentinel({
    apiKey: process.env.BETTER_AUTH_API_KEY,
    security: {
      credentialStuffing: {
        enabled: true,
        thresholds: { challenge: 3, block: 5 },
      },
      compromisedPassword: { enabled: true, action: "block" },
      impossibleTravel: { enabled: true, action: "challenge" },
    },
  })],
});

const authClient = createAuthClient({
  plugins: [sentinelClient({ autoSolveChallenge: true })],
});
```

## Managed email

On Pro plans and above, `@better-auth/infra` provides `sendEmail()` and reusable `createEmailSender()` clients. They read `BETTER_AUTH_API_KEY` and optionally `BETTER_AUTH_API_URL`. Typed templates cover verification, password reset, email change, sign-in and verification OTPs, magic links, two-factor codes, organization/application invitations, deletion, and stale-account alerts. Results have `{ success, messageId?, error? }`.

```ts
await sendEmail({
  template: "verify-email",
  to: user.email,
  variables: {
    verificationUrl: url,
    userEmail: user.email,
    userName: user.name,
    appName: "Example",
  },
});
```

In production, schedule delivery with a platform background primitive rather than awaiting it in the response path, unless request semantics require completion.

## Managed SMS

The same package supplies `sendSMS()` and `createSMSSender()` on Pro plans and above. With phone auth plus `dash()` or `sentinel()`, verification, two-factor, and OTP sign-in messages are sent automatically. Use compact E.164 numbers. Auth templates are `phone-verification`, `two-factor`, and `sign-in-otp`; no template sends a generic verification message.

```ts
const result = await sendSMS({
  to: "+14155551234",
  code: "123456",
  template: "phone-verification",
});
```

## Serverless background tasks

Connect `advanced.backgroundTasks.handler` to a lifetime primitive such as Vercel `waitUntil` or Cloudflare `ExecutionContext.waitUntil`. Affected responses may return before background database writes finish, so those writes are eventually consistent.

```ts
import { waitUntil } from "@vercel/functions";

export const auth = betterAuth({
  advanced: {
    backgroundTasks: { handler: waitUntil },
  },
});
```

`runInBackground()` always schedules response-tail work. `runInBackgroundOrAwait()` uses the handler if present and awaits otherwise.

## Duplicate-package request state

`No request state found` after an upgrade often indicates multiple resolved copies of `better-auth`, `@better-auth/core`, or `better-call`. Inspect dependency paths, align all Better Auth packages in production dependencies, and force one `better-call` resolution when an older Yarn or pnpm layout still duplicates it.

```sh
pnpm why better-auth
pnpm why @better-auth/core
pnpm why better-call
```

## Proxy diagnostics

If request URLs are inferred from forwarded headers, verify the front proxy strips user-supplied `X-Forwarded-Host` and `X-Forwarded-Proto`. Dynamic origins callbacks must tolerate initialization calls without a request. Treat URL derivation and origin authorization as separate diagnostics.
