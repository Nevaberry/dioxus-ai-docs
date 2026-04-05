# Core Plugins (2FA, Passkey, Bearer, JWT, etc.)

## 2FA: Passwordless Users & Server-Side Flow

The `allowPasswordless` option lets OAuth/passkey/magic-link users enable 2FA without a password:

```ts
twoFactor({ allowPasswordless: true })
```

Server-side 2FA flow requires checking `twoFactorRedirect` with `in` operator (not inferred in TS) and forwarding cookies:

```ts
const { headers: responseHeaders, response } = await auth.api.signInEmail({
  returnHeaders: true,
  body: { email: "test@test.com", password: "test" },
});
if ("twoFactorRedirect" in response) {
  // Forward responseHeaders cookies into next auth.api 2FA call
}
```

2FA OTP and backup codes support encrypted/hashed storage:

```ts
twoFactor({
  otpOptions: {
    storeOTP: "encrypted", // "plain" | "encrypted" | "hashed" | custom encryptor
    sendOTP: async ({ user, otp }, ctx) => { /* send */ },
  },
  backupCodes: {
    storeBackupCodes: "encrypted", // "plain" | "encrypted" | custom encryptor
  },
  twoFactorPage: "/auth/two-factor", // custom 2FA redirect page
})
```

## Admin: Custom Access Control System

Define typed permissions with `createAccessControl` from `better-auth/plugins/access` (separate import for bundle size):

```ts
import { createAccessControl } from "better-auth/plugins/access";
import { defaultStatements, adminAc } from "better-auth/plugins/admin/access";

const statement = {
  ...defaultStatements,
  project: ["create", "share", "update", "delete"],
} as const; // `as const` required for type inference

const ac = createAccessControl(statement);
const admin = ac.newRole({
  project: ["create", "update"],
  ...adminAc.statements,
});
const editor = ac.newRole({ project: ["create", "update"] });

// Server: admin({ ac, roles: { admin, editor } })
// Client: adminClient({ ac, roles: { admin, editor } })
```

Permission checks — server-side async and client-side sync:

```ts
// Server: checks user's actual role in DB
await auth.api.userHasPermission({
  body: { userId: "id", permissions: { project: ["create"] } },
});
// Or check role directly (no DB query):
await auth.api.userHasPermission({
  body: { role: "admin", permissions: { project: ["create"] } },
});

// Client: async (checks current user)
await authClient.admin.hasPermission({ permissions: { project: ["create"] } });
// Client: sync (checks role definition, no server call)
authClient.admin.checkRolePermission({
  role: "admin",
  permissions: { project: ["create"] },
});
```

## Passkey: Pre-Auth Registration & WebAuthn Extensions

Passkey-first registration without requiring a session:

```ts
// Server
passkey({
  registration: {
    requireSession: false,
    resolveUser: async ({ ctx, context }) => {
      return { id: "user-id", name: "user@example.com" };
    },
    extensions: { credProps: true },
  },
})

// Client
await authClient.passkey.addPasskey({
  name: "Primary passkey",
  context: "signed-registration-token",
  extensions: { credProps: true },
  returnWebAuthnResponse: true,
});
```

Expo passkeys require matching cookie prefixes:

```ts
// Server: passkey({ advanced: { webAuthnChallengeCookie: "my-app-passkey" } })
// Client: expoClient({ storage: SecureStore, cookiePrefix: "my-app" })
```

## Bearer: Token Retrieval & Client Config

The bearer plugin returns tokens via `set-auth-token` response header:

```ts
const authToken = ctx.response.headers.get("set-auth-token");

const authClient = createAuthClient({
  fetchOptions: {
    auth: {
      type: "Bearer",
      token: () => localStorage.getItem("bearer_token") || "",
    },
  },
});
```

`requireSignature` option forces token signing.

## JWT: JWKS Endpoints, Key Rotation & Custom Signing

Import from `better-auth/plugins`:

```ts
import { jwt } from "better-auth/plugins";
import { jwtClient } from "better-auth/client/plugins";
```

Three ways to retrieve JWTs:

1. `await authClient.token()` — client plugin method
2. `GET /api/auth/token` — direct endpoint
3. `ctx.response.headers.get("set-auth-jwt")` — from any `getSession` call

