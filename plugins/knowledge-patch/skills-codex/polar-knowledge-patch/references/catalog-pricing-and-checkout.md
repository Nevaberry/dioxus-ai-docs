# Catalog, Pricing, and Checkout

## Product variants and checkout selection

Polar represents variants as separate products offered together in a
checkout.

Products can no longer combine monthly and yearly pricing, although existing
combinations continue to work.

Use `products` instead of the deprecated checkout fields `product_id` and
`product_price_id`. `ProductPrice.type` and
`ProductPrice.recurring_interval` are deprecated; recurrence is set on
`Product`.

## Pricing capabilities

Products can define amounts in multiple currencies with an organization-level
default presentment currency. Fixed discounts can define currency-specific
amounts.

Subscription products support daily, weekly, and custom interval counts.
Polar also supports:

- Tax-inclusive prices.
- Seat-based one-time products.
- API-created checkouts with fixed, free, or custom ad-hoc price overrides.

## Local payments and zero-amount taxes

Eligible checkouts automatically expose these methods for one-time EUR
purchases:

- Bancontact.
- BLIK.
- EPS.
- iDEAL/Wero.
- Przelewy24.
- Bizum.

UPI supports one-time INR purchases and recurring INR subscriptions.

Free and other zero-amount orders no longer have tax calculated.

## Checkout session and link controls

Checkout and Customer Portal sessions accept `return_url`.
Dashboard-created static Checkout Links can also set `return_url`.

Checkout Links persist `reference_id` and standard UTM query parameters into
Checkout metadata.

Seat checkouts accept `min_seats` and `max_seats`. The business-purchase
option requires a business billing name and full address.

## Embedded checkout host allowlist

Adding any host under Settings → Preferences → Embedding makes the configured
list an allowlist.

Organizations created from August 4, 2026 need hosts configured before
embedding. Older organizations remain unrestricted until their first host is
added.

## Discount redemption limits

Discount creation and updates accept `max_redemptions_per_customer`.

Polar identifies repeat use by any of these signals:

- Customer ID.
- Plus-alias-normalized email.
- Payment card.

## Trial configuration and abuse prevention

Trials are configured on subscription products. Organization-level abuse
prevention checks normalized email and card fingerprints.

Checkout's `allow_trial` can force a purchase without the product's normal
trial.
