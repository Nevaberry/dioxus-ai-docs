# Platform Products and Operations

## Admin Portal and embedded administration

Admin Portal supports a BYOK intent. Its client namespace is `adminPortal` in
Node SDK v9 and later.

## Connect

Connect applications can let users choose an organization during authorization.
Connect supports JWT templates for MCP and OAuth applications and Client ID
Metadata Documents for MCP clients.

## MCP authorization

Use AuthKit to authorize MCP servers. Standalone OAuth adds OAuth to a server
that retains its existing authentication. Pipes MCP is a deployable MCP server
that grants time-limited access to third-party data connections.

## WorkOS CLI

Bootstrap an AuthKit integration with:

```sh
npx workos@latest
```

AuthKit can securely authenticate users of command-line applications.

## Pipes data connections

Pipes lets application users connect third-party accounts. Supported connection
types include Asana, Box, Dropbox, Front, GitLab, HelpScout, HubSpot, Intercom,
Jira, and Sentry.

## Audit Logs

Audit Logs can stream log data to Microsoft Sentinel. Node integrations can list
schemas with `auditlogs.listSchemas`.

## API keys

Organization-owned API keys can be managed through an API.

## Stripe seat synchronization

Stripe Seat Sync can automatically report active organization-member counts to
Stripe.

## Custom email delivery and suppression

WorkOS can deliver email through a customer's Amazon SES, Postmark, Resend,
SendGrid, or Mailgun account. Applications can check whether an email address is
suppressed and remove it from the suppression list.

## Vault BYOK

Vault supports customer-managed encryption keys from AWS KMS and Azure Key
Vault.

## AuthKit analytics

AuthKit Add-ons can send signup, sign-in, and related events to Google Analytics
or Segment.
