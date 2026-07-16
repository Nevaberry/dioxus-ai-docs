# Infrastructure and Observability

## Managed dashboard and activity tracking

The paid `@better-auth/infra` package connects an auth instance to Better Auth Infrastructure through `dash()`. It exposes dashboard administration, analytics, event tracking, and audit APIs.

Optional activity tracking adds `lastActiveAt` to the user schema, so enabling it requires a migration.

```ts
export const auth = betterAuth({
  plugins: [
    dash({
      apiKey: process.env.BETTER_AUTH_API_KEY,
      activityTracking: { enabled: true, updateInterval: 300_000 },
    }),
  ],
});
```

## Audit logs

`dash()` records user, session, account, verification, organization, and security events without manual instrumentation. Add `dashClient()` to query by event, organization, identifier, or user. Pagination defaults to 50 records and is capped at 100.

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

The Pro-tier `sentinel()` plugin can log, challenge, or block:

- Credential stuffing, compromised passwords, and stale-account access.
- Impossible travel, suspicious IPs, excessive velocity, and disallowed geographies.
- Trial abuse, bots, and invalid email domains.

Challenge mode requires `sentinelClient()`. It supplies an `X-Visitor-ID` fingerprint and automatically returns solved proof-of-work in `X-PoW-Solution`.

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

## Managed authentication email

`@better-auth/infra` provides `sendEmail()` and reusable `createEmailSender()` clients on Pro plans and above. They read `BETTER_AUTH_API_KEY` and optional `BETTER_AUTH_API_URL`.

Typed templates cover verification, password reset, email change, sign-in and verification OTPs, magic links, two-factor codes, organization and application invitations, deletion, and stale-account alerts. Calls return `{ success, messageId?, error? }`.

Production auth callbacks should schedule delivery with a platform background primitive rather than await it in the response path.

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

## Managed authentication SMS

The package also provides `sendSMS()` and `createSMSSender()` on Pro plans and above. With phone auth plus `dash()` or `sentinel()`, verification, two-factor, and OTP sign-in messages are sent automatically.

Numbers must be compact E.164 strings. Supported auth templates are `phone-verification`, `two-factor`, and `sign-in-otp`; omitting `template` sends a generic verification message.

```ts
const result = await sendSMS({
  to: "+14155551234",
  code: "123456",
  template: "phone-verification",
});
```

## OpenTelemetry

Better Auth emits experimental spans for endpoints, database operations, hooks, and middleware through the `better-auth` tracer (since `1.6.0`). Register a provider before creating the auth instance; no Better Auth option is needed.

```ts
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import {
  ConsoleSpanExporter,
  SimpleSpanProcessor,
} from "@opentelemetry/sdk-trace-base";

const provider = new NodeTracerProvider({
  spanProcessors: [new SimpleSpanProcessor(new ConsoleSpanExporter())],
});
provider.register();
```

## Background-task handler

`advanced.backgroundTasks.handler` connects deferred auth work to a platform lifetime primitive such as Vercel `waitUntil` or Cloudflare `ExecutionContext.waitUntil`. Responses may return before deferred database work completes, so affected writes are eventually consistent.

```ts
import { waitUntil } from "@vercel/functions";

export const auth = betterAuth({
  advanced: {
    backgroundTasks: { handler: waitUntil },
  },
});
```

Within request hooks, `ctx.context.runInBackground()` is fire-and-forget. `runInBackgroundOrAwait()` also uses the handler when configured, but awaits when there is no handler; use it for required work such as email delivery.

```ts
hooks: {
  after: createAuthMiddleware(async (ctx) => {
    ctx.context.runInBackground(sendAnalytics());
    await ctx.context.runInBackgroundOrAwait(sendRequiredEmail());
  }),
}
```

## Dynamic and proxy-derived base URLs

`baseURL` can be an allowlisted dynamic configuration for previews, proxies, and multi-domain applications. Without an explicit URL, server clients also check `VERCEL_URL` and `NEXTAUTH_URL`.

```ts
baseURL: {
  allowedHosts: ["myapp.com", "*.vercel.app", "preview-*.myapp.com"],
  fallback: "https://myapp.com",
  protocol: "auto",
}
```

When no configured or environment-provided URL exists, `advanced.trustedProxyHeaders` derives it from `X-Forwarded-Host` and `X-Forwarded-Proto`. Enable this only behind a proxy that strips untrusted values, and retain a `trustedOrigins` allowlist.

An asynchronous origins callback must handle `undefined` during initialization and direct `auth.api` calls:

```ts
export const auth = betterAuth({
  advanced: { trustedProxyHeaders: true },
  trustedOrigins: async (request) =>
    request ? await queryTrustedDomains() : ["https://app.example.com"],
});
```

## Client IP detection

The server automatically detects client IPs. Captcha and security features should use that server-derived value rather than an arbitrary client header.

## Duplicate request-state failures

`No request state found` after an upgrade can indicate multiple resolved copies of `better-auth`, `@better-auth/core`, or `better-call`. Inspect the dependency graph, align all Better Auth packages to compatible versions in production dependencies, and enforce one `better-call` resolution if older Yarn or pnpm still duplicates it.

```sh
pnpm why better-auth
pnpm why @better-auth/core
pnpm why better-call
```
