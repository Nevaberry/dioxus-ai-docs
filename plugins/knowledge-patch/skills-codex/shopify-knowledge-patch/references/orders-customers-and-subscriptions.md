# Orders, Customers, and Subscriptions

## Nullable fields and bulk-operation errors

`DiscountAutomaticBasic.minimumRequirement` and
`DiscountAutomaticFreeShipping.minimumRequirement` can be `null`.

`ReverseFulfillmentOrder.order` can be `null` without a GraphQL error when
`read_all_orders` is absent, the order is more than 60 days old, or it no longer
exists.

`BulkOperationUserError` is public. Errors from `bulkOperationRunQuery` include
`code`.

## Order creation and draft pricing

`orderCreate` accepts `order.customer.toUpsert` to create or update and associate a
customer while creating an order. It can also attach multiple tracking numbers to
each fulfillment.

`DraftOrderLineItemInput.priceOverride` replaces catalog price. The caller must
manage currency conversion, and the override is stripped from bundles or their
components.

## Exchanges

`CalculateExchangeLineItemInput.variantId` selects the variant added in an exchange.

## Business entities and company-location tax

`BusinessEntity` and `businessEntities` expose a merchant's legal operating
entities. Entity identifiers also appear on REST orders and order webhooks.

Move company-location tax exemptions and registration IDs to
`CompanyLocationTaxSettings`. Replace all of the following with
`companyLocationTaxSettingsUpdate`:

- `companyLocationAssignTaxExemptions`
- `companyLocationCreateTaxRegistration`
- `companyLocationRevokeTaxExemptions`
- `companyLocationRevokeTaxRegistration`

## Subscription relationships

Customer API `Order.subscriptionContracts` exposes contracts associated with an
order. `SubscriptionLine.concatenatedOriginContract` identifies the source contract
when a line was formed by concatenation. Pickup subscription methods expose
`pickupAddress`.

## Order address tax recalculation

Beginning with API version `2026-10`, updating an order's shipping address
recalculates its taxes.

## Order correlation and attribution

Orders expose `checkoutToken` and `cartToken`. Sales-channel apps can configure order
attribution for channel filters. `BusinessEntity.legalEntityId` and payment-mandate
IDs are available for correlation.

## Subscription calculation and actors

`SubscriptionContractCalculation` is available in early access.
Subscription-contract and billing-attempt mutations expose an `actor` field.

## Draft-order data and removals

Draft-order deposit fields are available in the Admin and Customer Account GraphQL
APIs. Customer Account draft orders expose discount-application information while
deprecating `discountedUnitPrice`.

GraphQL Admin `2026-10` removes
`DraftOrderDiscountNotAppliedWarning.priceRule`, and `2026-07` removes
`DraftOrderLineItem.grams`.

## Financial and customer-tax behavior

Customer tax settings are available in the Admin API.
`LineItem.priceAfterAllDiscountsBeforeTaxesSet` exposes a post-discount, pre-tax
amount.

The `totalUnsettledSet` calculation for pending captures and POS 11.5 custom-line-item
discount rounding have changed. Retest calculations that depend on them.
