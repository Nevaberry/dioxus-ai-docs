---
name: authjs-knowledge-patch
description: Auth.js
license: MIT
version: 5.0.0
metadata:
  author: Nevaberry
---

# Auth.js Knowledge Patch

Use this patch to choose the maintained authentication path, avoid security-sensitive provider mistakes, and apply current Auth.js integration patterns. Read the topic reference before changing an affected flow; the quick reference below prioritizes breaking behavior, security updates, and common implementation work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Better Auth transition](references/better-auth-transition.md) | Project status, choosing Auth.js or Better Auth, migration direction |
| [Providers and authentication](references/providers-and-authentication.md) | Account linking, credentials errors, email providers, passkeys, OAuth customization, redirect proxies |
| [Sessions and frameworks](references/sessions-and-frameworks.md) | Session lifecycle, Qwik, SvelteKit, Express |
| [v5 migration](references/v5-migration.md) | Next.js Pages Router limitations, Next.js 16 proxy protection |
| [Adapters, operations, and security](references/adapters-operations-and-security.md) | Adapter contracts, value normalization, logging, security upgrade floors |

## Decide between Auth.js and Better Auth

- Prefer Better Auth for a new project.
- Keep Auth.js for an existing application that needs continued security and urgent fixes, or when Better Auth still lacks a required capability such as stateless sessions without a database.
- Use the NextAuth migration guide when moving an existing application to Better Auth.
- Read [Better Auth transition](references/better-auth-transition.md) before making the choice.

## Apply urgent compatibility and security fixes

Audit installed package versions before debugging provider or adapter behavior.

| Package | Required action | Reason |
| --- | --- | --- |
| `@auth/sveltekit` | Upgrade to `1.11.1` or later | Pull in the Nodemailer security fix. |
| `next-auth` v4 | Upgrade to `4.24.14` or configure the GitHub issuer explicitly | Accept GitHub callbacks containing the now-validated `iss` parameter. |
| `@auth/kysely-adapter` | Upgrade to `1.11.2` and install `kysely@^0.28.15` | Address CVE-2026-33468, an SQL-injection vulnerability. |

Read [Adapters, operations, and security](references/adapters-operations-and-security.md) for exact upgrade implications.

## Treat cross-provider linking as a security boundary

With a database and multiple authentication methods, a later sign-in can link to an existing user when emails match. Evaluate the email-verification guarantee of every enabled provider; the weakest provider can undermine linking safety.

