# Providers and Authentication

## Contents

- [Database-backed account linking](#database-backed-account-linking)
- [Credentials failures](#credentials-failures)
- [Email providers](#email-providers)
- [Experimental passkeys](#experimental-passkeys)
- [OAuth provider customization](#oauth-provider-customization)
- [Apple and redirect proxies](#apple-and-redirect-proxies)

## Database-backed account linking

When a database and multiple authentication methods are configured, Auth.js attempts to link a later sign-in to existing `User` and `Account` records if the email matches.

Treat each enabled provider's email-verification behavior as part of the account-linking trust boundary. A provider that does not strongly establish email ownership can make an email match unsafe even when every other provider verifies email reliably.

Before adding an authentication method:

1. Determine whether and when it marks an email as verified.
2. Check whether attackers can choose or change the asserted email.
3. Exercise sign-in against an existing account with the same email.
4. Confirm that the resulting `User` and `Account` linkage matches the intended policy.

## Credentials failures

### Built-in pages

Return `null` from `authorize` to reject credentials. A built-in-page flow redirects with these query values:

```text
?error=CredentialsSignin&code=credentials
```

### Form actions and server-side handling

Expect the same rejection to surface as a thrown `CredentialsSignin` in a form action or custom server-side flow. Catch it at the application boundary and return or redirect with an appropriate response.

Subclass `CredentialsSignin` to replace the public `code`:

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

The code is visible in the URL. Use a generic value that does not reveal whether the username, password, account state, or another secret caused rejection.

## Email providers

All providers with `type: "email"` require a database adapter for the verification-token flow.

### Loops

Create a Loops transactional template before configuring the provider. The template must contain the case-sensitive `url` variable, which receives the magic link. Configure both credentials explicitly:

```ts
Loops({
  apiKey: process.env.AUTH_LOOPS_KEY,
  transactionalId: process.env.AUTH_LOOPS_TRANSACTIONAL_ID,
})
```

### Custom HTTP email service

Represent an arbitrary HTTP mail service as a raw email provider. `sendVerificationRequest` receives the recipient in `identifier` and the magic link in `url`.

```ts
NextAuth({
  adapter,
  providers: [
    {
      id: "http-email",
      name: "Email",
      type: "email",
      maxAge: 60 * 60 * 24,
      async sendVerificationRequest({ identifier, url }) {
        await sendMagicLinkOverHttp({ recipient: identifier, url })
      },
    },
  ],
})
```

Initiate sign-in with the provider's `id`, such as `http-email`.

## Experimental passkeys

Passkeys remain experimental. Require all of the following:

- Node.js 20 or later.
- A compatible database adapter.
- The adapter migration that adds an `Authenticator` table.
- `@simplewebauthn/server@9.0.3` as the server peer dependency.
- The singular `Passkey` provider.
- `experimental.enableWebAuthn: true`.

The known package floors are:

| Package | Floor |
| --- | --- |
| `next-auth` | `5.0.0-beta.17` |
| `@auth/sveltekit` | `1.0.2` |
| `@auth/prisma-adapter` | `1.3.3` |
| `@auth/unstorage-adapter` | `2.1.0` |
| `@auth/drizzle-adapter` | `1.1.1` |

Treat these as passkey feature floors, not recommended pins. Apply newer security floors too; in particular, use `@auth/sveltekit@1.11.1` or later to include the Nodemailer security fix.

Install and configure the server pieces:

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

The built-in sign-in page exposes the passkey action automatically after configuration.

### Custom passkey pages

Also install `@simplewebauthn/browser@9.0.1` and import the WebAuthn-specific helper:

```ts
import { signIn } from "next-auth/webauthn"
```

Let an authenticated user register another passkey with `action: "register"`. Let an unauthenticated user sign in without that option:

```ts
await signIn("passkey", { action: "register" })
await signIn("passkey")
```

## OAuth provider customization

### Persist custom fields

Return additional fields from an OAuth provider's `profile()` callback to persist them on `User`. Use its `account()` callback to add fields to, or omit unneeded fields from, the associated `Account` row.

Keep schema migrations synchronized with any new persisted fields.

### Override nested options

Options passed to a built-in OAuth provider are deeply merged with the provider defaults. Override only the nested value that needs to change:

```ts
Auth0({
  authorization: { params: { scope: "openid custom_scope" } },
})
```

### Set a provider-specific transport

Assign a fetch-compatible proxy or other custom transport to the symbol-keyed `[customFetch]` option. This confines the transport override to that provider's OAuth traffic.

```ts
NextAuth({
  providers: [GitHub({ [customFetch]: proxy })],
})
```

## Apple and redirect proxies

The Apple provider does not support Auth.js `RedirectProxyUrl`. If a deployment normally shares a redirect proxy across environments, use a different callback strategy for Sign in with Apple.
