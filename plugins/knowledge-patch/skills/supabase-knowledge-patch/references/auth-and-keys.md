# Authentication, OAuth, hooks, and keys

## API and signing keys

### Hosted publishable and secret API keys

Hosted projects support `sb_publishable_...` and `sb_secret_...` alongside legacy `anon` and `service_role` JWT keys. Publishable keys identify public components and select `anon` until a user JWT selects `authenticated`; secret keys select `service_role`, bypass RLS, and belong only in trusted backends. Create a separate revocable secret per component. Browsers receive `401` for secret keys, but any exposure is still a compromise.

### Non-JWT key migration and compatibility

Run new and legacy keys concurrently for zero-downtime migration, then deactivate legacy keys; they can be reactivated. Opaque keys are validated by the hosted gateway and belong in `apikey`, not `Authorization`. A user bearer token remains separate.

Edge Functions cannot perform built-in JWT verification on opaque keys: deploy with JWT verification disabled and authorize `apikey` in code. Public Realtime connections made only with a public key expire after 24 hours unless maintained with a user or supported third-party Auth token.

### Asymmetric JWT signing-key lifecycle

Signing keys have standby, current, previously-used, and revoked states. Migration imports the legacy secret and creates a standby asymmetric key; rotate issuance, keep old unexpired JWTs trusted, wait at least their lifetime plus 15 minutes, then revoke. State changes are throttled for roughly five minutes and all but permanent deletion are reversible.

Before rotation, replace direct legacy-secret verification and Edge Function Verify JWT behavior with `supabase.auth.getClaims()` or JWKS. Custom verification must account for ten-minute edge caching and possibly another ten-minute library cache; hosted services apply revocation immediately, but external verifier caches may need purging.

Legacy secret revocation first requires disabling legacy `anon`/`service_role` JWT keys in favor of publishable/secret keys.

### Imported signing keys and custom JWTs

Private material cannot be exported after key creation. To mint externally, generate and import an ES256 standby key:

```sh
supabase gen signing-key --algorithm ES256
supabase gen bearer-jwt --role authenticated --sub <user-uuid>
```

JWT headers need matching `alg` and `kid`; claims need `role`, `exp`, and optionally `sub`. Data API requests still need a publishable, secret, `anon`, or `service_role` value in `apikey`; the bearer JWT is not a replacement.

### AWS KMS-backed RS256 signing keys

RS256 signing keys may use AWS KMS so signing operations remain in managed key infrastructure.

### Automatic revocation of leaked secret keys

New-format secret keys detected in public GitHub repositories are automatically revoked and the project owner is notified. Treat a leak as an immediate outage and rotate dependent services.

## Hooks and messaging

### Auth audit-log storage

Auth events are stored in both `auth.audit_log_entries` and external log storage by default. Dashboard Authentication > Audit Logs can disable database writes without removing the dashboard copy; dashboard ingestion can lag and has limited query support.

### Before User Created hook

This hook runs immediately before inserting into `auth.users`; the proposed user does not yet exist in Postgres. A Postgres function or HTTP endpoint returns `{}` or `204` to continue, or an `error` object to reject. Grant execution only to `supabase_auth_admin`:

```sql
create or replace function public.before_user_created(event jsonb)
returns jsonb language plpgsql as $$
begin
  if coalesce(lower(event->'user'->>'email'), '') not like '%@example.com' then
    return jsonb_build_object('error', jsonb_build_object(
      'http_code', 400, 'message', 'Company email required'));
  end if;
  return '{}'::jsonb;
end;
$$;
grant execute on function public.before_user_created(jsonb) to supabase_auth_admin;
revoke execute on function public.before_user_created(jsonb) from authenticated, anon, public;
```

### HTTP Auth hook contract

HTTP hooks use Standard Webhooks headers and a `v1,whsec_<base64-secret>` secret. Verify the raw, uncompressed body before parsing. Payloads are limited to 20 KB, every response needs `Content-Type: application/json`, and the invocation budget is five seconds. Only `429`/`503` with a nonempty `retry-after` are retried: at most three retries with two-second backoff. Postgres-hook failures are never retried; HTTP `400`/`403` surface as internal errors.

Custom Access Token, MFA Verification, and Password Verification require response bodies, so `204` is invalid for them.

### Send Email hook and secure email changes

