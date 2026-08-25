# Customization

## Apply appearance at the right level

The `appearance` object contains `theme`, `options`, `variables`, `elements`,
`captcha`, and `cssLayerName`. Set it on the SDK integration for global styling,
nest a component key such as `signIn` to affect every instance of that
component, or pass it directly to one component for a single-instance override.

`options` contains non-CSS controls: `animations`, `shimmer`, `logoImageUrl`,
`logoLinkUrl`, `logoPlacement`, `helpPageUrl`, `privacyPageUrl`, `termsPageUrl`,
`showOptionalFields`, `socialButtonsPlacement`, `socialButtonsVariant`, and
`unsafe_disableDevelopmentModeWarnings`.

Social providers default to block buttons when fewer than three are configured
and icon buttons otherwise. Logo placement defaults to `inside`, animations and
shimmer to `true`, and optional fields to hidden.

```tsx
<ClerkProvider
  appearance={{
    options: {
      logoPlacement: 'outside',
      socialButtonsPlacement: 'bottom',
    },
    signIn: { variables: { colorPrimary: '#6c47ff' } },
  }}
>
  {children}
</ClerkProvider>
```

## Compose supplied themes

Install themes from `@clerk/ui` and import them from `@clerk/ui/themes`.
Available choices are the default theme, `simple`, `shadcn`, `dark`,
`shadesOfPurple`, and `neobrutalism`. `theme` can be an array; themes apply
left-to-right and the last overlapping style wins.

```tsx
import { dark, neobrutalism } from '@clerk/ui/themes'

<ClerkProvider appearance={{ theme: [dark, neobrutalism] }} />
```

The default theme follows light/dark mode only when CSS `color-scheme` is set.
The shadcn theme targets Tailwind v4. Import
`@clerk/ui/themes/shadcn.css` after `tailwindcss` so Tailwind generates classes
otherwise present only in the external theme. Tailwind v3 requires supplying
the shadcn variables manually.

## Migrate renamed variables

These names were deprecated on 2025-07-15 and are scheduled for removal in the
next major:

| Deprecated | Replacement |
| --- | --- |
| `colorText` | `colorForeground` |
| `colorTextOnPrimaryBackground` | `colorPrimaryForeground` |
| `colorTextSecondary` | `colorMutedForeground` |
| `spacingUnit` | `spacing` |
| `colorInputText` | `colorInputForeground` |
| `colorInputBackground` | `colorInput` |

Each appearance variable is also exposed in kebab case with `--clerk-`, such as
`--clerk-color-primary`.

Generated variants use `color-mix()` and relative color syntax. The stated
minimum browsers for those two features respectively are Chrome 111/119,
Firefox 113/120, and Safari 16.2/16.4. Use direct color values rather than CSS
variables or modern color functions when older browsers must be supported.

## Target stable elements and layer Tailwind v4

In component markup, human-readable `cl-*` classes before the lock marker are
stable; generated classes after it are internal. Remove `cl-` to create an
`appearance.elements` key. Values may be custom class names or inline style
objects.

For Tailwind v4, put Clerk styles in a cascade layer declared before
`utilities`:

```tsx
<ClerkProvider
  appearance={{
    cssLayerName: 'clerk',
    elements: {
      formButtonPrimary: 'bg-violet-600 hover:bg-violet-500',
    },
  }}
/>
```

```css
@layer theme, base, clerk, components, utilities;
@import 'tailwindcss';
```

## Theme native iOS views

iOS views use `ClerkTheme`, whose main areas are `colors`, Dynamic Type-aligned
`fonts`, and `design.borderRadius`. Apply a complete theme through SwiftUI's
`\.clerkTheme` environment key, scope it to a view tree, or override one path
such as `\.clerkTheme.colors.primary`. Views follow system light/dark mode.

```swift
AuthView()
  .environment(\.clerkTheme, ClerkTheme(
    colors: .init(primary: .purple),
    design: .init(borderRadius: 12.0)
  ))
```

Fonts can use one family name or per-text-style values. Asset Catalog colors
can provide distinct light and dark variants.

## Localize embedded components

Component localization is experimental and ships in `@clerk/localizations`.
Export names remove the BCP 47 hyphen, so `fr-FR` becomes `frFR`. Pass an
exported locale or a custom string tree to the integration's `localization`
prop. This affects embedded components only; hosted Account Portal stays
English.

```tsx
import { frFR } from '@clerk/localizations'

<ClerkProvider localization={frFR}>{children}</ClerkProvider>
```

Custom copy uses keys from the English localization file. Override API errors
under `unstable__errors`.

```tsx
<ClerkProvider
  localization={{
    formButtonPrimary: 'Continue',
    unstable__errors: {
      not_allowed_access: 'Use a company email.',
    },
  }}
/>
```

