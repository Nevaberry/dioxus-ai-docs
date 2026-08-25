# Security, Authentication, and Policy

## Security-sensitive upgrade fixes

### Authorization and privilege boundaries

3.7.2 closes unauthorized draft-line adjustment and administrator
password-reset privilege escalation. It also closes cross-channel Promotion
and FacetValue deletion and cross-channel Asset and StockLocation writes.

### Authentication, injection, and request handling

- 3.5.3 addresses native-auth timing enumeration.
- 3.6.2 addresses SQL injection through `languageCode` and Postgres search.
- 3.6.4 addresses asset-import SSRF.
- 3.6.5 addresses Dashboard XSS, SQLite list-query denial of service, and Shop
  API list-data exposure.

## Production credentials

From 3.7, production startup fails while the default superadmin password is
configured.

## External account linking

A custom `AuthenticationStrategy` must return `verified: true` for a
provider-verified email before an external login can link to an existing
account. Creating a new account is unaffected.

## API keys

3.6 adds core API-key authentication and Dashboard key management. API-key
sessions resolve their `Administrator` through the key owner.

## Row-level authorization

`EntityAccessControlStrategy` is the extension point for row-level access
control.

## Proxy handling

`ApiOptions` accepts `trustProxy`.

## Password policy

The password validation strategy supports `maxLength` and enforces a default
maximum.

## Customer-to-channel assignment

From 3.7, `CustomerChannelAssignmentStrategy` controls automatic
customer-to-channel assignment.

_Source batch: `official-changelog-2025-current`._
