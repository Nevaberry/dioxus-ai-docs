# Authentication and Sessions

## Editable identity data and customization

Dashboard users can edit user and organization metadata, including external
IDs. AuthKit supports custom metadata, external IDs, and JWT templates.

AuthKit is localized in 90 languages; embedded widgets can use a user's
preferred language. The sign-in UI identifies the last-used login method, and
authentication UI styling supports custom CSS and Google Fonts.

## Applications and platform embedding

WorkOS can manage identities and users across multiple applications. Platform
builders can embed AuthKit into every application created on their platform.

## Authentication providers

AuthKit includes built-in Intuit, Vercel, and Slack sign-in providers. Slack
sign-in uses the hosted AuthKit flow and does not require a separate Slack OAuth
implementation.

## Invitations

Two additional invitation events support tracking changes to pending
invitations. Invitations can also carry role selection; see the authorization
reference.

## Session management

Session APIs list active sessions and revoke a session by ID. Organization-aware
AuthKit token refresh remembers the most recently used organization.

## OAuth and redirect configuration

Configure custom OAuth scopes in the dashboard. Production redirect URIs may
contain wildcards.

## User email lifecycle

AuthKit synchronizes user email addresses with social login providers. User
email addresses can also be changed through the API or dashboard.

## Password history

Password history can reject reuse of up to 10 prior passwords for a user.

## Radar signup controls

Radar can block disposable-email services and traffic from selected countries
or regions. It can challenge suspicious signups by SMS.
