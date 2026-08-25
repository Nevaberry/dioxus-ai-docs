# Customers, Orders, and Drafts

## Customer webhook payload migration

In `2025-01`, embedded customer payloads no longer include:

- `tags`
- `email_marketing_consent`
- `sms_marketing_consent`
- `last_order_id`
- `last_order_name`
- `total_spent`
- `orders_count`

Consume these webhook topics instead:

- `CUSTOMER_TAGS_ADDED` and `CUSTOMER_TAGS_REMOVED`
- `CUSTOMERS_EMAIL_MARKETING_CONSENT_UPDATE`
- `CUSTOMERS_MARKETING_CONSENT_UPDATE`
- `CUSTOMERS_PURCHASING_SUMMARY`

## Order creation, draft pricing, and exchanges

`orderCreate` accepts `order.customer.toUpsert` to create or update a customer
and associate that customer while creating an order.

`DraftOrderLineItemInput.priceOverride` replaces the catalog price, but
requires caller-managed currency conversion. It is stripped from bundles and
their components.

`CalculateExchangeLineItemInput.variantId` selects the variant added in an
exchange.

## Business entities and company-location tax

`BusinessEntity` and the `businessEntities` query expose a merchant's legal
operating entities. Entity identifiers also appear on REST orders and order
webhooks.

Move company-location tax exemptions and registration IDs to
`CompanyLocationTaxSettings`. Replace these mutations with
`companyLocationTaxSettingsUpdate`:

- `companyLocationAssignTaxExemptions`
- `companyLocationCreateTaxRegistration`
- `companyLocationRevokeTaxExemptions`
- `companyLocationRevokeTaxRegistration`

## Bundle representations

Use `AbandonedCheckoutLineItem.components` and Customer API `LineItem.group`
to render bundle components beneath their parent. Order-create webhooks
identify bundled line items with `sales_line_item_group_id`.

## Order mutation behavior

`orderCreate` can attach multiple tracking numbers to each fulfillment.
Beginning with API version `2026-10`, updating an order's shipping address
recalculates its taxes.

## Order correlation and attribution

Orders expose `checkoutToken` and `cartToken`. Sales-channel apps can
configure order attribution for channel filters.

`BusinessEntity.legalEntityId` and payment-mandate IDs are also available for
correlation.

## Draft-order commerce data

Draft-order deposit fields are available in the Admin and Customer Account
GraphQL APIs. Customer Account draft orders expose discount-application
information while deprecating `discountedUnitPrice`.

GraphQL Admin `2026-10` removes
`DraftOrderDiscountNotAppliedWarning.priceRule`. GraphQL Admin `2026-07`
removes `DraftOrderLineItem.grams`.

## Marketing consent and engagements

Cumulative marketing engagements are deprecated. WhatsApp marketing consent
is available through both the Admin and Customer Account APIs.
