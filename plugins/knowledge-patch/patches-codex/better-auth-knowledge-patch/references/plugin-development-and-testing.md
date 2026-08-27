# Plugin Development and Testing

## Unified request middleware

Global before/after hooks and plugin hooks use `AuthMiddleware`. Global hooks can be direct middleware; plugin hooks remain matcher/handler entries. After middleware reads the returned response from `ctx.context.returned`.

```ts
import { createAuthMiddleware } from "better-auth/api";

hooks: {
  before: createAuthMiddleware(async (ctx) => {
    console.log(ctx.path);
  }),
  after: createAuthMiddleware(async (ctx) => {
    console.log(ctx.context.returned);
  }),
}
```

Callbacks in email OTP, magic-link, phone-number, and organization plugins that formerly received `request` now receive `ctx`; access the request as `ctx.request`. See the migration reference for the exact callback set.

## Plugin context and registry

`PluginContext<Options>` is generic. Plugins may augment `BetterAuthPluginRegistry`, allowing `getPlugin()` and `hasPlugin()` to infer registered plugin types. A plugin `init()` receives the same mutable context used throughout the auth lifecycle and may return arbitrary context keys for other plugins.

`AuthContext` exposes the runtime Better Auth version for compatibility checks and diagnostics. Use the `AuthClient` helper for client typing and `inferAuth` when types should be inferred from the auth instance.

## Error codes

Plugin `$ERROR_CODES` expects `Record<string, RawError>`, not a plain string map. `defineErrorCodes()` creates `{ code, message }` values accepted by `APIError.from()`. Error responses contain a machine-readable `code`.

```ts
$ERROR_CODES: defineErrorCodes({
  MY_ERROR: "My error message",
})
```

`@better-auth/i18n` supplies typed translations and locale detection through headers, cookies, or sessions.

```ts
plugins: [i18n({
  defaultLocale: "en",
  detection: ["header", "cookie"],
  translations: {
    en: { USER_NOT_FOUND: "User not found" },
    fr: { USER_NOT_FOUND: "Utilisateur introuvable" },
  },
})]
```

## Adapter operations

Create adapters with `createAdapterFactory`; `createAdapter` is removed. Individual adapter predicates accept `mode: "insensitive"` for case-insensitive string matching.

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

Database `create.after`, `update.after`, and `delete.after` hooks run after transaction commit. Place atomic follow-up changes inside the original adapter operation or transaction.

## Background work

`ctx.context.runInBackground()` schedules fire-and-forget work after the response. `runInBackgroundOrAwait()` also uses a configured handler, but awaits when no handler exists; use it for work that must complete, such as required email delivery.

```ts
hooks: {
  after: createAuthMiddleware(async (ctx) => {
    ctx.context.runInBackground(sendAnalytics());
    await ctx.context.runInBackgroundOrAwait(sendRequiredEmail());
  }),
}
```

A platform handler under `advanced.backgroundTasks.handler` changes deferred writes to eventual consistency. Plugin behavior that relies on immediately visible data must account for that.

## Test utilities

The `testUtils` plugin exposes factories, persistence helpers, login headers, sessions, tokens, and optional OTP capture at `auth.$context.test` for integration and end-to-end tests.

```ts
plugins: [testUtils({ captureOTP: true })]

const test = (await auth.$context).test;
const user = await test.saveUser(
  test.createUser({ email: "test@example.com" }),
);
const { headers, session, token } = await test.login({ userId: user.id });
const otp = test.getOTP(user.email);
```

Adapter authors import `testAdapter` and `createTestSuite` from `@better-auth/test-utils/adapter`; the former `better-auth/adapters/test` export is removed.

## Generated OpenAPI

The `openAPI()` plugin serves a Scalar reference at `/api/auth/reference`, including core and plugin endpoints. Generate the schema directly with `await auth.api.generateOpenAPISchema()` or through `/api/auth/open-api/generate-schema`. `disableDefaultReference` removes the UI route while retaining the schema endpoint.

## Custom admin roles

Defining custom `admin` or `user` roles replaces that role's built-in permissions. Merge `defaultStatements` and `adminAc.statements` to retain them, and pass the same access controller and roles to server and client plugins.

```ts
const ac = createAccessControl({
  ...defaultStatements,
  project: ["create"],
} as const);
const adminRole = ac.newRole({
  ...adminAc.statements,
  project: ["create"],
});
```

`checkRolePermission` checks a role definition synchronously, not the signed-in user. Use client `hasPermission` or server `userHasPermission` for user authorization. The admin plugin can create users with optional passwords when configured.
