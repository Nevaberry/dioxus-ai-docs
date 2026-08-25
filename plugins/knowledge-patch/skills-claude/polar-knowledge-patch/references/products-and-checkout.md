# Products and checkout

## Product variants

Polar models variants as separate products that are offered together in a
checkout.

Products can no longer combine monthly and yearly pricing. Existing products
with that combination continue to work.

For checkout selection, use `products`. It replaces the deprecated
`product_id` and `product_price_id` fields.

Recurrence belongs on `Product`. `ProductPrice.type` and
`ProductPrice.recurring_interval` are deprecated.

## Pricing capabilities

A product can define amounts in multiple currencies, with an
organization-level default presentment currency. Fixed discounts can define
currency-specific amounts.

Subscription products support daily and weekly intervals as well as custom
interval counts.

Pricing also supports:

- tax-inclusive prices;
- seat-based one-time products; and
- API-created checkouts with fixed, free, or custom ad-hoc price overrides.

## Local payment methods and zero-amount tax

Eligible checkout sessions automatically make Bancontact, BLIK, EPS,
iDEAL/Wero, Przelewy24, and Bizum available for one-time purchases in EUR.

UPI is available for one-time INR purchases and recurring INR subscriptions.

Tax is not calculated for free orders or other zero-amount orders.

## Return URLs and attribution

Checkout sessions and Customer Portal sessions accept `return_url`.
Dashboard-created static Checkout Links can set it as well.

Checkout Links persist `reference_id` and standard UTM query parameters into
Checkout metadata.

## Seat and business checkout controls

Seat checkouts accept `min_seats` and `max_seats`.

When the business-purchase option is used, the checkout requires a business
billing name and full address.

## Embedded checkout hosts

Adding any host under Settings → Preferences → Embedding makes the
configured host list an allowlist.

Organizations created from August 4, 2026 must configure hosts before they can
embed checkout. Older organizations remain unrestricted until the first host
is added.

## Discount redemption limits

Discount creation and update operations accept
`max_redemptions_per_customer`.

Polar recognizes repeat use by any of these identifiers:

- customer ID;
- email after plus-alias normalization; or
- payment card.

## Trial controls

Configure trials on subscription products. Organization-level trial-abuse
prevention checks normalized email and card fingerprints.

Checkout's `allow_trial` can force a purchase without the trial normally
configured on the product.
