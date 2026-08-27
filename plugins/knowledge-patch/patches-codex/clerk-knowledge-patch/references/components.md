# Components

## Configure combined prebuilt sign-in and sign-up

`<SignIn withSignUp>` keeps an unknown user in the prebuilt sign-in surface and
offers sign-up. `withSignUp` defaults to `true` only when
`CLERK_SIGN_IN_URL` is set; otherwise it defaults to `false`.
`transferable={false}` separately stops an OAuth attempt for an unknown email
from becoming an opaque sign-up transfer.

```tsx
<SignIn withSignUp transferable={false} />
```

The combined flow now supports strict user-enumeration protection without an
additional prop: it verifies email or phone before deciding whether to sign in
or create the user. The instance must use Open access, cannot use username
identifiers, and cannot begin with password. Disable password or prefer OTP.
Development warns about an invalid password-preferred configuration with
`sign_up_if_missing_password_preferred`. Account Portal does not support this
combined flow.

## Wire an embedded Waitlist

`<Waitlist />` requires Waitlist mode and a `waitlistUrl` on `<ClerkProvider>` or
`<SignIn>`. Use `afterJoinWaitlistUrl` on the component for post-join routing.
The Next.js component requires `@clerk/nextjs` 6.2.0 or newer.

```tsx
<ClerkProvider waitlistUrl="/waitlist">
  <Waitlist afterJoinWaitlistUrl="/thanks" />
</ClerkProvider>
```

## Know the Google One Tap boundary

`<GoogleOneTap />` requires custom credentials for the Google social connection
and does not render when a Clerk user is already signed in. It does not return a
Google access or refresh token; choose another flow when the application must
call Google APIs for the user. ITP and FedCM support default to enabled.

## Move UserButton sign-out redirects

`afterSignOutUrl` and `afterMultiSessionSingleSignOutUrl` are deprecated on
`<UserButton />`; move them to `<ClerkProvider>`. Keep
`afterSwitchSessionUrl` on `<UserButton />` for multi-session account changes.

```tsx
<ClerkProvider
  afterSignOutUrl="/signed-out"
  afterMultiSessionSingleSignOutUrl="/accounts"
>
  <UserButton afterSwitchSessionUrl="/dashboard" />
</ClerkProvider>
```

## Authorize UI with Show

`<Show>` accepts a Role, Permission, Feature, or Plan object in `when`, or a
callback receiving `has` for compound checks. `fallback` renders when the check
fails.

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

This only hides client content. Repeat every sensitive authorization check on
the server.

## Render Clerk loading states in Astro

`<ClerkLoaded>` renders in both `ready` and `degraded` states. In Astro,
`<ClerkLoaded>` and `<ClerkLoading>` are React islands imported from
`@clerk/astro/react`, not the normal Astro component entry, and require React.

```astro
---
import { ClerkLoaded, ClerkLoading } from '@clerk/astro/react'
---
<ClerkLoading client:load>Loading...</ClerkLoading>
<ClerkLoaded client:load>Ready or degraded</ClerkLoaded>
```

## Redirect inside Chrome extensions

Chrome extension versions of `<RedirectToSignIn />` and
`<RedirectToSignUp />` depend on React Router. Both replace the current history
entry rather than adding a new entry.

## Guard Billing drawers

`<CheckoutButton />` and `<SubscriptionDetailsButton />` from React, Next.js,
and Vue experimental entry points throw unless nested under
`<Show when="signed-in">`. Both default to the current user. Setting
`for="organization"` also throws unless an Organization is active.

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

## Pass SignOutButton props directly

In `@clerk/react` 6.1.3 and `@clerk/vue` 2.0.7,
`<SignOutButton />` deprecates `signOutOptions`. Pass `redirectUrl` and
`sessionId` directly. The nested object still works temporarily but logs a
deprecation warning.

```tsx
<SignOutButton redirectUrl="/signed-out" sessionId={sessionId} />
```
