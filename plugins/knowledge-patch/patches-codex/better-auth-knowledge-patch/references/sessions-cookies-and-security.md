# Sessions, Cookies, and Request Security

## Database-free stateless authentication

Omitting `database` enables stateless session management. Access-token, account-info, and refresh-token endpoints remain available. `account.storeAccountCookie` can defer account persistence into a signed cookie.

```ts
export const auth = betterAuth({
  socialProviders: { google: { clientId, clientSecret } },
  account: { storeAccountCookie: true },
});

const accessToken = await authClient.getAccessToken();
const accountInfo = await authClient.accountInfo();
```

Cookies are chunked when necessary, and the session-store cookie cache uses JWE by default. Client sessions can refetch by polling or window focus; `disableSignal` disables the client's normal abort-signal behavior. The default API error page may be restyled or replaced with a custom path.

## Cookie-cache refresh and invalidation

`cookieCache.refreshCache: true` refreshes a stateless cookie after 80% of `maxAge`; the object form refreshes when `updateAge` seconds remain. Increment `cookieCache.version` to invalidate cookies carrying an older version.

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

The stateless cache's `maxAge` cannot outlive session `expiresIn`.

## Session freshness

`freshAge` is measured from `createdAt`, not `updatedAt`. Refreshing a session cannot keep it fresh indefinitely, so sensitive operations may require a new sign-in sooner than older refresh-based assumptions suggest.

## Secondary-storage placement

When secondary storage is configured, sessions live there instead of the primary database by default. Set `storeSessionInDatabase` to retain database-backed sessions and `preserveSessionInDatabase` to keep their rows when revoking sessions.

```ts
secondaryStorage,
session: {
  storeSessionInDatabase: true,
  preserveSessionInDatabase: true,
}
```

Sessions loaded from secondary storage do not contain `id`.

## Custom sessions

Fields produced by `customSession` are recomputed on every fetch and are not placed in cookie cache or secondary storage. Add the matching client plugin for type inference when the server auth type is importable.

```ts
plugins: [customSessionClient<typeof auth>()]
```

Additional session fields can be changed without reauthentication through `authClient.updateSession()`. Per-request refresh skipping and read-replica-aware deferred refresh are available for specialized data paths.

## Verification data

Verification values can be stored only in secondary storage or retained in the database. Identifiers may be plain or hashed globally, with per-purpose overrides such as `email-verification` and `password-reset`.

```ts
verification: {
  storeIdentifier: "hashed",
  storeInDatabase: false,
}
```

## Secret rotation

An ordered `secrets` array encrypts new data with the first key and keeps older keys available for decryption. This avoids invalidating all sessions or tokens during a rotation. The environment form is `BETTER_AUTH_SECRETS="2:new-secret,1:old-secret"`.

```ts
secrets: [
  { version: 2, value: "new-secret-key-at-least-32-chars" },
  { version: 1, value: "old-secret-key-at-least-32-chars" },
]
```

## OAuth-token storage

Provider access and refresh tokens are plain by default. Prefer the built-in database encryption setting:

```ts
export const auth = betterAuth({
  account: { encryptOAuthTokens: true },
});
```

For a custom encryption scheme, transform tokens in an account `create.before` hook and decrypt them on reads. Do not assume a post-commit `after` hook can provide atomic encryption.

## Rate limits

Rejected requests do not consume quota. Default sign-in/sign-up limits are three requests per 10 seconds; password-reset and OTP defaults are three per 60 seconds. Plugins may contribute rules, and `advanced.ipAddress.ipv6Subnet` groups IPv6 addresses.

Counters use process memory by default. Choose database, secondary, or custom storage for durable multi-instance limits. `customRules` supports exact and wildcard paths, asynchronous limit functions, and `false` to exempt a path. Rejections provide retry seconds in `X-Retry-After`.

```ts
rateLimit: {
  storage: "secondary-storage",
  customRules: {
    "/get-session": false,
    "/two-factor/*": async () => ({ window: 10, max: 3 }),
  },
},
advanced: { ipAddress: { ipv6Subnet: 64 } },
```

## CSRF and origin checks

CSRF and origin validation are independent. `disableCSRFCheck` disables only CSRF defenses. `disableOriginCheck` additionally disables callback/redirect URL validation and, for compatibility, CSRF defenses too.

Cookie-less email sign-in/sign-up form navigations use Fetch Metadata to prevent first-login CSRF. Non-browser clients that use cookies should send an appropriate `Origin` or `Referer`.

Wildcard entries are accepted in `trustedOrigins`. An asynchronous origins callback must handle an undefined request during initialization and direct `auth.api` calls.

```ts
trustedOrigins: async (request) =>
  request ? await queryTrustedDomains() : ["https://app.example.com"]
```

## Proxies and request-derived URLs

`baseURL` can be an allowlisted dynamic object for previews, proxies, and multiple domains. Without an explicit value, server clients also fall back to `VERCEL_URL` and `NEXTAUTH_URL`.

```ts
baseURL: {
  allowedHosts: ["myapp.com", "*.vercel.app", "preview-*.myapp.com"],
  fallback: "https://myapp.com",
  protocol: "auto",
}
```

When no configured or environment URL exists, `advanced.trustedProxyHeaders` derives a base URL from `X-Forwarded-Host` and `X-Forwarded-Proto`. Enable it only behind a proxy that strips attacker-supplied forwarded headers, and retain a `trustedOrigins` allowlist.

## Client IP and request controls

Server-side client IP detection is automatic. Never accept a remote IP from a client-controlled header unless the trusted proxy chain normalizes it. Request validation may treat CSRF, origin, callback, and redirect checks as separate policy decisions.
