# Application examples

## Iframe embedding policy

Login and Console pages reject framing by default with `frame-ancestors 'none'`, `X-Frame-Options: deny`, and `SameSite=Lax` cookies. Enabling **Allow IFrame** in the instance Security Policy for an explicit parent-host allowlist removes `X-Frame-Options`, changes `frame-ancestors` to those hosts, and uses `SameSite=None`, which requires HTTPS except on localhost.

```http
Content-Security-Policy: frame-ancestors https://app.example.com
```

## Guest-account lifecycle

A privileged service account can silently create a temporary user tagged with timestamped guest metadata, then use OAuth 2.0 token exchange and user impersonation to issue a normal token for an HTTP-only client cookie. Registration upgrades that same identity by adding permanent profile and credential data and removing the guest tag. If the guest instead signs in to an existing account, merge the application data and delete the orphaned temporary user.

## Restricting Management Console access

The Management Console cannot be completely disabled. Set the instance default redirect URI to the application, and self-hosters can additionally block Console access with a WAF or reverse proxy. On Cloud, first grant the administrators' organization access to the default `ZITADEL` project, then use the Update Project API to enable `hasProjectCheck`; Console hides this switch for the default project, and enabling it before the grant risks administrator lockout.

```sh
curl -X PUT "https://${CUSTOM_DOMAIN}/management/v1/projects/${PROJECT_ID}" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${PAT}" \
  --data '{"name":"ZITADEL","projectRoleAssertion":false,"projectRoleCheck":false,"hasProjectCheck":true,"privateLabelingSetting":"PRIVATE_LABELING_SETTING_UNSPECIFIED"}'
```
