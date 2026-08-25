# Service integrations and identity providers

## Bootstrap organizations

The hosted `${CUSTOM_DOMAIN}/ui/login/register/org` form creates an organization and first user with `ORG_OWNER`. Deployments that provision customers themselves can disable it through `AdminService.SetRestrictions`.

A custom onboarding flow can instead call `POST /admin/v1/orgs/_setup` with the organization, one password-authenticated human, and optional roles, which default to `ORG_OWNER`.

```json
{
  "org": {"name": "Acme", "domain": "acme.example"},
  "human": {
    "userName": "owner",
    "profile": {"firstName": "Ada", "lastName": "Lovelace"},
    "email": {"email": "ada@acme.example", "isEmailVerified": true},
    "password": "replace-me"
  }
}
```

## Place and control external identity providers

An external provider can be an instance default available to every organization or belong to one organization for tenant-specific SSO. The applicable login policy must enable **External IDP Allowed**. Provider settings separately control automatic creation and profile updates, manual creation and linking, and automatic username/email matching. Disable manual options when an automatic flow must not expose edit or link choices.

Automatic linking is organization-scoped and requires the external email to be verified. Current Login validates configured linking conditions and protects against external-identity pre-hijacking. When provider user information changes, maintained releases restore propagation to the local user.

ZITADEL can itself be configured as an external provider in version 4.17.0, including add/update/get/list/delete, intent start/retrieval, Login V1 **Sign in with ZITADEL**, active-provider listing, and instance-role synchronization.

## Route provider callbacks

External OAuth and OIDC providers use `${CUSTOM_DOMAIN}/ui/login/login/externalidp/callback` with Login V1 and `${CUSTOM_DOMAIN}/idps/callback` with Login V2. Apple's form-post response needs the V1 callback's `/form` suffix; the V2 callback already accepts POST.

Identity-provider intents provide success and failure URLs. Current releases provide fallback plus `postError` routes, correct the success callback, preserve OIDC or SAML failure context, and guard an absent `defaultRedirectUri` on failed-precondition paths.

## Configure common provider types

### Generic OIDC and OAuth

The Generic OIDC template takes issuer, client ID, and secret, and ensures `openid` is requested. The separate Generic OAuth template takes explicit authorization, token, and user-information endpoints plus the response field used as external user ID, supporting providers such as LinkedIn where that field is `sub`. External OAuth and OIDC provider authorization can use PKCE.

### Microsoft Entra OIDC

The Microsoft template always sends `openid` and `User.Read`. Entra should return `email`, `family_name`, `given_name`, and `preferred_username`; ZITADEL's **Email Verified** option treats its email as verified because Entra does not send that claim. Common, Organizations, Consumers, or a specific Tenant ID must match the account types configured on the Entra application. Maintained releases correct unmarshalling of Entra user information from intent results.

### External SAML

When ZITADEL consumes an external SAML IdP, import the IdP's metadata and give it ZITADEL's SP metadata at `/idps/{providerID}/saml/metadata`. Provider details expose separate **ACS Login Form** for Login V1, **ACS Intent API** for Login V2 or programmatic flows, and **Single Logout** URLs. Use the matching ACS as consumer URL and recipient, and the metadata URL as SP entity ID or audience. SAML intent results contain typed form-post data.

### JWT provider relay

A JWT IdP defines issuer, header name, JWKS endpoint, JWT endpoint, and optional audience. ZITADEL validates signature, `iss`, `exp`, `iat`, and configured `aud` but does not re-authenticate the user. The JWT endpoint must recover the browser session, preserve every ZITADEL query parameter, and proxy the token in the configured header to the matching callback.

```text
Login V1  https://${CUSTOM_DOMAIN}/ui/login/idps/jwt?<unchanged-query>  x-custom-tkn: <JWT>
Login V2  https://${CUSTOM_DOMAIN}/idps/jwt?<unchanged-query>           x-custom-tkn: <JWT>
```

### LDAP

An LDAP provider declares `schema://host:port` servers, `BaseDN`, search bind credentials, user base, attribute mappings, and a required ID attribute. Login-name filters are OR-joined while required object classes are AND-joined. Escape the username before embedding it in filters. Non-ASCII bind distinguished names and special characters in login identifiers are supported. Prefer LDAPS or StartTLS; timeout `0s` uses the 60-second default.

```text
filters [uid, email] + login user@example.com
=> (|(uid=user@example.com)(email=user@example.com))
```

