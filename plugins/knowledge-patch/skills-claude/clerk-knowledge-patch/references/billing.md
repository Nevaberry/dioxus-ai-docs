# Billing

## Service and Stripe boundaries

Clerk uses Stripe only as a payment processor. Clerk Plans and Subscriptions are
not Stripe Billing objects, though payment and customer records appear in
Stripe. A Stripe account cannot already be linked to another platform, and
development and production need separate accounts.

Billing is USD-only, is not a merchant of record, and has no native refund,
tax/VAT, or 3D Secure confirmation support. It is unavailable in Brazil, India,
Malaysia, Mexico, Singapore, and Thailand. A refund issued in Stripe does not
change Clerk's income or MRR calculations.

## Payers, the default Plan, and visibility

User and Organization Plans can coexist. Enabling Billing assigns every new
user or Organization the free default Plan. Cancellation, non-payment, or a
paid-Plan downgrade returns the payer to it. The default cannot be replaced,
but its name, slug, and visibility can change. `Publicly available` determines
whether a Plan or Feature appears in `<PricingTable />`, `<UserProfile />`, or
`<OrganizationProfile />`.

## Features gate Custom Permissions

When Billing is enabled on an instance with existing Custom Permissions, Clerk
adds matching Features to the free Organization Plan to preserve access. A
Permission such as `org:teams:manage` appears in tokens and API responses and
passes `has()` only while the active Plan contains the `teams` Feature; otherwise
it fails even if assigned to the member.

## Price-transition timing

- Free to paid activates and charges immediately only with no active
  Subscription. If a canceled Subscription is still running, the new Plan is
  upcoming until it ends.
- Paid to paid starts after the current paid period.
- Paid to free schedules the default Plan at the current period boundary.

## Free trials

Only customers who have never paid and never used a trial qualify. A payment
method is required by default; if that requirement is disabled, a customer
without one is not charged automatically at expiry. Cancellation preserves
access until the original trial end. An uncanceled trial charges the default
payment method at expiry.

Clerk sends `subscriptionItem.freeTrialEnding` and customer email three days
before expiry, immediately for a shorter trial. Only active trials can be
managed, and extensions must be 1–365 days.

## Custom React checkout

Next.js and React export checkout primitives from their `/experimental` entry
points. `useCheckout()` accepts `{ for, planId, planPeriod }`, where the period
is `month` or `annual`, or uses `<CheckoutProvider />`. Data stays null until
`start()`. Wrap consumers in `<ClerkLoaded>` and
`<Show when="signed-in">`.

Existing cards pass `paymentMethodId` to `confirm()`. New cards render
`<PaymentElement />` inside `<PaymentElementProvider checkout={checkout}>`.
After confirmation, `finalize()` synchronizes client/server identity and
revalidates server-component authorization.

```tsx
const { checkout } = useCheckout({
  for: 'user', planId: 'cplan_123', planPeriod: 'month',
})
await checkout.start()
const { error } = await checkout.confirm({ paymentMethodId })
if (!error) await checkout.finalize({
  navigate: ({ decorateUrl }) => window.location.assign(decorateUrl('/')),
})
```

## Billing data hooks and authorization

From the React and Next.js `/experimental` entry points, `usePlans()`,
`useSubscription()`, `usePaymentMethods()`, `usePaymentAttempts()`, and
`useStatements()` read user or Organization data. They support pagination
options such as `infinite`, `pageSize`, `hasNextPage`, and `fetchNext`.
`useSubscription()` is for display and refresh, not authorization; use `has()`
or `<Show>` for entitlements.

## Frontend and backend selectors

The frontend `clerk.billing` defaults payer-specific reads to the current user
when `orgId` is absent and can read Plans, Subscriptions, statements, and
payment attempts or start checkout. `getPlans()` returns public Plans and uses
`for: 'user' | 'organization'` to choose a payer.

The Backend SDK uses
`clerkClient.billing.getPlanList({ payerType: 'user' | 'org' })`; its maximum
list limit is 500.

## Discounts and promotion codes

Discounts from batch `2026-07-31-2026-08-17` may be reusable percentages or
fixed amounts, last one cycle, a fixed number of cycles, or indefinitely, and
carry separate monthly and annual amounts. A Dashboard-applied discount affects
an active Subscription and can be revoked for the next renewal. Checkout promo
codes can cap total redemptions, restrict use to new subscribers, and expose
redemption counts.
