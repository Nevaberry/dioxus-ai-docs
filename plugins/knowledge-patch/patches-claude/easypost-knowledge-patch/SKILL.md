---
name: easypost-knowledge-patch
description: EasyPost
version: null
license: MIT
metadata:
  author: Nevaberry
---


# EasyPost Knowledge Patch

## Use this patch

Load this skill before implementing or reviewing EasyPost address verification,
tracking, shipment purchase, label handling, carrier-account operations, or SDK
upgrades.

Before changing an integration:

1. Identify whether each resource is being created, retrieved, verified,
   purchased, converted, listed, or deleted.
2. Preserve presence-based request semantics: for address verification, sending
   a key with `false` is not the same as omitting it.
3. Supply every required input before creating an immutable Address, Tracker, or
   Shipment.
4. Distinguish EasyPost IDs from caller references and carrier display names
   from API carrier strings.
5. Account for default date windows, maximum page sizes, and rate limits on
   index endpoints.
6. For SDK changes, identify the language, runtime, middleware hooks, HTTP
   client hooks, and whether callers depend on model-class instances.

## Reference index

| Reference | Topics |
| --- | --- |
| [addresses.md](references/addresses.md) | Creation-time verification, carrier verification, existing Addresses, normalization |
| [trackers.md](references/trackers.md) | Tracker creation, statuses, scan data, lookup, test codes, deletion |
| [shipments-labels-and-rates.md](references/shipments-labels-and-rates.md) | Shipment creation and purchase, labels, claims, rate adjustments, international and carrier rules |
| [accounts-events-and-subscriptions.md](references/accounts-events-and-subscriptions.md) | Carrier accounts, groups, webhooks, JWT sessions, subscriptions |
| [sdk-and-api.md](references/sdk-and-api.md) | Node.js SDK migration, generic requests, timestamps, index throttling |

## Critical request-semantics guardrails

- On `POST /v2/addresses`, the presence of `verify` or `verify_strict` triggers
  delivery and ZIP verification even if its value is `false`. Omit both keys to
  avoid verification.
- `verify_strict` takes precedence over `verify` and errors for an unverified
  address; a correctable address is corrected and returned.
- `POST /v2/shipments` creates an immutable Shipment. Provide all creation and
  rating inputs up front.
- Shipment `line_items` are request-only: they support carrier-claim automation,
  are not passed to the carrier, and are not returned in the response.
- `GET /v2/shipments/:id` accepts an ID or caller-supplied `reference`, but
  references are not unique. Use the generated ID for reliable retrieval.
- `GET /v2/trackers/:id` accepts only a Tracker ID. Code-based lookup belongs on
  `GET /v2/trackers` with the plural `tracking_codes` array.
- Trackers are immutable. Deleting one permanently removes it, stops future
  webhook Event deliveries, and makes later retrieval return `404 Not Found`.

## Address verification quick reference

Choose creation-time verification behavior deliberately:

| Request shape | Behavior |
| --- | --- |
| Neither verification key present | Do not verify |
| `verify` present | Return the Address with per-check results |
| `verify_strict` present | Error if unverified; correct and return if correctable |
| Verification key plus `verify_carrier: "ups"` or `"fedex"` | Use that carrier's Address Verification Service |

Carrier verification reports the service used in
`verifications.verify_carrier`. To verify an immutable existing Address, call
`GET /v2/addresses/:id/verify`; the normalized replacement is wrapped in
`address`.

For US and Canadian addresses, verification can move a recognized trailing
unit from `street1` to an empty `street2` when `street1` exceeds 35 characters.
Street-name abbreviation occurs only for USPS verification and only when the
validated `street1` exceeds 40 characters.

See [addresses.md](references/addresses.md) for verification result fields and
examples.

## Shipment creation and purchase quick reference

- Creating a Shipment with valid `to_address`, `from_address`, and `parcel`
  automatically populates `rates`; each value may be an existing ID or an
  inline object.
- International destinations, including US territories, require
  `customs_info`.
- If omitted, `return_address` defaults to `from_address`.
- `carrier_accounts` limits rating. Any invalid or disabled supplied account
  causes an error.
- Buy a selected rate with `POST /v2/shipments/:id/buy` and a `rate.id`. The
  response fills `tracking_code` and `postage_label`.
- Optional purchase `insurance` is a USD string. Labels default to PNG unless
  `options.label_format` requests another format.
