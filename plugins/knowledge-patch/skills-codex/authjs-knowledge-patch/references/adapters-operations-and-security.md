# Adapters, Operations, and Security

## Adapter surface by authentication flow

A local adapter can implement only the methods and tables used by the enabled
flows. An adapter distributed as an official package must implement the entire
`Adapter` interface.

| Flow | Required methods |
| --- | --- |
| User and account management | `createUser`, `getUser`, `getUserByAccount`, `updateUser`, `linkAccount` |
| Database sessions | `createSession`, `getSessionAndUser`, `updateSession`, `deleteSession` |
| Passwordless email | `getUserByEmail`, `createVerificationToken`, `useVerificationToken` |

Auth.js does not currently invoke `deleteUser` or `unlinkAccount`, so do not
design a local authentication flow around those methods.

## Normalize arbitrary adapter values

Official adapters must accept user-supplied properties and convert
database-native values to plain JavaScript objects in both directions. Base
conversion on the runtime value type rather than a fixed list of field names;
custom models can introduce additional properties, including dates.

## Custom logger precedence

Providing custom `logger` handlers causes Auth.js to ignore the separate
`debug` option. Route debug output through `logger.debug`, together with the
warning and error handlers.

```ts
NextAuth({
  logger: {
    error: (code, ...message) => log.error(code, message),
    warn: (code, ...message) => log.warn(code, message),
    debug: (code, ...message) => log.debug(code, message),
  },
})
```

## Security and dependency floors

### SvelteKit and Nodemailer

Upgrade `@auth/sveltekit` releases older than `1.11.1` to `1.11.1` or later.
That release addresses a security issue inherited from `nodemailer`.

### NextAuth.js v4 and the GitHub issuer

GitHub OAuth callbacks now contain an `iss` parameter that `openid-client`
validates unconditionally. `next-auth@4.24.14` supplies the GitHub provider's
default issuer as `https://github.com/login/oauth`. Earlier releases without an
explicit issuer can therefore fail authentication. Upgrade or configure that
issuer explicitly.

### Kysely SQL-injection fix

Upgrade to `@auth/kysely-adapter@1.11.2` and ensure the installed Kysely package
satisfies its `kysely@^0.28.15` peer dependency. That floor addresses
CVE-2026-33468, an SQL-injection vulnerability, so upgrading only the adapter
without resolving the peer version is insufficient.

## Hardened request and OAuth behavior

These behaviors apply since 4.24.15.

### Treat malformed bearer values as unauthenticated

`getToken()` returns `null` instead of throwing when the `Authorization` header
contains a malformed Bearer value. Handle the result as an unauthenticated
request and do not depend on exception handling for this case.

### Bind OAuth check cookies to their provider

OAuth state, nonce, and PKCE check cookies are tied to the provider that
created them. Auth.js rejects a callback handled by a different provider.
Sign-ins already in flight during the upgrade fail once; a retry starts with
cookies in the new format and succeeds normally.

### Validate normalized email addresses

Email sign-in applies NFKC normalization before validating the address. This
prevents visually confusable Unicode forms of `@` from bypassing validation.

### Keep an explicit canonical URL authoritative

In trusted-host mode, an explicitly configured `NEXTAUTH_URL` takes precedence
over the auto-detected forwarded host. Keep the configured URL as the intended
canonical origin when forwarded-host information is present.

### Preserve CommonJS compatibility for uuid

The v4 line pins `uuid` to `^11.1.1`. This restores `require()` compatibility
on Node.js versions earlier than 20.19; `uuid` 14.x is ESM-only and broke those
CommonJS consumers.