Verify with jose using the JWKS endpoint:

```ts
import { createRemoteJWKSet, jwtVerify } from "jose";
const JWKS = createRemoteJWKSet(new URL("http://localhost:3000/api/auth/jwks"));
const { payload } = await jwtVerify(token, JWKS, {
  issuer: "http://localhost:3000",
  audience: "http://localhost:3000",
});
```

Key configuration — default EdDSA/Ed25519, supports ES256, RSA256, PS256, ECDH-ES, ES512:

```ts
jwt({
  jwks: {
    keyPairConfig: { alg: "ES256" },
    rotationInterval: 60 * 60 * 24 * 30, // 30 days
    gracePeriod: 60 * 60 * 24 * 30,
    disablePrivateKeyEncryption: false,
    jwksPath: "/.well-known/jwks.json",
  },
  jwt: {
    definePayload: ({ user }) => ({ id: user.id, email: user.email }),
    issuer: "https://example.com",
    expirationTime: "1h",
  },
  adapter: {
    getJwks: async (ctx) => await customStorage.getAllKeys(),
    createJwk: async (ctx, webKey) => await customStorage.createKey(webKey),
  },
})
```

**OAuth provider mode compatibility**: disable JWT `/token` endpoint and `set-auth-jwt` header to avoid conflicts:

```ts
betterAuth({
  disabledPaths: ["/token"],
  plugins: [jwt({ disableSettingJwtHeader: true })],
})
```

Custom signing supports localized (local private key) and remote (KMS) signing via `jwt.sign` function.

## Device Authorization (RFC 8628)

OAuth 2.0 device flow for CLI apps, smart TVs, IoT:

```ts
import { deviceAuthorization } from "better-auth/plugins";
import { deviceAuthorizationClient } from "better-auth/client/plugins";

deviceAuthorization({ verificationUri: "/device", expiresIn: "30m", interval: "5s" })

// Client — request device code
const { data } = await authClient.device.code({ client_id: "my-cli", scope: "openid profile" });
// data.user_code, data.verification_uri, data.verification_uri_complete

// Client — poll for token
const { data } = await authClient.device.token({
  grant_type: "urn:ietf:params:oauth:grant-type:device_code",
  device_code: data.device_code,
  client_id: "my-cli",
});

// User-facing: verify code, then approve/deny
await authClient.device.approve({ userCode });
await authClient.device.deny({ userCode });
```

User codes use `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` (no 0/O/1/I confusion).

## Test Utils Plugin

```ts
import { testUtils } from "better-auth/plugins";
export const auth = betterAuth({ plugins: [testUtils({ captureOTP: true })] });

const ctx = await auth.$context;
const test = ctx.test;

// Factories (in-memory only)
const user = test.createUser({ email: "test@e.com" });
const org = test.createOrganization({ name: "Acme" });

// Database helpers
await test.saveUser(user);
await test.deleteUser(user.id);
await test.addMember({ userId: user.id, organizationId: org.id, role: "admin" });

// Auth helpers
const { session, headers, cookies, token } = await test.login({ userId: user.id });
const headers = await test.getAuthHeaders({ userId: user.id });
const cookies = await test.getCookies({ userId: user.id, domain: "localhost" }); // Playwright-compatible

// OTP capture
const otp = test.getOTP("user@example.com");
test.clearOTPs();
```

## One-Time Token Plugin

Cross-domain session transfer with single-use tokens:

```ts
import { oneTimeToken } from "better-auth/plugins/one-time-token";
import { oneTimeTokenClient } from "better-auth/client/plugins";

const { token } = await authClient.oneTimeToken.generate();
await authClient.oneTimeToken.verify({ token });

// Options: expiresIn (minutes), storeToken ("plain" | "hashed" | custom), generateToken, disableClientRequest
```

## Captcha Plugin

Bot protection. Supports reCAPTCHA, Cloudflare Turnstile, hCaptcha, CaptchaFox:

```ts
import { captcha } from "better-auth/plugins";
import { captchaClient } from "better-auth/client/plugins";
captcha({ provider: "cloudflare-turnstile", secretKey: "..." })
```
