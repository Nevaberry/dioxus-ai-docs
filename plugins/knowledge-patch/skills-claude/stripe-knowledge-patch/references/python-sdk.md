# Stripe Python SDK

## API pins and Python support

Python SDK v12, v13, v14, and v15 pin API versions
`2025-03-31.basil`, `2025-09-30.clover`, `2025-11-17.clover`, and
`2026-03-25.dahlia`, respectively. V13 drops Python 3.6. V15 drops Python 3.7
and 3.8, so it requires Python 3.9 or later.

Python v15.4 changes its pinned API version to `2026-07-29.dahlia`. Test the
Dahlia contract when relying on the SDK's default version.

## Service access and method signatures

### V1 service namespace

V12.5 copies services previously exposed directly on `StripeClient` into
`client.v1`. V13 deprecates direct access such as `client.customers`.

```python
customers = client.v1.customers.list()
```

### Invoice Line Item modification

In v13, `InvoiceLineItem.modify()` and `modify_async()` require both `invoice`
and `line_item_id`. `InvoiceLineItem.ModifyParam` is removed.

## Async I/O and transport ownership

### Stream reads

V12 renames `StripeStreamResponseAsync.read()` to `read_async()`. Obtaining the
stream remains asynchronous.

```diff
- body = await response.read()
+ body = await response.read_async()
```

### Async dependencies and aiohttp sessions

From v13.0.1, install the `async` extra for asynchronous HTTP dependencies:

```sh
pip install 'stripe[async]'
```

V14.4 lets `AIOHTTPClient` accept a caller-provided session or connector when
the integration owns its aiohttp transport.

## Paging

From v12.5.1, explicitly passing `starting_after=None` paginates backward,
matching omission of the argument instead of the earlier forward traversal.

Use v13.1.1 or later for context-scoped paged lists; it restores the
`stripe-context` header on follow-up requests.

## Parameters, imports, and compatibility names

### Generated parameter types

V13 moves generated request parameter types from separate resource and service
nesting to shared top-level names such as `AccountCreateParams`. Use v13.0.1 or
later when importing the new nested parameter classes.

### Removed compatibility exports

V13 removes deprecated compatibility module exports. Import their classes
directly from `stripe`. It also replaces `FileUpload` with `File` and renames
`Urllib2Client` to `UrllibClient`, which is available at package top level for
custom HTTP-client configuration.

```python
from stripe import File, UrllibClient
```

## Event notifications and request context

### V13 notification surface

V13 replaces `StripeClient.parse_thin_event()` and `ThinEvent` with
`parse_event_notification()` and typed `EventNotification` classes.
Notifications provide `fetch_event()` and, where applicable,
`fetch_related_object()`; unknown types use `UnknownEventNotification`. V2 Event
and EventDestination resources move under `stripe.v2.core`.

```diff
- notification = client.parse_thin_event(...)
+ notification = client.parse_event_notification(...)
event = notification.fetch_event()
```

### Stripe context

V13 accepts a `StripeContext` as the `stripe_context` request value and changes
`EventNotification.context` from a string to that object. Pass the object
through instead of treating it as an ordinary string.

### Parser separation

V15 raises when a payload is passed to the wrong parser. Use
`stripe.Webhook.construct_event()` for snapshot payloads and
`StripeClient.parse_event_notification()` for Event Notification payloads.

## Decimal values

V15 changes every `decimal_string` request and response field from `str` to the
standard-library `decimal.Decimal`. Construct request values from strings to
preserve decimal precision. Response attributes are already `Decimal` objects.

```python
from decimal import Decimal

params = {"unit_amount_decimal": Decimal("1.25")}
```

## StripeObject behavior

V15 removes `dict` inheritance from `StripeObject`; `.get()`, `.update()`, and
`.items()` no longer exist. Attribute and bracket access remain available. Use
`.to_dict()` for a recursive native-Python snapshot; mutating that snapshot does
not change the original object.

```python
snapshot = obj.to_dict()
obj["description"] = "updated"
```

## Python v15.4 generated changes

Remove `proof_of_registration` from Account creation documents and
`dynamic_tax_rates` from Checkout Session line-item creation parameters. V15.4
adds `FinancialConnections.Authorization`, Financial Connections Session
`bank_account_token`, Account setting `sepa_debit_payments`, and Issuing
Authorization request-history reason `stripe_internal_error`. Generated models,
serializers, and exhaustive reason handling must accept them.
