---
name: polar-knowledge-patch
description: Polar
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Polar Knowledge Patch

Use this skill for Polar SDK, Core API, Customer Portal, checkout, billing,
subscription, benefit, event, meter, webhook, metrics, and integration work.
Start with the breaking and deprecated behavior below, then open the reference
file that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [Clients, authentication, and operations](references/clients-auth-and-operations.md) | Preview SDKs, environments, API and Customer Portal authentication, pagination, rate limits, webhooks, OAuth2, SSO, and integrations |
| [Catalog, pricing, and checkout](references/catalog-pricing-and-checkout.md) | Product variants, recurrence, prices, payment methods, checkout controls, embedding, discounts, and trials |
| [Customers, billing, and self-service](references/customers-billing-and-self-service.md) | External IDs, Customer State, credit balances, invoice numbering, portal email, data export, and email behavior |
| [Subscriptions, members, and benefits](references/subscriptions-members-and-benefits.md) | Subscription mutation, scheduled updates, pause and resume, B2B members, seats, benefits, and license keys |
| [Events, meters, and metrics](references/events-meters-and-metrics.md) | Event hierarchy and idempotency, event types, meter units and time zones, and Metrics API semantics |

## Breaking and deprecated behavior

### Product recurrence and checkout selection

- A product can no longer combine monthly and yearly pricing. Existing
  combinations continue to work.
- Represent variants as separate products and offer those products together in
  a checkout.
- Use `products` instead of the deprecated checkout fields `product_id` and
  `product_price_id`.
- `ProductPrice.type` and `ProductPrice.recurring_interval` are deprecated.
  Set recurrence on `Product`.

See [Catalog, pricing, and checkout](references/catalog-pricing-and-checkout.md).

### Metrics query selection

- Select requested values with the `metrics` query parameter.
- The deprecated `focus_metrics` parameter has been removed.
- Metrics calculations exclude pending and unpaid orders and include only paid
  and refunded orders.

See [Events, meters, and metrics](references/events-meters-and-metrics.md).

### Embedded checkout allowlisting

- Adding any host under Settings → Preferences → Embedding turns the configured
  host list into an allowlist.
- Organizations created from August 4, 2026 must configure hosts before
  embedding.
- Older organizations remain unrestricted until their first host is added.

See [Catalog, pricing, and checkout](references/catalog-pricing-and-checkout.md).

## SDK and environment quick reference

The typed 2026-04 TypeScript and Python clients are prereleases.

```bash
npm install @polar-sh/sdk@next
pip install --pre polar-sdk
```

```ts
import { createPolar } from "@polar-sh/sdk/2026-04";

const polar = createPolar({
  accessToken: process.env.POLAR_ACCESS_TOKEN!,
  environment: "sandbox",
});
```

```python
from polar.v2026_04 import Polar
```

- Both clients target production unless `environment: "sandbox"` in
  TypeScript or `environment="sandbox"` in Python is set.
- Sandbox data and credentials are isolated from production.

## Authentication quick reference

- Backend Core API calls use an Organization Access Token at
  `https://api.polar.sh/v1` or the sandbox base URL.
- Customer-facing code creates a Customer Access Token through
  `/v1/customer-sessions/` and uses the restricted `/v1/customer-portal/`
  surface.
- A Customer Access Token is customer-scoped. It cannot create products, issue
  refunds, or perform other organization-level operations.

List endpoints use one-based `page` and `limit`. Both default to 1 and 10,
respectively, and `limit` has a maximum of 100. Read
`pagination.total_count` and `pagination.max_page` from list responses.

See [Clients, authentication, and operations](references/clients-auth-and-operations.md).

## Checkout and pricing quick reference

### Prices and intervals

- Products can define amounts in multiple currencies; the organization has a
  default presentment currency.
- Fixed discounts can define currency-specific amounts.
- Subscription products support daily, weekly, and custom interval counts.
- Polar also supports tax-inclusive prices, seat-based one-time products, and
  fixed, free, or custom ad-hoc price overrides on API-created checkouts.

### Checkout controls

- Checkout and Customer Portal sessions accept `return_url`; dashboard-created
  static Checkout Links can set it too.
- Checkout Links persist `reference_id` and standard UTM query parameters into
  Checkout metadata.
- Seat checkouts accept `min_seats` and `max_seats`.
- The business-purchase option requires a business billing name and full
  address.

### Discounts and trials

- Discount creation and update accept `max_redemptions_per_customer`.
- Repeat redemption is identified by customer ID, plus-alias-normalized email,
  or payment card.
- Configure trials on subscription products. Organization-level abuse
  prevention checks normalized email and card fingerprints.
- Set Checkout's `allow_trial` to force a purchase without the product's normal
  trial.

See [Catalog, pricing, and checkout](references/catalog-pricing-and-checkout.md).

## Subscription quick reference

- Create subscriptions through the API without Checkout.
- Move an existing subscription from an archived price to the current price of
  the same product with proration.
- Add, change, or remove its discount.
- Change its current billing-period end unless it is already canceled.
- Use `next_period` proration behavior for product, price, and seat changes.
  Subscription objects and webhooks expose the pending update.
- Pausing takes effect at period end, stops billing, and revokes benefits. It
  does not delete the subscription or payment method.
- Resuming starts a new period and charges immediately. An automatic resume
  date is optional.
- Pause and resume transitions emit `subscription.paused` and
  `subscription.resumed`.

See [Subscriptions, members, and benefits](references/subscriptions-members-and-benefits.md).

## Customer and B2B quick reference

### Customer identity and state

- Customers have `external_id` get, update, and delete operations, and list
  queries can filter by external ID.
- A checkout's `external_customer_id` is copied to the customer created after
  payment.
- Customer State returns active subscriptions and granted benefits in one API
  call or webhook and correctly represents trialing subscriptions.

### Members and seats

- `GET /v1/members` is paginated and supports customer filtering. Polar
  automatically creates an owner member.
- Member roles are `owner`, `billing_manager`, and `member`.
- Ownership transfer demotes the former owner to billing manager.
- Member sessions use the `polar_mst_` prefix.
- Benefits can be member-specific; events accept `member_id` or
  `external_member_id`.
- Seats can be assigned by API, and customer seat changes are automatically
  prorated.

See [Customers, billing, and self-service](references/customers-billing-and-self-service.md)
and [Subscriptions, members, and benefits](references/subscriptions-members-and-benefits.md).

## Events and delivery quick reference

- Events accept `parent_id` for hierarchies and `external_id` as an idempotency
  key.
- Event types are created from event names and support display names and a
  statistics endpoint. Events can carry cost metadata.
- Webhook payloads include a Standard Webhooks timestamp.
- By default, an endpoint is disabled after 10 consecutive failures.
  Organization members are notified, and the endpoint must be manually
  re-enabled after the receiver is fixed.

See [Events, meters, and metrics](references/events-meters-and-metrics.md) and
[Clients, authentication, and operations](references/clients-auth-and-operations.md).
