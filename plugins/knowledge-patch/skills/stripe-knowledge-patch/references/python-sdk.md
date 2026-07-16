# Stripe Python SDK v12-v15

## SDK-to-API pins

| Python SDK | Associated API release |
| --- | --- |
| v12.0.0 | `2025-03-31.basil` |
| v12.1.0 | `2025-04-30.basil` |
| v12.2.0 | `2025-05-28.basil` |
| v12.3.0 | `2025-06-30.basil` |
| v12.4.0 | `2025-07-30.basil` |
| v12.5.0 | `2025-08-27.basil` |
| v13.0.0 | `2025-09-30.clover` |
| v13.1.0 | `2025-10-29.clover` |
| v14.0.0 | `2025-11-17.clover` |
| v14.1.0 | `2025-12-15.clover` |
| v14.3.0 | `2026-01-28.clover` |
| v14.4.0 | `2026-02-25.clover` |
| v15.0.0 | `2026-03-25.dahlia` |
| v15.3.0 | `2026-06-24.dahlia` |

Preview package pins are channel-specific; see [Preview package pins](#preview-package-pins).

## Runtime and installation requirements

- v13 drops Python 3.6 and requires pip 10 or newer after the package moves to `pyproject.toml`.
- v15 drops Python 3.7 and 3.8, making Python 3.9 the minimum.
- From v13.0.1, `pip install "stripe[async]"` installs optional dependencies for asynchronous HTTP calls.

## Core client migrations

### Async stream reads

`StripeStreamResponseAsync.read()` is removed in v12.0.0. Await `read_async()` for streamed responses such as Quote PDFs.

```python
stream = await stripe.Quote.pdf_async("qt_123")
body = await stream.read_async()
```

### StripeClient v1 namespace

- v12.5 copies v1 services under `StripeClient.v1`.
- v13 deprecates direct accessors such as `client.customers`.
- Resource-style class methods are unaffected.

```python
client = stripe.StripeClient("sk_test_...")
customers = client.v1.customers.list()
```

### Parameter classes and method signatures

v13 unifies resource and service request-param classes into shared top-level types such as `AccountCreateParams`. Replace annotations that name old nested types such as `Account.CreateParams` or service-local `CreateParams`.

- Use v13.0.1 or newer when importing nested types through paths such as `stripe.params.checkout`.
- `InvoiceLineItem.modify` and `modify_async` require both `invoice` and `line_item_id`.
- Generated `InvoiceLineItem.ModifyParam` is removed.

```python
stripe.InvoiceLineItem.modify("in_123", "il_123", description="Updated")
```

### Compatibility export removals

v13 removes deprecated module shims:

- `stripe.http_client`;
- `stripe.webhook`;
- `stripe.oauth`;
- `stripe.util`; and
- `stripe.api_resources`.

Import public classes directly from `stripe`. The same release:

- replaces `FileUpload` with `File`;
- renames `Urllib2Client` to top-level `UrllibClient`; and
- requires direct use of the standard-library `io` module.

v14.0.1 makes `stripe.error` globally accessible again.

## Event notifications

v13 replaces the thin-event surface:

- `StripeClient.parse_thin_event` becomes `parse_event_notification`;
- `ThinEvent` becomes typed `stripe.events.*EventNotification` classes;
- helpers are snake-case `fetch_event()` and `fetch_related_object()`;
- v2 Event resources move under `stripe.v2.core`; and
- notification context changes from `str` to `StripeContext`.

v15 raises when a payload is sent to the wrong parser. Use `Webhook.construct_event` for snapshot events and `parse_event_notification` for thin notifications.

## Async HTTP client ownership

From v14.4.0, `AIOHTTPClient` accepts a caller-provided session or connector. Use this to control connector settings and session lifetime instead of always relying on SDK-owned resources.

## Decimal values in v15

Every generated `decimal_string` request and response field becomes `decimal.Decimal` instead of `str`, including:

- decimal quantities and unit amounts;
- Checkout foreign-exchange rates;
- Climate quantities;
- Issuing amount fields;
- Price and Plan decimal amounts; and
- Accounts v2 ownership percentages.

Construct decimal inputs from strings and stringify explicitly for non-Stripe serializers.

```python
from decimal import Decimal

quantity = Decimal("1.25")
serialized = str(quantity)
```

## StripeObject is not a dict

In v15, `StripeObject` stops inheriting from `dict`.

- `.get()` and `.items()` are unavailable.
- Membership checks continue to work.
- Dot and bracket assignment continue to work.
- `.update()` remains only as a metadata convenience.
- Use `getattr(obj, "field", None)` for optional access.
- Use `obj.to_dict()` for a recursively converted, detached native-dict view.

## Stable generated contracts

### Billing and payments

In v15.3, `Billing.CreditGrant.priority` becomes required, and the generated surface adds:

- `billing_cycle_anchor_config` to Checkout Subscription data;
- custom fields, description, and footer to Subscription Invoice settings;
- payment-method options to Topups; and
- `release_details` to Reserve Holds.

Payment support expands with:

- Sunbit;
- Satispay for Invoice, Subscription, and future-use flows;
- WeChat Pay Checkout options;
- Sui and `usdsui` crypto values;
- Pix fingerprints; and
- Bizum and Blik buyer IDs.

### Reporting, identity, and compliance

- Card details add `transaction_link_id`.
- Payment Attempt and Payment Record card details remove `stored_credential_usage`.
- Their description, IIN, and issuer fields become optional.
- Refund reporting makes `refunded` optional.
- Mastercard compliance dispute evidence is added.
- Financial Connections Accounts add status details.
- Identity adds a validated-redaction state.
- Balance Transactions add `tax_fund`.
- Money-movement, tax-calculation, and financial-account error codes expand.

### V2 product and account contracts

- Product Catalog Imports add `mode` and a `promotion` feed type.
- Accounts v2 add the Sunbit merchant capability.
- Account identity attestations replace `storer` and `crypto_storer` with `money_manager` and `crypto_money_manager`.
- Update exhaustive configuration and terms-of-service handling for the renamed values.

## Preview subscriptions and shared payments

### Subscriptions and shared payments

The v15.3 beta surface adds:

- `Subscription.pause`;
- resume-time `payment_behavior`;
- Subscription status details;
- Bizum and Scalapay Granted Token details;
- expandable Trial Offer transition Prices;
- more recipient-bank destinations; and
- CHAPS support.

It also makes:

- `Subscription.billing_schedules` required;
- `SharedPayment.GrantedToken.agent_details` required; and
- `SubscriptionItem.billed_until` non-nullable.

### Other beta resources

The same v15.3 beta surface adds an IAM Activity Log retrieve API and Mastercard Issuing settlements.

## Preview resources and payment schemas

### Resource families

The v15.3 private-preview builds add:

- Delegated Checkout Orders;
- v2 Billing Contracts and quantity changes;
- v2 Account Signals;
- Gift Cards and Gift Card Operations;
- Tax Funds; and
- Radar Customer Evaluations.

Additional shapes include:

- Person birth addresses;
- debt-repayment money-service transactions;
- Issuing Token decision data;
- crypto static and refund addresses;
- Tax performance locations;
- provisional Issuing-dispute credit; and
- card-present multicapture controls.

### Payment schema changes

- Tamara is available across payment and setup flows.
- WeChat Pay adds mini-program clients.
- Card capture adds `automatic_delayed`.
- Crypto verification adds Ethereum and Polygon networks plus `usdg` and `usdp` currencies.
- Money-service beneficiary fields move to the parent detail.
- Sender `name` splits into `given_name` and `surname`.
- Payment Records gain card reporting.
- Refunds can reference Payment Attempt and Payment Records.
- Gift-card and card-detail fields are removed or narrowed.

## Preview package pins

Treat each preview tag as an independent contract:

- The v15.3 beta package pins `2026-05-27.private`.
- Its private-preview line advances through `2026-06-10.preview`.
- The v15.4 beta and first private-preview build pin `2026-06-24.preview`.
- Later v15.4 private-preview builds pin `2026-07-01.preview` and `2026-07-08.preview`.

Do not treat these tags as one stable Dahlia schema; migrate tag by tag.

## Preview Accounts and shared resource migrations

### Accounts and money management

In the v15.4 beta:

- Accounts v2 rename the `storer` configuration, include paths, terms, and typed notifications to `money_manager`.
- Associated capability-restriction values expand.
- Batch Jobs remove `maximum_rps` and make metadata optional.
- Money Management replaces US-bank `swift_code` with `bic`.
- Financial Account list filtering replaces singular `status` with `statuses`.
- Outbound payments and transfers add processing and review states plus under-review notifications.

### Shared resource changes

Also in the v15.4 beta:

- Many v1 payment, Customer, Checkout, Issuing, and Token resources add `redaction`.
- Financial Connections status details add `active` and an institution-requirement cause.
- Financial Connections Session account limit becomes emptyable.
- Invoice previews can pause Subscriptions.
- Quote previews accept Satispay.
- Shared Payment details expose Bizum and Blik buyer IDs plus Pix fingerprints.
- `invoice_payment.detached` is removed from modifiable webhook events.

## Preview infrastructure, money movement, and Billing Contracts

### Crypto, health, IAM, payouts, and accounts

The v15.4 private-preview line adds:

- Crypto Customer, payment-token, wallet, Onramp Session, and transaction-limit resources;
- v2 health Alerts;
- Payout Intents;
- financial-address debit simulation;
- IAM API-key permissions and expiration;
- credit Financial Accounts; and
- Account Session financial-account and recipient-list components.

### Money Management rails and transactions

- Transactions add Issuing and platform-funded-credit categories and flows.
- Recipient capabilities enumerate ACH, BECS, EFT, Fedwire, FPS, NPP, RTP, SEPA, and SWIFT rails.

### Checkout and Financial Connections

- Checkout automatic tax adds address-collection precision.
- Collected tax IDs change from plural `tax_ids` to singular `tax_id`.
- Checkout Items can reference Subscriptions.
- Financial Connections filters can require payment-method support.

### Terminal and Issuing

- Terminal Readers add gift-card activation, balance, cash-out, reload, and deactivation actions.
- Issuing adds richer Authorization and Transaction network data, program and device details, and enriched merchant data.
- Issuing returns separate available and current balance responses.

### Billing Contracts

The evolving v2 Billing Contract shape adds:

- status transitions;
- billing-cycle anchors;
- bill settings;
- pricing-line IDs and priorities; and
- `multiply_pricing`.

It removes:

- `one_time_fees`;
- `status_details`;
- older contract-detail fields;
- `multiplier`; and
- several symbolic start and end boundary values.

Pricing override discriminators change from `multiplier` to `multiply_pricing`. Multiple start/end unions narrow to literal timestamps. Typed activated, canceled, created, ended, and updated notifications are added.

### Network transfers

- Accounts can expose `related_network_object`.
- `network_business_profile_wallet` is available as both a recipient destination and payout method.
- Money Management Received Credits add `stripe_network_transfer`.
- Payout and Financial Account previews add payout-method options, returned-debit details, and more bank-transfer identity fields.
