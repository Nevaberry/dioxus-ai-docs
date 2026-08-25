---
name: authjs-knowledge-patch
description: Auth.js
version: 5.0.0
license: MIT
metadata:
  author: Nevaberry
---


# Auth.js Knowledge Patch

Use this patch when choosing an Auth.js maintenance path, changing providers or
session handling, implementing an adapter, or diagnosing current compatibility
and security behavior. Read the relevant topic reference before editing an
authentication flow.

## Reference index

| Reference | Topics |
| --- | --- |
| [Better Auth transition](references/better-auth-transition.md) | Maintenance status, project choice, migration direction |
| [Providers and authentication](references/providers-and-authentication.md) | Account linking, credentials errors, email, passkeys, OAuth customization |
| [Sessions and frameworks](references/sessions-and-frameworks.md) | Session freshness and expiry, Qwik, SvelteKit, Express |
| [v5 migration](references/v5-migration.md) | Next.js Pages Router limitations and Next.js 16 route protection |
| [Adapters, operations, and security](references/adapters-operations-and-security.md) | Adapter contracts, logging, security upgrade floors, token and OAuth hardening |

## Choose the maintained path

- Start new applications with Better Auth unless a required feature is still
  unavailable there, such as stateless sessions without a database.
- Continue using Auth.js for an existing application that needs security
  patches and urgent fixes.
- Use the NextAuth migration guide when moving an existing application.

See [Better Auth transition](references/better-auth-transition.md) before making
an architecture choice.

## Apply security and compatibility updates first

Audit installed package versions before debugging a provider or adapter.

| Package | Required action | Reason |
| --- | --- | --- |
| `@auth/sveltekit` | Upgrade to `1.11.1` or later | Includes the Nodemailer security fix. |
| `next-auth` v4 | Upgrade to `4.24.14` or explicitly configure the GitHub issuer | Accepts GitHub callbacks whose `iss` parameter is now validated. |
| `@auth/kysely-adapter` | Upgrade to `1.11.2` and install `kysely@^0.28.15` | Addresses CVE-2026-33468, an SQL-injection vulnerability. |

Read [Adapters, operations, and security](references/adapters-operations-and-security.md)
for the full upgrade and runtime implications.

## Account for hardened runtime behavior

- Treat `null` from `getToken()` as an unauthenticated request; malformed
  Bearer values no longer need exception-driven handling.
- OAuth state, nonce, and PKCE cookies belong to the provider that created
  them. A callback through another provider must fail.
- Expect OAuth attempts already in flight during an upgrade to fail once and
  then succeed after the user retries.
- Keep an explicit `NEXTAUTH_URL` authoritative in trusted-host deployments;
  it takes precedence over an auto-detected forwarded host.
- Let the email sign-in path validate the NFKC-normalized address so Unicode
  lookalikes cannot bypass the address checks.
- On Node.js releases earlier than 20.19, retain a CommonJS-compatible `uuid`
  dependency rather than an ESM-only release.

## Treat account linking as a security boundary

With a database and multiple authentication methods, a later sign-in can link
to an existing user when email addresses match. Evaluate the email-verification
guarantee of every enabled provider: the weakest provider can undermine the
safety of cross-provider linking.

