# Sessions, Cookies, and Request Security

## Database-free stateless authentication

Omitting `database` enables stateless session management. Access-token, account-info, and refresh-token endpoints remain usable, and account data can be deferred from persistence into a signed cookie.

```ts
export const auth = betterAuth({
  socialProviders: {
    google: { clientId, clientSecret },
  },
  account: { storeAccountCookie: true },
});

const accessToken = await authClient.getAccessToken();
const accountInfo = await authClient.accountInfo();
```

## Cookie-cache behavior

Session-store cookie cache uses JWE by default. Cookies are automatically chunked when they exceed a single-cookie limit.

`cookieCache.refreshCache: true` refreshes a stateless cookie after 80% of `maxAge`. The object form refreshes when `updateAge` seconds remain. Incrementing `cookieCache.version` invalidates all stateless sessions carrying an older version.

```ts
session: {
  cookieCache: {
    enabled: true,
    maxAge: 300,
    refreshCache: { updateAge: 60 },
    version: "2",
  },
}
```

The stateless cache `maxAge` follows session `expiresIn`, preventing cached data from outliving the session.

## Session freshness

`freshAge` is measured from session `createdAt`, not `updatedAt`. Refreshing cannot extend freshness indefinitely; sensitive operations may require reauthentication sooner than code based on refresh timestamps expects.

## Secondary-storage placement

Configuring secondary storage moves sessions there instead of the primary database by default. `storeSessionInDatabase` keeps them in the database as well. `preserveSessionInDatabase` retains database records after revocation.

```ts
secondaryStorage,
session: {
  storeSessionInDatabase: true,
  preserveSessionInDatabase: true,
}
```

Sessions read from secondary storage do not include `id`.

## Custom session fields

Fields returned by `customSession` are not written to cookie cache or secondary storage, so its callback runs on every fetch. Install the matching client plugin for type inference when the auth type can be imported.

```ts
plugins: [customSessionClient<typeof auth>()]
```

Custom additional session fields can be changed without reauthentication through `authClient.updateSession()`:

```ts
await authClient.updateSession({ theme: "dark", language: "en" });
```

Session refresh also supports read-replica-aware deferred refresh and per-request refresh skipping.

## Client refetch behavior

Client sessions can refetch by polling and on window focus. `disableSignal` turns off the client's default abort-signal behavior. Expo polling requires `expo-network`.

## Verification storage

Verification values may live only in secondary storage or be retained in the database too. Identifiers can be plain or hashed globally, with per-purpose overrides such as `email-verification` and `password-reset`.

```ts
verification: {
  storeIdentifier: "hashed",
  storeInDatabase: false,
}
```

## Durable and per-path rate limits

Rate-limit counters use process memory by default. Choose database, secondary, or custom storage in multi-instance deployments.

Rejected requests no longer consume quota. Default sign-in and sign-up limits are three requests per 10 seconds; password reset and OTP defaults are three per 60 seconds. Plugins can add rules.

`customRules` supports exact and wildcard paths, asynchronous limit functions, and `false` to exempt a path. A rejected request reports retry seconds through `X-Retry-After`.

```ts
rateLimit: {
  storage: "secondary-storage",
  customRules: {
    "/get-session": false,
    "/two-factor/*": async () => ({ window: 10, max: 3 }),
  },
}
```

IPv6 limiting can group clients by a configured subnet:

```ts
advanced: { ipAddress: { ipv6Subnet: 64 } }
```

## Secret rotation

An ordered `secrets` array encrypts new data with the first key and keeps older keys for decryption. This avoids forced invalidation during rotation.

```ts
secrets: [
  { version: 2, value: "new-secret-key-at-least-32-chars" },
  { version: 1, value: "old-secret-key-at-least-32-chars" },
]
```

The environment equivalent is:

```sh
BETTER_AUTH_SECRETS="2:new-secret,1:old-secret"
```

## CSRF and origin validation

CSRF and origin validation run as separate controls. `disableCSRFCheck` disables CSRF checks only. `disableOriginCheck` disables callback/redirect URL validation and, for backward compatibility, CSRF defenses too.

Cookie-less email sign-in and sign-up form navigations use Fetch Metadata to prevent cross-site first-login CSRF. Non-browser clients using cookies should send a valid `Origin` or `Referer`.

Wildcard entries are accepted in `trustedOrigins`. An asynchronous origin callback must handle an undefined request during initialization and direct `auth.api` use.

When `advanced.trustedProxyHeaders` derives base URL from `X-Forwarded-Host` and `X-Forwarded-Proto`, use it only behind a proxy that strips untrusted header values and retain an origin allowlist.

## Provider-token storage

Account access and refresh tokens are unencrypted by default. Enable built-in encryption:

```ts
account: { encryptOAuthTokens: true }
```

If custom cryptography is required, encrypt in an account `create.before` database hook and decrypt on read.

## Sensitive account operations

`verifyPassword` checks the current user's password without a new sign-in. User deletion is disabled by default and, once enabled, requires a valid password, fresh session, or email verification for passwordless accounts.

## Error-page behavior

The default API error page can be restyled or replaced with a custom path. Keep error responses enumeration-safe; for example, `/change-email` always acknowledges with `{ status: true }` without revealing address existence.
