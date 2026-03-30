# Authentication Flows

## Core 3 Custom Flow API

The custom flow API changed significantly in Core 3. The old pattern (`signUp.create()` → `prepareEmailAddressVerification()` → `attemptEmailAddressVerification()` → `setActive()`) is replaced with a method-chaining API.

### Sign-up (email/password)

```tsx
const { signUp, errors, fetchStatus } = useSignUp()

// Step 1: Start sign-up with password
const { error } = await signUp.password({ emailAddress, password })

// Step 2: Send verification code
await signUp.verifications.sendEmailCode()

// Step 3: Verify code
await signUp.verifications.verifyEmailCode({ code })

// Step 4: Finalize (replaces setActive)
if (signUp.status === 'complete') {
  await signUp.finalize({
    navigate: ({ session, decorateUrl }) => {
      if (session?.currentTask) return // handle pending session tasks
      const url = decorateUrl('/')
      url.startsWith('http') ? (window.location.href = url) : router.push(url)
    },
  })
}
```

### Sign-in (email OTP)

```tsx
const { signIn, errors, fetchStatus } = useSignIn()

// Step 1: Create sign-in
await signIn.create({ identifier: emailAddress })

// Step 2: Send and verify code
await signIn.emailCode.sendCode()
const { error } = await signIn.emailCode.verifyCode({ code })

// Step 3: Finalize
if (signIn.status === 'complete') {
  await signIn.finalize({ navigate: ({ decorateUrl }) => { /* ... */ } })
}
```

Key changes: `errors` object has `errors.fields.emailAddress`, `errors.fields.password`, `errors.fields.code` for field-level errors. `fetchStatus` is `'fetching'` or `'idle'` for loading states. `signUp.status` can be `'complete'` or `'missing_requirements'`. `signUp.unverifiedFields` and `signUp.missingFields` for tracking requirements.

## Reverification (Step-up Auth)

Re-verify user credentials before sensitive actions (e.g., money transfers). Uses `useReverification()` hook on client and `has({ reverification })` on server.

### Server-side (Next.js Server Action)

```ts
'use server'
import { auth, reverificationError } from '@clerk/nextjs/server'

export const transferMoney = async () => {
  const { has } = await auth.protect()

  // Presets: 'strict_mfa' | 'strict' (10m) | 'moderate' (1h) | 'lax'
  if (!has({ reverification: 'strict' })) {
    return reverificationError('strict')
  }

  return { success: true }
}
```

For Route Handlers, use `reverificationErrorResponse('strict')` instead (returns a Fetch `Response`). For non-Clerk frameworks, return a 403 JSON: `{ "clerk_error": { "type": "forbidden", "reason": "reverification-error" } }`.

### Client-side

```tsx
'use client'
import { useReverification } from '@clerk/nextjs'
import { transferMoney } from '../actions'

export default function Page() {
  // Wraps the action — auto-shows verification modal if needed, retries on success
  const performTransfer = useReverification(transferMoney)

  const handleClick = async () => {
    const result = await performTransfer()
    if (!result) return // user cancelled reverification
  }

  return <button onClick={handleClick}>Transfer</button>
}
```

`useReverification()` also works with `fetch` calls — wraps any async function that might return a reverification error.

## Session Tasks (Post-auth Requirements)

Sessions can be in a `pending` state when tasks must be completed after auth (e.g., choosing an Organization, resetting a compromised password, setting up MFA).

Three session states: `signed-in` (active), `pending` (authenticated but tasks incomplete — treated as signed-out by default), `signed-out`.

### Task Components

```tsx
import { TaskChooseOrganization } from '@clerk/nextjs' // when Personal Accounts disabled
import { TaskResetPassword } from '@clerk/nextjs'       // force password reset
import { TaskSetupMFA } from '@clerk/nextjs'             // require MFA setup

<TaskChooseOrganization redirectUrlComplete="/dashboard" />
```

### Middleware Handling of Pending Sessions

