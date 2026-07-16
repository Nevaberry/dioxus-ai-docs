# Customization

## Appearance hierarchy

The current `appearance` object contains:

- `theme`
- `options`
- `variables`
- `elements`
- `captcha`
- `cssLayerName`

Set it on the SDK integration for global styling. Nest a component key such as `signIn` to affect every instance of that component, or pass `appearance` directly to one component for a single-instance override.

```tsx
<ClerkProvider appearance={{
  options: {
    logoPlacement: 'outside',
    socialButtonsPlacement: 'bottom',
  },
  signIn: {
    variables: { colorPrimary: '#6c47ff' },
  },
}}>
  {children}
</ClerkProvider>
```

## Non-CSS appearance options

`options` supports:

- `animations`
- `shimmer`
- `logoImageUrl`
- `logoLinkUrl`
- `logoPlacement`
- `helpPageUrl`
- `privacyPageUrl`
- `termsPageUrl`
- `showOptionalFields`
- `socialButtonsPlacement`
- `socialButtonsVariant`
- `unsafe_disableDevelopmentModeWarnings`

Defaults:

- Social providers render as block buttons when fewer than three are configured, and icon buttons otherwise.
- `logoPlacement` is `inside`.
- Animations and shimmer are enabled.
- Optional fields are hidden.

## Themes and composition

Install themes from `@clerk/ui` and import theme objects from `@clerk/ui/themes`. Available choices are the default theme, `simple`, `shadcn`, `dark`, `shadesOfPurple`, and `neobrutalism`.

`theme` also accepts an array. Themes apply left to right; the last theme wins for overlapping styles.

```tsx
import { dark, neobrutalism } from '@clerk/ui/themes'

<ClerkProvider appearance={{ theme: [dark, neobrutalism] }} />
```

The default theme follows light/dark mode only when CSS `color-scheme` is set.

The shadcn theme is built for Tailwind v4. Import `@clerk/ui/themes/shadcn.css` after `tailwindcss` so Tailwind generates classes referenced only by the external theme. Tailwind v3 requires manually supplying the shadcn variables.

## Appearance variable migration

These variable names were deprecated on 2025-07-15 and are scheduled for removal in the next major release:

| Deprecated | Replacement |
| --- | --- |
| `colorText` | `colorForeground` |
| `colorTextOnPrimaryBackground` | `colorPrimaryForeground` |
| `colorTextSecondary` | `colorMutedForeground` |
| `spacingUnit` | `spacing` |
| `colorInputText` | `colorInputForeground` |
| `colorInputBackground` | `colorInput` |

Every appearance variable is also available as a kebab-case CSS custom property with the `--clerk-` prefix, such as `--clerk-color-primary`.

Generated color variants use `color-mix()` and relative color syntax. Stated minimum browser versions are:

| Feature | Chrome | Firefox | Safari |
| --- | ---: | ---: | ---: |
| `color-mix()` | 111 | 113 | 16.2 |
| Relative color syntax | 119 | 120 | 16.4 |

Use direct color values instead of CSS variables or modern color functions when supporting older browsers.

## Stable element hooks

In inspected Clerk markup, human-readable `cl-*` classes before the lock marker are stable. Generated classes after the marker are internal.

For `appearance.elements`, remove the `cl-` prefix to form the key. Values may be custom class names or inline style objects.

```tsx
<ClerkProvider appearance={{
  cssLayerName: 'clerk',
  elements: {
    formButtonPrimary: 'bg-violet-600 hover:bg-violet-500',
  },
}} />
```

Tailwind v4 utilities need Clerk styles in an earlier cascade layer. Set `cssLayerName` and declare the layer before `utilities`.

```css
@layer theme, base, clerk, components, utilities;
@import 'tailwindcss';
```

## Native iOS theming

Clerk iOS views use `ClerkTheme`, which contains `colors`, Dynamic Type-aligned `fonts`, and `design.borderRadius`.

Apply a complete theme through SwiftUI's `\.clerkTheme` environment key, scope it to one view and its descendants, or override an individual path such as `\.clerkTheme.colors.primary`. The views automatically follow system light/dark mode.

```swift
AuthView()
  .environment(\.clerkTheme, ClerkTheme(
    colors: .init(primary: .purple),
    design: .init(borderRadius: 12.0)
  ))
```

Fonts can use one family name or a separate value per text style. Asset Catalog colors can provide light and dark variants.

## Component localization

Prebuilt-component localization is experimental and comes from `@clerk/localizations`. Locale export names remove the BCP 47 hyphen; for example, `fr-FR` becomes `frFR`.