## Own email and SMS delivery when customizing it

Email and SMS templates interpolate Handlebars values such as `{{app.name}}`;
triple braces leave special characters unescaped. Delivery is configured per
template. If Clerk delivery is disabled, consume `emails.created` or
`sms.created` webhooks. Custom SMS message content requires this self-delivery
path.

## Meet Clerk Elements setup constraints

The beta `@clerk/elements` package targets Next.js App Router on Clerk Core 2.
Sign-in and sign-up pages must be optional catch-all routes. TypeScript must use
`moduleResolution: "bundler"` for package type resolution.

```text
npm install @clerk/elements
```

```tsx
// app/sign-in/[[...sign-in]]/page.tsx
import * as Clerk from '@clerk/elements/common'
import * as SignIn from '@clerk/elements/sign-in'
```

## Build valid Elements flows

`SignIn.Root` and `SignUp.Root` own flow state and validate the rendered flow
against instance configuration; an invalid sign-in flow throws in development.
Roots infer `/sign-in` or `/sign-up`, accept an explicit `path`, and support
`routing="virtual"` for modal flows.

Sign-in steps are `start`, `verifications`, `choose-strategy`,
`forgot-password`, and `reset-password`. Sign-up steps are `start`, `continue`,
and `verifications`. `Strategy` conditionally renders the active method,
`SupportedStrategy` changes methods, and `Action` submits, navigates, or resends
with a `resendableAfter` fallback. `SignUp.Captcha` renders Turnstile and is
valid only inside `start`.

```tsx
<SignIn.Root>
  <SignIn.Step name="verifications">
    <SignIn.Strategy name="email_code">
      <Clerk.Field name="code">
        <Clerk.Input />
      </Clerk.Field>
      <SignIn.Action submit>Verify</SignIn.Action>
      <SignIn.Action
        resend
        fallback={({ resendableAfter }) => resendableAfter}
      >
        Resend
      </SignIn.Action>
    </SignIn.Strategy>
  </SignIn.Step>
</SignIn.Root>
```

## Use Elements field and loading state

`Field` associates labels, inputs, and errors. `FieldError` and `GlobalError`
can expose `message` and `code`; `FieldState` exposes validity plus password-rule
messages and codes.

A `code` field defaults to a numeric six-character `otp` input, supporting
`length`, `autoSubmit`, segmented rendering, and password-manager offset.
Password rules run live only with `validatePassword`. A sign-in input with
`autoComplete="webauthn"` attempts passkey autofill.

`Loading` can report global, step, or provider state; provider scopes use names
such as `provider:google`. Markup elements accept `className`, and many support
`asChild`; the child must forward its ref and spread incoming props. State is
also available through `data-valid`, `data-invalid`, and related attributes.

## Extend the UserButton menu

Place `UserButton.Action` and `UserButton.Link` inside `UserButton.MenuItems`.
An action's `open` must equal a `UserButton.UserProfilePage` URL. Actions named
`signOut` or `manageAccount` reposition the built-ins rather than adding new
entries.

```tsx
<UserButton>
  <UserButton.MenuItems>
    <UserButton.Action
      label="Help"
      labelIcon={<HelpIcon />}
      open="help"
    />
    <UserButton.Link label="Docs" labelIcon={<DocsIcon />} href="/docs" />
    <UserButton.Action label="signOut" />
  </UserButton.MenuItems>
  <UserButton.UserProfilePage
    label="Help"
    labelIcon={<HelpIcon />}
    url="help"
  >
    <Help />
  </UserButton.UserProfilePage>
</UserButton>
```

Astro serializes component props to strings, so it cannot receive `onClick`
directly. Add an identifying prop and register a browser event listener.

## Extend profile navigation

- Dedicated user profile: `UserProfile.Page` and `UserProfile.Link`.
- UserButton modal: `UserButton.UserProfilePage` and
  `UserButton.UserProfileLink`.
- Dedicated Organization profile: `OrganizationProfile.Page` and
  `OrganizationProfile.Link`.
- OrganizationSwitcher modal: `OrganizationSwitcher.OrganizationProfilePage`
  and `OrganizationSwitcher.OrganizationProfileLink`.

Switch from modal to page navigation with `userProfileMode="navigation"` and
`userProfileUrl`, or the corresponding Organization settings. Reorder default
user routes with `account` and `security`, and Organization routes with
`members` and `general`. The first sidenav item cannot be a custom link.

## Install Clerk's shadcn registry entries

The Next.js quickstart registry entry installs provider/theme integration,
catch-all auth pages, protected-route middleware, a header, and light/dark
support. Sign-in, sign-up, waitlist, provider, and middleware entries are also
available independently.

```text
npx shadcn@latest add @clerk/nextjs-quickstart
```
