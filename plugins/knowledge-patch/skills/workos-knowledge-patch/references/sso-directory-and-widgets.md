# SSO, Directory Sync, Domains, and Widgets

## Directory and identity-provider attributes

Directory data includes these predefined attributes:

- `display_name`;
- `employee_number`;
- `organization`;
- `phone_numbers`;
- `manager_name`; and
- `manager_id`.

Surface identity-provider custom attributes in AuthKit by mapping values from
SAML responses or from standard and custom OIDC profile attributes.

## Entra nested groups

Azure Entra ID does not expand deeply nested group membership transitively over
SCIM. Do not assume a Directory Sync integration will automatically receive
members inherited through deep Entra group nesting.

## Embedded administration widgets

Embed administration widgets for:

- user profiles;
- organization switching;
- SSO setup and connection status;
- domain verification;
- Directory Sync; and
- log streaming.

Widgets can translate into the user's preferred language. Admin Portal prompts a
customer to verify a domain before configuring SSO.

## SSO session lifecycle and notifications

Handle the `Timed-out` SSO session state and the additional SSO lifecycle
events. When organizations provide IT administrator email addresses, WorkOS can
notify those administrators directly about SSO connection issues.

## Sign-in consent

SSO can present an additional consent screen designed to protect sign-in flows
from login CSRF and phishing attempts. Do not treat it as an unexpected
application redirect.

## Connection types

SSO supports Clever connections and the following OIDC connection types:

- Okta OIDC;
- Entra ID OIDC; and
- Google OIDC.

## Standalone SSO OAuth tokens

Pass `provider_scopes` when extra provider authorization is required in a
Standalone SSO authorization URL. The resulting SSO token response can include
`oauth_tokens`.

## Certificate-renewal events

Consume WorkOS webhook events for SAML certificate renewals so applications can
track renewal state without polling.
