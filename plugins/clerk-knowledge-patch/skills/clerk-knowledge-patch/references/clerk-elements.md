# Clerk Elements

`@clerk/elements` provides unstyled, composable components for building fully custom sign-in/sign-up UIs. Currently supports Next.js App Router only.

```bash
npm install @clerk/elements
```

## Sign-in Anatomy

Steps: `'start'` | `'verifications'` | `'choose-strategy'` | `'forgot-password'` | `'reset-password'`

```tsx
import * as Clerk from '@clerk/elements/common'
import * as SignIn from '@clerk/elements/sign-in'

<SignIn.Root>
  <SignIn.Step name="start">
    <Clerk.Connection name="google">
      <Clerk.Icon /> Sign in with Google
    </Clerk.Connection>
    <Clerk.Field name="identifier">
      <Clerk.Label>Email</Clerk.Label>
      <Clerk.Input />
      <Clerk.FieldError />
    </Clerk.Field>
    <SignIn.Action submit>Continue</SignIn.Action>
  </SignIn.Step>

  <SignIn.Step name="verifications">
    <SignIn.Strategy name="email_code">
      <Clerk.Field name="code">
        <Clerk.Label>Code</Clerk.Label>
        <Clerk.Input type="otp" autoSubmit />
        <Clerk.FieldError />
      </Clerk.Field>
      <SignIn.Action submit>Verify</SignIn.Action>
      <SignIn.Action resend fallback={({ resendableAfter }) => <p>Resend in {resendableAfter}s</p>}>
        Resend code
      </SignIn.Action>
    </SignIn.Strategy>
    <SignIn.Strategy name="password">
      <Clerk.Field name="password">
        <Clerk.Label>Password</Clerk.Label>
        <Clerk.Input />
        <Clerk.FieldError />
      </Clerk.Field>
      <SignIn.Action submit>Sign In</SignIn.Action>
    </SignIn.Strategy>
    <SignIn.Action navigate="choose-strategy">Use another method</SignIn.Action>
  </SignIn.Step>

  <SignIn.Step name="choose-strategy">
    <SignIn.SupportedStrategy name="phone_code">Send code to phone</SignIn.SupportedStrategy>
    <SignIn.SupportedStrategy name="password">Use password</SignIn.SupportedStrategy>
  </SignIn.Step>

  <SignIn.Step name="forgot-password">
    <SignIn.SupportedStrategy name="reset_password_email_code">Reset via email</SignIn.SupportedStrategy>
  </SignIn.Step>

  <SignIn.Step name="reset-password">
    <Clerk.Field name="password"><Clerk.Label>New password</Clerk.Label><Clerk.Input /><Clerk.FieldError /></Clerk.Field>
    <Clerk.Field name="confirmPassword"><Clerk.Label>Confirm</Clerk.Label><Clerk.Input /><Clerk.FieldError /></Clerk.Field>
    <SignIn.Action submit>Update password</SignIn.Action>
  </SignIn.Step>
</SignIn.Root>
```

## Sign-up Anatomy

Steps: `'start'` | `'continue'` | `'verifications'`

```tsx
import * as SignUp from '@clerk/elements/sign-up'

<SignUp.Root>
  <SignUp.Step name="start">
    <Clerk.Connection name="google">Sign up with Google</Clerk.Connection>
    <Clerk.Field name="emailAddress"><Clerk.Label>Email</Clerk.Label><Clerk.Input /><Clerk.FieldError /></Clerk.Field>
    <SignUp.Captcha />  {/* Cloudflare Turnstile widget */}
    <SignUp.Action submit>Sign up</SignUp.Action>
  </SignUp.Step>

  <SignUp.Step name="continue">  {/* Additional required fields (e.g. after social sign-up) */}
    <Clerk.Field name="username"><Clerk.Label>Username</Clerk.Label><Clerk.Input /><Clerk.FieldError /></Clerk.Field>
    <SignUp.Action submit>Continue</SignUp.Action>
    <SignUp.Action navigate="start">Go back</SignUp.Action>
  </SignUp.Step>

  <SignUp.Step name="verifications">
    <SignUp.Strategy name="email_code">
      <Clerk.Field name="code"><Clerk.Label>Code</Clerk.Label><Clerk.Input type="otp" /><Clerk.FieldError /></Clerk.Field>
      <SignUp.Action submit>Verify</SignUp.Action>
    </SignUp.Strategy>
  </SignUp.Step>
</SignUp.Root>
```

## Key Patterns

- **Strategy names (sign-in):** `password`, `email_code`, `phone_code`, `email_link`, `passkey`, `totp`, `backup_code`, `reset_password_email_code`, `reset_password_phone_code`, `enterprise_sso`, `web3_metamask_signature`, `web3_coinbase_wallet_signature`, `web3_okx_wallet_signature`
- **Strategy names (sign-up):** `email_code`, `email_link`, `phone_code`
- **Loading states:** `<Clerk.Loading scope="provider:google">{(isLoading) => ...}</Clerk.Loading>` — scope defaults to current step or `'global'`
- **Cross-flow navigation:** `<Clerk.Link navigate="sign-up">` renders a link between sign-in and sign-up flows
- **Virtual routing for modals:** `<SignIn.Root routing="virtual">` — no URL changes
- **OTP segmented input:**

```tsx
<Clerk.Input type="otp" render={({ value, status }) => <span data-status={status}>{value}</span>} />
```
- **Password validation:** `<Clerk.Input type="password" validatePassword />` with `<Clerk.FieldState>{({ state, codes, message }) => ...}</Clerk.FieldState>`
- **All components support `asChild` prop** for composition with existing component libraries

## shadcn/ui CLI Integration

Clerk publishes a shadcn/ui registry:

```bash
# Full quickstart (layout, sign-in/up pages, middleware, header, theme provider)
npx shadcn@latest add @clerk/nextjs-quickstart

# Individual pages
npx shadcn@latest add @clerk/nextjs-sign-in-page
npx shadcn@latest add @clerk/nextjs-sign-up-page
npx shadcn@latest add @clerk/nextjs-waitlist-page

# Individual components/files
npx shadcn@latest add @clerk/nextjs-clerk-provider
npx shadcn@latest add @clerk/nextjs-middleware
```
