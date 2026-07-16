# Payments and Entitlements

## Stripe billing models

Stripe can synchronize organization member count to a per-seat price. Plans also support usage-oriented `lineItems`, deferred changes through `scheduleAtPeriodEnd`, and tracked `billingInterval` values.

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

Before granting a free trial, Stripe checks every subscription belonging to the user.

## Stripe references and upgrades

Stripe permits only one active or trialing subscription per reference. To change an existing subscription, pass its Stripe subscription ID to `subscription.upgrade`; otherwise a second billed subscription can be created.

Custom references require `authorizeReference`. A manually defined `subscription.referenceId` must remain non-unique so canceled customers can subscribe again. Organization billing must pass `customerType: "organization"`; user billing is the default.

```ts
stripe({
  stripeClient,
  stripeWebhookSecret,
  subscription: {
    enabled: true,
    plans: [{ name: "team", priceId: "price_team" }],
    authorizeReference: ({ user, referenceId, action }) =>
      canManageBilling(user.id, referenceId, action),
  },
  organization: { enabled: true },
})

await authClient.subscription.upgrade({
  plan: "team",
  referenceId: organization.id,
  customerType: "organization",
  subscriptionId: current.stripeSubscriptionId,
  successUrl: "/billing/success",
  cancelUrl: "/billing",
});
```

## Stripe cancellation recovery

Cancellation opens Stripe Billing Portal. A subscription scheduled to cancel remains active until it actually ends.

`subscription.restore` clears a still-active pending cancellation or releases a pending plan-change schedule. It cannot revive a subscription whose status is already `canceled` and whose `endedAt` is set.

```ts
await authClient.subscription.restore({
  subscriptionId: current.stripeSubscriptionId,
  referenceId: organization.id,
  customerType: "organization",
});
```

## Autumn

`autumn-js/better-auth` can make the billable customer a user, an organization, both, or a custom identity returned by `identify`. It creates customers automatically and assigns configured default plans.

Autumn is queried directly instead of synchronized through application webhooks. React uses `AutumnProvider` and `useCustomer`; server code checks entitlement and records usage through the auth API.

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

## Polar

`@polar-sh/better-auth` composes checkout, portal, usage, and webhook modules under `polar({ use: [...] })`. Automatically created customers use the Better Auth user ID as Polar `externalId`; no local mapping is necessary.

A user's customer state and ordinary subscription list exclude subscriptions bought by a parent organization. Organization checkout should set `referenceId`, and access checks should list subscriptions with that same reference.

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

const { data: subscriptions } =
  await authClient.customer.subscriptions.list({
    query: { active: true, referenceId: organization.id },
  });
```

## Creem

`persistSubscriptions: true` is the default and requires a migration. Database mode stores webhook-synchronized subscriptions, enables automatic cross-plan trial-abuse prevention, and supports client access checks. API mode has no client `hasAccessGranted`, and server access checks remain limited.

Database mode enables high-level `onGrantAccess` and `onRevokeAccess` hooks. `hasAccessGranted` keeps access through the paid period even after early cancellation.

```ts
creem({
  apiKey: process.env.CREEM_API_KEY!,
  webhookSecret: process.env.CREEM_WEBHOOK_SECRET!,
  persistSubscriptions: true,
  onGrantAccess: async ({ metadata }) => grant(metadata?.referenceId),
  onRevokeAccess: async ({ metadata }) => revoke(metadata?.referenceId),
})

const { data } = await authClient.creem.hasAccessGranted();
```

## Dodo Payments

`authClient.dodopayments.checkout()` is deprecated. Configure a product slug and call `checkoutSession()`.

Checkout allows unauthenticated users by default unless `authenticatedUsersOnly` is set. The webhook module defaults to `/api/auth/dodopayments/webhooks`.

```ts
checkout({
  products: [{ productId: "pdt_id", slug: "premium-plan" }],
  successUrl: "/dashboard/success",
  authenticatedUsersOnly: true,
})

const { data } = await authClient.dodopayments.checkoutSession({
  slug: "premium-plan",
});
```

## Openfort bearer and encryption sessions

The Openfort server integration requires Better Auth `bearer()` before `openfort()`. Its `encryptionSession` module mounts `/api/auth/encryption-session` and uses three Shield credentials.

On the client, configure the Better Auth bearer client, return its session token from `OpenfortProvider.thirdPartyAuth`, and exchange that token at the mounted endpoint from `getEncryptionSession`.

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

## Openfort chains and recovery

`@openfort/react` supports EVM, Solana, or both. EVM peers are `viem` and `wagmi`; the Solana peer is `@solana/kit`. The provider does not require a Wagmi/React Query bridge unless Wagmi hooks are used.

`OpenfortProvider` connects on login by default. Set `connectOnLogin: false` to leave wallet creation to embedded-wallet hooks, with automatic, passkey, or password recovery.

```tsx
const { create } = useEthereumEmbeddedWallet();

await create({ recoveryMethod: RecoveryMethod.PASSKEY });
```
