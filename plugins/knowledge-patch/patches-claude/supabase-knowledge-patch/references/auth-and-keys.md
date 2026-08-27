# Authentication, OAuth, Hooks, and Keys

Use this reference for Auth flows, identity providers, hooks, signing keys, passkeys, MFA, and API-key lifecycle.

## Supabase JS compatibility (`supabase-js-2.101.0`)

### OAuth 2.1 and custom-provider administration
The Auth client now covers OAuth 2.1 client administration and updates, authorization-consent management, grant listing and revocation, and admin CRUD for custom OIDC/OAuth providers. Custom provider identifiers use the `custom:` prefix, and client creation or update accepts `token_endpoint_auth_method`.

### Auth initialization and error controls
Auth can opt into thrown errors, use a predicate for `detectSessionInUrl`, and disable constructor auto-initialization with `skipAutoInitialize`. The lock acquisition timeout is configurable and now defaults to five seconds.

### Auth redirect behavior
In browsers, `signInWithSSO()` now redirects automatically, while `getAuthorizationDetails()` no longer redirects.

### Synchronous auth-state callbacks
Passing an async function directly to `onAuthStateChange` is deprecated.

### Additional Auth request inputs
`UserAttributes` now includes `currentPassword`, and `getAuthenticatorAssuranceLevel()` accepts an optional JWT.

### X OAuth 2.0 provider
Supabase Auth now includes X as an OAuth 2.0 sign-in provider.

## Hooks, OAuth, MFA, SAML, and JWTs

### Auth audit-log destinations
Auth events are written to both `auth.audit_log_entries` and external log storage by default. Hosted projects can disable database writes without losing dashboard logs; external logs can lag briefly and are queried through the dashboard.

### Security-notification email templates
Projects can opt into templates for password, email, and phone changes; identity linking and unlinking; and MFA enrollment and removal. These templates expose event-specific values such as `{{ .OldEmail }}`, `{{ .OldPhone }}`, `{{ .Provider }}`, and `{{ .FactorType }}` and can be managed through Auth configuration in the Management API.

### Expanded Auth Hook surface
Auth Hooks can be Postgres `jsonb -> jsonb` functions or HTTP endpoints and can run before user creation, before token issuance, around password or MFA verification, or instead of built-in email and SMS delivery. A before-user-created hook sees request metadata and a not-yet-inserted user and can reject creation, while a custom-access-token hook must preserve the required JWT claims.

### Auth Hook trust and retry contract
Postgres hooks should grant only `supabase_auth_admin` access; HTTP hooks use Standard Webhooks signatures, receive uncompressed payloads capped at 20 KB, and do not use JWT verification. HTTP responses require JSON, and only `429` or `503` with a nonempty `retry-after` are retried—up to three retries inside a five-second total budget—while `400` and `403` surface as internal errors.

### Secure email-change hook pairing
With Secure Email Change enabled, a Send Email Hook must send two messages, and the backward-compatible hash names are reversed: the current address uses `token` with `token_hash_new`, while the new address uses `token_new` with `token_hash`. Enabling this hook replaces SMTP only while the email provider itself remains enabled.

### Native OAuth identity linking
With manual linking enabled, native apps can attach an OAuth identity without a browser redirect by passing the provider ID token as `token` and its access token as `access_token` to `linkIdentity()`. Unlinking is allowed only for a signed-in user who still has at least two linked identities.

### Phone factors for MFA
Phone MFA shares the phone-login provider configuration, but a Send SMS Hook can replace the native messaging provider. Enroll with `mfa.enroll({ factorType: 'phone', phone })`, then call `mfa.challenge({ factorId })` and `mfa.verify({ factorId, challengeId, code })`.

### Custom OAuth/OIDC provider defaults
A project can have at most three custom providers, and server-side PKCE is enabled for each by default. OIDC providers can accept extra platform audiences through `acceptable_client_ids`, allow accounts without email through `email_optional`, override discovery with `discovery_url`, or—only for incompatible providers—disable nonce validation with `skip_nonce_check`.

### SAML account isolation
SAML identities are never automatically linked to same-email password or OAuth users, so email is not unique and application data must reference the user UUID. Removing a SAML connection immediately signs out its users and leaves those existing accounts inaccessible even if the connection is later added again.

### OAuth 2.1 consent UI
The OAuth server redirects authorization requests to the Site URL plus `authorization_url_path` with an `authorization_id`; the application must preserve it across login, fetch details, call the approve or deny method, and follow the returned `redirect_to`. Client redirect URIs require exact matches and do not support the wildcard rules used by normal Auth redirect URLs.

```toml
[auth.oauth_server]
enabled = true
authorization_url_path = "/oauth/consent"
allow_dynamic_registration = false
```

### OAuth scopes do not authorize database access
The `openid`, `email`, `profile`, and `phone` scopes control ID-token and UserInfo fields only. OAuth access tokens carry `client_id`, so database authorization must use RLS, for example `auth.uid() = user_id and auth.jwt()->>'client_id' = '<allowed-client>'`; direct user sessions have no `client_id`.

