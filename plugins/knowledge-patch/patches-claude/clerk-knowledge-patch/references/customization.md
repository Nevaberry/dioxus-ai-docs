# Customization

## Appearance hierarchy and options

The `appearance` object has `theme`, `options`, `variables`, `elements`,
`captcha`, and `cssLayerName`. Set it at the integration for global styling,
nest a component key such as `signIn` to style every instance of that
component, or pass it directly for a single-instance override.

`options` contains `animations`, `shimmer`, `logoImageUrl`, `logoLinkUrl`,
`logoPlacement`, `helpPageUrl`, `privacyPageUrl`, `termsPageUrl`,
`showOptionalFields`, `socialButtonsPlacement`, `socialButtonsVariant`, and
`unsafe_disableDevelopmentModeWarnings`. Social buttons are block-style below
three providers and icons otherwise. Logo placement defaults to `inside`,
animations and shimmer to `true`, and optional fields to hidden.

```tsx
<ClerkProvider appearance={{
  options: { logoPlacement: 'outside', socialButtonsPlacement: 'bottom' },
  signIn: { variables: { colorPrimary: '#6c47ff' } },
}}>
  {children}
</ClerkProvider>
```

## Themes and color mode

Install themes from `@clerk/ui` and import them from `@clerk/ui/themes`.
Available themes are default, `simple`, `shadcn`, `dark`, `shadesOfPurple`, and
`neobrutalism`. An array composes left-to-right, with later overlapping styles
winning.

```tsx
import { dark, neobrutalism } from '@clerk/ui/themes'
<ClerkProvider appearance={{ theme: [dark, neobrutalism] }} />
```

The default follows light/dark mode only when CSS `color-scheme` is set. The
shadcn theme targets Tailwind v4; import `@clerk/ui/themes/shadcn.css` after
`tailwindcss` so Tailwind generates externally referenced classes. Tailwind v3
needs the shadcn variables supplied manually.

## Variable migrations and browser support

These names, deprecated on 2025-07-15, are scheduled for removal in the next
major:

| Deprecated | Replacement |
| --- | --- |
| `colorText` | `colorForeground` |
| `colorTextOnPrimaryBackground` | `colorPrimaryForeground` |
| `colorTextSecondary` | `colorMutedForeground` |
| `spacingUnit` | `spacing` |
| `colorInputText` | `colorInputForeground` |
| `colorInputBackground` | `colorInput` |

Every variable also appears in kebab case with `--clerk-`, for example
`--clerk-color-primary`. Generated variants depend on `color-mix()` and relative
color syntax. The documented browser floors are Chrome 111/119, Firefox
113/120, and Safari 16.2/16.4 respectively. Use direct color values rather than
CSS variables or modern color functions for older browsers.

## Stable element hooks and Tailwind layers

Human-readable `cl-*` classes before the lock marker are stable; generated
classes after it are internal. Remove `cl-` for an `appearance.elements` key.
Values may be class names or inline style objects.

For Tailwind v4, put Clerk styles in a cascade layer before `utilities`:

```tsx
<ClerkProvider appearance={{
  cssLayerName: 'clerk',
  elements: { formButtonPrimary: 'bg-violet-600 hover:bg-violet-500' },
}} />
```

```css
@layer theme, base, clerk, components, utilities;
@import 'tailwindcss';
```

## Native iOS themes

iOS views use `ClerkTheme`, including `colors`, Dynamic Type-aligned `fonts`,
and `design.borderRadius`. Apply a whole theme through SwiftUI's
`\.clerkTheme` environment key or override a path such as
`\.clerkTheme.colors.primary`. Views automatically follow system light/dark
mode.

```swift
AuthView()
  .environment(\.clerkTheme, ClerkTheme(
    colors: .init(primary: .purple),
    design: .init(borderRadius: 12.0)
  ))
```

Fonts can use one family or per-text-style values. Asset Catalog colors can
define distinct light and dark variants.