The hook replaces SMTP only while the Email provider stays enabled; disabling the provider also disables email signup. Secure-email-change fields are intentionally crossed for compatibility:

```text
current address (user.email):     token     + token_hash_new
new address (user.new_email):     token_new + token_hash
```

With secure changes disabled, send one message to the new address using the available OTP and `token_hash`.

### Additional Auth security notifications

Hosted Auth has security-notification templates for password, email, and phone changes, identity linking/unlinking, and MFA enrollment/removal.

### One-megabyte Auth request limit

Auth request bodies are capped at 1 MB.

## MFA, passkeys, and identities

### Phone MFA factors

Phone MFA shares phone-login provider configuration; a Send SMS hook may use another SMS or WhatsApp provider. Use explicit enroll/challenge/verify, after which the session refreshes to `aal2`:

```ts
const { data: factor } = await supabase.auth.mfa.enroll({
  factorType: 'phone', phone: '+15551234567',
})
const { data: challenge } = await supabase.auth.mfa.challenge({ factorId: factor.id })
await supabase.auth.mfa.verify({
  factorId: factor.id, challengeId: challenge.id, code,
})
```

Codes last up to five minutes; successively issued codes remain valid until expiry. Only one verified phone factor can use a given number.

### Passkey authentication and management

Auth supports discoverable-credential sign-in and progressive passkey enrollment, with user and admin list/delete endpoints. `/options` is rate-limited, friendly names can derive from AAGUIDs, and successful deletion returns bodyless `204`.

### Native ID-token identity linking

With manual linking enabled, attach a native OAuth identity without redirect by passing a provider ID token and optional access token. Google, Apple, Facebook, Kakao, and Keycloak are supported.

```ts
await supabase.auth.linkIdentity({
  provider: 'google', token: googleIdToken, access_token: googleAccessToken,
})
```

Unlinking is permitted only while at least two linked identities remain.

### Web3 authentication

`auth.signInWithWeb3()` verifies Ethereum and Solana standard wallet-signed messages. In a browser, supply `chain` and optionally a statement; it can use `window.ethereum` or `window.solana`.

### Explicit Auth redirect initialization

Client construction initializes Auth from URL or persisted storage automatically. Call `await supabase.auth.initialize()` explicitly when application code must inspect OAuth, magic-link, or recovery redirect errors.

## Custom and third-party identity providers

### Clerk third-party authentication

Clerk users can access Data API, Storage, Realtime, and Edge Functions without migrating to Supabase Auth.

### Custom OAuth and OIDC identity providers

Define up to three providers beyond built-ins. Identifiers require `custom:`. Generic OAuth2 needs authorization, token, and UserInfo URLs; OIDC needs an issuer and uses discovery/JWKS. Create providers only from an admin server client:

```ts
await supabase.auth.admin.customProviders.createProvider({
  provider_type: 'oidc', identifier: 'custom:corp', name: 'Corporate IdP',
  client_id: 'web-client-id', client_secret: process.env.IDP_CLIENT_SECRET!,
  issuer: 'https://id.example.com', scopes: ['openid', 'profile', 'email'],
})
```

PKCE is server-managed by default and OIDC adds `openid`. Options include `acceptable_client_ids`, `email_optional`, custom `discovery_url`, and last-resort `skip_nonce_check`. Type and identifier are immutable.

### Per-provider custom OAuth claim allowlists

Each custom provider can define `custom_claims_allowlist` independently rather than using one global filter.

### Auth0, Cognito, Firebase, and WorkOS token trust

First-class integrations let these providers' JWTs authorize Data API, Storage, Realtime, and Functions without token translation. Register the integration, require `role: authenticated` (otherwise Postgres uses `anon`), and provide a current token callback:

```ts
const supabase = createClient(url, publishableKey, {
  accessToken: async () => auth0.getTokenSilently(),
})
```

Tokens must use asymmetric signing and a `kid`; changes can take 30 minutes to propagate, and Supabase Auth cannot yet be disabled. Auth0 HS256/PS256 are unsupported. Self-hosted Firebase needs restrictive `iss` and `aud` RLS because Firebase publishes a shared key set.

### X OAuth 2.0 provider support

Auth supports X/Twitter's OAuth 2.0 sign-in flow.

### Zero-downtime SAML service-provider key rotation

