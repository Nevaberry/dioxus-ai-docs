# API and SDK migrations

## Customer cards

With Square API version `2025-01-23`, `Customer.cards` is retired. Enumerate
cards with `ListCards?customer_id=...` and gift cards with
`ListGiftCards?customer_id=...`.

`CreateCustomerCard` and `DeleteCustomerCard` remain deprecated, although no
retirement date is given for them here.

## Reader SDK and Mobile Authorization

Reader SDK and its Mobile Authorization API were scheduled for retirement on
December 31, 2025. Migrate to Mobile Payments SDK, which has its own
authorization methods.

## Rewritten language SDKs

The rewritten SDK generations change class and method shapes and add
auto-pagination. Follow the respective migration guides for ongoing API
updates.

| Language | SDK generation | Details |
| --- | ---: | --- |
| Node.js | 40 | Uses native `fetch` |
| PHP | 41 | — |
| Java | 44 | — |
| .NET | 41 | — |
| Python | 42 | Supports Pydantic validation and `ApiError`-derived exceptions; requires Python 3.8+ |
| Ruby | 44 | Requires Ruby 3.1+ |

As of June, every webhook payload has a corresponding SDK object.

## Labor `Shift` to `Timecard`

All `Shift` endpoints, types, and webhooks are deprecated in favor of
`Timecard` equivalents for create, update, delete, retrieve, and search.
`GetShift` becomes `RetrieveTimecard`.

Square GraphQL adds `timecards` for Labor data, replacing deprecated `shifts`.

## Inventory movement model

As of Square version `2026-07-15`, cross-location movement is an `ADJUSTMENT`
with `from_location_id` and `to_location_id`.

The following are retired:

- `TRANSFER`
- `InventoryTransfer`
- `RetrieveInventoryTransfer`
- `InventoryAdjustment.location_id`

Responses now expose the `UNTRACKED` state plus Square-generated inferred and
component adjustments.

## Loyalty reward definitions

`LoyaltyProgramRewardTier.definition` is retired. Resolve reward discount
details through `pricing_rule_reference` instead.

## Offline payment requests

`CreatePayment.offline_payment_details` was deprecated in August and scheduled
for retirement on November 19, 2025.
