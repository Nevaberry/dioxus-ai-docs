# Platform Products and Operations

Use this reference to select and integrate Connect, MCP, CLI authentication,
Pipes, Radar, Vault BYOK, Audit Logs, email delivery, analytics, Stripe, and
Agents.

## Connect

Connect applications can let users select an organization during
authorization. Connect supports JWT templates for MCP and OAuth applications
and Client ID Metadata Documents for MCP clients.

The Node SDK has a Connect module. Automatic pagination accepts pagination
options and serializes them when following pages.

## MCP authorization

- AuthKit can authorize an MCP server with hosted user authentication.
- Standalone OAuth adds OAuth to a server that keeps its existing
  authentication system.
- Pipes MCP is a deployable MCP server that grants time-limited access to
  third-party data connections.

## WorkOS CLI and command-line authentication

Bootstrap an AuthKit integration with:

```sh
npx workos@latest
```

AuthKit can also authenticate users of command-line applications. Use the
public-client PKCE flow and retain the verifier in secure storage across
process restarts.

## Pipes

Pipes lets application users connect accounts from Asana, Box, Dropbox, Front,
GitLab, HelpScout, HubSpot, Intercom, Jira, and Sentry.

The SDK additions attributed to `10.10.0` add Pipes API-key installation plus
Data Integration operations and models.

## Radar and headless AuthKit

Radar can block disposable email services and traffic from selected countries
or regions. It can challenge suspicious signups by SMS.

The Node SDK exposes Radar, includes Radar fields on headless AuthKit methods,
supports completing challenges, and returns typed challenge errors.

## Vault and BYOK

Vault supports customer-managed encryption keys from AWS KMS and Azure Key
Vault. Admin Portal provides a BYOK intent.

In Node SDK v10, object listing returns auto-paginatable object summaries and
generated key and object response fields use camelCase. Vault also supports
rekeying, object-list filters, and version checks when deleting objects. Handle
the typed `vault.byok_key.verification_completed` event.

## Audit Logs and log streaming

List Audit Log schemas with `auditlogs.listSchemas`. Audit Logs can stream data
to Microsoft Sentinel. Embeddable administration also provides a log-streaming
widget.

## Email delivery and suppression

WorkOS can deliver email through a customer's Amazon SES, Postmark, Resend,
SendGrid, or Mailgun account. Applications can check suppressed addresses and
remove them from the suppression list.

## Analytics and billing

AuthKit Add-ons send signup, sign-in, and related events to Google Analytics or
Segment. Stripe Seat Sync sends active organization-member counts to Stripe
automatically.

## Agents

The SDK contracts attributed to `10.10.0` add
`linkClaimAttemptToExternalUser`, agent-registration read methods, credential
validation, and the agent registration ID in API-key validation results.

## Request behavior for platform clients

The HTTP client supports configurable automatic retries (`10.10.0`). DELETE
requests also retain parameters supplied through `{ query: ... }` in that SDK
contract, which matters for platform operations that filter or scope deletion.