SAML service-provider keys can rotate without interrupting authentication during transition.

## OAuth 2.1 and OIDC server

### OAuth 2.1 server and consent UI

A project can be an OAuth 2.1/OIDC identity provider; local support needs CLI 2.54.11+. The authorization path joins the Auth Site URL. `/auth/v1/oauth/authorize` redirects there with `authorization_id`; the UI calls `getAuthorizationDetails()`, then `approveAuthorization()` or `denyAuthorization()` and follows `redirect_to`.

```toml
[auth.oauth_server]
enabled = true
authorization_url_path = "/oauth/consent"
allow_dynamic_registration = false
```

Clients begin at `/auth/v1/oauth/authorize`, not the consent UI. Token, UserInfo, JWKS, authorization-server discovery, and OIDC discovery endpoints are also exposed.

### OAuth client registration and flows

Register dashboard or admin-API clients with exact redirect URI matches; wildcards are forbidden. Public clients use `token_endpoint_auth_method: 'none'`. Confidential clients default to `client_secret_basic` and may use `client_secret_post`; generated secrets appear once.

Only authorization-code-with-PKCE and refresh-token grants exist—no password or client credentials. Codes are single-use, PKCE-bound, and expire after ten minutes. `supabase-js` does not implement a third-party client flow.

### OAuth client authentication-method updates

An existing client can change `token_endpoint_auth_method`; registration no longer fixes it permanently.

### OAuth scopes, tokens, and OIDC requirements

Supported scopes are `openid`, `email`, `profile`, and `phone`; missing scope defaults to `email`. Custom scopes are unsupported. Scopes control ID-token/UserInfo fields, not Data API permissions. Access tokens are ordinary user tokens plus `client_id`.

`openid` returns a one-hour ID token and requires asymmetric signing; issuance fails under HS256. Refresh tokens may rotate, so always replace the stored token when a new one is returned.

### OAuth-aware RLS and user grants

Use `auth.jwt()->>'client_id'` in RLS; direct sessions have no `client_id`. Custom Access Token hooks see `authentication_method: 'oauth_provider/authorization_code'`. Users list approvals with `getUserGrants()` and revoke with `revokeGrant(clientId)`; revocation deletes client refresh tokens and invalidates that user's active sessions for that client.

### OAuth authentication for custom MCP servers

A separately built MCP server can use issuer `https://<project-ref>.supabase.co/auth/v1`; discovery is `/.well-known/oauth-authorization-server/auth/v1`. Dynamic registration permits any client to register, so require explicit consent, validate redirect domains, monitor registration, and enforce `client_id`-aware RLS instead of relying on scopes.

## Migration and production safeguards

### Auth0 password migration

Admin creation accepts Auth0 bcrypt/Argon2 hashes, a preserved UUIDv4 ID, and confirmed-address flags, enabling one-off or rolling password migration. OAuth users continue through their provider; Auth0 organizations have no direct mapping.

### Firebase migration utilities

`supabase-community/firebase-to-supabase` migrates Firebase Auth users with Scrypt parameters, copies Storage through a local staging directory, and flattens one Firestore collection into one table. Hooks can split nested documents to related JSON files. Imported buckets default private and need policies.

### Production Auth traffic defaults

Review defaults before launch: 360 OTP requests/hour; 60-second resend window; 360 verification requests/IP/hour and 1,800 refreshes/IP/hour, each with burst 30; MFA challenge/verify 15/IP/minute with burst 30; anonymous sign-in 30/IP/hour with burst 30; custom SMTP starts at 30 new users/hour.

### Single-use Auth links and mail scanners

Mail security scanners can consume single-use signup/recovery links. Send users first to a controlled landing page with an explicit button to the original URL, and disable SMTP link tracking that rewrites confirmation links.

### Organization SAML SSO accounts

SSO identities do not auto-link to password/social identities sharing an email. Remove and reinvite an existing member under SSO. Disabling the provider immediately blocks all SSO users; retain a non-SSO owner.

### Organization MFA enforcement

An MFA-enrolled owner can require MFA-backed dashboard sessions; unenrolled members immediately lose organization/project access without losing membership. Personal access tokens are unaffected. Account MFA uses TOTP without recovery codes, and enabling it signs out other sessions, so retain a separate backup factor.