- When the carrier service is known, include both `service` and
  `carrier_accounts` in `POST /v2/shipments` for one-call purchase.
- V2 shipment validation rejects missing or zero-valued parcel details.

Label conversion through
`GET /v2/shipments/:id/label?file_format=ZPL` supports `PDF`, `ZPL`, and `EPL2`,
but requires an original PNG label. Conversion works best from a 4x6 PNG to
ZPL.

See [shipments-labels-and-rates.md](references/shipments-labels-and-rates.md)
for line-item requirements, list behavior, rate rules, claims, and carrier
options.

## Tracker quick reference

- Omitting `carrier` from `POST /v2/trackers` invokes auto-detection. Ambiguous
  codes can match multiple carriers, and explicit carrier selection is faster.
- Some carriers require carrier-specific credentials for third-party tracking.
- Creating the same `tracking_code` and `carrier` for the same user within three
  months returns the original Tracker rather than a duplicate.
- Current status values are `unknown`, `pre_transit`, `in_transit`,
  `out_for_delivery`, `delivered`, `available_for_pickup`,
  `return_to_sender`, `failure`, `cancelled`, and `error`.
- Historical scans are in `tracking_details`. Their timestamps use a local zone
  inferred from a sufficiently complete `tracking_location`; otherwise they use
  UTC.
- `POST /v2/trackers/batch` accepts up to 100 tracking codes.

Tracker lists default to one month ago through the current day's end. A single
datetime bound creates a one-month span around that bound; older matches need an
explicit `start_datetime`. `page_size` defaults to 20 and caps at 100.

The API `carrier` value is not always the display name. Preserve exact strings
such as `ColumbusLastMile`, `DhlEcs`, `LaserShipV2`, `PassportGlobal`,
`TforceConcise`, and `UspsShip`.

See [trackers.md](references/trackers.md) for status detail, carrier detail,
test-mode codes, and deletion behavior.

## SDK and API migration guardrails

For the Node.js SDK:

- Use a supported runtime; Node 16 support was dropped.
- Replace `superagentMiddleware` with `httpMiddleware`.
- Replace `fetchClient` with `httpClient`.
- Account for the SDK using `fetch` instead of `superagent`.
- Treat returned API resources as plain JSON-compatible objects, not model-class
  instances.

The C#, Java, Node.js, PHP, and Ruby SDKs expose a generic request interface for
arbitrary endpoints, including endpoints without typed resource wrappers.
Supported API endpoints standardize timestamps as ISO 8601.

Index endpoints have request-per-second rate limiting. Integrations that
enumerate resources must tolerate throttling rather than assume unrestricted
pagination.

See [sdk-and-api.md](references/sdk-and-api.md) for the consolidated migration
surface.

## Account, event, and subscription quick reference

- Carrier-account APIs cover registration, platform-account types and
  configuration, and team-authorized status updates. Platform account
  availability exposes access and setup options.
- BYOCA support extends to all users, and most carrier accounts no longer need a
  separate manual registration step.
- Groups support subgroup creation, viewing, listing, and deletion, plus
  sub-account assignment. Sub-account lists can include group information.
- `shipment.invoice.updated` reports billed-shipment disputes.
- `payment.created` and `payment.failed` are emitted again for bank and
  credit-card charges.
- Embeddable components and customer portals can create JWT-authenticated
  sessions.
- SAML invitations accept `return_to_url` for the post-acceptance destination.
- Advanced Tracking subscriptions can be canceled, and their brand
  customization can be synchronized.
- A subscription plan can be charged immediately when it is created.

See [accounts-events-and-subscriptions.md](references/accounts-events-and-subscriptions.md)
for the complete platform-operation details.

## Integration review checklist

- Test omission separately from `false` for address verification keys.
- Keep immutable-resource creation payloads complete.
- Store generated Shipment and Tracker IDs where deterministic retrieval is
  required.
- Use plural `tracking_codes` only on the Tracker list endpoint.
- Request older list data with explicit datetime bounds and respect page-size
  caps.
- Preserve carrier API strings exactly.
- Accept ISO 8601 timestamps and the documented tracker status set.
- Handle throttling while enumerating index endpoints.
- Recheck Node.js middleware, HTTP client, runtime, and returned-object
  assumptions during SDK upgrades.
- Apply carrier-specific delivery, customs, claim, and label rules before
  purchase.
