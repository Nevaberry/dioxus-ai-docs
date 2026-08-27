# Migrations and platform integration

## Track Alert v2

Track Alert and Track Alert with Photo are premium APIs available globally.
Their events include `gmtOffset` in `(-/+)HH.MM` form to explain local-time
conversion.

Version 2 of both APIs removes the `destination` object. Migrating clients must
not require or deserialize it.

## Shipping, Pickup, account, and tracking schemas

`LabelDelivery_EMail` no longer has:

- `UndeliverableEMailAddress`
- `FromEMailAddress`
- `FromName`
- `Memo`
- `Subject`
- `SubjectCode`

`Master_SoldTo.AttentionName` is no longer required.

Pickup creation adds `Notification` and
`PickupCreationRequest_Notification`. `StateProvince` is optional.

Open Account adds `RateTypeCode` and `RateConstructCode`.

Track by Reference Number adds `destCountry`, `destZip`, and `shipperNum`.

## Consistent arrays by API version

New API versions make fields documented as arrays consistently return arrays.

Use `v2403` for:

- Shipping
- Rating
- Pickup
- Dangerous Goods Chemical Reference Data

Use `v2` for:

- Dangerous Goods Acceptance Audit Pre-check
- Pre Notification
- Paperless Documents
- Locator
- Quantum View
- Ship Void
- Address Validation
- Landed Cost

Older paths retain inconsistent scalar-or-array behavior for compatibility.

## DigiCert trust-store migration

Clients that connect to `onlinetools.ups.com` with a locally maintained
certificate trust store must follow the DigiCert migration guidance and update
that store.

Browser clients and systems that automatically trust public certificate
authorities need no action.

## OAuth callback registration

Authorization-code callbacks may use localhost. A localhost URL must use
`http://` and include a port.

Supplied `state` and `scope` query parameters are returned to the client.

Enter multiple callback URLs as a comma-separated list with no spaces:

```text
http://localhost:3000/callback,https://shop.example.com/ups/callback
```

## OAuth Steppingstone mode

For migrations that cannot yet replace SOAP/XML payloads with REST payloads,
the Steppingstone model accepts the existing SOAP/XML format while moving
authentication to OAuth 2.0.

## Developer Portal security and onboarding

Accessing API credentials or an application in the Developer Portal prompts
users to reauthenticate with MFA.

Commerce Guard and Global Checkout can be requested directly through the
application add/edit flow.

## Central webhook credentials

Manage Webhook Credentials configures and maintains webhook credentials
centrally instead of managing them separately at each integration point.

## UPS MCP server

UPS provides an MCP server exposing Track and Address Validation tools for
agent integrations.
