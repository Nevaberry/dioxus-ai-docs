# SSO, Directory Sync, Domains, and Widgets

## Directory and identity-provider attributes

Directory data includes `display_name`, `employee_number`, `organization`,
`phone_numbers`, `manager_name`, and `manager_id` as predefined attributes.
Identity-provider custom attributes can appear in AuthKit through mappings from
SAML responses and standard or custom OIDC profile attributes.

## Embedded administration widgets

Embeddable widgets cover user profiles, organization switching, SSO setup and
status, domain verification, Directory Sync, and log streaming. Admin Portal
prompts customers to verify a domain before they configure SSO.

## SSO session lifecycle and consent

SSO sessions have a `Timed-out` state and additional lifecycle events.
Organizations with configured IT-admin email addresses can receive direct
notifications about SSO connection issues.

SSO adds a consent screen intended to reduce login CSRF and phishing risks.

## Providers and OAuth tokens

SSO supports Clever, Okta OIDC, Entra ID OIDC, and Google OIDC connections.
Standalone SSO authorization URLs accept `provider_scopes`; token responses can
include `oauth_tokens`.

## Entra nested groups

Azure Entra ID does not expand deeply nested groups transitively over SCIM.
Directory Sync integrations must not assume that membership inherited through
deep nesting will be expanded automatically.

## Certificate renewal

WorkOS emits webhook events for SAML certificate renewals.
