# Platform Products and Operations

## Contents

- [Admin Portal](#admin-portal)
- [Connect](#connect)
- [MCP authorization](#mcp-authorization)
- [WorkOS CLI](#workos-cli)
- [Pipes](#pipes)
- [Radar](#radar)
- [Vault BYOK](#vault-byok)
- [Audit Logs and log streaming](#audit-logs-and-log-streaming)
- [Organization API keys](#organization-api-keys)
- [Stripe Seat Sync](#stripe-seat-sync)
- [Email delivery and suppression](#email-delivery-and-suppression)
- [AuthKit analytics](#authkit-analytics)

## Admin Portal

Admin Portal supports a BYOK intent. Use it when directing an administrator into
customer-managed key configuration.

## Connect

Connect authorization can let a user select an organization. Connect also
supports:

- JWT templates for MCP and OAuth applications; and
- Client ID Metadata Documents for MCP clients.

## MCP authorization

Choose among the MCP-oriented products according to the surrounding
authentication architecture:

- Use AuthKit to authorize MCP servers.
- Use Standalone OAuth to add OAuth to a server that retains its existing
  authentication.
- Use Pipes MCP as a deployable MCP server that grants time-limited access to
  third-party data connections.

## WorkOS CLI

Bootstrap an AuthKit integration with:

```sh
npx workos@latest
```

AuthKit also supports secure authentication for users of command-line
applications.

## Pipes

Use Pipes to let application users connect third-party accounts. Supported
connections include:

- Asana;
- Box;
- Dropbox;
- Front;
- GitLab;
- HelpScout;
- HubSpot;
- Intercom;
- Jira; and
- Sentry.

## Radar

Use Radar signup controls to:

- block disposable email services;
- block traffic from selected countries or regions; and
- challenge suspicious signups by SMS.

## Vault BYOK

WorkOS Vault accepts customer-managed encryption keys from AWS KMS and Azure Key
Vault.

## Audit Logs and log streaming

Stream Audit Log data to Microsoft Sentinel.

## Organization API keys

Manage API keys belonging to organizations through the API.

## Stripe Seat Sync

Use Stripe Seat Sync to send active organization-member counts to Stripe
automatically.

## Email delivery and suppression

Send WorkOS email through a customer's:

- Amazon SES;
- Postmark;
- Resend;
- SendGrid; or
- Mailgun account.

Check whether an email address is suppressed and remove it from the suppression
list when appropriate.

## AuthKit analytics

Use AuthKit Add-ons to send signup, sign-in, and related events to Google
Analytics or Segment.
