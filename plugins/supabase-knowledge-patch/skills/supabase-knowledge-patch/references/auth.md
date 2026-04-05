# Auth

## OAuth 2.1 Server — Supabase as Identity Provider

Supabase Auth can now act as a full OAuth 2.1 and OpenID Connect identity provider, enabling "Sign in with [Your App]" flows. Enable in `config.toml`:

```toml
[auth.oauth_server]
enabled = true
authorization_url_path = "/oauth/consent"
allow_dynamic_registration = false
```

Exposed endpoints include `/auth/v1/oauth/authorize`, `/auth/v1/oauth/token`, `/auth/v1/.well-known/jwks.json`, and OIDC discovery at `/auth/v1/.well-known/openid-configuration`.

New `supabase-js` OAuth methods for building consent UI:

```typescript
// Get details about the authorization request
const { data } =
  await supabase.auth.oauth.getAuthorizationDetails(authorizationId);
// data.client.name, data.redirect_uri, data.scope

// Approve or deny
const { data: approved } =
  await supabase.auth.oauth.approveAuthorization(authorizationId);
// approved.redirect_to — redirect user here

const { data: denied } =
  await supabase.auth.oauth.denyAuthorization(authorizationId);
```

OAuth access tokens include a `client_id` claim identifying which OAuth client obtained the token. Supports `authorization_code` with PKCE and `refresh_token` grant types. OpenID Connect ID tokens require asymmetric JWT signing (RS256/ES256).

## Custom OAuth/OIDC Providers

Add any standards-compliant identity provider with the `custom:` prefix (up to 3 per project):

```javascript
// OAuth2 provider (manual endpoints)
await supabase.auth.admin.customProviders.createProvider({
  provider_type: 'oauth2',
  identifier: 'custom:my-idp',
  name: 'My IDP',
  client_id: 'id',
  client_secret: 'secret',
  authorization_url: 'https://idp.example.com/oauth/authorize',
  token_url: 'https://idp.example.com/oauth/token',
  userinfo_url: 'https://idp.example.com/oauth/userinfo',
  scopes: ['profile', 'email'],
});

// OIDC provider (auto-discovery from issuer)
await supabase.auth.admin.customProviders.createProvider({
  provider_type: 'oidc',
  identifier: 'custom:my-oidc',
  name: 'OIDC Provider',
  client_id: 'id',
  client_secret: 'secret',
  issuer: 'https://auth.example.com',
});

// Sign in
await supabase.auth.signInWithOAuth({ provider: 'custom:my-idp' });

// Manage: list, update, delete
await supabase.auth.admin.customProviders.listProviders();
await supabase.auth.admin.customProviders.updateProvider('custom:my-idp', {
  enabled: false,
});
await supabase.auth.admin.customProviders.deleteProvider('custom:my-idp');
```

Options: `acceptable_client_ids` for multi-platform OIDC, `email_optional: true`, `pkce_enabled`, `authorization_params`, `discovery_url`, `skip_nonce_check`.

## Web3 Authentication (Ethereum & Solana)

Sign in with Web3 wallets using EIP-4361 standard. Enable in `config.toml`:

```toml
[auth.web3.ethereum]
enabled = true

[auth.web3.solana]
enabled = true
```

```typescript
// Ethereum — uses window.ethereum by default
const { data, error } = await supabase.auth.signInWithWeb3({
  chain: 'ethereum',
  statement: 'I accept the Terms of Service at https://example.com/tos',
  wallet: selectedWallet, // optional: EIP-6963 wallet selection
})

// Solana — uses window.solana by default
const { data, error } = await supabase.auth.signInWithWeb3({
  chain: 'solana',
  statement: 'I accept the Terms of Service at https://example.com/tos',
  wallet: window.phantom, // optional: specific wallet
})

// Custom message+signature (Ethereum only)
await supabase.auth.signInWithWeb3({
  chain: 'ethereum',
  message: '<EIP-4361 message>',
  signature: '<hex signature>',
})
```

Rate limiting via `[auth.rate_limit] web3 = 30`. Solana Wallet Adapter (`useWallet()` hook) is also supported.

## OAuth Token Security with RLS

OAuth JWTs include a `client_id` claim. Use it in RLS policies to control per-client data access:

```sql
-- Only direct user sessions (no OAuth clients)
CREATE POLICY "No OAuth access to payments" ON payment_methods FOR ALL USING (
  auth.uid () = user_id
  AND (auth.jwt () ->> 'client_id') IS NULL
);

-- Specific client access
CREATE POLICY "Mobile app reads profiles" ON profiles FOR
SELECT
  USING (
    auth.uid () = user_id
    AND (auth.jwt () ->> 'client_id') = 'mobile-app-client-id'
  );
```

Custom Access Token Hook receives `client_id` in the payload, enabling per-client claim customization (e.g., different `aud` values for different OAuth clients).

## Auth Hooks via HTTP Endpoints (Edge Functions)

Auth hooks can now be HTTP endpoints (not just Postgres functions). Configure in `config.toml`:

```toml
[auth.hook.send_sms]
enabled = true
uri = "http://host.docker.internal:54321/functions/v1/send_sms"
secrets = "env(SEND_SMS_HOOK_SECRETS)"
```

HTTP hooks use Standard Webhooks spec with `webhook-id`, `webhook-timestamp`, `webhook-signature` headers. Secret format: `v1,whsec_<base64-secret>`. Verify with Standard Webhooks library:

```typescript
Deno.serve(async (req) => {
  const payload = await req.text()
  const hookSecret = Deno.env.get('SEND_SMS_HOOK_SECRETS').replace('v1,whsec_', '')
  const headers = Object.fromEntries(req.headers)
  const wh = new Webhook(hookSecret)
  const data = wh.verify(payload, headers) // throws if invalid
  // process verified payload...
})
```

20KB payload limit. Use `--no-verify-jwt` when serving locally since hooks fire before JWT issuance.
