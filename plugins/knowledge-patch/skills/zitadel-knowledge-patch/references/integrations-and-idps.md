# Service integration and identity providers

- [Hosted organization bootstrap](#hosted-organization-bootstrap)
- [External IdP placement and account controls](#external-idp-placement-and-account-controls)
- [External-provider callback routes](#external-provider-callback-routes)
- [Generic external-provider templates](#generic-external-provider-templates)
- [Microsoft Entra OIDC template](#microsoft-entra-oidc-template)
- [External SAML provider endpoint roles](#external-saml-provider-endpoint-roles)
- [JWT identity-provider relay](#jwt-identity-provider-relay)
- [LDAP provider contract](#ldap-provider-contract)
- [Generic OIDC provider migration](#generic-oidc-provider-migration)
- [Cloudflare Zero Trust OIDC](#cloudflare-zero-trust-oidc)
- [Google Cloud Workforce Identity Federation](#google-cloud-workforce-identity-federation)
- [Google Workspace SAML identity matching](#google-workspace-saml-identity-matching)
- [Apache mod_auth_openidc](#apache-mod_auth_openidc)
- [Service-account client credentials](#service-account-client-credentials)
- [Service-account personal access tokens](#service-account-personal-access-tokens)
- [Service-account public-key registration](#service-account-public-key-registration)
- [Introspection credentials belong to API applications](#introspection-credentials-belong-to-api-applications)
- [Direct System API authentication](#direct-system-api-authentication)
- [Event API audit queries](#event-api-audit-queries)

## Hosted organization bootstrap

The hosted `${CUSTOM_DOMAIN}/ui/login/register/org` form creates an organization and its first user with `ORG_OWNER`; deployments that provision customers themselves can disable it through `AdminService.SetRestrictions`. A custom onboarding flow can instead call `POST /admin/v1/orgs/_setup` with the organization, one password-authenticated human, and optional roles, which default to `ORG_OWNER`.

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

## External IdP placement and account controls

An external provider can be an instance default available to every organization or belong to one organization for tenant-specific SSO; the applicable login policy must enable **External IDP Allowed**. Provider settings independently control automatic creation and profile updates, manual account creation and linking, and automatic matching by username or email, so disable the manual options when an automatic flow must not expose an edit or link choice.

## External-provider callback routes

External OAuth and OIDC providers use `${CUSTOM_DOMAIN}/ui/login/login/externalidp/callback` with Login V1 and `${CUSTOM_DOMAIN}/idps/callback` with Login V2. Apple's form-post response needs the V1 callback's `/form` suffix, while the V2 callback already accepts POST.

## Generic external-provider templates

The Generic OIDC template takes an issuer, client ID and secret, and ensures `openid` is requested. The separate Generic OAuth template takes explicit authorization, token, and user-information endpoints plus the response field used as the external user ID, enabling providers such as LinkedIn whose user ID is `sub`.

## Microsoft Entra OIDC template

The Microsoft template always sends `openid` and `User.Read`; Entra should return `email`, `family_name`, `given_name`, and `preferred_username`, and ZITADEL's **Email Verified** option is what treats its email as verified because Entra does not send that claim. Its Common, Organizations, Consumers, or specific Tenant ID mode must match the account types configured on the Entra application.

## External SAML provider endpoint roles

When ZITADEL consumes an external SAML IdP, import that IdP's metadata and give the upstream provider ZITADEL's SP metadata at `/idps/{providerID}/saml/metadata`. The provider details expose distinct **ACS Login Form** for Login V1, **ACS Intent API** for Login V2 or programmatic flows, and **Single Logout** URLs; use the matching ACS as both consumer URL and recipient, and the metadata URL as the SP entity ID or audience.

## JWT identity-provider relay

A JWT IdP is configured with an issuer, header name, JWKS endpoint, JWT endpoint, and optional audience; ZITADEL validates the signature, `iss`, `exp`, and configured `aud` but does not re-authenticate the user. The JWT endpoint must recover the existing browser session, preserve every query parameter from ZITADEL, and proxy the token in the configured header to the matching callback.

```text
Login V1  https://${CUSTOM_DOMAIN}/ui/login/idps/jwt?<unchanged-query>  x-custom-tkn: <JWT>
Login V2  https://${CUSTOM_DOMAIN}/idps/jwt?<unchanged-query>           x-custom-tkn: <JWT>
```

## LDAP provider contract

An LDAP provider declares `schema://host:port` servers, `BaseDN`, search bind credentials, user base, attribute mappings, and a required ID attribute; login-name filters are OR-joined while required object classes are AND-joined. Prefer LDAPS or enable StartTLS, and note that a configured timeout of `0s` uses the 60-second default.

```text
filters [uid, email] + login user@example.com
=> (|(uid=user@example.com)(email=user@example.com))
```

## Generic OIDC provider migration

The instance Admin and organization Management `MigrateGenericOIDCProvider` operations convert an existing generic provider to the Google or Entra template without deleting its linked users. With Terraform, remove the old generic resource from state, call the migration API, then import the typed resource as `<provider-id>:<client-secret>` before applying again.

```sh
terraform state rm zitadel_idp_oidc.old
terraform import zitadel_idp_google.google '<provider-id>:<client-secret>'
```

## Cloudflare Zero Trust OIDC

Cloudflare's application callback is `https://<team>.cloudflareaccess.com/cdn-cgi/access/callback`, and the ZITADEL application must enable **User Info inside ID Token** or Cloudflare reports that no email was returned. Configure `openid profile email` and disable PKCE because this integration cannot supply the client secret in the PKCE mode Cloudflare expects.

```json
{"scopes":["openid","profile","email"],"pkce_enabled":false}
```

## Google Cloud Workforce Identity Federation

Google Cloud Workforce Identity Federation uses a ZITADEL Web application with the Implicit grant, ID-token response type, and no client authentication, plus Google's `auth.cloud.google` workforce-pool callback. Set the access-token type to JWT and enable both roles and user information in the ID token; map project roles into the Google group claim format when group-based IAM bindings are needed.

## Google Workspace SAML identity matching

Google Workspace SSO requires the same domain to be verified and set as an organization domain in ZITADEL, and the Workspace username must equal the ZITADEL username rather than merely sharing its email address. The organization-wide profile uses entity ID `google.com/a/<domain>` and ACS `https://www.google.com/a/<domain>/acs`; Workspace super administrators cannot be used to test SSO.

## Apache `mod_auth_openidc`

Register Apache as a PKCE application and enable Development Mode when its redirect is non-HTTPS. `mod_auth_openidc` needs a protected vanity redirect path with no content and uses S256 PKCE without a client secret.

```apache
OIDCProviderMetadataURL https://${CUSTOM_DOMAIN}/.well-known/openid-configuration
OIDCClientID <client-id>
OIDCRedirectURI https://app.example/secure/callback
OIDCCryptoPassphrase <random-secret>
OIDCScope "openid profile"
OIDCPKCEMethod S256
```

## Service-account client credentials

Generating a service-account client secret reveals the secret only once; exchange it with HTTP Basic authentication and the `client_credentials` grant, for which ZITADEL requires the `openid` scope. The resulting service-account access token is opaque by default, but its token type can be changed to JWT in the service-account settings.

```sh
curl -u "$CLIENT_ID:$CLIENT_SECRET" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials&scope=openid' \
  "https://${CUSTOM_DOMAIN}/oauth/v2/token"
```

## Service-account personal access tokens

Personal access tokens are available only for service accounts, may have an expiration or remain unexpired, and are displayed only once. Send them directly as bearer tokens without a token exchange; they remain usable until expiration or deletion.

## Service-account public-key registration

A service account can use a key generated and downloaded once by ZITADEL or register an existing public key through `UserService.AddKey`; the service-account JWT profile then uses the corresponding private key. A generated key with an expiration date expires at midnight on that date.

## Introspection credentials belong to API applications

A resource server that calls introspection is registered as an API application and authenticates that call with either an application JWT profile or Basic credentials; this identity is separate from the frontend that supplied the token. A service account represents an outbound machine identity and is not an application type in ZITADEL.

## Direct System API authentication

The self-hosted-only System API cannot be accessed by a service account: define a lowercase system-user ID and public key in runtime `SystemAPIUsers`, sign a JWT with `iss` and `sub` set to that ID and `aud` set to the exact public URL including scheme and port, and send it directly without an OAuth token exchange. Omitting memberships grants the default System membership with `SYSTEM_OWNER`; explicit System, IAM, or Organization memberships can narrow its roles and aggregate scope.

```yaml
SystemAPIUsers:
  - system-user-1:
      Path: /keys/system-user-1.pub
      Memberships:
        - MemberType: System
          Roles: [SYSTEM_OWNER]
```

## Event API audit queries

Reading the Event API requires `IAM_OWNER_VIEWER` or `IAM_OWNER`; `POST /admin/v1/events/_search` can filter by sequence, editor user, event or aggregate type and ID, resource owner, and creation date. `/admin/v1/events/types/_search` and `/admin/v1/aggregates/types/_search` enumerate the technical and localized values clients can put into those filters.

```http
POST /admin/v1/events/_search
Content-Type: application/json

{"asc":false,"limit":1000,"creation_date":"2026-07-01T00:00:00Z","aggregate_types":["user"]}
```
