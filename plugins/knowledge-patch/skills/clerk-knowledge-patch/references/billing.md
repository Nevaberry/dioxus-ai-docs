# Billing

## Stripe boundary and service limits

Clerk uses Stripe as its payment processor, but Clerk Plans and Subscriptions are not Stripe Billing objects. Payment and customer records appear in Stripe. A Stripe account connected to Clerk must not already be linked to another platform, and development and production require separate Stripe accounts.

Current constraints:

- USD only.
- Clerk is not the merchant of record.
- No native refunds.
- No native tax or VAT calculation.
- No native 3D Secure confirmation.
- Unavailable in Brazil, India, Malaysia, Mexico, Singapore, and Thailand.
- A refund issued directly in Stripe does not update Clerk income or MRR calculations.

## Plans and default behavior

User and Organization Plans may be enabled together. Enabling Billing assigns every new user or Organization the free default Plan.

Cancellation, non-payment, and a downgrade from a paid Plan return the payer to the default. The default Plan cannot be replaced, but its name, slug, and public visibility can change.

The `Publicly available` setting controls whether Plans and Features appear in `<PricingTable />`, `<UserProfile />`, and `<OrganizationProfile />`.

## Features and Custom Permissions

If Billing is enabled in an instance that already has Custom Permissions, Clerk adds their corresponding Features to the free Organization Plan to preserve access.

A Permission such as `org:teams:manage` appears in session tokens and API responses and passes `has()` only while the active Plan contains the `teams` Feature. If the Feature is absent, the check returns `false` even when the member was assigned that Permission.

Always authorize access with `has()` or `<Show>`; do not infer entitlement from a displayed Subscription alone.

## Price-transition timing

- Free to paid: activates and charges immediately only when no other Subscription is active.
- Free to paid while a canceled Subscription remains active: the new paid Plan is upcoming until the old Subscription ends.
- Paid to paid: begins after the current paid period.
- Paid to free: schedules the default Plan at the current period boundary.

## Free-trial lifecycle

A customer is eligible only if they have never paid for a Subscription and have never used a trial.

- A payment method is required by default.
- If that requirement is disabled, a customer without a payment method is not charged automatically at expiry.
- Canceling preserves access until the original trial end.
- An uncanceled trial charges the default payment method at expiry.
- Clerk sends `subscriptionItem.freeTrialEnding` and customer email three days before expiry, or immediately for a trial shorter than three days.
- Only active trials can be managed.
- Extensions must be from 1 through 365 days.

## Experimental React checkout

Next.js and React export custom checkout primitives from `/experimental`. `useCheckout()` accepts `{ for, planId, planPeriod }` directly or receives shared state from `<CheckoutProvider />`. Its data fields remain `null` until `start()`.

Wrap consumers in `<ClerkLoaded>` and `<Show when="signed-in">`.

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
    <button onClick={async () => {
      const { error } = await checkout.confirm({ paymentMethodId })
      if (!error) {
        await checkout.finalize({
          navigate: ({ decorateUrl }) =>
            window.location.assign(decorateUrl('/')),
        })
      }
    }}>
      Complete purchase
    </button>
  )
}
```

Existing cards pass `paymentMethodId` to `confirm()`. New cards render `<PaymentElement />` inside `<PaymentElementProvider checkout={checkout}>`. After confirmation, `finalize()` synchronizes frontend and backend identity state and revalidates server-component authorization.

## Experimental Billing data hooks

The Next.js and React `/experimental` entry points expose:

- `usePlans()`
- `useSubscription()`
- `usePaymentMethods()`
- `usePaymentAttempts()`
- `useStatements()`

They support pagination options and state such as `infinite`, `pageSize`, `hasNextPage`, and `fetchNext`. `useSubscription()` is for display and refresh, not authorization.

## Authenticated Billing drawers

`<CheckoutButton />` and `<SubscriptionDetailsButton />` come from React, Next.js, and Vue experimental entry points. They throw unless nested inside `<Show when="signed-in">`.

Both default to the current user. With `for="organization"`, they also throw unless an Organization is active.

```tsx
import {
  CheckoutButton,
  SubscriptionDetailsButton,
} from '@clerk/nextjs/experimental'

<Show when="signed-in">
  <CheckoutButton planId="cplan_123" planPeriod="month" />
  <SubscriptionDetailsButton />
</Show>
```

## Frontend Billing API

The frontend `clerk.billing` resource defaults payer-specific reads to the current user when `orgId` is absent. It can read Plans, Subscriptions, statements, and payment attempts, and it can start checkout.

`getPlans()` returns only publicly visible Plans and chooses the payer with `for: 'user' | 'organization'`.

## Backend plan selector

The JavaScript Backend SDK uses `clerkClient.billing.getPlanList({ payerType: 'user' | 'org' })` to select a payer and list Plans:

```ts
await clerkClient.billing.getPlanList({
  payerType: 'user', // or 'org'
})
```

The maximum `limit` is 500.

## Administrative details

Python `clerk.billing` can list Plans and prices, create customer-specific prices, manage Subscription items and free trials, create price transitions, and read statements and payment attempts.

- Custom prices use cents, have a 100-cent minimum, and default to USD.
- Cancellation defaults to the end of the period unless `end_now=True`.
- Repeating a trial extension with the same future timestamp is idempotent.
- `create_price()` accepts `supported_billing_periods`; created and listed prices return it.
- Statement group-item and payment-attempt totals include `discounts`.
- User and Organization resources can read Subscriptions and credit balances and adjust credit balances.
