# Providers and Authentication

## Database-backed account linking

When a database and multiple authentication methods are configured, Auth.js
tries to link a later sign-in to existing `User` and `Account` records if the
email address matches. The email-verification guarantees of every enabled
provider therefore become part of the account-linking security boundary.

Before adding a provider, determine whether it verifies email ownership to the
same standard as the existing providers. Do not assume equal email strings
alone demonstrate that both identities have the same owner.

## Credentials failures and public codes

The effect of returning `null` from a Credentials provider's `authorize`
callback depends on how authentication was invoked:

- A built-in sign-in page redirects to
  `?error=CredentialsSignin&code=credentials`.
- A form action or custom server-side caller receives a thrown
  `CredentialsSignin` and must catch it.

Subclass `CredentialsSignin` to choose a different URL-visible `code`. Because
that value is public, use a generic classification and never encode whether a
specific account exists or which credential failed.

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

## Email providers

Every email-type provider requires a database adapter to store and consume
verification tokens.

### Loops magic links

Create the Loops transactional template before enabling the provider. The
template must accept the case-sensitive `url` variable containing the magic
link. Configure both the API key and transactional-template ID.

```ts
Loops({
  apiKey: process.env.AUTH_LOOPS_KEY,
  transactionalId: process.env.AUTH_LOOPS_TRANSACTIONAL_ID,
})
```

### Custom HTTP email delivery

An arbitrary HTTP email service can be represented by a raw provider object
with `type: "email"`. Implement `sendVerificationRequest`; its input contains
the recipient in `identifier` and the magic link in `url`. Start sign-in with
the provider's configured `id`.

```ts
NextAuth({
  adapter,
  providers: [
    {
      id: "http-email",
      name: "Email",
      type: "email",
      maxAge: 60 * 60 * 24,
      sendVerificationRequest,
    },
  ],
})
```

## Experimental passkeys

Passkey support is experimental and requires all of the following:

- Node.js 20 or newer.
- A compatible database adapter and its migration for an `Authenticator`
  table.
- `@simplewebauthn/server@9.0.3`.
- The singular `Passkey` provider.
- `experimental.enableWebAuthn: true`.

The current compatible package floors are `next-auth@5.0.0-beta.17`,
`@auth/sveltekit@1.0.2`, `@auth/prisma-adapter@1.3.3`,
`@auth/unstorage-adapter@2.1.0`, and `@auth/drizzle-adapter@1.1.1`.

```bash
npm install @simplewebauthn/server@9.0.3
```

```ts
export default {
  adapter: PrismaAdapter(prisma),
  providers: [Passkey],
  experimental: { enableWebAuthn: true },
}
```

The built-in sign-in page exposes the configured passkey action automatically.

### Custom registration and sign-in

A custom page also needs `@simplewebauthn/browser@9.0.1`. Import the WebAuthn
variant of `signIn` from `next-auth/webauthn`.

Only an already authenticated user should register another passkey, using
`action: "register"`. An unauthenticated user signs in without that option.

```ts
import { signIn } from "next-auth/webauthn"

await signIn("passkey", { action: "register" })
await signIn("passkey")
```

## OAuth provider customization

### Persist additional fields

Return additional properties from an OAuth provider's `profile()` callback to
persist them on the `User`. Use its `account()` callback to add fields to or
omit unneeded fields from the associated `Account` row.

### Override nested defaults

Options passed to a built-in OAuth provider are deeply merged with its
defaults. Override only the needed nested value rather than reproducing the
complete provider configuration.

```ts
Auth0({
  authorization: { params: { scope: "openid custom_scope" } },
})
```

### Install a provider-specific transport

Assign a fetch-compatible proxy or transport to the symbol-keyed
`[customFetch]` option. This scopes the custom transport to that provider's
OAuth traffic.

```ts
NextAuth({
  providers: [GitHub({ [customFetch]: proxy })],
})
```

### Avoid redirect proxies with Apple

The Apple provider does not support Auth.js `RedirectProxyUrl`. A deployment
that otherwise uses a shared redirect proxy must choose another callback
strategy for Sign in with Apple.
