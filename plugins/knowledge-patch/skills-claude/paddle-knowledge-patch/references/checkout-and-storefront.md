# Checkout and Storefront

## Express, upsell, and recovery checkout

Express checkout prioritizes Apple Pay on mobile. It prioritizes Google Pay on
Android and Chrome.

The early-access post-purchase upsell checkout supports reduced-friction
one-click purchases.

Automated abandoned-checkout emails may include an optional recovery discount.

## Checkout domains

Four API operations support approved checkout domains. They can list and
inspect the domains and trigger Apple Pay verification.

Hosted checkout can use branded custom subdomains. This capability was
announced as early access.

## Paddle UI

Paddle UI supplies customizable React components for:

- checkout;
- pricing;
- subscription management.

Paddle UI is based on shadcn/ui and is installed with the shadcn CLI.

## External iOS purchase flows

An iOS app can direct users to either an external hosted checkout or a web
checkout deployed to Vercel. RevenueCat is used for fulfillment.

## Regional payment methods

UPI supports one-time and recurring INR payments in India.

Recurring payments also support:

- KakaoPay;
- Naver Pay;
- Alipay.

One-time checkout also supports:

- Korean local cards and wallets;
- WeChat Pay;
- Pix;
- Bancontact.

## Currencies and locales

Paddle added billing for CLP, PEN, VND, and COP.

It also added:

- `pt-BR` across customer-facing features;
- Traditional Chinese for checkout;
- Turkish for checkout and subscription emails.

## Automatic location and tax localization

Prices can automatically display tax-inclusive or tax-exclusive amounts based
on customer location. An account setting makes this behavior the default for
newly created prices.

Paddle.js price previews detect the visitor's location when location data is
omitted.

## Updating an open checkout

Paddle.js can update these values on an already-open checkout:

- items;
- discounts;
- customer information;
- custom data.

Checkout events distinguish invalid or missing input from payment errors such
as having no valid payment method. Frontends can therefore handle those cases
with separate fallback paths.

## Client-side previews and payment methods

Price previews return localized, formatted prices that include tax and discount
calculations.

Paddle.js can preview complete transaction totals without a server call.
Preview responses can report valid payment methods. Checkout can be restricted
to a selected set of payment methods.
