# Authentication and Sessions

## Identity data and token customization

Edit user and organization metadata, including external ID, in the dashboard.
AuthKit supports custom metadata, external ID, and JWT templates, so keep token
generation and application-side metadata handling aligned with the configured
template.

AuthKit keeps a user's email address synchronized with their social login
provider. User email addresses can also be changed through the API or dashboard.

## Presentation and localization

AuthKit is localized in 90 languages and identifies the last-used login method
in the sign-in UI. Customize the authentication UI with CSS and Google Fonts.

## Applications and platform embedding

Use WorkOS to manage identity and users across multiple applications. Platform
builders can embed AuthKit separately into each application created on their
platform.

## Authentication providers

AuthKit includes built-in Intuit and Vercel providers.

AuthKit also supports Sign in with Slack. Use it as a hosted sign-in option
instead of building and maintaining a separate Slack OAuth flow.

## Invitations

Handle the two additional invitation lifecycle events when tracking changes to
pending invitations. Do not infer pending-invitation state only from the
original creation and acceptance events.

## Session management

Use the Session Management API to list active sessions and revoke an individual
session by ID.

AuthKit token refresh remembers the most recently used organization. Preserve
that organization-aware behavior when wrapping or replacing the built-in refresh
flow.

## OAuth and redirects

Configure custom OAuth scopes in the dashboard. Production redirect URIs may
contain wildcards; validate that a deployment's redirect still matches the
dashboard configuration.

## Password history

Configure password history to reject reuse of as many as 10 previous passwords
for a user.
