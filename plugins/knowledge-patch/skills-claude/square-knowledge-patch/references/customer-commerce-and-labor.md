# Customers, invoices, subscriptions, and labor

## Invoice creator, attachments, and hosted links

`Invoice.creator_team_member_id` identifies a logged-in team member who created
an invoice in Dashboard or the Invoices app.

Sandbox allows only 1 KB total attachments per invoice, compared with 25 MB in
production.

Once an invoice is published and reaches any scheduled date, `public_url`
points to a temporary hosted payment link. Retrieving the invoice refreshes an
aging link. Link expiry or regeneration emits no `invoice.updated` webhook.

## Completed subscriptions

Fixed-phase subscriptions can enter the non-billing, non-resumable `COMPLETED`
status. They expose their expected `completed_date` and can receive a
`SubscriptionAction` of type `COMPLETE`.

Plans containing any non-fixed-length phase have no defined completion date,
so `completed_date` is unset.

## Scheduled shifts

Beta scheduling provides these operations for draft and published schedules:

- `CreateScheduledShift`
- `UpdateScheduledShift`
- `PublishScheduledShift`
- `BulkPublishScheduledShifts`
- `RetrieveScheduledShift`
- `SearchScheduledShifts`

## Timecard migration

All `Shift` endpoints, types, and webhooks are deprecated in favor of
`Timecard` equivalents for create, update, delete, retrieve, and search.
`GetShift` becomes `RetrieveTimecard`.

## GraphQL Labor entry points

Square GraphQL adds `scheduledShifts` and `timecards` for Labor data.
`timecards` replaces deprecated `shifts`.
