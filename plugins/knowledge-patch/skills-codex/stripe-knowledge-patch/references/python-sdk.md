# Stripe Python SDK

## Version, API pin, and runtime matrix (`python-sdk-stable-2025-2026`)

| SDK | Pinned API release |
| --- | --- |
| v12 | `2025-03-31.basil` |
| v13 | `2025-09-30.clover` |
| v14 | `2025-11-17.clover` |
| v15 | `2026-03-25.dahlia` |

V13 drops Python 3.6. V15 drops Python 3.7 and 3.8 and requires Python 3.9 or
newer.

Python v15.4 changes its pinned API version to `2026-07-29.dahlia`
(`sdk-stable-through-2026-08-10`). Test against the Dahlia contract when taking
that release and relying on the SDK default.

## Services, methods, and paging

### V1 service namespace (`python-sdk-stable-2025-2026`)

V12.5 copies formerly top-level `StripeClient` services into `client.v1`. V13
deprecates direct access such as `client.customers`; use:

```python
customers = client.v1.customers.list()
```

### Invoice line-item signatures (`python-sdk-stable-2025-2026`)

In v13, `InvoiceLineItem.modify()` and `modify_async()` require both `invoice`
and `line_item_id`. The former `InvoiceLineItem.ModifyParam` type is removed.

Generated request parameter types move from separate resource and service
nesting to shared top-level names such as `AccountCreateParams`. Use v13.0.1 or
later when importing the new nested parameter classes.

### Paging edge cases (`python-sdk-stable-2025-2026`)

From v12.5.1, explicitly passing `starting_after=None` paginates backward,
matching omission of the argument rather than the earlier forward traversal.
Use v13.1.1 or later for context-scoped paged lists; it restores the
`stripe-context` header on follow-up page requests.

## Async I/O and HTTP clients

### Stream reads (`python-sdk-stable-2025-2026`)

V12 renames `StripeStreamResponseAsync.read()` to `read_async()`. Obtaining the
stream remains async, and its contents are read with:

```diff
- body = await response.read()
+ body = await response.read_async()
```

### Dependencies and session injection (`python-sdk-stable-2025-2026`)

From v13.0.1, install the dependencies for asynchronous HTTP calls with:

```sh
pip install 'stripe[async]'
```

V14.4 allows `AIOHTTPClient` to accept a caller-provided session or connector
when the integration manages its own aiohttp transport.

## Event notifications and context

### Typed notification surface (`python-sdk-stable-2025-2026`)

V13 replaces `StripeClient.parse_thin_event()` and `ThinEvent` with
`parse_event_notification()` and typed `EventNotification` classes. Instances
provide `fetch_event()` and, when applicable, `fetch_related_object()`; unknown
types use `UnknownEventNotification`. V2 Event and EventDestination resources
move beneath `stripe.v2.core`.

```diff
- notification = client.parse_thin_event(...)
+ notification = client.parse_event_notification(...)
event = notification.fetch_event()
```

### StripeContext (`python-sdk-stable-2025-2026`)

V13 accepts `StripeContext` as a `stripe_context` request value and changes
`EventNotification.context` from a string to that object. Pass the object
through when forwarding context instead of treating it as an ordinary string.

### Parser separation (`python-sdk-stable-2025-2026`)

V15 raises when a payload is passed to the wrong webhook parser. Use
`stripe.Webhook.construct_event()` for snapshots and
`StripeClient.parse_event_notification()` for event-notification payloads.

## Imports and object behavior

### V13 compatibility removals (`python-sdk-stable-2025-2026`)

V13 removes deprecated compatibility module exports; import their classes
directly from `stripe`. It replaces `FileUpload` with `File` and renames
`Urllib2Client` to `UrllibClient`. `UrllibClient` is exported at package top
level:

```python
from stripe import File, UrllibClient
```

### Decimal fields (`python-sdk-stable-2025-2026`)

V15 changes every `decimal_string` request and response field from `str` to the
standard-library `decimal.Decimal`. Construct request values from strings to
preserve decimal precision; response attributes are already `Decimal` objects.

```python
from decimal import Decimal

params = {"unit_amount_decimal": Decimal("1.25")}
```

### StripeObject is not a dict (`python-sdk-stable-2025-2026`)

V15 removes `StripeObject`'s `dict` inheritance. `.get()`, `.update()`, and
`.items()` no longer exist. Attribute and bracket access remain available; use
`.to_dict()` for a recursive native-Python snapshot. Mutating that snapshot does
not change the original object.

```python
snapshot = obj.to_dict()
obj["description"] = "updated"
```

## Generated contracts (`sdk-stable-through-2026-08-10`)

Python v15.4 removes `proof_of_registration` from Account creation documents
and `dynamic_tax_rates` from Checkout Session line-item creation parameters.
Remove those fields before upgrading generated request code.

V15.4 exposes `FinancialConnections.Authorization` and adds
`bank_account_token` to Financial Connections Sessions. Account update settings
also add `sepa_debit_payments`. Preserve all three generated additions.

Generated SDKs add `stripe_internal_error` to Issuing Authorization request-
history reasons. Exhaustive reason handling must accept the new value.
