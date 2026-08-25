# Pricing, Tax, and Catalog

## Regional payment methods, currencies, and locales

UPI supports one-time and recurring INR payments in India. Recurring payments
also support KakaoPay, Naver Pay, and Alipay. One-time checkout supports Korean
local cards and wallets, WeChat Pay, Pix, and Bancontact.

Paddle added CLP, PEN, VND, and COP billing, `pt-BR` across customer-facing
features, Traditional Chinese for checkout, and Turkish for checkout and
subscription emails.

## Automatic location and tax localization

Prices can automatically display tax-inclusive or tax-exclusive amounts
according to customer location. An account setting makes that behavior the
default for newly created prices.

Paddle.js price previews also detect visitor location when location data is
omitted.

## Transaction discounts and discount groups

A transaction can receive a one-off discount object without creating a catalog
discount.

Discount groups organize catalog discounts and can be fetched, renamed, or
archived through the API. Discount codes are case-insensitive.

## Tax-aware adjustments

Setting `tax_mode` for a partial refund lets amounts be supplied tax-exclusive
for Paddle to calculate tax.

Adjustment webhooks include `tax_rates_used`, with subtotal, tax, and total
grouped by rate. Transaction totals expose tax charged after credits.

## Non-catalog items and subscription snapshots

Transactions and one-time subscription charges can use inline product or price
attributes without catalog entries. Recurring non-catalog items can be added
when updating a subscription.

Subscription items contain complete price and product snapshots from the time
each item was added.