### OAuth-backed MCP authentication
Supabase Auth can secure a separately built MCP server but does not provide the MCP server itself. MCP clients discover the issuer at `https://<project-ref>.supabase.co/.well-known/oauth-authorization-server/auth/v1`; optional dynamic registration lets any client register, so consent, redirect validation, and client review remain application responsibilities.

### Asymmetric signing-key migration
Migrating the legacy JWT secret creates an asymmetric standby key; rotating starts new issuance while both old and new signatures remain trusted, and revocation is a later explicit step after old access tokens expire. Direct legacy-secret verification and Edge Functions' legacy Verify JWT setting can break during rotation, so those paths should move to `getClaims()` or JWKS verification before the switch.

### JWKS cache timing
The JWKS endpoint is cached at the edge for ten minutes and client libraries may cache it for another ten, so custom verifiers should allow roughly twenty minutes for key propagation and expose a cache-busting path. Supabase services do not use that cache and honor revocation immediately, while external backends can continue accepting a revoked key until their caches refresh.

### First-class third-party Auth JWTs
Clerk, Firebase Auth, Auth0, Amazon Cognito, and WorkOS tokens can be supplied through the client's `accessToken` callback and used with Data APIs, Storage, Realtime, and Functions. Tokens must be asymmetrically signed with a `kid` and carry `role: "authenticated"` or Postgres falls back to `anon`; provider key rotations can take up to thirty minutes to propagate, and Supabase Auth itself cannot be disabled.

### Self-hosted Firebase issuer isolation
Firebase uses one signing-key set across all projects; hosted Supabase rejects JWTs from unregistered Firebase projects, but self-hosters must enforce the expected `iss` and `aud` with restrictive policies on database tables, Storage, and Realtime. The policy must admit either the project's own Auth issuer or both `iss = 'https://securetoken.google.com/<firebase-project-id>'` and `aud = '<firebase-project-id>'`.

## Auth service capabilities

### Passkey authentication and administration
Auth 2.188.0 adds discoverable-credential authentication, progressive enrollment, user management endpoints, and admin endpoints for listing and deleting passkeys. The authentication `/options` endpoint is rate-limited, and successful passkey deletion returns `204`.

### One-megabyte request-body limit
Auth 2.188.0 adds middleware that limits request bodies to 1 MB, so clients must keep Auth requests below that ceiling.

### Custom providers enabled by default
Auth 2.188.0 enables custom providers by default; upgraded deployments should no longer assume the feature requires an explicit opt-in.

### AWS KMS-backed RS256 signing keys
Auth 2.191.0 supports RS256 signing keys backed by AWS KMS.

### Zero-downtime SAML SP key rotation
Auth 2.191.0 supports rotating SAML service-provider keys without authentication downtime.

### Per-provider custom OAuth claim allowlists
Auth 2.192.0 adds a per-provider `custom_claims_allowlist` for custom OAuth providers.

## Data API configuration, types, and errors

### Hosted publishable and secret API keys
Hosted projects support opaque `sb_publishable_...` and `sb_secret_...` keys alongside the legacy long-lived JWT `anon` and `service_role` keys. A publishable key selects `anon` unless a separate user JWT selects `authenticated`; a secret key selects `service_role`, bypasses RLS, must stay server-side, and is rejected with `401` when used from a browser.

```sh
curl "$SUPABASE_URL/rest/v1/items?select=*" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "Authorization: Bearer $USER_JWT"
```

### Opaque-key migration and compatibility
Opaque keys can be created, rotated, and revoked independently while legacy keys remain active for a zero-downtime migration, but they are hosted-only and cannot serve as bearer JWTs. Edge Functions' built-in verification understands only JWT-based keys, so opaque-key callers require `--no-verify-jwt` plus explicit `apikey` validation in the function; a public Realtime connection using only an API key is limited to 24 hours unless upgraded with user authentication.

## Security and compliance

### Automatic revocation of leaked secret keys
Supabase automatically revokes new-format secret keys detected in public GitHub repositories and notifies the project owner with rotation instructions. This applies to secret keys, not publishable keys.

## JavaScript client behavior

### Web3 wallet authentication
`signInWithWeb3()` authenticates Ethereum or Solana users by verifying a wallet-signed SIWE or SIWS message. With an injected browser wallet, pass the chain and an optional statement:

```ts
const { data, error } = await supabase.auth.signInWithWeb3({
  chain: 'ethereum',
  statement: 'I accept the Terms of Service at https://example.com/tos',
})
```

### Explicit Auth initialization
The Auth client calls `initialize()` automatically, but code that needs to inspect an OAuth, magic-link, or password-recovery redirect error should await it explicitly and inspect its result.

```ts
const result = await supabase.auth.initialize()
if (result.error) throw result.error
```

## Platform capabilities (`1.26.08`)

### ChatGPT sign-in beta
Supabase now supports signing in with a ChatGPT account in beta. A Supabase connection can also be added to ChatGPT on desktop, web, and mobile through the ChatGPT plugins directory.
