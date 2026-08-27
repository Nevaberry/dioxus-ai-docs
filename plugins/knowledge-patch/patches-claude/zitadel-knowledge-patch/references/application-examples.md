# Application examples

## Embed Login or Console in an iframe

Login and Console pages reject framing by default with `frame-ancestors 'none'`, `X-Frame-Options: deny`, and `SameSite=Lax` cookies. Enable **Allow IFrame** in the instance Security Policy with an explicit parent-host allowlist. This removes `X-Frame-Options`, changes `frame-ancestors` to the allowed hosts, and uses `SameSite=None`, which requires HTTPS except on localhost.

```http
Content-Security-Policy: frame-ancestors https://app.example.com
```

## Implement a guest-account lifecycle

A privileged service account can silently create a temporary user tagged with timestamped guest metadata, then use OAuth 2.0 token exchange and user impersonation to issue a normal token for an HTTP-only client cookie. Registration upgrades the same identity by adding permanent profile and credential data and removing the guest tag. If the guest signs in to an existing account instead, merge application data and delete the orphaned temporary user.

## Restrict Management Console access

The Management Console cannot be completely disabled. Set the instance default redirect URI to the application; self-hosters can additionally block Console with a WAF or reverse proxy.

On Cloud, first grant the administrators' organization access to the default `ZITADEL` project, then use Update Project to enable `hasProjectCheck`. Console hides this switch for the default project. Enabling it before the grant can lock out administrators.

```sh
curl -X PUT "https://${CUSTOM_DOMAIN}/management/v1/projects/${PROJECT_ID}" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${PAT}" \
  --data '{"name":"ZITADEL","projectRoleAssertion":false,"projectRoleCheck":false,"hasProjectCheck":true,"privateLabelingSetting":"PRIVATE_LABELING_SETTING_UNSPECIFIED"}'
```