## Migrate a generic OIDC provider

Instance Admin and organization Management `MigrateGenericOIDCProvider` operations convert a generic provider to the Google or Entra template without deleting linked users. With Terraform, remove the old generic resource from state, call the migration API, then import the typed resource as `<provider-id>:<client-secret>` before applying.

```sh
terraform state rm zitadel_idp_oidc.old
terraform import zitadel_idp_google.google '<provider-id>:<client-secret>'
```

## Apply integration-specific requirements

### Cloudflare Zero Trust OIDC

Cloudflare's callback is `https://<team>.cloudflareaccess.com/cdn-cgi/access/callback`. Enable **User Info inside ID Token** or Cloudflare reports that no email was returned. Configure `openid profile email` and disable PKCE because this integration cannot supply the client secret in the PKCE mode Cloudflare expects.

```json
{"scopes":["openid","profile","email"],"pkce_enabled":false}
```

### Google Cloud Workforce Identity Federation

Use a Web application with Implicit grant, ID-token response, and no client authentication, plus Google's `auth.cloud.google` workforce-pool callback. Set access-token type to JWT and enable roles and user information in the ID token. Map project roles into Google's group-claim format when group-based IAM bindings are needed.

### Google Workspace SAML

Verify the same domain and set it as an organization domain in ZITADEL. The Workspace username must equal the ZITADEL username, not merely share the email. The organization-wide profile uses entity ID `google.com/a/<domain>` and ACS `https://www.google.com/a/<domain>/acs`. Workspace super administrators cannot test SSO.

### Apache `mod_auth_openidc`

Register Apache as a PKCE application and enable Development Mode for a non-HTTPS redirect. The module needs a protected vanity redirect path with no content and uses S256 PKCE without a client secret.

```apache
OIDCProviderMetadataURL https://${CUSTOM_DOMAIN}/.well-known/openid-configuration
OIDCClientID <client-id>
OIDCRedirectURI https://app.example/secure/callback
OIDCCryptoPassphrase <random-secret>
OIDCScope "openid profile"
OIDCPKCEMethod S256
```

## Authenticate service and system callers

### Service-account client credentials

A generated client secret is shown once. Exchange it with HTTP Basic and `client_credentials`; ZITADEL requires `openid`. The access token is opaque by default, but the service-account setting can switch it to JWT and the API can specify a machine user's access-token type.

```sh
curl -u "$CLIENT_ID:$CLIENT_SECRET" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials&scope=openid' \
  "https://${CUSTOM_DOMAIN}/oauth/v2/token"
```

### Personal access tokens and public keys

PATs are available only for service accounts, can expire or remain unexpired, and are displayed once. Send them directly as bearer tokens without exchange; they remain valid until expiration or deletion.

A service account can use a key generated and downloaded once or register an existing public key through `UserService.AddKey`; the JWT bearer profile uses the private key. A generated key with an expiration date expires at midnight on that date. ECDSA and ED25519 public keys are supported.

### Introspection credentials

A resource server calling introspection is an API application and authenticates with an application JWT profile or Basic credentials. This identity is separate from the frontend that supplied the token. A service account represents an outbound machine identity and is not an application type.

### Direct System API JWT

The self-hosted-only System API cannot use a service account. Define a lowercase system-user ID and public key in `SystemAPIUsers`; sign a JWT with `iss` and `sub` set to that ID and `aud` set to the exact public URL including scheme and port, then send it directly without OAuth exchange. X.509 certificates can also back system-API-user tokens.

Omitting memberships grants default System membership with `SYSTEM_OWNER`; explicit System, IAM, or Organization memberships narrow roles and aggregate scope.

```yaml
SystemAPIUsers:
  - system-user-1:
      Path: /keys/system-user-1.pub
      Memberships:
        - MemberType: System
          Roles: [SYSTEM_OWNER]
```

## Query audit events

The Event API requires `IAM_OWNER_VIEWER` or `IAM_OWNER`. `POST /admin/v1/events/_search` filters by sequence, editor, event or aggregate type and ID, resource owner, and creation date. `/admin/v1/events/types/_search` and `/admin/v1/aggregates/types/_search` enumerate technical and localized filter values.

```http
POST /admin/v1/events/_search
Content-Type: application/json

{"asc":false,"limit":1000,"creation_date":"2026-07-01T00:00:00Z","aggregate_types":["user"]}
```