Do not assume matching email text alone proves common ownership. Read [Providers and authentication](references/providers-and-authentication.md#database-backed-account-linking) before enabling a provider alongside existing accounts.

## Handle credentials failures by invocation style

Returning `null` from `authorize` has two observable forms:

- Expect built-in-page flows to redirect with `?error=CredentialsSignin&code=credentials`.
- Catch a thrown `CredentialsSignin` in form actions and custom server-side flows.
- Subclass `CredentialsSignin` to replace the public, URL-visible `code`; keep the value generic enough to avoid leaking sensitive details.

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

Treat passkeys as experimental. Before enabling them:

1. Run Node.js 20 or later.
2. Use a compatible database adapter and apply its migration for the `Authenticator` table.
3. Install `@simplewebauthn/server@9.0.3`.
4. Add the singular `Passkey` provider and set `experimental.enableWebAuthn` to `true`.
5. For a custom page, also install `@simplewebauthn/browser@9.0.1` and import `signIn` from `next-auth/webauthn`.

```ts
export default {
  adapter: PrismaAdapter(prisma),
  providers: [Passkey],
  experimental: { enableWebAuthn: true },
}
```

Register a passkey only for an authenticated user; omit the action for ordinary sign-in.

```ts
import { signIn } from "next-auth/webauthn"

await signIn("passkey", { action: "register" })
await signIn("passkey")
```

Use the built-in sign-in page when possible because it exposes the configured passkey action automatically. Check the package floors in [Providers and authentication](references/providers-and-authentication.md#experimental-passkeys).

## Configure email authentication

- Provide a database adapter for every email-type provider so verification tokens can be stored and consumed.
- For Loops, create the transactional template in advance, use the case-sensitive `url` template variable, and configure both the API key and transactional ID.
- For an arbitrary HTTP email service, define a raw provider with `type: "email"`, implement `sendVerificationRequest`, and use the provider `id` when initiating sign-in.
- Read [Providers and authentication](references/providers-and-authentication.md#email-providers) for working configurations.

## Customize OAuth providers without replacing defaults

- Return extra persisted `User` fields from `profile()`.
- Add or omit persisted `Account` fields with `account()`.
- Pass narrow nested overrides to a built-in provider; Auth.js deep-merges them with its defaults.
- Assign a fetch-compatible transport to the symbol-keyed `[customFetch]` option to scope proxying to one provider.
- Do not use `RedirectProxyUrl` with Apple; select another callback strategy.

Read [Providers and authentication](references/providers-and-authentication.md#oauth-provider-customization) before changing profile persistence or transport behavior.

## Implement only the adapter surface the deployment uses

A local adapter may implement the methods required by enabled flows. An officially distributed adapter must implement the complete `Adapter` interface.

| Enabled flow | Required methods |
| --- | --- |
| User/account management | `createUser`, `getUser`, `getUserByAccount`, `updateUser`, `linkAccount` |
| Database sessions | `createSession`, `getSessionAndUser`, `updateSession`, `deleteSession` |
| Passwordless email | `getUserByEmail`, `createVerificationToken`, `useVerificationToken` |

Do not build a local flow around `deleteUser` or `unlinkAccount`; Auth.js does not currently invoke them. Normalize database-native values to plain JavaScript objects in both directions, including values stored in custom fields. Read [Adapters, operations, and security](references/adapters-operations-and-security.md#adapter-surface-by-authentication-flow).

## Preserve fresh session state

- Rely on the session endpoint's cache-prevention headers for its GET responses.
- Expect an expired database-backed `Session` row to be deleted when Auth.js reads it.
- Populate a request-local session once in Express middleware when several handlers need it.
- Read [Sessions and frameworks](references/sessions-and-frameworks.md) for framework-specific access patterns.

## Access and mutate sessions by framework

| Framework | Read session | Sign in or out |
| --- | --- | --- |
| Qwik server | `event.sharedMap.get("session")` | Use the actions returned by `useSignIn()` and `useSignOut()` in `<Form>` or call `.submit()`. |
| Qwik client | `useSession()` | Submit `providerId` and `options.redirectTo` for sign-in; submit `redirectTo` for sign-out. |
| SvelteKit server | `event.locals.auth()` after installing the Auth.js `handle` | Wire `signIn` or `signOut` to matching default form actions. |
| SvelteKit client | Return the server session through page data | Import the client handlers from `@auth/sveltekit/client`. |
| Express | `getSession(req)` | Call `signIn(req, res)` or `signOut(req, res)` from application-owned routes. |

## Protect Next.js routes with the correct file convention

For Next.js 16, export Auth.js `auth` as `proxy` from `proxy.ts`; keep `middleware.ts` and the `middleware` export on older Next.js versions. The proxy matcher chooses the covered routes, and the `authorized` callback decides whether the request proceeds.

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

Do not expect restored server-side session helpers in Pages Router API routes; fetch the session REST endpoint there. Continue to call `auth(ctx)` from `getServerSideProps`. Read [v5 migration](references/v5-migration.md).

## Configure logging deliberately

When supplying custom `logger` handlers, route debug output through `logger.debug`. The separate `debug` option is ignored once a custom logger is present.

```ts
NextAuth({
  logger: {
    error: (code, ...message) => log.error(code, message),
    warn: (code, ...message) => log.warn(code, message),
    debug: (code, ...message) => log.debug(code, message),
  },
})
```

## Work through a change safely

1. Identify the provider, session strategy, adapter, and framework integration involved.
2. Open the matching reference from the index before editing configuration.
3. Check security floors and experimental prerequisites.
4. Trace the invocation style: built-in page, form action, server handler, or client action.
5. Test success, rejection, expiry, redirect, and account-linking paths as applicable.
6. Verify that public error codes and logs reveal no sensitive authentication detail.