Pass an imported locale or a custom string tree through the integration's `localization` prop. This changes embedded components only; hosted Account Portal content remains English.

```tsx
import { frFR } from '@clerk/localizations'

<ClerkProvider localization={frFR}>{children}</ClerkProvider>
```

Custom copy uses keys from the English localization file. Override API errors under `unstable__errors`.

```tsx
<ClerkProvider localization={{
  formButtonPrimary: 'Continue',
  unstable__errors: {
    not_allowed_access: 'Use a company email.',
  },
}} />
```

## Email and SMS templates

Email and SMS templates interpolate Handlebars values such as `{{app.name}}`; triple braces leave special characters unescaped.

Delivery is configured per template. If Clerk delivery is disabled, consume `emails.created` or `sms.created` webhooks and deliver the message yourself. Changing SMS message content requires this self-delivery path.

## Clerk Elements setup

The beta `@clerk/elements` package targets Next.js App Router on Clerk Core 2. Sign-in and sign-up pages must use optional catch-all routes. TypeScript requires `moduleResolution: "bundler"` for its types.

```bash
npm install @clerk/elements
```

```tsx
// app/sign-in/[[...sign-in]]/page.tsx
import * as Clerk from '@clerk/elements/common'
import * as SignIn from '@clerk/elements/sign-in'
```

## Clerk Elements flow structure

`SignIn.Root` and `SignUp.Root` own flow state and validate rendered steps against instance settings. An invalid sign-in flow throws during development. Roots infer `/sign-in` or `/sign-up`, accept an explicit `path`, and support `routing="virtual"` for modal flows.

Sign-in steps:

- `start`
- `verifications`
- `choose-strategy`
- `forgot-password`
- `reset-password`

Sign-up steps:

- `start`
- `continue`
- `verifications`

`Strategy` conditionally renders the required method. `SupportedStrategy` switches methods. `Action` submits, navigates, or resends; resend actions receive a `resendableAfter` fallback. `SignUp.Captcha` renders Turnstile and is valid only inside the `start` step.

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

## Elements fields, state, and loading

`Field` connects labels, inputs, and errors. `FieldError` and `GlobalError` can expose `message` and `code`; `FieldState` exposes validity plus password-rule messages and codes.

A `code` field defaults to a numeric, six-character `otp` input. It supports `length`, `autoSubmit`, segmented rendering, and password-manager offset. Password rules run live only with `validatePassword`. A sign-in input with `autoComplete="webauthn"` attempts passkey autofill.

`Loading` reports global, current-step, or provider state. Provider scopes use names such as `provider:google`.

Markup-rendering elements accept `className`, and many accept `asChild`. The child must forward its ref and spread incoming props so Clerk handlers and attributes survive. Validity is also available through `data-valid`, `data-invalid`, and related state attributes.

## UserButton menu extensions

Nest `UserButton.Action` and `UserButton.Link` inside `UserButton.MenuItems` to add callbacks, profile openers, or links. An action's `open` value must match a `UserButton.UserProfilePage` URL.

Actions labeled `signOut` or `manageAccount` reposition existing defaults instead of creating new items.

```tsx
<UserButton>
  <UserButton.MenuItems>
    <UserButton.Action label="Help" labelIcon={<HelpIcon />} open="help" />
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

Astro component props become strings, so an `onClick` callback cannot be passed directly. Use an identifying prop and attach a browser event listener.

## Profile navigation extensions

- Dedicated user profile: `UserProfile.Page` and `UserProfile.Link`.
- UserButton modal: `UserButton.UserProfilePage` and `UserProfileLink`.
- Dedicated Organization profile: `OrganizationProfile.Page` and `OrganizationProfile.Link`.
- OrganizationSwitcher modal: `OrganizationSwitcher.OrganizationProfilePage` and `OrganizationProfileLink`.

Switch a default modal to a page with `userProfileMode="navigation"` plus `userProfileUrl`, or the corresponding Organization props.

Default user routes can be reordered with labels `account` and `security`; default Organization routes use `members` and `general`. The first sidenav item cannot be a custom link.

## shadcn registry

Clerk publishes shadcn/ui registry entries for Next.js. The quickstart adds provider and theme integration, catch-all authentication pages, protected-route middleware, a header, and light/dark support.

```bash
npx shadcn@latest add @clerk/nextjs-quickstart
```

Sign-in, sign-up, waitlist, provider, and middleware entries can also be installed independently.
