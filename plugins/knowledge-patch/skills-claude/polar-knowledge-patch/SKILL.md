---
name: polar-knowledge-patch
description: Polar
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Polar Knowledge Patch

Use this skill when implementing or reviewing Polar SDK usage, API
authentication, products, checkouts, subscriptions, customer access, benefits,
events, meters, billing operations, webhooks, or integrations.

## Reference index

| Reference | Topics |
| --- | --- |
| [SDK and API access](references/sdk-and-api-access.md) | Preview SDK imports, environments, tokens, pagination, and rate limits |
| [Products and checkout](references/products-and-checkout.md) | Variants, pricing, payment methods, checkout controls, discounts, and trials |
| [Customers and subscriptions](references/customers-and-subscriptions.md) | External IDs, Customer State, subscription mutation, pause/resume, members, and seats |
| [Benefits, events, and meters](references/benefits-events-and-meters.md) | Feature flags, license keys, event hierarchies, metering, and webhook delivery |
| [Billing and integrations](references/billing-and-integrations.md) | Metrics, balances, invoices, OAuth2, SSO, customer email, and integrations |

## Preview SDK setup

The typed 2026-04 clients are prereleases. Install and import the TypeScript
client with:

```sh
npm install @polar-sh/sdk@next
```

```ts
import { createPolar } from "@polar-sh/sdk/2026-04";
```

For Python, install and import the client with:

```sh
pip install --pre polar-sdk
```

```python
from polar.v2026_04 import Polar
```

Both clients target production by default. Select the isolated sandbox by
setting `environment: "sandbox"` in TypeScript or `environment="sandbox"` in
Python. Sandbox credentials and data do not cross into production.

```ts
import { createPolar } from "@polar-sh/sdk/2026-04";

const polar = createPolar({
  accessToken: process.env.POLAR_ACCESS_TOKEN!,
  environment: "sandbox",
});
```

## Keep Core and customer access separate

- Authenticate backend Core API requests with an Organization Access Token.
- Send Core API requests to `https://api.polar.sh/v1` or the sandbox base URL.
- For customer-facing code, create a Customer Access Token through
  `/v1/customer-sessions/`.
- Use that token only with the restricted `/v1/customer-portal/` surface.
- A Customer Access Token is customer-scoped. It cannot create products,
  issue refunds, or perform other organization-level operations.

## Migrate deprecated product and checkout fields

Treat a variant as a separate product and offer the related products together
in one checkout.

- Do not combine monthly and yearly pricing on a new product. Existing
  combinations continue to work.
- Use `products` instead of deprecated checkout fields `product_id` and
  `product_price_id`.
- Set recurrence on `Product`; `ProductPrice.type` and
  `ProductPrice.recurring_interval` are deprecated.
- Select requested Metrics API values with `metrics`; `focus_metrics` has
  been removed.

## Choose checkout and pricing behavior

Products support amounts in multiple currencies and an organization-level
default presentment currency. Fixed discounts can carry currency-specific
amounts. Subscription intervals can be daily, weekly, or use a custom interval
count.

Other supported pricing paths include:

- tax-inclusive prices;
- seat-based one-time products; and
- API-created checkouts using fixed, free, or custom ad-hoc price overrides.

For eligible one-time EUR purchases, checkout automatically exposes Bancontact,
BLIK, EPS, iDEAL/Wero, Przelewy24, and Bizum. UPI supports one-time INR
purchases and recurring INR subscriptions. Polar does not calculate tax for
free or other zero-amount orders.

## Apply checkout controls

- Set `return_url` on Checkout sessions and Customer Portal sessions.
- Dashboard-created static Checkout Links can also set `return_url`.
- Checkout Links persist `reference_id` and standard UTM query parameters into
  Checkout metadata.
- Use `min_seats` and `max_seats` to constrain seat checkouts.
- The business-purchase option requires a business billing name and full
  address.

Adding any host under Settings → Preferences → Embedding changes the
configured host list into an allowlist. Organizations created from August 4,
2026 must configure hosts before embedding. Older organizations remain
unrestricted until their first host is added.

## Control discount reuse and trials

Set `max_redemptions_per_customer` when creating or updating a discount. Repeat
use is recognized through customer ID, plus-alias-normalized email, or payment
card.

Configure trials on subscription products. Organization-level abuse prevention
uses normalized email and card fingerprints. Set Checkout's `allow_trial` to
force a purchase without the trial normally configured on the product.

## Mutate subscriptions safely

Subscriptions can be created directly through the API without Checkout. For an
existing subscription:

- move from an archived price to the current price of the same product with
  proration;
- add, change, or remove its discount; and
- change the current billing-period end unless the subscription is already
  canceled.

Use the `next_period` proration behavior to schedule product, price, or seat
changes. The pending change appears on subscription objects and webhooks.

Pausing takes effect at period end, stops billing, and revokes benefits without
deleting the subscription or payment method. Resuming begins a new period and
charges immediately. An automatic resume date is optional. These transitions
emit `subscription.paused` and `subscription.resumed`.

## Work with members and seats

`GET /v1/members` is paginated and supports customer filtering. Polar creates
an owner member automatically. Member roles are `owner`, `billing_manager`, and
`member`; transferring ownership demotes the former owner to billing manager.

- Member-session tokens use the `polar_mst_` prefix.
- Benefits can be member-specific.
- Events accept `member_id` or `external_member_id`.
- Assign seats through the API.
- Customer seat changes are automatically prorated.

## Preserve entitlement and event semantics

The Feature Flag benefit exposes entitlement state through APIs and webhooks,
but customers cannot see its JSON metadata. Subscription cancellation
automatically revokes benefits. Failed-payment revocation may be immediate or
may follow the payment-retry grace window.

Use `parent_id` to form event hierarchies and `external_id` as an idempotency
key. Event names create event types. Event types support display names and a
statistics endpoint, and events can include cost metadata.

## Handle operational boundaries

- List endpoints use one-based `page` and `limit` values. Defaults are page 1
  and limit 10; the maximum limit is 100.
- Read `pagination.total_count` and `pagination.max_page` from list responses.
- Production allows 500 requests per minute and sandbox allows 100 per minute,
  per organization, customer, or OAuth2 client.
- Unauthenticated license validation, activation, and deactivation allow three
  requests per second. A 429 response includes `Retry-After`.
- A webhook endpoint is disabled after 10 consecutive failures by default.
  Organization members are notified, and the endpoint must be manually
  re-enabled after its receiver is fixed.

Consult the topic references before changing behavior whose details are not in
this quick reference.
