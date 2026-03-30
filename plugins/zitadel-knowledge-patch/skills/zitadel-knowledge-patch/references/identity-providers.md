# Identity Providers & Federation

## Supported IdP Types

| Template | Protocol | Notes |
|----------|----------|-------|
| Google | OIDC | Dedicated template with Google-specific defaults |
| Apple | OIDC | Uses `form_post` response mode; V1 callback ends in `/form` |
| Entra ID (Azure AD) | OIDC | Configurable tenant: Common, Organizations, Consumers, or specific Tenant ID |
| Entra ID SAML | SAML | Uses SAML Toolkit enterprise app in Entra |
| GitHub | OAuth | Uses Generic OAuth under the hood |
| GitLab | OIDC | Supports self-hosted instances |
| LinkedIn | OAuth | Uses Generic OAuth template |
| Keycloak | OIDC | Uses Generic OIDC template |
| Okta (OIDC) | OIDC | Uses Generic OIDC template |
| Okta (SAML) | SAML | Uses SAML SP template |
| OneLogin | SAML | Uses SAML SP template |
| PingFederate | SAML | Uses SAML SP template |
| Generic OIDC | OIDC | Any OIDC-compliant provider; requires issuer URL |
| Generic OAuth | OAuth | Requires explicit auth, token, user endpoints + ID attribute |
| SAML SP | SAML | Any SAML IdP; uses metadata URL or XML |
| LDAP | LDAP | Native LDAP bind authentication |
| JWT IdP | JWT | WAF/proxy-based SSO using external JWTs |

## Callback URLs: Login V1 vs V2

- **Login V1**: `${CUSTOM_DOMAIN}/ui/login/login/externalidp/callback`
- **Login V1 (Apple/form_post)**: `${CUSTOM_DOMAIN}/ui/login/login/externalidp/callback/form`
- **Login V2**: `${CUSTOM_DOMAIN}/idps/callback` (accepts both GET and POST)

## Generic OAuth Provider (Not OIDC)

For providers without OIDC discovery, use Generic OAuth. Unlike Generic OIDC (which only needs issuer URL), it requires:
- Authorization endpoint URL
- Token endpoint URL
- User info endpoint URL
- ID attribute name (field in userinfo response for user ID)

## JWT IdP: WAF/Proxy-Based SSO

For systems that issue JWTs but aren't full OIDC providers (WAFs, legacy apps):

1. App initiates OIDC login with Zitadel
2. Zitadel redirects to configured **JWT Endpoint** (behind WAF/legacy domain)
3. WAF recognizes session, generates JWT, injects in configured **HTTP header**
4. WAF proxies request (with query params) to Zitadel's `/idps/jwt` endpoint
5. Zitadel validates JWT signature (via Keys Endpoint), issuer, expiry
6. OIDC flow completes

Configuration fields:
- **JWT Endpoint**: URL where Zitadel redirects (must share domain with existing app for cookies)
- **Issuer**: Expected `iss` claim value
- **Keys Endpoint**: Public key URL for signature verification
- **Header Name**: HTTP header carrying JWT (defaults to `Authorization`)

```js
// Cloudflare Worker forwarding JWT to Zitadel
export default {
  async fetch(request, env) {
    const jwt = await getJwtForCurrentSession(request, env);
    const userUrl = new URL(request.url);
    const zitadelUrl = new URL(env.ZITADEL_JWT_IDP_ENDPOINT);
    userUrl.searchParams.forEach((v, k) => zitadelUrl.searchParams.set(k, v));
    return fetch(zitadelUrl.toString(), {
      method: "GET",
      headers: { "x-custom-tkn": jwt },
      redirect: "manual",
    });
  }
}
```

## LDAP Configuration

Native LDAP/Active Directory support (not via OIDC/SAML wrapper):

| Field | Description |
|-------|-------------|
| Servers | `ldap://host:389` or `ldaps://host:636` (list) |
| BaseDN | Base DN (e.g., `dc=example,dc=com`) |
| BindDN + BindPassword | Admin credentials for search |
| Userbase | Base attribute for lookup (typically `dn`) |
| User Filters | Attributes OR-joined in search (e.g., `uid`, `email`) |
| User Object Classes | Required objectClasses AND-joined |
| LDAP Attributes | Mapping to Zitadel attrs (ID attribute required) |
| StartTLS | Enable TLS upgrade |
| Timeout | Connection timeout (default 60s) |

LDAP requires network access from Zitadel to LDAP server — **not available on Zitadel Cloud**.

## IdP Template Common Settings

All templates share these provisioning settings:
- **Automatic creation**: Auto-create user on first external login
- **Automatic update**: Sync profile changes on each login
- **Automatic linking**: Auto-link to existing account by username/email match
- **Account creation allowed**: Allow manual account creation during external login
- **Account linking allowed**: Allow manual linking to existing account

## Organization-Level IdP Scoping (B2B)

- **Instance-level (default)**: Available to all orgs — use for universal providers (Google, GitHub)
- **Organization-level**: Scoped to specific org — use for B2B (Customer A → Entra ID, Customer B → Okta)

Login policy must have "External IDP Allowed" enabled. Use `urn:zitadel:iam:org:domain:primary:{domain}` scope to show only that org's IdPs.

## IdP Migration API

Migrate Generic OIDC → specific template (Entra ID/Google) without breaking linked users:
- Instance-level: `AdminService.MigrateGenericOIDCProvider`
- Org-level: `ManagementService.MigrateGenericOIDCProvider`

For Terraform: remove old from state, make API migration call, import as new resource type.

## Account Linking Auto-Redirect

Once linked to an external IdP, login **automatically redirects** to that IdP — no choice between local/external. Only on external login failure does Zitadel fall back to local auth. Users only choose during **registration**, not subsequent logins.
