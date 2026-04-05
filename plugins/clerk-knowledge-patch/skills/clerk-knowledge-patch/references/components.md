# Components

## `<Show>` Component

Core 3 introduced `<Show>` as the unified control component, replacing `<SignedIn>` and `<SignedOut>`.

```tsx
import { Show, SignInButton, UserButton } from '@clerk/react'

<Show when="signed-in">
  <UserButton />
</Show>
<Show when="signed-out">
  <SignInButton />
</Show>
```

### Authorization Checks

```tsx
import { Show } from '@clerk/nextjs'

// Permission-based (recommended over role-based)
<Show when={{ permission: 'org:invoices:create' }} fallback={<p>No access</p>}>
  <InvoiceForm />
</Show>

// Role-based
<Show when={{ role: 'org:billing' }} fallback={<p>No access</p>}>
  <BillingDashboard />
</Show>

// Plan-based (billing)
<Show when={{ plan: 'bronze' }} fallback={<p>Upgrade required</p>}>
  <PremiumContent />
</Show>

// Feature-based (recommended over plan-based)
<Show when={{ feature: 'premium_access' }} fallback={<p>Feature unavailable</p>}>
  <PremiumFeature />
</Show>

// Callback for complex logic — receives `has()` function
<Show
  when={(has) => has({ role: 'org:admin' }) || has({ role: 'org:billing_manager' })}
  fallback={<p>Admins or Billing Managers only</p>}
>
  <SettingsPage />
</Show>
```

Full `when` type: `'signed-in' | 'signed-out' | { feature: string } | { permission: string } | { plan: string } | { role: string } | (has) => boolean`

Also supports `treatPendingAsSignedOut` prop (default `true`) — controls whether pending sessions are treated as signed out.

## `<UserAvatar />` Component

Standalone component that renders the authenticated user's avatar. Simpler than `<UserButton>` when you just need the image.

```tsx
import { Show, UserAvatar, SignInButton } from '@clerk/nextjs'

<Show when="signed-in">
  <UserAvatar />  {/* Just the avatar image, no dropdown menu */}
</Show>
```

Props: `rounded?: boolean`, `appearance?`, `fallback?: ReactNode`.

## `<Waitlist />` Component

For Waitlist mode — lets users sign up for early access before app launch. Requires enabling Waitlist mode in the Clerk Dashboard first.

```tsx
import { Waitlist } from '@clerk/nextjs' // available in @clerk/nextjs@6.2.0+

// Must set waitlistUrl on <ClerkProvider> or <SignIn> for proper functionality
<Waitlist />
```

Props: `afterJoinWaitlistUrl?: string`, `signInUrl?: string`, `appearance?`, `fallback?`.

## Billing Components (Experimental)

Four components for Clerk's built-in billing. `CheckoutButton`, `PlanDetailsButton`, and `SubscriptionDetailsButton` are from the `/experimental` subpath. `PricingTable` is in the main package.

```tsx
import { Show, PricingTable } from '@clerk/nextjs'
import { CheckoutButton, PlanDetailsButton, SubscriptionDetailsButton } from '@clerk/nextjs/experimental'
// For @clerk/react: import from '@clerk/react' and '@clerk/react/experimental'

// PricingTable — displays all plans and features, works signed-in or signed-out
<PricingTable />
<PricingTable for="organization" /> {/* org-level plans */}

// CheckoutButton — MUST be inside <Show when="signed-in">
<Show when="signed-in">
  <CheckoutButton
    planId="cplan_xxx"
    planPeriod="month"        // 'month' | 'annual'
    for="user"                // 'user' | 'organization'
    onSubscriptionComplete={() => console.log('Done!')}
    newSubscriptionRedirectUrl="/dashboard"
  />
</Show>

// PlanDetailsButton — opens plan details drawer
<PlanDetailsButton planId="cplan_xxx" initialPlanPeriod="month" />

// SubscriptionDetailsButton — MUST be inside <Show when="signed-in">
<Show when="signed-in">
  <SubscriptionDetailsButton
    for="user"                // 'user' | 'organization'
    onSubscriptionCancel={() => console.log('Canceled')}
  />
</Show>
```

All billing buttons accept custom children and preserve click handlers on nested elements.

## UserButton Custom Menu Items

`<UserButton>` supports custom actions, links, and reordering via `<UserButton.MenuItems>`:

```tsx
<UserButton>
  <UserButton.MenuItems>
    {/* Reorder defaults by referencing them by label */}
    <UserButton.Action label="signOut" />

    {/* Custom action */}
    <UserButton.Action label="Open chat" labelIcon={<ChatIcon />} onClick={() => openChat()} />

    {/* Custom link */}
    <UserButton.Link label="Billing" labelIcon={<BillingIcon />} href="/billing" />

    {/* Custom page (opens in UserProfile modal) */}
    <UserButton.Action label="Settings" labelIcon={<GearIcon />} open="custom-settings" />

    <UserButton.Action label="manageAccount" />
  </UserButton.MenuItems>
</UserButton>
```

Default labels for reordering: `"manageAccount"` and `"signOut"`. Use `has({ permission: '...' })` from `useAuth()` to conditionally render menu items.

## `<SignOutButton />` Prop Deprecation

The `signOutOptions` prop is deprecated. Use top-level props instead:

```tsx
// Before (deprecated — emits warning)
<SignOutButton signOutOptions={{ redirectUrl: '/', sessionId: 'sess_123' }}>
  Sign out
</SignOutButton>

// After
<SignOutButton redirectUrl="/" sessionId="sess_123">
  Sign out
</SignOutButton>
```

## `UNSAFE_PortalProvider`

When using Clerk components inside portaled UI libraries (Radix Dialog, React Aria), Clerk's own portals render on `document.body` and become non-interactive. `UNSAFE_PortalProvider` redirects Clerk portals into the dialog container.

```tsx
'use client'
import { useRef } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { UNSAFE_PortalProvider, UserButton } from '@clerk/nextjs'

export function UserDialog() {
  const containerRef = useRef<HTMLDivElement>(null)

  return (
    <Dialog.Root>
      <Dialog.Trigger>Open Dialog</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay />
        <Dialog.Content ref={containerRef}>
          <UNSAFE_PortalProvider getContainer={() => containerRef.current}>
            <UserButton />
          </UNSAFE_PortalProvider>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
```

## `prefetchUI={false}` Replaces Headless Variant

The `clerkJSVariant: 'headless'` option and headless bundle are removed. Use `prefetchUI={false}` on `ClerkProvider` to avoid loading UI components when only using hooks/auth:

```tsx
<ClerkProvider prefetchUI={false}>
  <App /> {/* Only hooks like useAuth(), no prebuilt UI components */}
</ClerkProvider>
```
