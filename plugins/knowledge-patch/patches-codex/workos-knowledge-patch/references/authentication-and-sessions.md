# Authentication and Sessions

Use this reference for identity data, AuthKit customization, applications,
providers, invitations, sessions, email lifecycle, and OAuth configuration.

## Identity and metadata

User and organization metadata, including external ID, can be edited in the
dashboard. AuthKit supports custom metadata, external ID, and JWT templates.

At the SDK level, `Profile`, `User`, and `Actions` expose `name`; User
Management values carry `signalsId`; and organization memberships expose
`directoryManaged`. Authentication event deserialization preserves SSO
context.

## Presentation and localization

AuthKit is localized in 90 languages. Embedded widgets can translate into the
user's preferred language, and the sign-in interface identifies the last-used
login method. Customize authentication UI with CSS and Google Fonts.

## Applications and platform embedding

WorkOS can manage identity and users across multiple applications. A platform
can embed AuthKit into each application created on that platform.

## Authentication providers

AuthKit has built-in Intuit and Vercel providers. Sign in with Slack provides a
hosted Slack sign-in option without requiring a separate Slack OAuth flow.

Identity deserialization normalizes GitHub's provider value to `GitHubOAuth`,
not `GithubOAuth`.

## Authorization URL inputs

The Node SDK's `getAuthorizationUrl` accepts:

- `claimNonce` for nonce-bound claims;
- `invitationToken` for invitation flows; and
- `max_age` for requested authentication age.

Standalone SSO authorization URLs accept `provider_scopes`, and their token
responses can include `oauth_tokens`.

## Invitations and email lifecycle

Invitations accept `role_slug`. Two additional invitation events allow pending
invitation changes to be tracked.

AuthKit keeps a user's email synchronized with the social provider. Email can
also be changed through the API or dashboard. Password-history policy can
reject reuse of up to 10 previous passwords.

## Session management

Session APIs list active sessions and revoke an individual session by ID.
AuthKit token refresh remembers the most recently used organization.
`CookieSession` is exported from the Node package root.

When calling `CookieSession.refresh()` under the SDK contract attributed to
`10.10.0`, distinguish retryable transient failures from terminal refresh
failures rather than treating every failure identically.

Action contexts expose the authentication method, so action handlers can
inspect how the active authentication was performed (`10.10.0`).

## OAuth and redirect configuration

Custom OAuth scopes are configurable in the dashboard. Production redirect
URIs may contain wildcards. Keep the application's dashboard redirect and
logout settings aligned with deployed hosts and paths.
