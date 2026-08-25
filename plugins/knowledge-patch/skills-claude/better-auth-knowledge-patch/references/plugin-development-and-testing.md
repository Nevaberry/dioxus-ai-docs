# Plugin Development and Testing

## Unified request middleware

Global and plugin hooks use the `AuthMiddleware` abstraction (since 1.5-guide). Global handlers may be direct middleware; plugin hooks remain matcher/handler entries. After middleware reads the result from `ctx.context.returned`.

```ts
import { createAuthMiddleware } from "better-auth/api";

hooks: {
  before: createAuthMiddleware(async (ctx) => inspect(ctx.path)),
  after: createAuthMiddleware(async (ctx) => inspect(ctx.context.returned)),
}
```

## Plugin context and lifecycle

`PluginContext<Options>` is generic. Plugins can augment `BetterAuthPluginRegistry` so `getPlugin()` and `hasPlugin()` infer registered types. `init()` receives the same mutable context reference used throughout the auth lifecycle and may return arbitrary context keys for other plugins.

`AuthContext.version` exposes the running Better Auth version for compatibility checks and diagnostics (since 1.5.0).

## Error codes and localization

Plugin `$ERROR_CODES` is `Record<string, RawError>`, not a string map. Use the object returned by `defineErrorCodes()`; errors include a machine-readable `code`, and `APIError.from()` accepts the resulting `{ code, message }`.

```ts
$ERROR_CODES: defineErrorCodes({
  MY_ERROR: "My error message",
})
```

`@better-auth/i18n` provides typed translations and locale detection from headers, cookies, or sessions.

```ts
i18n({
  defaultLocale: "en",
  detection: ["header", "cookie"],
  translations: {
    en: { USER_NOT_FOUND: "User not found" },
    fr: { USER_NOT_FOUND: "Utilisateur introuvable" },
  },
})
```

## Adapter predicates and IDs

Any adapter can perform a case-insensitive string comparison by adding `mode: "insensitive"` to an individual `where` clause (since 1.6.0).

```ts
await adapter.findOne({
  model: "user",
  where: [{
    field: "email",
    value: "user@example.com",
    mode: "insensitive",
  }],
});
```

`advanced.database.generateId` callbacks may return `false` or `undefined` for a model to let the database generate that ID.

## Background work

`ctx.context.runInBackground()` is fire-and-forget. `runInBackgroundOrAwait()` delegates to the configured handler but awaits when there is none, which suits work that must complete, such as required email delivery.

```ts
hooks: {
  after: createAuthMiddleware(async (ctx) => {
    ctx.context.runInBackground(sendAnalytics());
    await ctx.context.runInBackgroundOrAwait(sendRequiredEmail());
  }),
}
```

Connect serverless lifetime primitives through `advanced.backgroundTasks.handler`. Once configured, deferred writes are eventually consistent because the response may return first.

## Auth test utilities

`testUtils` exposes factories, persistence helpers, login headers/sessions/tokens, and optional OTP capture through `auth.$context.test`.

```ts
plugins: [testUtils({ captureOTP: true })]

const test = (await auth.$context).test;
const user = await test.saveUser(test.createUser({ email: "test@example.com" }));
const { headers, session, token } = await test.login({ userId: user.id });
const otp = test.getOTP(user.email);
```

Adapter suites come from `@better-auth/test-utils/adapter`, not the removed `better-auth/adapters/test`.

## OpenAPI reference

`openAPI()` serves Scalar at `/api/auth/reference` and includes core and plugin endpoints. Generate the schema directly with `await auth.api.generateOpenAPISchema()` or fetch `/api/auth/open-api/generate-schema`. `disableDefaultReference` removes only the default reference UI and retains the schema route.

## Custom OAuth state

Social sign-in `additionalData` survives the OAuth redirect. Read it in hooks, middleware, or endpoints with `getOAuthState<T>()` (since 1.4.0).

```ts
await authClient.signIn.social({
  provider: "google",
  additionalData: { referralCode: "ABC123", source: "landing-page" },
});
```

## Custom adapter schema

The CLI can call a custom adapter's `createSchema`, and Better Auth's schema definitions use Zod 4 (since 1.3.0).
