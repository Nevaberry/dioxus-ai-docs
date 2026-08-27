# Components

## Combined sign-in and sign-up

`<SignIn withSignUp>` keeps an unknown user inside the prebuilt sign-in flow and
prompts sign-up. `withSignUp` defaults to `true` only when
`CLERK_SIGN_IN_URL` is set; otherwise it is `false`. `transferable={false}`
separately prevents an unknown-email OAuth attempt from becoming an opaque
sign-up transfer.

```tsx
<SignIn withSignUp transferable={false} />
```

## Waitlist wiring

`<Waitlist />` requires Waitlist mode and `waitlistUrl` on `<ClerkProvider>` or
`<SignIn>`. Its `afterJoinWaitlistUrl` controls post-join navigation. The
Next.js component requires `@clerk/nextjs` 6.2.0 or newer.

```tsx
<ClerkProvider waitlistUrl="/waitlist">
  <Waitlist afterJoinWaitlistUrl="/thanks" />
</ClerkProvider>
```

## Google One Tap

`<GoogleOneTap />` requires custom credentials for the Google social connection
and does not render for an already signed-in Clerk user. It supplies neither a
Google access token nor refresh token; use another flow when the application
must call Google APIs. ITP and FedCM support default to enabled.

## Sign-out redirects

In `@clerk/react` 6.1.3 and `@clerk/vue` 2.0.7, `<SignOutButton />` deprecates
`signOutOptions`. Pass `redirectUrl` and `sessionId` directly:

```tsx
<SignOutButton redirectUrl="/signed-out" sessionId={sessionId} />
```

`afterSignOutUrl` and `afterMultiSessionSingleSignOutUrl` are deprecated on
`<UserButton />`; move both to `<ClerkProvider>`. Only
`afterSwitchSessionUrl` stays on the button.

```tsx
<ClerkProvider afterSignOutUrl="/signed-out" afterMultiSessionSingleSignOutUrl="/accounts">
  <UserButton afterSwitchSessionUrl="/dashboard" />
</ClerkProvider>
```

## Unified authorization display

`<Show>` accepts a Role, Permission, Feature, or Plan object in `when`, or a
callback receiving `has` for compound logic. `fallback` renders when the check
fails. This only hides client content; enforce sensitive authorization again on
the server.

```tsx
<Show
  when={(has) => has({ permission: 'org:invoices:create' }) || has({ plan: 'pro' })}
  fallback={<Upgrade />}
>
  <Invoices />
</Show>
```

## Astro loading controls

`<ClerkLoaded>` renders in both `ready` and `degraded` states. In Astro,
`<ClerkLoaded>` and `<ClerkLoading>` are React islands from
`@clerk/astro/react`, require React support, and are not imported from the
ordinary Astro component entry point.

```astro
---
import { ClerkLoaded, ClerkLoading } from '@clerk/astro/react'
---
<ClerkLoading client:load>Loading...</ClerkLoading>
<ClerkLoaded client:load>Ready or degraded</ClerkLoaded>
```

## Chrome extension redirects

Chrome extension `<RedirectToSignIn />` and `<RedirectToSignUp />` rely on
React Router and replace the current history entry rather than pushing one.

## Authenticated Billing drawers

Experimental React, Next.js, and Vue `<CheckoutButton />` and
`<SubscriptionDetailsButton />` throw unless nested in
`<Show when="signed-in">`. They default to the current user. With
`for="organization"`, they also require an Active Organization.

```tsx
import { CheckoutButton, SubscriptionDetailsButton } from '@clerk/nextjs/experimental'

<Show when="signed-in">
  <CheckoutButton planId="cplan_123" planPeriod="month" />
  <SubscriptionDetailsButton />
</Show>
```
