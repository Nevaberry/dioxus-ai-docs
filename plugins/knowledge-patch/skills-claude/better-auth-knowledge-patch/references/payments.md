# Payments and Entitlements

## Autumn

`autumn-js/better-auth` can bill a user, organization, both, or a custom identity from `identify`. It auto-creates customers and assigns default plans. Autumn is queried directly rather than synchronized by application webhooks: React uses `AutumnProvider`/`useCustomer`, while server code checks and records usage through auth APIs.

```ts
plugins: [
  organization(),
  autumn({ customerScope: "user_and_organization" }),
]

const { allowed } = await auth.api.check({
  headers,
  body: { featureId: "messages" },
});
if (allowed) {
  await auth.api.track({
    headers,
    body: { featureId: "messages", value: 1 },
  });
}
```

## Stripe ownership and upgrades

Stripe permits one active/trialing subscription per reference. To change it, pass the existing Stripe subscription ID to `subscription.upgrade`; omitting it may create a second billed subscription. Custom references require `authorizeReference`. A manually defined `subscription.referenceId` must remain non-unique so canceled customers can resubscribe. Organization billing needs `customerType: "organization"` because user billing is default.

```ts
await authClient.subscription.upgrade({
  plan: "team",
  referenceId: organization.id,
  customerType: "organization",
  subscriptionId: current.stripeSubscriptionId,
  successUrl: "/billing/success",
  cancelUrl: "/billing",
});
```

## Stripe cancellation and trials

Cancellation opens the Billing Portal; a scheduled cancellation remains active until the end. `subscription.restore` clears a still-active pending cancellation or releases a pending plan-change schedule, but cannot revive status `canceled` with `endedAt`.

Trial eligibility checks every subscription belonging to the user (since 1.5.0), not merely the current subscription.

## Stripe organization and usage billing

Stripe can synchronize organization member counts to a seat price (since 1.5-guide). Plans accept usage-oriented `lineItems`, `scheduleAtPeriodEnd`, and tracked `billingInterval`.

```ts
stripe({
  stripeClient,
  stripeWebhookSecret,
  subscription: {
    enabled: true,
    plans: [{
      name: "team",
      priceId: "price_base",
      seatPriceId: "price_seat",
    }],
  },
  organization: { enabled: true },
})
```

## Polar

`@polar-sh/better-auth` composes checkout, portal, usage, and webhook modules under `polar({ use: [...] })`. Automatically created customers use the Better Auth user ID as Polar `externalId`.

```ts
polar({
  client: polarSDK,
  createCustomerOnSignUp: true,
  use: [
    checkout({
      products: [{ productId: "product_id", slug: "pro" }],
      successUrl: "/success?checkout_id={CHECKOUT_ID}",
      authenticatedUsersOnly: true,
    }),
    portal(),
    usage(),
    webhooks({ secret: process.env.POLAR_WEBHOOK_SECRET! }),
  ],
})
```

A user's normal customer/subscription state excludes purchases made by a parent organization. Organization checkout must set `referenceId`, and entitlement lookup must list subscriptions with the same reference.

```ts
const { data: subscriptions } =
  await authClient.customer.subscriptions.list({
    query: { active: true, referenceId: organization.id },
  });
```

## Creem

`persistSubscriptions: true` is the default and requires migration. It stores webhook-synchronized subscriptions, prevents cross-plan trial abuse automatically, and enables client access checks. API mode has no client `hasAccessGranted` and limited server checks.

Database mode enables `onGrantAccess` and `onRevokeAccess`. `hasAccessGranted` keeps access through the paid period even after early cancellation.

```ts
creem({
  apiKey: process.env.CREEM_API_KEY!,
  webhookSecret: process.env.CREEM_WEBHOOK_SECRET!,
  persistSubscriptions: true,
  onGrantAccess: async ({ metadata }) => grant(metadata?.referenceId),
  onRevokeAccess: async ({ metadata }) => revoke(metadata?.referenceId),
})
```

## Dodo Payments

`authClient.dodopayments.checkout()` is deprecated. Configure a product slug and call `checkoutSession()`. Checkout allows unauthenticated users unless `authenticatedUsersOnly` is true. Webhooks mount at `/api/auth/dodopayments/webhooks` by default.

```ts
const { data } = await authClient.dodopayments.checkoutSession({
  slug: "premium-plan",
});
```

## Openfort

The server requires Better Auth `bearer()` before `openfort()`. Its `encryptionSession` module mounts `/api/auth/encryption-session` using three Shield credentials. On the client, install the bearer client, return the session token from `OpenfortProvider.thirdPartyAuth`, and exchange it from `getEncryptionSession`.

```ts
plugins: [
  bearer(),
  openfort({
    client: openfortSDK,
    use: [encryptionSession({
      config: {
        apiKey: process.env.SHIELD_PUBLISHABLE_KEY!,
        secretKey: process.env.SHIELD_SECRET_KEY!,
        encryptionPart: process.env.SHIELD_ENCRYPTION_SHARE!,
      },
    })],
  }),
]
```

`@openfort/react` supports EVM, Solana, or both. EVM peers are `viem` and `wagmi`; Solana uses `@solana/kit`. No Wagmi/React Query bridge is needed unless Wagmi hooks are used. The provider connects at login by default; `connectOnLogin: false` defers wallet creation to embedded-wallet hooks with automatic, passkey, or password recovery.

```tsx
const { create } = useEthereumEmbeddedWallet();
await create({ recoveryMethod: RecoveryMethod.PASSKEY });
```
