# Infrastructure and Observability

## Managed dashboard and activity tracking

The paid `@better-auth/infra` package connects auth to Better Auth Infrastructure through `dash()`, providing dashboard administration, analytics, event tracking, and audit APIs. Activity tracking adds `lastActiveAt` to the user schema and requires migration.

```ts
dash({
  apiKey: process.env.BETTER_AUTH_API_KEY,
  activityTracking: { enabled: true, updateInterval: 300_000 },
})
```

## Audit logs

`dash()` records user, session, account, verification, organization, and security events. Add `dashClient()` to query by event, organization, identifier, or user. Pagination defaults to 50 and caps at 100.

```ts
const logs = await authClient.dash.getAuditLogs({
  session: (await authClient.getSession()).data,
  eventType: "user_signed_in",
  limit: 100,
  offset: 0,
});
```

## Sentinel

Pro-tier `sentinel()` can log, challenge, or block credential stuffing, impossible travel, trial abuse, compromised passwords, stale-account access, disallowed geographies, bots, suspicious IPs, excessive velocity, and invalid email domains.

Challenge mode requires `sentinelClient()`: it sends the `X-Visitor-ID` fingerprint and can solve proof-of-work into `X-PoW-Solution`.

```ts
sentinel({
  apiKey: process.env.BETTER_AUTH_API_KEY,
  security: {
    credentialStuffing: {
      enabled: true,
      thresholds: { challenge: 3, block: 5 },
    },
    compromisedPassword: { enabled: true, action: "block" },
  },
})
```

## Managed email

`sendEmail()` and `createEmailSender()` are available on Pro plans and read `BETTER_AUTH_API_KEY` plus optional `BETTER_AUTH_API_URL`. Typed templates cover verification, password reset, email change, sign-in/verification OTP, magic links, 2FA, organization/application invitations, deletion, and stale-account alerts. Calls return `{ success, messageId?, error? }`.

Production callbacks should schedule delivery with a platform lifetime primitive rather than awaiting it in the response path.

## Managed SMS

`sendSMS()` and `createSMSSender()` are also Pro features. With phone auth plus `dash()` or `sentinel()`, verification, 2FA, and OTP sign-in messages are automatic. Numbers are compact E.164. Templates are `phone-verification`, `two-factor`, and `sign-in-otp`; omitting the template sends generic verification.

## OpenTelemetry

Experimental automatic spans cover endpoints, database operations, hooks, and middleware through the `better-auth` tracer (since 1.6.0). Register a provider before constructing auth; no Better Auth option is required.

```ts
const provider = new NodeTracerProvider({
  spanProcessors: [new SimpleSpanProcessor(new ConsoleSpanExporter())],
});
provider.register();
```

## Serverless background tasks

`advanced.backgroundTasks.handler` connects deferred work to a lifetime primitive such as Vercel `waitUntil` or Cloudflare `ExecutionContext.waitUntil`.

```ts
import { waitUntil } from "@vercel/functions";

betterAuth({
  advanced: { backgroundTasks: { handler: waitUntil } },
})
```

Affected database writes become eventually consistent because responses may return before the work finishes. `runInBackgroundOrAwait()` awaits only when no handler is configured; `runInBackground()` remains fire-and-forget.

## Proxy and request-state diagnostics

Dynamic `baseURL` can allow preview/multi-domain hosts with a fallback. If using `advanced.trustedProxyHeaders`, accept forwarded host/protocol only behind a proxy that strips untrusted inputs.

After upgrades, `No request state found` often means duplicate `better-auth`, `@better-auth/core`, or `better-call`. Align scoped packages to compatible versions and force a single `better-call` resolution.