## Component localization

Experimental localizations come from `@clerk/localizations`; exported names
remove the BCP 47 hyphen, so `fr-FR` becomes `frFR`. Pass a locale or custom
string tree through `localization`. It affects embedded components, not the
English-only hosted Account Portal.

```tsx
import { frFR } from '@clerk/localizations'
<ClerkProvider localization={frFR}>{children}</ClerkProvider>
```

Custom copy uses English localization keys. Override API messages under
`unstable__errors`.

## Email and SMS templates

Templates interpolate Handlebars values such as `{{app.name}}`; triple braces
leave special characters unescaped. Delivery is per-template. If Clerk delivery
is disabled, consume `emails.created` or `sms.created` webhooks. Changing SMS
message content requires this self-delivery path.

## Clerk Elements setup

The beta `@clerk/elements` package targets Next.js App Router on Clerk Core 2.
Sign-in and sign-up pages require optional catch-all routes. TypeScript needs
`moduleResolution: "bundler"`.

```text
app/sign-in/[[...sign-in]]/page.tsx
```

```ts
import * as Clerk from '@clerk/elements/common'
import * as SignIn from '@clerk/elements/sign-in'
```

## Elements flow structure

`SignIn.Root` and `SignUp.Root` own state and validate rendered flows against
instance settings; invalid sign-in flows throw in development. Roots infer
`/sign-in` or `/sign-up`, accept `path`, and support `routing="virtual"` for
modal flows.

Sign-in steps are `start`, `verifications`, `choose-strategy`,
`forgot-password`, and `reset-password`. Sign-up uses `start`, `continue`, and
`verifications`. `Strategy` renders a method, `SupportedStrategy` switches
methods, and `Action` submits, navigates, or resends with a `resendableAfter`
fallback. `SignUp.Captcha` is valid only in `start` and renders Turnstile.

## Elements fields, state, and loading

`Field` connects labels, inputs, and errors. `FieldError` and `GlobalError`
expose `message` and `code`; `FieldState` exposes validity and password-rule
messages/codes. A `code` field defaults to a numeric six-character `otp` input,
with `length`, `autoSubmit`, segmented rendering, and password-manager offset.
Password rules run live only with `validatePassword`. A sign-in input with
`autoComplete="webauthn"` attempts passkey autofill.

`Loading` can observe global, step, or provider state; provider scopes use
`provider:google`. Markup-producing elements accept `className`, and many allow
`asChild`. The child must forward its ref and spread incoming props. State is
also available through `data-valid`, `data-invalid`, and related attributes.

## UserButton menu extensions

Nest `UserButton.Action` and `UserButton.Link` in `UserButton.MenuItems`.
An action's `open` must match a `UserButton.UserProfilePage` URL. Actions named
`signOut` or `manageAccount` reposition defaults instead of creating entries.
Astro turns component props into strings, so it cannot receive `onClick`
directly; use an identifying prop plus a browser event listener.

## Profile navigation extensions

Dedicated user profiles use `UserProfile.Page`/`Link`; the `UserButton` modal
uses `UserButton.UserProfilePage`/`UserProfileLink`. Organization equivalents
are `OrganizationProfile.Page`/`Link` and
`OrganizationSwitcher.OrganizationProfilePage`/`OrganizationProfileLink`.
Switch a modal to navigation with `userProfileMode="navigation"` and
`userProfileUrl`, or the corresponding Organization props.

Reorder default user routes through labels `account` and `security`, and
Organization routes through `members` and `general`. The first sidenav item
cannot be a custom link.

## shadcn registry

Clerk publishes Next.js shadcn/ui registry entries. The quickstart installs the
provider/theme, catch-all auth pages, protected middleware, header, and
light/dark support. Sign-in, sign-up, waitlist, provider, and middleware entries
are independently installable.

```sh
npx shadcn@latest add @clerk/nextjs-quickstart
```
