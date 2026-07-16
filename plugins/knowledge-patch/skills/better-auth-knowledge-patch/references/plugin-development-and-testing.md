# Plugin Development and Testing

## Unified request hooks

Global and plugin before/after hooks use the same `AuthMiddleware` abstraction. Global handlers may be declared directly; plugin hooks remain matcher/handler entries. After middleware reads the response from `ctx.context.returned`.

```ts
import { createAuthMiddleware } from "better-auth/api";

hooks: {
  before: createAuthMiddleware(async (ctx) => console.log(ctx.path)),
  after: createAuthMiddleware(async (ctx) =>
    console.log(ctx.context.returned)),
}
```

Plugin form:

```ts
const plugin = {
  id: "example",
  hooks: {
    before: [{
      matcher: (ctx) => ctx.path.startsWith("/example"),
      handler: createAuthMiddleware(async (ctx) => {
        // Inspect or replace request behavior.
      }),
    }],
  },
} satisfies BetterAuthPlugin;
```

## Plugin context and registry typing

`PluginContext<Options>` is generic. A plugin may augment `BetterAuthPluginRegistry`, allowing `getPlugin()` and `hasPlugin()` to infer registered plugin types.

`init()` receives the same mutable context object used by the full auth lifecycle. It may return arbitrary context keys for other plugins.

`AuthContext` exposes the running Better Auth version for compatibility checks and diagnostics.

## Error codes

A plugin `$ERROR_CODES` property expects `Record<string, RawError>`, not a string map. Assign the result of `defineErrorCodes()`.

```ts
$ERROR_CODES: defineErrorCodes({
  MY_ERROR: "My error message",
})
```

`defineErrorCodes()` produces `{ code, message }` values accepted by `APIError.from()`. Auth error responses carry machine-readable `code` fields.

## Database hooks and transaction timing

Database `create.after`, `update.after`, and `delete.after` hooks run after the transaction commits. They cannot provide atomic follow-up writes. Put such writes in the adapter during the main operation.

For OAuth token encryption implemented manually, use an account `create.before` hook, which can replace the data before persistence:

```ts
databaseHooks: {
  account: {
    create: {
      before(account) {
        const data = { ...account };
        if (data.accessToken) data.accessToken = encrypt(data.accessToken);
        if (data.refreshToken) data.refreshToken = encrypt(data.refreshToken);
        return { data };
      },
    },
  },
}
```

Prefer `account.encryptOAuthTokens: true` when custom handling is unnecessary.

## Adapter factories and schema generation

`createAdapter` is removed; use `createAdapterFactory`. Custom adapters can expose `createSchema` so the CLI can generate their schema.

Case-insensitive comparison is portable across adapters through `mode: "insensitive"` on an individual `where` clause.

```ts
await adapter.findOne({
  model: "user",
  where: [{ field: "email", value: email, mode: "insensitive" }],
});
```

`getMigrations` is exported from `better-auth/db/migration`, not from the package root.

## Auth test utilities

The `testUtils` plugin exposes user factories, persistence helpers, login headers, sessions, tokens, and optional OTP capture through `auth.$context.test` for integration and end-to-end tests.

```ts
plugins: [testUtils({ captureOTP: true })]

const test = (await auth.$context).test;
const user = await test.saveUser(
  test.createUser({ email: "test@example.com" }),
);
const { headers, session, token } = await test.login({ userId: user.id });
const otp = test.getOTP(user.email);
```

For adapter suites, import `testAdapter` and `createTestSuite` from `@better-auth/test-utils/adapter`. The old `better-auth/adapters/test` path is removed.

## OpenAPI reference generation

`openAPI()` serves a Scalar reference at `/api/auth/reference` with core and plugin endpoints.

Generate the schema in code with:

```ts
const schema = await auth.api.generateOpenAPISchema();
```

It is also exposed at `/api/auth/open-api/generate-schema` as an additional Scalar source. `disableDefaultReference` hides the default reference UI while preserving the schema endpoint.

## Plugin-contributed rate limits

Plugins may contribute rate-limit rules. Rejected requests do not consume quota. Use exact or wildcard paths, asynchronous rule functions, and `false` exemptions consistently with global `customRules`.

## Server/client type pairing

When a plugin has a client companion, install the matching client plugin so endpoint and additional-field inference works. Examples include organization, dynamic organization roles, custom sessions, Sentinel challenges, API keys, and Electron.