```tsx
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

const isProtectedRoute = createRouteMatcher(['/dashboard(.*)'])

export default clerkMiddleware(async (auth, req) => {
  const { isAuthenticated, sessionStatus, redirectToSignIn } = await auth()

  // Redirect pending users to complete tasks
  if (!isAuthenticated && sessionStatus === 'pending' && isProtectedRoute(req)) {
    const url = req.nextUrl.clone()
    url.pathname = '/session-tasks'
    return NextResponse.redirect(url)
  }

  if (!isAuthenticated && isProtectedRoute(req)) return redirectToSignIn()
})
```

### `treatPendingAsSignedOut` Prop

Default `true` — controls how pending sessions behave with `<Show>`, `useAuth()`, and `auth()`:

```tsx
// Access userId even for pending sessions
const { userId } = await auth({ treatPendingAsSignedOut: false })

// Show content to pending users
<Show when="signed-in" treatPendingAsSignedOut={false}>
  <p>Signed-in AND pending users see this</p>
</Show>
```

`<RedirectToTasks />` control component redirects users with pending tasks to the appropriate task page.

## signUpIfMissing (Privacy-preserving Sign-in-or-up)

Prevents user enumeration by proceeding to verification regardless of whether the account exists. Only after verification does the backend reveal if the account is new.

```tsx
const { signIn } = useSignIn()
const { signUp } = useSignUp()

// Step 1: Start — always goes to verification, even if user doesn't exist
await signIn.create({ identifier: emailAddress, signUpIfMissing: true })
await signIn.emailCode.sendCode()

// Step 2: Verify — error code reveals if transfer is needed
const { error } = await signIn.emailCode.verifyCode({ code })

if (error?.errors[0]?.code === 'sign_up_if_missing_transfer') {
  // User doesn't exist — transfer verified identity to sign-up
  await signUp.create({ transfer: true })

  if (signUp.status === 'missing_requirements') {
    // Collect additional fields (e.g., legal acceptance, name)
    await signUp.update({ legalAccepted: true })
  }
  if (signUp.status === 'complete') await signUp.finalize({ navigate: /* ... */ })
} else if (signIn.status === 'complete') {
  await signIn.finalize({ navigate: /* ... */ })
}
```

Restrictions: password strategy not supported (needs a verification step), only email/phone/Web3 identifiers (not username), not available in restricted/waitlist sign-up modes.

## Session Token v2 Claims

Session tokens now use v2 claims (v1 deprecated April 2025). New claims: `v` (version), `pla` (plan, e.g. `u:free` or `o:pro`), `fea` (features, e.g. `o:dashboard,o:teams`), `sts` (session status, e.g. `pending`).

Organization claims are now compact under the `o` key: `o.id`, `o.slg` (slug), `o.rol` (role without `org:` prefix), `o.per` (permissions as comma-separated), `o.fpm` (feature-permission bitmask). This replaced the verbose v1 claims (`org_id`, `org_slug`, `org_role`, `org_permissions`). Use Clerk SDKs with API version `2025-04-10` to decode automatically.

## Structured `Errors<T>` Type

Custom sign-in/sign-up flows return a typed `errors` object:

```ts
interface Errors<T> {
  fields: T           // SignInFields or SignUpFields — typed per-field errors
  raw: ClerkError[] | null         // unparsed API errors
  global: ClerkGlobalHookError[] | null  // errors not tied to a field
}

// SignInFields: { identifier, password, code } — each FieldError | null
// SignUpFields: { firstName, lastName, emailAddress, phoneNumber, password, username, code, captcha, legalAccepted }

// FieldError shape:
interface FieldError {
  code: string        // machine-readable error code
  message: string     // developer-facing message
  longMessage?: string // user-facing message (localizable via code)
}
```

Usage:

```tsx
const { signUp, errors, fetchStatus } = useSignUp()

// Field-level errors
if (errors.fields.emailAddress) {
  console.log(errors.fields.emailAddress.longMessage) // "That email is already in use"
}

// Global errors (not field-specific)
errors.global?.forEach((err) => {
  if (err.isClerkApiResponseError()) {
    // Narrowed to ClerkAPIResponseError
  }
  if (err.isClerkRuntimeError()) {
    // Narrowed to ClerkRuntimeError
  }
})
```
