# API Keys & Stripe Billing

## API Key Plugin (`@better-auth/api-key`)

**v1.5 breaking**: Moved from `better-auth/plugins` to `@better-auth/api-key`.

### Session Mocking from API Keys

`enableSessionForAPIKeys: true` creates a mock session whenever `x-api-key` header is present:

```ts
apiKey({ enableSessionForAPIKeys: true, apiKeyHeaders: ["x-api-key"] })
// Or custom getter: customAPIKeyGetter: (ctx) => ctx.request.headers.get("x-api-key")
```

Only works with user-owned keys (`references: "user"`), not org-owned keys.

### Multiple Configurations

```ts
apiKey([
  { configId: "public", defaultPrefix: "pk_", rateLimit: { enabled: true, maxRequests: 100, timeWindow: 3600000 } },
  { configId: "secret", defaultPrefix: "sk_", enableMetadata: true },
])
```

All operations must specify `configId` when using multiple configs.

### Organization-Owned Keys

```ts
apiKey([
  { configId: "org-keys", defaultPrefix: "org_", references: "organization" },
])
// Create: auth.api.createApiKey({ body: { configId: "org-keys", organizationId: "org_123" } })
```

Uses org plugin's RBAC — add `apiKey: ["create", "read", "update", "delete"]` to AC statements and roles.

### Storage Modes

```ts
apiKey({ storage: "database" })              // default
apiKey({ storage: "secondary-storage" })     // Redis only
apiKey({ storage: "secondary-storage", fallbackToDatabase: true }) // Redis with DB fallback + cache warming
apiKey({ storage: "secondary-storage", customStorage: { get, set, delete } }) // custom
```

### Remaining, Refill & Expiration

- `remaining`: decremented per use, key disabled at 0 (null = unlimited)
- `refillInterval` + `refillAmount`: auto-reset remaining to refillAmount after interval
- `expiresIn`: key expires after duration

### Permissions

```ts
apiKey({
  defaultPermissions: { project: ["read"] },
})
// Create with permissions: body: { permissions: { project: ["read", "write"] } }
// Verify with required permissions: body: { key, requiredPermissions: { project: ["write"] } }
// Update: body: { keyId, permissions: { project: ["read"] } }
```

### v1.5 Schema Changes

- `userId` → `referenceId`
- New `configId` field (defaults to `"default"`)
- Client: `apiKey.userId` → `apiKey.referenceId`, new `apiKey.references` (`"user"` or `"organization"`)

---

## Stripe Plugin (`@better-auth/stripe`)

### Setup

```ts
import { stripe } from "@better-auth/stripe";
import Stripe from "stripe";

const stripeClient = new Stripe(process.env.STRIPE_SECRET_KEY!);
export const auth = betterAuth({
  plugins: [
    stripe({
      stripeClient,
      stripeWebhookSecret: process.env.STRIPE_WEBHOOK_SECRET!,
      createCustomerOnSignUp: true,
    }),
  ],
});

// Client
import { stripeClient } from "@better-auth/stripe/client";
const authClient = createAuthClient({
  plugins: [stripeClient({ subscription: true })],
});
```

Webhook endpoint auto-registered at `/api/auth/stripe/webhook`.

### Subscription Plans

```ts
stripe({
  stripeClient,
  stripeWebhookSecret: "...",
  subscription: {
    enabled: true,
    plans: [
      {
        name: "pro",
        priceId: "price_xxx",
        annualDiscountPriceId: "price_yyy",
        limits: { projects: 20, storage: 50 },
        freeTrial: { days: 14 },
        prorationBehavior: "create_prorations",
        seatPriceId: "price_per_seat", // per-seat line item
      },
    ],
    // Dynamic plans: plans: async () => fetchPlansFromDB(),
  },
});
```

### Client API

```ts
// Create/upgrade subscription
await authClient.subscription.upgrade({
  plan: "pro",
  successUrl: "/dashboard",
  cancelUrl: "/pricing",
  annual: true,
  subscriptionId: "sub_x", // REQUIRED when upgrading existing
  seats: 5,
  scheduleAtPeriodEnd: true,
});

// List active subscriptions
const { data: subs } = await authClient.subscription.list();

// Cancel
await authClient.subscription.cancel({ returnUrl: "/account", subscriptionId: "sub_x" });

// Restore pending cancellation
await authClient.subscription.restore({ subscriptionId: "sub_x" });

// Billing portal
await authClient.subscription.billingPortal({ returnUrl: "/billing", disableRedirect: true });
```

### Organization Billing

```ts
stripe({
  stripeClient,
  stripeWebhookSecret: "...",
  subscription: { enabled: true, plans: [...] },
  organization: { enabled: true },
});

await authClient.subscription.upgrade({
  plan: "team",
  referenceId: activeOrg.id,
  customerType: "organization",
  seats: 10,
  successUrl: "/success",
  cancelUrl: "/pricing",
});
```

### Reference Authorization

```ts
subscription: {
  authorizeReference: async ({ user, referenceId, action }) => {
    // action: "upgrade-subscription" | "cancel-subscription" | "restore-subscription" | "list-subscription"
    const member = await db.members.findFirst({
      where: { userId: user.id, organizationId: referenceId },
    });
    return member?.role === "owner";
  },
}
```

### Webhook Lifecycle Hooks

```ts
subscription: {
  onSubscriptionComplete: async ({ subscription, plan }) => { /* checkout completed */ },
  onSubscriptionCreated: async ({ subscription, plan }) => { /* created outside checkout */ },
  onSubscriptionUpdate: async ({ subscription }) => { /* updated */ },
  onSubscriptionCancel: async ({ subscription, cancellationDetails }) => { /* canceled */ },
}
```

Custom webhook events via top-level `onEvent: async (event) => { ... }`.

### Trial Abuse Prevention

Automatic: once a user has had any trial, no new trials are offered. Tracks via `trialStart`/`trialEnd` fields. Cannot be overridden.

### Schema

Adds `subscription` table (plan, referenceId, stripeCustomerId, stripeSubscriptionId, status, periodStart/End, cancelAtPeriodEnd, seats, trialStart, trialEnd, billingInterval, stripeScheduleId) and `stripeCustomerId` field on `user` and `organization` tables.
