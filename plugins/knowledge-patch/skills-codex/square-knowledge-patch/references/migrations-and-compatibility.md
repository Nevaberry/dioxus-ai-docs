# Migrations and compatibility

## Customer cards

With Square API version `2025-01-23`, `Customer.cards` is retired. Enumerate
cards with `ListCards?customer_id=...` and gift cards with
`ListGiftCards?customer_id=...`.

`CreateCustomerCard` and `DeleteCustomerCard` remain deprecated. No retirement
date is specified for them here.

## Reader SDK and Mobile Authorization

Reader SDK and its Mobile Authorization API were scheduled for retirement on
December 31, 2025. Migrate to Mobile Payments SDK, which has its own
authorization methods.

## Rewritten language SDKs

The rewritten SDK generations are:

- Node.js 40
- PHP 41
- Java 44
- .NET 41
- Python 42
- Ruby 44

These generations change class and method shapes and add auto-pagination.
Integrations should follow the respective migration guides for ongoing API
updates.

Node.js uses native `fetch`. Python supports Pydantic validation and
`ApiError`-derived exceptions with Python 3.8+. Ruby requires 3.1+. As of
June, every webhook payload has a corresponding SDK object.

## Webhook retries

The final retry policy is at most 11 retries over 24 hours for webhook
subscriptions on every Square API version. It supersedes the January policy of
19 retries over 48 hours.

## Labor scheduling and Timecard migration

Beta scheduling provides these operations for draft and published schedules:

- `CreateScheduledShift`
- `UpdateScheduledShift`
- `PublishScheduledShift`
- `BulkPublishScheduledShifts`
- `RetrieveScheduledShift`
- `SearchScheduledShifts`

All `Shift` endpoints, types, and webhooks are deprecated in favor of
`Timecard` equivalents for create, update, delete, retrieve, and search.
`GetShift` becomes `RetrieveTimecard`.

## Offline payment details

`CreatePayment.offline_payment_details` was deprecated in August and was
scheduled for retirement on November 19, 2025.

## Loyalty reward definitions

`LoyaltyProgramRewardTier.definition` is retired. Resolve reward discount
details through `pricing_rule_reference` instead.

## Cross-location inventory movement

As of Square version `2026-07-15`, cross-location movement is an `ADJUSTMENT`
with `from_location_id` and `to_location_id`.

The following are retired:

- `TRANSFER`
- `InventoryTransfer`
- `RetrieveInventoryTransfer`
- `InventoryAdjustment.location_id`

Responses expose the `UNTRACKED` state plus Square-generated inferred and
component adjustments.
