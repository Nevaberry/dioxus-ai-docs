# Providers and Authentication

## Database-backed account linking

When a database and multiple authentication methods are configured, Auth.js attempts to link a later sign-in to existing `User` and `Account` records when the email matches. The email-verification guarantee of every enabled provider therefore affects account-linking security.

Before adding a provider, determine how it verifies and reports email ownership. Do not treat equal email strings by themselves as sufficient proof that two provider accounts share an owner.

## Credentials failures

### Built-in page flow

When `authorize` returns `null`, the built-in-page flow redirects with:

```text
?error=CredentialsSignin&code=credentials
```

The `code` is URL-visible. Override it with a `CredentialsSignin` subclass when the default public code is not appropriate.

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

### Form actions and custom server flows

In a form action or custom server-side invocation, the same failed authorization is delivered as a thrown `CredentialsSignin`. Catch that error at the server boundary rather than expecting the redirect response used by the built-in page.

## Email providers

Every email-type provider requires a database adapter for its verification-token flow.

### Loops magic links

Create the Loops transactional template before enabling the provider. The template must use the case-sensitive `url` variable for the magic link. Configure both the API key and transactional-template ID.

```ts
Loops({
  apiKey: process.env.AUTH_LOOPS_KEY,
  transactionalId: process.env.AUTH_LOOPS_TRANSACTIONAL_ID,
})
```

### Custom HTTP email service

Represent an arbitrary HTTP mail service as a raw provider with `type: "email"`. Implement `sendVerificationRequest`; its callback receives the recipient as `identifier` and the magic link as `url`. Start sign-in with the provider's configured `id`.

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

Passkey support is experimental. It requires all of the following:

- Node.js 20 or later.
- A compatible database adapter and its migration adding an `Authenticator` table.
- `@simplewebauthn/server@9.0.3`.
- The singular `Passkey` provider.
- `experimental.enableWebAuthn: true`.

The applicable Auth.js package floors are:

| Package | Minimum version |
| --- | --- |
| `next-auth` | `5.0.0-beta.17` |
| `@auth/sveltekit` | `1.0.2` |
| `@auth/prisma-adapter` | `1.3.3` |
| `@auth/unstorage-adapter` | `2.1.0` |
| `@auth/drizzle-adapter` | `1.1.1` |

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

The built-in sign-in page exposes the passkey action when the provider is configured.

### Custom passkey pages

Custom pages additionally require `@simplewebauthn/browser@9.0.1`. Import the WebAuthn-specific `signIn` function from `next-auth/webauthn`.

```ts
import { signIn } from "next-auth/webauthn"

await signIn("passkey", { action: "register" })
await signIn("passkey")
```

Use `action: "register"` only when an authenticated user is adding a passkey. Omit the action when an unauthenticated user signs in.

## OAuth provider customization

### Persist additional fields

Return additional fields from `profile()` to persist them on the provider's `User`. Use `account()` to add fields to, or omit unneeded fields from, the associated `Account` row.

### Deep-merge built-in options

Auth.js deep-merges options passed to a built-in OAuth provider with that provider's defaults. Override only the required nested value.

```ts
Auth0({
  authorization: { params: { scope: "openid custom_scope" } },
})
```

### Scope a custom fetch to one provider

Assign a fetch-compatible proxy or other transport to the provider's symbol-keyed `[customFetch]` option. OAuth traffic for that provider uses the custom transport without changing other providers.

```ts
NextAuth({
  providers: [GitHub({ [customFetch]: proxy })],
})
```

### Apple redirect proxies

The Apple provider does not support Auth.js `RedirectProxyUrl`. A deployment that relies on a shared redirect proxy must use another callback strategy for Sign in with Apple.
