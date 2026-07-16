# Components

## Prebuilt sign-in-or-up

`<SignIn withSignUp>` prompts an unknown user to sign up without leaving the prebuilt sign-in flow.

- `withSignUp` defaults to `true` only when `CLERK_SIGN_IN_URL` is set.
- It otherwise defaults to `false`.
- `transferable={false}` separately prevents an OAuth attempt for an unknown email from becoming an opaque sign-up transfer.

```tsx
<SignIn withSignUp transferable={false} />
```

## Sign-out prop migrations

In `@clerk/react` 6.1.3 and `@clerk/vue` 2.0.7, `<SignOutButton />` deprecates `signOutOptions`. Pass `redirectUrl` and `sessionId` directly. The nested prop still works temporarily but emits a deprecation warning.

```tsx
<SignOutButton redirectUrl="/signed-out" sessionId={sessionId} />
```

`afterSignOutUrl` and `afterMultiSessionSingleSignOutUrl` are deprecated on `<UserButton />`; move them to `<ClerkProvider>`. `afterSwitchSessionUrl` remains on `<UserButton />`.

```tsx
<ClerkProvider
  afterSignOutUrl="/signed-out"
  afterMultiSessionSingleSignOutUrl="/accounts"
>
  <UserButton afterSwitchSessionUrl="/dashboard" />
</ClerkProvider>
```

## Waitlist routing

Embedded `<Waitlist />` requires Waitlist mode plus a `waitlistUrl` on `<ClerkProvider>` or `<SignIn>`. Set `afterJoinWaitlistUrl` on the component for post-join navigation. The Next.js component requires `@clerk/nextjs` 6.2.0 or newer.

```tsx
<ClerkProvider waitlistUrl="/waitlist">
  <Waitlist afterJoinWaitlistUrl="/thanks" />
</ClerkProvider>
```

## Google One Tap

`<GoogleOneTap />` requires the Google social connection to use custom credentials. It does not render for an already signed-in Clerk user.

The component does not return a Google access or refresh token. Use a different OAuth flow if the application must call Google APIs on the user's behalf. ITP support and FedCM support both default to enabled.

## Unified authorization rendering

`<Show>` accepts a Role, Permission, Feature, or Plan object in `when`, or a callback receiving `has` for compound conditions. `fallback` renders when the check fails.

```tsx
<Show
  when={(has) =>
    has({ permission: 'org:invoices:create' }) || has({ plan: 'pro' })
  }
  fallback={<Upgrade />}
>
  <Invoices />
</Show>
```

Client-side `<Show>` hides its children visually but does not protect their data. Repeat sensitive authorization checks on the server.

## Astro loading controls

`<ClerkLoaded>` renders in both `ready` and `degraded` states. In Astro, `<ClerkLoaded>` and `<ClerkLoading>` are React islands imported from `@clerk/astro/react`, not the usual Astro components entry point, and require React integration.

```astro
---
import { ClerkLoaded, ClerkLoading } from '@clerk/astro/react'
---
<ClerkLoading client:load>Loading...</ClerkLoading>
<ClerkLoaded client:load>Ready or degraded</ClerkLoaded>
```

## Chrome extension redirects

Chrome extension `<RedirectToSignIn />` and `<RedirectToSignUp />` depend on React Router. Both replace the current history entry instead of pushing a new one.

## Authenticated Billing drawers

`<CheckoutButton />` and `<SubscriptionDetailsButton />` are available from React, Next.js, and Vue `/experimental` entry points. They throw unless nested inside `<Show when="signed-in">`.

They default to the current user. If `for="organization"` is set, an Active Organization is also required.

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
