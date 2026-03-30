# Configuration & Reference

## Secret Rotation with BETTER_AUTH_SECRETS

Use `BETTER_AUTH_SECRETS` (plural env var) to roll over to a new secret without invalidating existing encrypted data. Allows gradual secret rotation.

## onAPIError Configuration

```ts
export const auth = betterAuth({
  onAPIError: {
    throw: true,           // throw errors instead of returning error responses (default: false)
    onError: (error, ctx) => { console.error("Auth error:", error); },
    errorURL: "/auth/error",
    customizeDefaultErrorPage: {
      colors: { background: "#fff", primary: "#0070f3", destructive: "#ef4444" },
      disableTitleBorder: false,
      disableCornerDecorations: false,
      disableBackgroundGrid: false,
    },
  },
});
```

## trustedProxyHeaders

Derive `baseURL` per-request from reverse proxy headers instead of hardcoding:

```ts
export const auth = betterAuth({
  // Omit baseURL — derived from proxy headers per-request
  advanced: { trustedProxyHeaders: true },
  trustedOrigins: ["https://example.com", "https://app.example.dev"],
});
```

Resolution priority: static `baseURL` > env vars (`BETTER_AUTH_URL`) > `X-Forwarded-Host` + `X-Forwarded-Proto` > request URL. Only enable if the proxy sets these headers.

## disabledPaths

```ts
export const auth = betterAuth({
  disabledPaths: ["/sign-up/email", "/sign-in/email"],
});
```

## disableCSRFCheck vs disableOriginCheck

Two separate security options with a surprising overlap:
- `advanced.disableCSRFCheck: true` — disables CSRF protection only
- `advanced.disableOriginCheck: true` — disables URL validation **AND also disables CSRF protection**

There is no way to disable URL validation without also disabling CSRF.

## verification.storeIdentifier

Control how verification tokens/OTPs are stored:

```ts
export const auth = betterAuth({
  verification: {
    storeIdentifier: "hashed",  // "plain" | "hashed" | custom hasher
    // Or per-prefix:
    // storeIdentifier: { default: "plain", overrides: { "magic-link": "hashed" } },
    storeInDatabase: false,     // false = use secondaryStorage when available
  },
});
```

## Rate Limit Storage & IPv6 Subnets

```ts
export const auth = betterAuth({
  rateLimit: {
    storage: "database",       // or "secondary-storage" or default in-memory
    customRules: {
      "/sign-in/email": { window: 10, max: 3 },
      "/get-session": false,
    },
  },
  advanced: {
    ipAddress: {
      ipAddressHeaders: ["cf-connecting-ip"],
      ipv6Subnet: 64,
    },
  },
});
```

## Client: $ERROR_CODES and disableSignal

```ts
const authClient = createAuthClient();
// Type-safe error code map for i18n:
type ErrorTypes = Partial<Record<keyof typeof authClient.$ERROR_CODES, { en: string; es: string }>>;
// Prevent hook rerenders on specific calls:
await authClient.updateUser({ name: "New" }, { disableSignal: true });
```

## Dual Module Hazard ("No request state found" Error)

If `No request state found. Please make sure you are calling this function within a runWithRequestState callback` appears, there are multiple versions of `better-auth` or `better-call` in the dependency tree.

**Diagnose:**

```bash
pnpm why @better-auth/core && pnpm why better-call
```

**Fixes:**
1. **Next.js**: Add `serverExternalPackages: ['better-auth']` to `next.config.js`
2. **Cloudflare Workers**: Enable `nodejs_compat` in `wrangler.toml`
3. **Yarn v1 / pnpm v9**: Force single `better-call` resolution:
   ```json
   { "dependencies": { "better-call": "^1.1.8" }, "resolutions": { "better-call": "^1.1.8" } }
   ```
4. Always install `better-auth` in `dependencies`, not `devDependencies`

## Browser Extensions

```ts
export const auth = betterAuth({
  trustedOrigins: ["chrome-extension://YOUR_EXTENSION_ID"],
});
```
