# Adapters, Operations, and Security

## Contents

- [Adapter surface by authentication flow](#adapter-surface-by-authentication-flow)
- [Normalize adapter values](#normalize-adapter-values)
- [Custom logging](#custom-logging)
- [Security and compatibility upgrades](#security-and-compatibility-upgrades)

## Adapter surface by authentication flow

A local adapter only needs the methods and tables exercised by enabled flows. An adapter distributed as an official package must implement the entire `Adapter` interface.

### User and account management

Implement:

- `createUser`
- `getUser`
- `getUserByAccount`
- `updateUser`
- `linkAccount`

### Database sessions

Also implement:

- `createSession`
- `getSessionAndUser`
- `updateSession`
- `deleteSession`

### Passwordless email

Also implement:

- `getUserByEmail`
- `createVerificationToken`
- `useVerificationToken`

Auth.js does not currently invoke `deleteUser` or `unlinkAccount`. Do not assume those methods participate in a local authentication flow merely because the interface defines them.

## Normalize adapter values

Official adapters must accept arbitrary user-supplied properties and translate database-native values to and from plain JavaScript objects.

Base conversion on runtime value type, not a fixed list of field names. Custom models may add fields containing dates or other database-native values, and those fields require the same normalization as built-in fields.

Apply normalization in both directions:

1. Convert plain input values into the database representation before persistence.
2. Convert database results back into plain JavaScript objects before returning them.

## Custom logging

Supplying custom `logger` handlers causes Auth.js to ignore the separate `debug` option. Handle debug output in the custom logger together with warnings and errors:

```ts
NextAuth({
  logger: {
    error: (code, ...message) => log.error(code, message),
    warn: (code, ...message) => log.warn(code, message),
    debug: (code, ...message) => log.debug(code, message),
  },
})
```

## Security and compatibility upgrades

### SvelteKit and Nodemailer

Upgrade `@auth/sveltekit` to `1.11.1` or later. Version `1.11.1` addresses a security issue inherited from Nodemailer.

### NextAuth.js v4 and GitHub issuer validation

Upgrade `next-auth` v4 applications using GitHub to `4.24.14`, or explicitly configure the issuer as `https://github.com/login/oauth`.

GitHub OAuth callbacks include an `iss` parameter that `openid-client` validates unconditionally. Earlier `next-auth` releases without an explicitly configured issuer can therefore fail authentication. Version `4.24.14` supplies the GitHub provider's issuer by default.

### Kysely adapter dependency floor

Upgrade `@auth/kysely-adapter` to `1.11.2` and ensure the installed `kysely` satisfies `^0.28.15`.

The raised peer-dependency floor addresses CVE-2026-33468, an SQL-injection vulnerability. Upgrading the adapter without resolving its peer dependency does not guarantee the fixed Kysely version is installed.
