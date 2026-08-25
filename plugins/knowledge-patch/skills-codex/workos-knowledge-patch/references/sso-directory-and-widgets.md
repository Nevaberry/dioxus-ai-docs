# SSO, Directory Sync, Domains, and Widgets

Use this reference for identity-provider data, SSO lifecycle and providers,
Directory Sync semantics, organization domains, and embedded administration.

## Directory and identity-provider attributes

Directory data includes these predefined attributes:

- `display_name`
- `employee_number`
- `organization`
- `phone_numbers`
- `manager_name`
- `manager_id`

AuthKit can surface identity-provider custom attributes. Map them from SAML
responses or from standard and custom profile attributes on OIDC connections.

## Entra nested groups

Azure Entra ID does not provide deep nested-group expansion over SCIM. A
Directory Sync integration must not assume that transitive membership from
deeply nested Entra groups will be expanded automatically.

## SSO lifecycle

SSO sessions can enter a `Timed-out` state and emit additional lifecycle
events. Organizations with IT administrator email addresses configured can
receive direct notifications about SSO connection issues.

SSO adds a consent screen intended to protect sign-in from login CSRF and
phishing. WorkOS also emits events when SAML certificates are renewed.

## SSO and authentication providers

SSO supports Clever, Okta OIDC, Entra ID OIDC, and Google OIDC connection
types. Standalone SSO authorization URLs accept `provider_scopes`, and the
token response can contain `oauth_tokens`.

## Multiple roles from identity providers

Organization memberships can hold multiple roles across AuthKit, SSO, and
Directory Sync. In Admin Portal, IT administrators can map identity-provider
groups to roles during SSO setup.

## Organization domains

Preserve `verification_prefix` when deserializing organization domains. Admin
Portal prompts customers to verify a domain before configuring SSO.

## Embedded administration

Embeddable widgets cover:

- user profiles and organization switching;
- SSO setup and status;
- domain verification;
- Directory Sync; and
- log streaming.

Widgets can translate into the user's preferred language.
