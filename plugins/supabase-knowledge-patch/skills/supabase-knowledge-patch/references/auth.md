# Auth

## OAuth 2.1 Server (Supabase as Identity Provider)

Supabase can now act as a full OAuth 2.1 identity provider. Third-party apps can authenticate users against your Supabase project using standard OAuth flows.

Enable in `supabase/config.toml`:

```toml
[auth.oauth_server]
enabled = true
authorization_url_path = "/oauth/consent"
allow_dynamic_registration = false
```

Endpoints exposed:
- Authorization: `/auth/v1/oauth/authorize`
- Token: `/auth/v1/oauth/token`
- JWKS: `/auth/v1/.well-known/jwks.json`
- Discovery: `/.well-known/oauth-authorization-server/auth/v1`
- OIDC: `/auth/v1/.well-known/openid-configuration`

New `supabase-js` methods for building consent UIs:

```typescript
// In your authorization page (e.g., /oauth/consent?authorization_id=...)
const { data } = await supabase.auth.oauth.getAuthorizationDetails(authorizationId)
// data.client.name, data.redirect_uri, data.scope

await supabase.auth.oauth.approveAuthorization(authorizationId)
// or
await supabase.auth.oauth.denyAuthorization(authorizationId)
```

Register OAuth clients via dashboard or Management API. Supports `authorization_code` with PKCE and `refresh_token` grant types. Public clients use `token_endpoint_auth_method: none`; confidential clients use `client_secret_basic` (default) or `client_secret_post`.

Requires asymmetric signing keys (RS256/ES256) for OIDC ID tokens — HS256 won't work.

## OAuth Token Security & RLS

OAuth access tokens include a `client_id` claim identifying which OAuth client obtained the token. Use this in RLS policies:

```sql
-- Only allow direct user sessions (no OAuth clients)
CREATE POLICY "No OAuth access to payments" ON payment_methods FOR ALL USING (
  auth.uid () = user_id
  AND (auth.jwt () ->> 'client_id') IS NULL
);

-- Allow specific OAuth client
CREATE POLICY "Mobile app reads profiles" ON profiles FOR
SELECT
  USING (
    auth.uid () = user_id
    AND (auth.jwt () ->> 'client_id') = 'mobile-app-client-id'
  );
```

OAuth scopes (`openid`, `email`, `profile`, `phone`) control OIDC data only — they do NOT control database access. Use RLS for that.

## Custom OAuth/OIDC Providers

Add any standards-compliant OAuth2 or OIDC identity provider with `custom:` prefix identifiers (up to 3 per project):

```javascript
// OAuth2 provider (manual endpoints)
await supabase.auth.admin.customProviders.createProvider({
  provider_type: 'oauth2',
  identifier: 'custom:my-provider',
  name: 'My Provider',
  client_id: 'your-client-id',
  client_secret: 'your-client-secret',
  authorization_url: 'https://provider.example.com/oauth/authorize',
  token_url: 'https://provider.example.com/oauth/token',
  userinfo_url: 'https://provider.example.com/oauth/userinfo',
  scopes: ['profile', 'email'],
});

// OIDC provider (auto-discovery from issuer)
await supabase.auth.admin.customProviders.createProvider({
  provider_type: 'oidc',
  identifier: 'custom:my-oidc',
  name: 'OIDC Provider',
  client_id: 'your-client-id',
  client_secret: 'your-client-secret',
  issuer: 'https://auth.example.com',
  scopes: ['openid', 'profile', 'email'],
});
```

Sign in users:

```javascript
await supabase.auth.signInWithOAuth({ provider: 'custom:my-provider' })
```

PKCE enabled by default. CRUD via `supabase.auth.admin.customProviders.*` (list, update, delete).

## Web3 Authentication

Sign in with Ethereum or Solana wallets using EIP-4361 (Sign-In with Ethereum) standard.

```toml
# supabase/config.toml
[auth.web3.ethereum]
enabled = true

[auth.web3.solana]
enabled = true
```

```typescript
// Ethereum — auto-detects window.ethereum
const { data, error } = await supabase.auth.signInWithWeb3({
  chain: 'ethereum',
  statement: 'I accept the Terms of Service at https://example.com/tos',
})

// Ethereum — specific wallet (EIP-6963 discovery)
await supabase.auth.signInWithWeb3({
  chain: 'ethereum',
  statement: '...',
  wallet: selectedWallet,
})

// Solana — auto-detects window.solana
await supabase.auth.signInWithWeb3({
  chain: 'solana',
  statement: 'I accept the Terms of Service at https://example.com/tos',
})

// Solana with Wallet Adapter
const wallet = useWallet()
await supabase.auth.signInWithWeb3({
  chain: 'solana',
  statement: '...',
  wallet,
})
```

Web3 accounts have no email/phone. Use `updateUser()` or `linkIdentity()` to add them later.

## JWT Signing Keys (Asymmetric)

New signing keys system replaces the legacy shared JWT secret. Supports ES256 (P-256, recommended), RS256, and HS256.

Key lifecycle states: **standby** -> **in use** (rotate) -> **previously used** -> **revoked** -> **deleted**. Each transition is reversible (except delete). Zero-downtime rotation — no users signed out.

JWKS endpoint for public key discovery:

```
GET https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json
```

Generate and import signing keys:

```bash
supabase gen signing-key --algorithm ES256
# Outputs JWK to import as standby key in dashboard

supabase gen bearer-jwt --role authenticated --sub <user-uuid>
# Mint custom JWTs with imported key
```

Revoking legacy JWT secret requires disabling `anon` and `service_role` keys first (they are JWTs signed by the legacy secret). Migrate to publishable/secret API keys instead.

## Before User Created Hook

New auth hook that runs before inserting a user into `auth.users`. Return an error to reject signup.

```sql
CREATE OR REPLACE FUNCTION public.before_user_created(event jsonb)
RETURNS jsonb AS $$
BEGIN
  -- Block disposable email domains
  IF (event->'user'->>'email') LIKE '%@disposable.com' THEN
    RETURN jsonb_build_object(
      'error', jsonb_build_object(
        'http_code', 400,
        'message', 'Disposable email addresses are not allowed.'
      )
    );
  END IF;
  RETURN '{}'::jsonb;
END;
$$ LANGUAGE plpgsql;
```

Input payload includes `metadata` (IP address, request ID) and `user` (full user object). Return `{}` or `204` to allow, return `{ "error": { "http_code": 400, "message": "..." } }` to reject.

## MCP Server Authentication

Use Supabase Auth's OAuth 2.1 server to authenticate MCP (Model Context Protocol) AI agents. MCP clients discover OAuth config from `/.well-known/oauth-authorization-server/auth/v1`, optionally register via dynamic client registration, then authenticate users through your consent flow. Existing RLS policies apply to MCP client tokens automatically.
