# Payments and Entitlements

Payment plugins use different identity, persistence, cancellation, and entitlement rules. Do not transfer assumptions between them.

## Autumn

`autumn-js/better-auth` can bill a user, organization, both, or a custom identity returned by `identify`. It automatically creates customers and assigns configured default plans. Autumn state is queried directly rather than synchronized through application webhooks. React uses `AutumnProvider` and `useCustomer`; server code calls auth APIs to check and record usage.

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

## Stripe

### Organization and usage billing

The Stripe plugin can synchronize organization member count to a per-seat price. Plans support usage `lineItems`, deferred changes through `scheduleAtPeriodEnd`, and tracked `billingInterval` values.

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

### References and upgrades

Stripe permits one active or trialing subscription per reference. To change one, pass its Stripe subscription ID to `subscription.upgrade`; omitting it may create a second billed subscription. Custom references require `authorizeReference`. A manually defined `subscription.referenceId` must remain non-unique so canceled customers can subscribe again. Organization billing must send `customerType: "organization"` because user billing is the default.

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

### Cancellation and restore

Cancellation opens Stripe Billing Portal, and a scheduled cancellation remains active until the period ends. `subscription.restore` can clear a still-active cancellation or release a pending plan-change schedule. It cannot revive a subscription whose status is already `canceled` and whose `endedAt` is set.

```ts
await authClient.subscription.restore({
  subscriptionId: current.stripeSubscriptionId,
  referenceId: organization.id,
  customerType: "organization",
});
```

Before granting a free trial, the plugin checks every subscription owned by the user.

## Polar

`@polar-sh/better-auth` composes checkout, portal, usage, and webhook modules under `polar({ use: [...] })`. Automatically created customers use the Better Auth user ID as Polar `externalId`, so no local mapping is required.

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

A user's customer state and ordinary subscription list exclude subscriptions bought by a parent organization. Organization checkout must set `referenceId`, and entitlement lookup must list subscriptions with that same reference.

```ts
const { data: subscriptions } =
  await authClient.customer.subscriptions.list({
    query: { active: true, referenceId: organization.id },
  });
```

## Creem

`persistSubscriptions: true` is the default and requires a migration. Database mode stores webhook-synchronized subscriptions, automatically prevents cross-plan trial abuse, enables the client access check, and supports `onGrantAccess`/`onRevokeAccess`. API mode has no client `hasAccessGranted`, and server access checks are more limited. A canceled subscription retains access through its paid period.

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

`authClient.dodopayments.checkout()` is deprecated. Configure a product slug and call `checkoutSession()`. Checkout allows anonymous users by default unless `authenticatedUsersOnly` is enabled. The webhook module defaults to `/api/auth/dodopayments/webhooks`.

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

## Openfort

### Bearer and encryption sessions

Place Better Auth's `bearer` plugin before `openfort`. The `encryptionSession` module mounts `/api/auth/encryption-session` using the three Shield credentials. On the client, add the bearer client, return its session token from `OpenfortProvider.thirdPartyAuth`, and exchange that token from `getEncryptionSession` at the mounted endpoint.

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

### Chains and recovery

`@openfort/react` supports EVM, Solana, or both. EVM peers are `viem` and `wagmi`; Solana uses `@solana/kit`. The provider does not need a Wagmi/React Query bridge unless Wagmi hooks are used. It connects on login by default; `connectOnLogin: false` leaves wallet creation to embedded-wallet hooks with automatic, passkey, or password recovery.

```tsx
const { create } = useEthereumEmbeddedWallet();
await create({ recoveryMethod: RecoveryMethod.PASSKEY });
```
