# Adapters, Operations, and Security

## Adapter surface by authentication flow

A local adapter may implement only the methods and tables exercised by enabled flows. An adapter distributed as an official package must implement the complete `Adapter` interface.

| Enabled flow | Required methods |
| --- | --- |
| User and account management | `createUser`, `getUser`, `getUserByAccount`, `updateUser`, `linkAccount` |
| Database sessions | `createSession`, `getSessionAndUser`, `updateSession`, `deleteSession` |
| Passwordless email | `getUserByEmail`, `createVerificationToken`, `useVerificationToken` |

Auth.js does not currently invoke `deleteUser` or `unlinkAccount`; do not design a local authentication flow around those methods being called.

## Normalize adapter values

Official adapters must accept arbitrary user-supplied properties and convert database-native values to plain JavaScript objects in both directions. Base conversion on value type rather than a list of known field names. Custom models can introduce more fields that need conversion, including dates.

## Custom logger precedence

Supplying custom `logger` handlers makes the separate `debug` option ineffective. Route debug output through `logger.debug` alongside warning and error output.

```ts
NextAuth({
  logger: {
    error: (code, ...message) => log.error(code, message),
    warn: (code, ...message) => log.warn(code, message),
    debug: (code, ...message) => log.debug(code, message),
  },
})
```

## Security and compatibility floors

### SvelteKit Nodemailer update

Upgrade `@auth/sveltekit` to `1.11.1` or later. That release addresses a security issue inherited from `nodemailer`.

### NextAuth.js v4 GitHub issuer

GitHub OAuth callbacks include an `iss` parameter that `openid-client` validates unconditionally. Earlier applications without an explicitly configured issuer can therefore fail authentication. `next-auth@4.24.14` sets the GitHub provider's default issuer to `https://github.com/login/oauth`; either upgrade to that release or later, or configure the issuer explicitly.

### Kysely adapter SQL-injection floor

Upgrade `@auth/kysely-adapter` to `1.11.2` and ensure the installed peer is `kysely@^0.28.15`. The raised peer floor addresses CVE-2026-33468, an SQL-injection vulnerability.

## v4.24.15 authentication hardening and compatibility

### Malformed Bearer tokens

`getToken()` returns `null` when the `Authorization` header contains a malformed Bearer value (since 4.24.15). Treat the result as unauthenticated; do not depend on exception handling for this case.

### Provider-bound OAuth check cookies

OAuth state, nonce, and PKCE check cookies are bound to the provider that created them (since 4.24.15). A callback handled by another provider is rejected. A sign-in already in flight when an upgrade is deployed can fail once, then succeed when the user retries.

### Unicode-normalized email validation

Email sign-in applies NFKC normalization before validating an address (since 4.24.15). This prevents homoglyph forms of `@` from bypassing validation.

### Explicit `NEXTAUTH_URL` precedence

In trusted-host mode, an explicit `NEXTAUTH_URL` takes precedence over the auto-detected forwarded host (since 4.24.15). Treat the configured URL as authoritative even when forwarded-host information is present.

### CommonJS-compatible `uuid`

The v4 line pins `uuid` to `^11.1.1` (since 4.24.15). This restores `require()` compatibility on Node.js versions earlier than 20.19; `uuid` 14.x is ESM-only and breaks those CommonJS consumers.
