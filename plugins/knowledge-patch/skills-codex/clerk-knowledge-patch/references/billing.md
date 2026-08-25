# Billing

## Keep Clerk Billing separate from Stripe Billing

Stripe is Clerk Billing's payment processor, but Clerk Plans and Subscriptions
are not Stripe Billing objects. Payment and customer records do appear in
Stripe. An existing Stripe account must not already be connected to another
platform, and development and production need separate Stripe accounts.

Clerk Billing:

- processes USD only;
- is not a merchant of record;
- does not provide native refunds, tax/VAT calculation, or 3D Secure
  confirmation; and
- is unavailable in Brazil, India, Malaysia, Mexico, Singapore, and Thailand.

Refunding through Stripe does not adjust Clerk's income or MRR calculations.

## Understand default Plans

User Plans and Organization Plans can run together. Enabling Billing assigns
every new payer the free default Plan. Cancellation, non-payment, and a
downgrade from a paid Plan return the payer to that default.

The default Plan cannot be replaced, although its name, slug, and public
visibility can change. `Publicly available` controls whether Plans and Features
appear in `<PricingTable />`, `<UserProfile />`, or `<OrganizationProfile />`.

## Gate Custom Permissions with Features

When Billing is enabled for an instance that already has Custom Permissions,
Clerk adds their corresponding Features to the free Organization Plan to keep
existing access working. A permission such as `org:teams:manage` is emitted in
session tokens and API responses, and passes `has()`, only while the active Plan
contains its `teams` Feature. Otherwise `has()` returns `false`, even if the
member was granted the permission.

## Schedule price transitions correctly

- Free to paid starts and charges immediately only when there is no active
  Subscription. If a canceled Subscription is still running, the new paid Plan
  remains upcoming until it ends.
- Paid to paid begins after the current paid period.
- Paid to free schedules the default Plan at the current period boundary.

## Implement the free-trial lifecycle

Only a customer who has never paid for a Subscription and never used a trial is
eligible. A payment method is required by default. If that requirement is
disabled, a customer without a method is not charged automatically at expiry.

Cancellation retains access until the original trial end. An uncanceled trial
charges the default payment method at expiry. Clerk emits
`subscriptionItem.freeTrialEnding` and sends the customer email three days
before expiry, or immediately for a trial shorter than three days. Only active
trials can be managed; an extension must be between 1 and 365 days.

## Build custom checkout

Next.js and React expose experimental checkout primitives from `/experimental`.
`useCheckout()` accepts `{ for, planId, planPeriod }` or receives shared state
from `<CheckoutProvider />`. Its data remains null until `start()`. Wrap
consumers in `<ClerkLoaded>` and `<Show when="signed-in">`.

Existing cards supply `paymentMethodId` to `confirm()`. New-card flows render
`<PaymentElement />` inside `<PaymentElementProvider checkout={checkout}>`.
After confirmation, `finalize()` synchronizes client/server identity and
revalidates server-component authorization.

```tsx
function Checkout({ paymentMethodId }) {
  const { checkout } = useCheckout({
    for: 'user',
    planId: 'cplan_123',
    planPeriod: 'month', // or 'annual'
  })

  if (checkout.status === 'needs_initialization') {
    return <button onClick={() => checkout.start()}>Start checkout</button>
  }

  return (
    <button
      onClick={async () => {
        const { error } = await checkout.confirm({ paymentMethodId })
        if (!error) {
          await checkout.finalize({
            navigate: ({ decorateUrl }) =>
              window.location.assign(decorateUrl('/')),
          })
        }
      }}
    >
      Complete purchase
    </button>
  )
}
```

## Read Billing data without authorizing from it

Experimental `usePlans()`, `useSubscription()`, `usePaymentMethods()`,
`usePaymentAttempts()`, and `useStatements()` expose user or Organization data.
Their pagination supports options and state such as `infinite`, `pageSize`,
`hasNextPage`, and `fetchNext`. `useSubscription()` is for display and refresh;
authorization still belongs in `has()` or `<Show>` and on the server.

## Choose frontend or backend plan selectors

Frontend `clerk.billing` defaults payer-specific reads to the current user when
`orgId` is absent. It can read Plans, Subscriptions, statements, and payment
attempts or start checkout. `getPlans()` returns publicly visible Plans only and
selects a payer with `for: 'user' | 'organization'`.

The Backend SDK uses
`clerkClient.billing.getPlanList({ payerType: 'user' | 'org' })`; its maximum
list limit is 500.

## Configure discounts and promo codes

Discounts may be reusable percentage or fixed-amount reductions for one cycle,
a fixed number of cycles, or indefinitely. Fixed discounts can specify separate
monthly and annual amounts. A Dashboard-applied discount affects an active
Subscription and can be revoked for the next renewal.

Checkout promo codes can cap total redemptions, allow only new subscribers, and
report redemption counts.