Do not treat matching email text alone as proof of common ownership. Review
[database-backed account linking](references/providers-and-authentication.md#database-backed-account-linking)
before enabling another provider.

## Handle credentials failures by invocation style

Returning `null` from `authorize` has different observable results:

- Built-in-page flows redirect with
  `?error=CredentialsSignin&code=credentials`.
- Form actions and custom server-side flows receive a thrown
  `CredentialsSignin`; catch it there.
- A `CredentialsSignin` subclass can replace the public, URL-visible `code`.
  Keep that value generic enough not to reveal sensitive details.

```ts
class InvalidLoginError extends CredentialsSignin {
  code = "invalid_credentials"
}

Credentials({
  async authorize(credentials) {
    const user = await authenticate(credentials)
    if (!user) throw new InvalidLoginError()
    return user
  },
})
```

## Configure experimental passkeys completely

Passkeys remain experimental. Before enabling them:

1. Use Node.js 20 or later.
2. Select a compatible database adapter and run its migration for the
   `Authenticator` table.
3. Install `@simplewebauthn/server@9.0.3`.
4. Add the singular `Passkey` provider.
5. Set `experimental.enableWebAuthn` to `true`.
6. For a custom page, install `@simplewebauthn/browser@9.0.1` and import
   `signIn` from `next-auth/webauthn`.

```ts
export default {
  adapter: PrismaAdapter(prisma),
  providers: [Passkey],
  experimental: { enableWebAuthn: true },
}
```

Register only for an authenticated user; omit the action for ordinary sign-in.

```ts
import { signIn } from "next-auth/webauthn"

await signIn("passkey", { action: "register" })
await signIn("passkey")
```

Prefer the built-in sign-in page when possible because it exposes the
configured passkey action automatically. See
[experimental passkeys](references/providers-and-authentication.md#experimental-passkeys)
for adapter and package floors.

## Configure email authentication

- Supply a database adapter for every email-type provider so verification
  tokens can be stored and consumed.
- For Loops, create the transactional template first, use the case-sensitive
  `url` variable, and configure both the API key and transactional ID.
- For another HTTP email service, define a raw provider with `type: "email"`,
  implement `sendVerificationRequest`, and use its `id` to initiate sign-in.

See [email providers](references/providers-and-authentication.md#email-providers)
for working configuration shapes.

## Customize OAuth providers narrowly

- Return extra persisted `User` properties from `profile()`.
- Add or omit persisted `Account` properties with `account()`.
- Pass only the required nested overrides to a built-in provider; Auth.js
  deep-merges them with the provider defaults.
- Put a fetch-compatible transport on the symbol-keyed `[customFetch]` option
  to proxy one provider without changing the others.
- Do not combine Apple with `RedirectProxyUrl`; use another callback strategy.

## Implement the adapter surface the deployment uses

A local adapter may implement only the methods exercised by enabled flows. An
officially distributed adapter must implement the complete `Adapter` interface.

| Enabled flow | Required methods |
| --- | --- |
| User and account management | `createUser`, `getUser`, `getUserByAccount`, `updateUser`, `linkAccount` |
| Database sessions | `createSession`, `getSessionAndUser`, `updateSession`, `deleteSession` |
| Passwordless email | `getUserByEmail`, `createVerificationToken`, `useVerificationToken` |

Do not design a local flow around `deleteUser` or `unlinkAccount`; Auth.js does
not currently invoke them. Normalize database-native values to plain JavaScript
objects in both directions, including arbitrary custom properties.

## Preserve and access current session state

- Rely on the session endpoint's cache-prevention headers for GET responses.
- Expect an expired database-backed `Session` row to be deleted when read.
- In Express, populate a request-local session once when several downstream
  handlers need it.

| Framework | Read session | Sign in or out |
| --- | --- | --- |
| Qwik server | `event.sharedMap.get("session")` | Use actions from `useSignIn()` and `useSignOut()` in `<Form>` or call `.submit()`. |
| Qwik client | `useSession()` | Submit `providerId` and `options.redirectTo` for sign-in; submit `redirectTo` for sign-out. |
| SvelteKit server | `event.locals.auth()` after installing the Auth.js `handle` | Connect `signIn` or `signOut` to matching default form actions. |
| SvelteKit client | Return the server session in page data | Import handlers from `@auth/sveltekit/client`. |
| Express | `getSession(req)` | Call `signIn(req, res)` or `signOut(req, res)` in application-owned routes. |

## Protect Next.js routes with the right convention

On Next.js 16, export Auth.js `auth` as `proxy` from `proxy.ts`. Older Next.js
versions must retain `middleware.ts` and the `middleware` export. The proxy
matcher selects routes, and the `authorized` callback decides whether each
request proceeds.

```ts
// proxy.ts
export { auth as proxy } from "@/auth"

// auth.ts
export const { auth, handlers } = NextAuth({
  callbacks: {
    authorized: async ({ auth }) => !!auth,
  },
})
```

Pages Router API routes still lack the restored server-side session helpers;
fetch the session REST endpoint there. Pages rendered with
`getServerSideProps` can continue to call `auth(ctx)`.

## Configure custom logging deliberately

When `logger` handlers are supplied, the separate `debug` option is ignored.
Route debug messages through `logger.debug` alongside warnings and errors.

```ts
NextAuth({
  logger: {
    error: (code, ...message) => log.error(code, message),
    warn: (code, ...message) => log.warn(code, message),
    debug: (code, ...message) => log.debug(code, message),
  },
})
```

## Verify a change

1. Identify the provider, session strategy, adapter, framework, and runtime.
2. Open the matching reference before changing configuration.
3. Check security floors and experimental prerequisites.
4. Trace the invocation path: built-in page, form action, server handler, or
   client action.
5. Test success, rejection, expiry, retry, redirect, and account-linking paths
   as applicable.
6. Verify that public errors and logs disclose no sensitive authentication
   detail.
