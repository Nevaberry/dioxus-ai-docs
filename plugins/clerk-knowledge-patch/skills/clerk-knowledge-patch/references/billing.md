# Billing

## Custom Checkout Flow (useCheckout + PaymentElement)

Clerk Billing provides a full custom checkout flow via experimental hooks. Lifecycle: `start()` → `confirm(data)` → `finalize({ navigate })`.

```tsx
'use client'
import { Show, ClerkLoaded } from '@clerk/nextjs'
import {
  CheckoutProvider,
  useCheckout,
  PaymentElementProvider,
  PaymentElement,
  usePaymentElement,
} from '@clerk/nextjs/experimental'
// For @clerk/react: import from '@clerk/react/experimental'

// Wrap in CheckoutProvider for shared state, or pass options directly to useCheckout()
export default function CheckoutPage() {
  return (
    <CheckoutProvider for="user" planId="cplan_xxx" planPeriod="month">
      <ClerkLoaded>
        <Show when="signed-in">
          <CustomCheckout />
        </Show>
      </ClerkLoaded>
    </CheckoutProvider>
  )
}

function CustomCheckout() {
  const { checkout } = useCheckout()

  if (checkout.status === 'needs_initialization') {
    return <button onClick={() => checkout.start()}>Start Checkout</button>
  }

  return (
    <PaymentElementProvider checkout={checkout}>
      <PaymentForm />
    </PaymentElementProvider>
  )
}

function PaymentForm() {
  const { checkout, errors, fetchStatus } = useCheckout()
  const { isFormReady, submit } = usePaymentElement()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // 1. Submit payment form to get payment method
    const { data, error } = await submit()
    if (error) return
    // 2. Confirm checkout with payment method
    const { error: confirmError } = await checkout.confirm(data)
    if (confirmError) return
    // 3. Complete checkout — revalidates server-side auth checks
    await checkout.finalize({
      navigate: ({ decorateUrl }) => {
        const url = decorateUrl('/')
        url.startsWith('http') ? (window.location.href = url) : router.push(url)
      },
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement fallback={<div>Loading...</div>} />
      {errors.global?.map((err, i) => <p key={i}>{err.longMessage || err.message}</p>)}
      <button type="submit" disabled={!isFormReady || fetchStatus === 'fetching'}>
        Pay {checkout.totals?.totalDueNow.currencySymbol} {checkout.totals?.totalDueNow.amountFormatted}
      </button>
    </form>
  )
}
```

Standalone usage (no provider): `const { checkout } = useCheckout({ planId, planPeriod, for: 'user' })`.

For existing payment methods, use `usePaymentMethods()` and pass `{ paymentMethodId }` to `checkout.confirm()` instead of using `PaymentElement`.

## Billing Hooks (All Experimental)

All imported from `@clerk/nextjs/experimental` or `@clerk/react/experimental`. Shared paginated interface: `{ data, isLoading, error, hasNextPage, fetchNext, revalidate, isFetching }`.

```tsx
import {
  usePlans,
  useSubscription,
  usePaymentMethods,
  usePaymentAttempts,
  useStatements,
} from '@clerk/nextjs/experimental'

// usePlans — list available subscription plans
const { data: plans } = usePlans({ for: 'user', infinite: true, pageSize: 10 })
// plan.id, plan.name, plan.description, plan.hasBaseFee, plan.currency
// plan.amountFormatted, plan.annualAmountFormatted, plan.annualMonthlyAmountFormatted
// plan.features[] — array of { id, name }

// useSubscription — current subscription (for display only, NOT for authorization)
const { data: subscription, revalidate } = useSubscription({ for: 'organization', keepPreviousData: true })
// subscription.status, subscription.activeAt, subscription.pastDueAt
// subscription.nextPayment.amount.amountFormatted, subscription.nextPayment.date
// subscription.subscriptionItems[]

// usePaymentMethods — saved payment methods
const { data: methods } = usePaymentMethods({ for: 'user', pageSize: 20 })
// method.id, method.cardType, method.last4, method.isDefault, method.status ('expired'|'disconnected')

// usePaymentAttempts — payment history
const { data: attempts } = usePaymentAttempts({ for: 'user', infinite: true })
// attempt.amount.amountFormatted, attempt.status ('paid'|'failed'|'pending')
// attempt.paidAt, attempt.failedAt, attempt.paymentSource.cardType, attempt.paymentSource.last4

// useStatements — billing statements
const { data: statements } = useStatements({ for: 'user' })
// statement.id, statement.totals.grandTotal.amountFormatted, statement.status
```

## Backend SDK Billing Methods (`clerkClient.billing`)

```ts
const client = await clerkClient()

// List plans (filter by payer type)
const { data, totalCount } = await client.billing.getPlanList({ payerType: 'org' })

// Get user/org subscription
const userSub = await client.billing.getUserBillingSubscription('user_123')
const orgSub = await client.billing.getOrganizationBillingSubscription('org_123')

// Cancel a subscription item (endNow: true = immediate, false = end of billing period)
await client.billing.cancelSubscriptionItem('subi_123', { endNow: true })

// Transition subscription item to a different price (custom plans)
// POST /v1/billing/subscription_items/{subi_123}/price_transition
// Body: { "from_price_id": "cprice_123", "to_price_id": "cprice_456" }
```

## Client-side Billing Object (`clerk.billing`)

Available via `useClerk()` — lower-level than hooks, useful for non-React or imperative scenarios:

```ts
const clerk = useClerk()

// Start checkout
const checkout = await clerk.billing.startCheckout({ planId: 'cplan_xxx', planPeriod: 'month', orgId?: 'org_123' })

// Get subscription, payment attempts, statements
const subscription = await clerk.billing.getSubscription({ orgId?: 'org_123' })
const attempts = await clerk.billing.getPaymentAttempts({ pageSize: 10, orgId?: 'org_123' })
const statement = await clerk.billing.getStatement({ id: 'statement_123' })
const statements = await clerk.billing.getStatements({ pageSize: 10 })
```

## B2B Billing: Permissions Depend on Plan Features

When using Clerk Billing with Organizations, Custom Permissions only work if the Feature part of the permission key is included in the org's active Plan. Critical gotcha:

```tsx
// Permission key format: org:<feature>:<permission>
// e.g., org:teams:manage — "teams" is the Feature

// If the org is NOT subscribed to a Plan that includes the "teams" Feature,
// has({ permission: 'org:teams:manage' }) will ALWAYS return false,
// even if the user has been assigned that permission.

// The fix: ensure the org's Plan includes the Feature before checking permissions.
```

## Free Trials

Plans can have free trials configured in the Dashboard. Key behaviors:

- Only users who have never had a paid subscription or trial can start one
- Payment method required by default (configurable in Dashboard)
- Canceling during trial keeps access until trial end date
- Webhook: `subscriptionItem.freeTrialEnding` fires 3 days before trial expires
- Trials can be extended (1–365 days) or canceled via Dashboard
