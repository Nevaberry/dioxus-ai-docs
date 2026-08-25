# Sessions, Cookies, and Request Security

## Stateless and database-free sessions

Omitting `database` enables stateless session management (since 1.4.0). Access-token, account-info, and refresh-token endpoints remain available, and `account.storeAccountCookie` can defer account persistence into a signed cookie.

```ts
export const auth = betterAuth({
  socialProviders: { google: { clientId, clientSecret } },
  account: { storeAccountCookie: true },
});
```

Cookies are chunked automatically when needed, and the session-store cookie cache uses JWE by default. Client sessions can refetch by polling or on window focus; `disableSignal` turns off the client's default abort signal.

## Cookie cache refresh, invalidation, and freshness

`cookieCache.refreshCache: true` refreshes after 80% of `maxAge`; the object form refreshes when `updateAge` seconds remain. Increment `cookieCache.version` to invalidate every stateless session carrying an older value.

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

`freshAge` is measured from `createdAt`, not `updatedAt`, so refresh cannot keep a session fresh indefinitely (since 1.6.0). The stateless cache's `maxAge` follows session `expiresIn`.

## Secondary-storage placement

When secondary storage is configured, sessions live there rather than in the primary database by default. `storeSessionInDatabase` retains database storage; `preserveSessionInDatabase` keeps database records on revocation.

```ts
secondaryStorage,
session: {
  storeSessionInDatabase: true,
  preserveSessionInDatabase: true,
}
```

Sessions read from secondary storage do not contain `id` (since 1.5-guide). Fields from `customSession` bypass cookie and secondary caches, so its callback runs on every fetch; use `customSessionClient<typeof auth>()` for client inference when the server auth type is importable.

Custom additional session fields can be changed without reauthentication through `authClient.updateSession()`. Session refresh also supports read replicas, per-request refresh skipping, and deferred refresh work.

## Verification storage

Verification data can live only in secondary storage or be retained in the database. Identifiers can be plain or hashed globally, with per-purpose overrides such as `email-verification` and `password-reset` (since 1.5-guide).

```ts
verification: {
  storeIdentifier: "hashed",
  storeInDatabase: false,
}
```

## Rate limits

Rejected requests do not consume quota. Default sign-in/sign-up limits are three requests per 10 seconds; password-reset and OTP limits are three per 60 seconds. IPv6 addresses can be grouped through `advanced.ipAddress.ipv6Subnet`.

Counters use process memory by default. Select database, secondary, or custom storage for multi-instance deployments. `customRules` accepts exact or wildcard paths, async limit functions, and `false` exemptions; rejection reports retry seconds in `X-Retry-After`.

Plugins may contribute their own path rules, which are combined with the core limiter configuration.

```ts
rateLimit: {
  storage: "secondary-storage",
  customRules: {
    "/get-session": false,
    "/two-factor/*": async () => ({ window: 10, max: 3 }),
  },
}
```

## Secret rotation

Use an ordered `secrets` array so the first key encrypts new data while older keys remain available for decryption. The environment form is `BETTER_AUTH_SECRETS="2:new-secret,1:old-secret"` (since 1.5-guide).

```ts
secrets: [
  { version: 2, value: "new-secret-key-at-least-32-chars" },
  { version: 1, value: "old-secret-key-at-least-32-chars" },
]
```

## CSRF, origins, and proxy-derived URLs

CSRF and origin validation are independent (since 1.5.0). Cookie-less email sign-in/sign-up form navigations use Fetch Metadata against first-login CSRF; non-browser clients using cookies should send `Origin` or `Referer`.

`disableCSRFCheck` disables only CSRF defenses. `disableOriginCheck` also disables callback/redirect validation and, for compatibility, CSRF defenses. Wildcards are accepted in `trustedOrigins`.

When neither config nor environment supplies `baseURL`, `advanced.trustedProxyHeaders` derives it from `X-Forwarded-Host` and `X-Forwarded-Proto`. Enable this only behind a proxy that strips attacker-supplied values, and keep origins allowlisted. Async `trustedOrigins` must handle an undefined request during initialization and direct `auth.api` calls.

```ts
advanced: { trustedProxyHeaders: true },
trustedOrigins: async (request) =>
  request ? await queryTrustedDomains() : ["https://app.example.com"],
```

Alternatively, `baseURL` accepts an allowlisted dynamic configuration with `allowedHosts`, `fallback`, and `protocol`; server-side clients also fall back to `VERCEL_URL` and `NEXTAUTH_URL`.

## OAuth token storage

Provider access and refresh tokens are plaintext by default. Prefer `account.encryptOAuthTokens: true` for built-in encryption. A custom account `create.before` hook can instead encrypt on write when application-specific handling is needed; decrypt correspondingly on reads.

## API-key and bearer session safety

API-key validation consumes rate limits and optional budgets. Let configured API-key headers feed `getSession` once; manually calling `verifyApiKey` before `getSession` counts twice. API-key mock sessions were disabled by default in 1.4.0 and require explicit `enableSessionForAPIKeys`.

The bearer plugin authenticates with the session token returned in `set-auth-token`, not a JWT-plugin token. `requireSignature` defaults to false; enable it when unsigned bearer session tokens are unacceptable.
