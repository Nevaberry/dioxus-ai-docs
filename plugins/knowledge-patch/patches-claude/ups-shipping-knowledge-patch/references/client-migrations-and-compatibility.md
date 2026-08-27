# Client Migrations and Compatibility

## Track Alert v2

Track Alert and Track Alert with Photo are premium APIs available globally.
Their events include `gmtOffset` in `(-/+)HH.MM` form to explain local-time
conversion.

Version 2 of both APIs removes the `destination` object. Migrating clients must
not require or deserialize it.

## Consistent array responses

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

## DigiCert trust-store migration

Clients that connect to `onlinetools.ups.com` with a locally maintained
certificate trust store must follow the DigiCert migration guidance and update
that store.

Browser clients and systems that automatically trust public certificate
authorities need no action.

## Expanded error-code surface

Shipping exposes these Label Recovery codes:

- `9801061`
- `9801062`
- `9801064`
- `9801065`
- `9801067`

Shipping also exposes code `120466`, and the description of `120200` changed.
Dangerous Goods adds `9190048`, and Pre Notification adds `9290059`.

Error handlers must accept these as known UPS codes.
