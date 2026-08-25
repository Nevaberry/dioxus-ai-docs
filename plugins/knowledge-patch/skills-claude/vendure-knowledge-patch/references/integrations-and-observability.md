# Integrations and observability

Source batch: `official-changelog-2025-current`.

## Email generation and transport

Email generators may be asynchronous. `SMTPTransportOptions` accepts
pooled-SMTP settings.

In 3.7, the email plugin moves from MJML 4 to 5 and nodemailer 6 to 9. Custom
templates and transports need compatibility review.

## Mollie

MolliePlugin moves to the Payments API and requires
`@mollie/api-client@4.3.3` for the 3.4 upgrade. It supports Klarna and a
plugin-level `immediateCapture` override.

## Stripe

`StripeService` is publicly exported for custom payment flows.

## Sentry

The Sentry plugin moves to `@sentry/nestjs`, changing its configuration, and
can capture logs. A missing DSN is logged rather than thrown.
