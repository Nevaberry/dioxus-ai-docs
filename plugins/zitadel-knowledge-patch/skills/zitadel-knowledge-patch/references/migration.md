# Migration Guides

## Migration Tools CLI (`zitadel-tools`)

Go CLI for converting exports from other identity providers into Zitadel's import JSON format:

```bash
# Auth0: requires two input files
zitadel-tools migrate auth0 --org= --passwords=./passwords.ndjson --multiline --email-verified --output=./importBody.json --timeout=5m0s <ORG_ID >--users=./profiles.json

# Keycloak: uses realm export JSON
zitadel-tools migrate keycloak --org= --output=./importBody.json --timeout=5m0s --multiline <ORG_ID >--realm=./realm-export.json
```

Install from: https://github.com/zitadel/zitadel-tools

## Bulk Import API (`POST /admin/v1/import`)

Accepts organizations with users, hashed passwords, OTP codes, and IdP links:

```json
{
  "timeout": "10m",
  "dataOrgs": {
    "orgs": [
      {
        "orgId": "<existing-org-id>",
        "humanUsers": [
          {
            "userId": "optional-custom-id",
            "user": {
              "userName": "user@example.com",
              "profile": { "firstName": "Jane", "lastName": "Doe" },
              "email": { "email": "jane@example.com", "isEmailVerified": true },
              "hashedPassword": {
                "value": "$2a$14$...",
                "algorithm": "bcrypt"
              },
              "otpCode": "JBSWY3DPEHPK3PXP",
              "requestPasswordlessRegistration": false,
              "idps": [
                { "configId": "<idp-config-id>", "externalUserId": "ext-id", "displayName": "name" }
              ]
            }
          }
        ]
      }
    ]
  }
}
```

**Limits**: Cloud has 5-minute timeout (~5,000 users per batch). Response includes `success` and `errors` arrays.

## Individual User Import (`ImportHumanUser`)

`POST /management/v1/users/human/_import` with same user schema (without org/batch wrapper).

## Export/Import Between Zitadel Instances

```bash
# Export
curl -X POST $SOURCE/admin/v1/export \
  -H "Authorization: Bearer $PAT" \
  -d '{
    "org_ids": [],
    "excluded_org_ids": [],
    "with_passwords": true,
    "with_otp": true,
    "timeout": "30s",
    "response_output": true
  }' -o export.json

# Import
curl -X POST $TARGET/admin/v1/import \
  -H "Authorization: Bearer $PAT" \
  -d '{"timeout": "10m", "data_orgsv1": '"$(cat export.json)"'}'
```

Export supports GCS output via `gcs_output: { path, bucket, serviceaccount_json }` for large datasets.

**Not migrated**: Global policies, instance members, global IDPs, global 2FA/MFA settings, machine keys, PATs, application keys, passkey credentials. Audit trail (events) is also lost.

## Password Hash Import & Rehashing

Supported algorithms: bcrypt, argon2, scrypt, md5, SHA2, PHPass, Drupal7. On first login, imported hash is validated then rehashed with configured algorithm (default: bcrypt).

If you can't transfer hashes, create users without passwords — they'll be prompted on first login.

## Just-in-Time Migration Patterns

**Zitadel-orchestrated** (Actions V2): Pre-authentication action target fetches user from legacy system, creates in Zitadel on first login. Optional post-auth action flags migrated users.

**Legacy-orchestrated**: Legacy system creates users in Zitadel via API on login, redirects with `login_hint`.

**Identity brokering**: Configure legacy system as external IdP (supports JWT-IDP for token-only). Users auto-register on first IdP login; Actions pull additional data from legacy.

## IdP-Linked User Migration

`configId` must reference a Zitadel IdP config using the **same Client ID** as the legacy system. The user's `sub` is bound to the IdP's Client ID.

## Passkey Migration Limitation

Passkeys (FIDO2/WebAuthn) cannot be directly migrated. New auth server must use same domain for existing registrations. Use `requestPasswordlessRegistration: true` to prompt re-registration.

## CockroachDB to PostgreSQL Migration

```bash
zitadel mirror --from-config cockroach.yaml --to-config postgres.yaml
```
CockroachDB support removed in v3.0.
