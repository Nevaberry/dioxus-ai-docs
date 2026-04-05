# Breaking Changes & New Features (v1.5)

## i18n Plugin (`@better-auth/i18n`)

Type-safe error message translations with automatic locale detection:

```ts
import { i18n } from "@better-auth/i18n";

export const auth = betterAuth({
  plugins: [
    i18n({
      defaultLocale: "en",
      detection: ["header", "cookie"],
      translations: {
        en: { USER_NOT_FOUND: "User not found" },
        fr: { USER_NOT_FOUND: "Utilisateur non trouvé" },
        es: { USER_NOT_FOUND: "Usuario no encontrado" },
      },
    }),
  ],
});
```

Error codes are fully typed — IDE autocompletes all available error codes from every registered plugin.

## Typed Error Codes (`defineErrorCodes` + `APIError.from()`)

Every error response now includes a machine-readable `code` field:

```ts
import { defineErrorCodes } from "@better-auth/core/utils/error-codes";
import { APIError } from "@better-auth/core/error";

export const MY_ERROR_CODES = defineErrorCodes({
  USER_NOT_FOUND: "User not found",
  INVALID_TOKEN: "The provided token is invalid",
});

throw APIError.from("BAD_REQUEST", MY_ERROR_CODES.USER_NOT_FOUND);
```

Response shape: `{ "code": "USER_NOT_FOUND", "message": "User not found" }`.

## SSO: SAML Single Logout (SLO) & Production Hardening

v1.5 adds SP-initiated and IdP-initiated SAML Single Logout:

```ts
import { sso } from "@better-auth/sso";
sso({
  saml: {
    enableSingleLogout: true,
    wantLogoutRequestSigned: true,
    wantLogoutResponseSigned: true,
  },
})
```

Additional SSO improvements:
- Signed SAML AuthnRequests with configurable signature/digest algorithms
- Multi-domain providers (bind SSO providers to multiple domains)
- InResponseTo validation (prevent SAML replay attacks)
- Algorithm restrictions (block deprecated signature/digest algorithms)
- Clock skew tolerance for SAML timestamp validation
- OIDC ID token `aud` claim validation
- Provider CRUD endpoints (list, get, update, delete SSO providers via API)
- Shared OIDC redirect URI for all OIDC providers

## Stripe: Per-Seat Billing (`seatPriceId`)

```ts
stripe({
  stripeClient,
  stripeWebhookSecret: "whsec_...",
  subscription: {
    enabled: true,
    plans: [
      {
        name: "team",
        priceId: "price_base_monthly",
        seatPriceId: "price_per_seat",
      },
    ],
  },
  organization: { enabled: true },
})
```

Member changes auto-sync seat quantity. Also adds `lineItems` for usage-based billing.

## API Key Plugin Moved to `@better-auth/api-key`

```ts
// Before:
import { apiKey } from "better-auth/plugins";
// After:
import { apiKey } from "@better-auth/api-key";
```

Schema changes: `userId` → `referenceId`, new `configId` field.

## Deprecated API Removals

| Removed | Replacement |
|---------|-------------|
| `createAdapter` | `createAdapterFactory` |
| `Adapter` type | `DBAdapter` |
| `onEmailVerification` | `afterEmailVerification` |
| `sendChangeEmailVerification` | `sendChangeEmailConfirmation` |
| `advanced.database.useNumberId` | `advanced.database.generateId: "serial"` |
| Organization `permission` field | `permissions` (plural) |
| `InferUser<O>` / `InferSession<O>` | `User<...>` / `Session<...>` from `"better-auth"` |
| `getMigrations` from `"better-auth"` | `"better-auth/db/migration"` |
| `@better-auth/core/utils` barrel | Individual subpaths (`/utils/id`, `/utils/json`, `/utils/error-codes`) |
| `better-auth/adapters/test` | `@better-auth/test-utils/adapter` |

## Plugin Type System Changes

`BetterAuthPluginRegistry` for typed `getPlugin()` / `hasPlugin()`:

```ts
declare module "@better-auth/core" {
  interface BetterAuthPluginRegistry<AuthOptions, Options> {
    "my-plugin": { creator: typeof myPlugin };
  }
}
const otherPlugin = ctx.getPlugin("my-plugin"); // typed return
const hasIt = ctx.hasPlugin("my-plugin"); // narrows to true
```

After hooks (`create.after`, `update.after`, `delete.after`) now run **after** transaction commits, not during. Plugin `init()` context is mutable and can inject custom values.

## CLI: `upgrade` Command and `--adapter` Flag

```bash
npx auth upgrade                   # upgrade all better-auth packages
npx auth generate --adapter prisma # generate schema for specific adapter without full config
npx auth generate --adapter drizzle
```

## Update Session Endpoint

New `/update-session` endpoint for updating custom additional session fields:

```ts
await authClient.updateSession({ theme: "dark", language: "en" });
```

## Experimental OpenTelemetry

```ts
export const auth = betterAuth({ experimental: { opentelemetry: true } });
```
