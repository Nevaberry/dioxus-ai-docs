# Integrations and Public Exports

## Email generation and transport

Email generators may be asynchronous. `SMTPTransportOptions` accepts
pooled-SMTP settings.

In 3.7, the email plugin moves from MJML 4 to 5 and nodemailer 6 to 9, so
custom templates and transports need compatibility review.

## Mollie integration

MolliePlugin moves to the Payments API and requires
`@mollie/api-client@4.3.3` for the 3.4 upgrade. It supports Klarna and a
plugin-level `immediateCapture` override.

## Stripe integration

`StripeService` is publicly exported for custom payment flows.

## Sentry integration

The Sentry plugin moves to `@sentry/nestjs`, changing its configuration, and
can capture logs. A missing DSN is logged rather than thrown.

## GraphiQL package

`@vendure/graphiql-plugin` is available as a standalone package.

## Public core exports

Core publicly exports:

- `OrderableAsset`.
- FSM utility functions.
- The `Province` entity.
- `ProvinceService`.

## Direct dependencies and validation packages

From 3.7, `@nestjs/terminus` is no longer supplied transitively. Custom health
checks must declare it directly.

The Dashboard supports Zod 4 and re-exports Zod from `@vendure/dashboard`.

_Source batch: `official-changelog-2025-current`._
